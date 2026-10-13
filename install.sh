#!/bin/sh
# install.sh — the Nerv bootstrap. Fetch the installer, verify it, run it. Nothing else.
#
#     curl https://nervlinux.org/install.sh | sh
#
# This file is short on purpose. It is the one thing everybody pipes to a shell, so it has to be
# readable in full before you run it, and it must contain no install logic: no partitioning, no
# network setup, no decisions about your disks. All of that lives in the binary it fetches, and
# that binary is verified against the key below — which is the whole security argument for a
# `curl | sh`. A bootstrap that fetches an UNVERIFIED binary is a different and much worse thing.
#
# POSIX sh, no bashisms: this runs on whatever the machine already has.
set -eu

# Where everything is fetched from. `nerv-repo put --dest install.sh` rewrites this line to the
# host it publishes to, so the copy served from an artifact host points at THAT host — which is
# what makes `curl http://<host>/install.sh | sh` complete on its own, with nothing to set and
# nothing to remember. NERV_BASE still overrides, for a mirror somewhere else.
BASE="${NERV_BASE:-http://repo.nervlinux.org}"

# The verify key: the Nerv installer signing key, ed25519, public half.
#
# This is the whole security argument for a `curl | sh`. The script is short enough to read in
# full before you run it, and everything it fetches afterwards is checked against the key you
# just read — so trusting this pipeline means trusting these lines and nothing else about the
# server that served them. A bootstrap that fetched an UNVERIFIED binary would be a different
# and much worse thing wearing the same command line.
#
# ed25519 rather than RSA because the point is that it fits on a screen, and openssl verifies
# it with no extra flags on every host this has to run on (Fedora, WSL2, Nerv).
VERIFY_KEY="-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAtTQJmRtNETYIqWBGuk6L7X23g4szNL0QKM1bBgaIo9g=
-----END PUBLIC KEY-----"

die() { printf '\033[1;31minstall.sh:\033[0m %s\n' "$*" >&2; exit 1; }
say() { printf '\033[1;36m::\033[0m %s\n' "$*"; }

# --- 1. what are we running on? ------------------------------------------------------------
case "$(uname -s)" in
    Linux) ;;
    *) die "$(uname -s) is not supported yet — the installer is Linux-only (Apple and WSL2 are
        separate work). You can still install from any Linux machine on the same network." ;;
esac
case "$(uname -m)" in
    aarch64|arm64) ARCH=aarch64 ;;
    x86_64|amd64)  ARCH=x86_64 ;;
    *) die "unsupported architecture: $(uname -m)" ;;
esac

# --- 2. the tools this script itself needs -------------------------------------------------
if command -v curl >/dev/null 2>&1; then
    FETCH='curl -fsSL -o'
elif command -v wget >/dev/null 2>&1; then
    FETCH='wget -qO'
else
    die "neither curl nor wget is available"
fi

BIN="nerv-install-$ARCH"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/nerv-install.XXXXXX")"
# Clean up on every exit path, including the failures. A half-downloaded installer left in /tmp
# is exactly the thing someone runs by hand a week later.
trap 'rm -rf "$WORK"' EXIT INT TERM

# --- 3. decide the verification policy BEFORE downloading anything -------------------------
# Order matters for the error you get: checking after the fetch means a 404 or a DNS failure
# masks the policy message, and the operator is told the wrong thing about why nothing ran.
if [ -z "$VERIFY_KEY" ] && [ "${NERV_INSTALL_UNVERIFIED:-0}" != "1" ]; then
    die "this bootstrap carries no verify key yet (signing is issues #8 and #121), so it will not
        fetch an unverified binary. If you understand that and want it anyway:

            curl $BASE/install.sh | NERV_INSTALL_UNVERIFIED=1 sh"
fi

say "fetching $BASE/bin/$BIN"
# shellcheck disable=SC2086
$FETCH "$WORK/$BIN" "$BASE/bin/$BIN" || die "could not fetch $BASE/bin/$BIN"

# --- 4. verify before executing ------------------------------------------------------------
if [ -n "$VERIFY_KEY" ]; then
    # shellcheck disable=SC2086
    $FETCH "$WORK/$BIN.sig" "$BASE/bin/$BIN.sig" || die "no signature for $BIN"
    command -v openssl >/dev/null 2>&1 || die "openssl is needed to verify the installer"
    printf '%s\n' "$VERIFY_KEY" > "$WORK/verify.pem"
    # pkeyutl -rawin, not `dgst -verify`. Ed25519 signs the message itself rather than a digest
    # handed to it, so `dgst` refuses the key outright — and the failure looks exactly like a bad
    # signature, which would send anyone debugging it after the wrong thing entirely.
    openssl pkeyutl -verify -pubin -inkey "$WORK/verify.pem" \
        -rawin -in "$WORK/$BIN" -sigfile "$WORK/$BIN.sig" \
        >/dev/null 2>&1 || die "SIGNATURE CHECK FAILED for $BIN — refusing to run it"
    say "signature verified"
else
    printf '\033[1;33mwarning:\033[0m no verify key is embedded in this bootstrap, and\n'
    printf '         NERV_INSTALL_UNVERIFIED=1 was set, so %s is being run UNVERIFIED.\n' "$BIN"
    printf '         Anything that can answer %s can decide what runs on your machine.\n' "$BASE"
fi

# --- 5. hand over --------------------------------------------------------------------------
# With no arguments this brings up the provisioning server and its dashboard, because that is
# what the operator running `curl … | sh` on their own machine wants: the target is a different
# machine and netboots. Any argument goes straight through, so `… | sh -s -- install --device …`
# still reaches the installer verbs.
[ "$#" -gt 0 ] || set -- serve
chmod +x "$WORK/$BIN"

# Privilege, and only here.
#
# Netboot needs two ports the target's firmware chooses rather than we do: TFTP's udp/69 and
# DHCPv6's udp/547. Both are privileged, so the server cannot come up without root.
#
# Everything above this line ran as the operator — the download, the key, the signature check.
# Escalating only for the last step means root runs one binary whose signature has already been
# checked, instead of a script piped in from the network. That is the better shape, and it is
# why this is at the bottom rather than a `doas sh` at the top.
#
# `env` carries NERV_BASE across: doas and sudo both clear the environment by default, so
# setting it on the exec line alone would drop it silently and send a mirror-based install back
# to the default host.
if [ "$(id -u)" -ne 0 ]; then
    for esc in doas sudo; do
        command -v "$esc" >/dev/null 2>&1 || continue
        say "netboot needs udp/69 and udp/547, so this last step asks for $esc"
        exec "$esc" env NERV_BASE="$BASE" "$WORK/$BIN" "$@"
    done
    # Name the ports and what they were for. A server that comes up without them looks healthy
    # and cannot boot anything, which is the failure this refuses to ship.
    die "netboot needs root for udp/69 and udp/547, and neither doas nor sudo is here.
       Re-run as root, or: NERV_BASE=$BASE $WORK/$BIN $*"
fi

say "starting the installer"
# exec, so the installer owns the terminal and this script is not in the signal path. WORK is
# removed by the trap only if exec fails, which is correct: after exec there is no script left.
NERV_BASE="$BASE" exec "$WORK/$BIN" "$@"
