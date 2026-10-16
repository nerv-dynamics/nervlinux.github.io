---
title:    Install
kind:     use
one-line: From a bare box to a running machine over the network — one command on a machine
          you already have, and no USB stick.
---

# Install

Installing Nerv needs two machines: the one you are sitting at, and the one you are installing.
Nothing is written to removable media, and nothing is typed into the target. The machine you are
sitting at becomes the installer; the target boots from it over the network.

You need:

- the **target** on the same network, able to boot from the network in its firmware
- the **operator machine**, any Linux box, with `curl` and `openssl`
- the target's disk, which **will be erased**

## Start the installer

One command. It fetches the installer, checks it against the key embedded in the script you just
read, and hands over:

```
$ curl -fsSL http://<host>/install.sh | sh
:: fetching http://<host>/bin/nerv-install-aarch64
:: signature verified
:: starting the installer
```

That is the whole bootstrap, and it is short on purpose: it contains no install logic, so it can be
read in full before it is run. Everything it fetches afterwards is checked against the key printed
in the script itself. Read it first if you like — `curl http://<host>/install.sh` alone prints it.

That includes the generation. Before anything is written to a disk, the installer checks the
signature on the file that says what the generation contains, and **refuses it outright if it
does not verify** — there is no override, because a truncated download and a tampered one look
identical at that point. One consequence you can meet in practice: a generation published
before this check existed carries no such signature and will be refused, so an old one has to be
republished before you can install from it.

A dashboard opens. Its header is the two ways a target can reach it — the first needs nothing
set anywhere, the second is the pair of values a DHCP server asks for — and what a target that
boots now will install:

```
  Nerv Linux - Netboot Server
  IPv6 - no configuration needed - [fd00:6e65:7276::1]
  IPv4 - set DHCP 66 to 10.0.0.5 and 67 to nerv-installer.efi
  Serving - gb10 2026-09-23 · kernel 7.2.7 · workstation

┌ Machines connected: 0 ─────────────────────────────────────────────┐
│  No machines visible                                               │
│                                                                    │
│  A machine joins this fleet by netbooting from the address above.  │
│  Nothing is written to any machine until you say so.               │
└────────────────────────────────────────────────────────────────────┘
  ↑↓ select   ⏎ configure   r reboot   s settings   q quit
```

## Boot the target

Set the target to boot from the network, and turn it on. On the same network segment that is
everything — the installer answers the target's own question about where to boot from, so there
is nothing to configure on either machine and nothing to undo afterwards.

Nothing is typed into the target either: no installer media, no kernel arguments, no console, and
no boot entry to create in its firmware.

### If the target is elsewhere, or its firmware has no IPv6

Then the network has to carry the answer, which is two fields every DHCP server has — a home
router or a corporate one:

| field | value |
|---|---|
| next-server, or *option 66* | the address the dashboard printed |
| boot filename, or *option 67* | `nerv-installer.efi` |

On a UniFi this is *Network → Advanced → Network Boot*; on dnsmasq it is `dhcp-boot`.

Worth knowing: **a boot filename applies to the whole network**, so anything else that netboots
while it is set also reaches this installer. Undo it when you are finished.

### What to turn off in the firmware first

Two settings are worth changing while you are in there, because the firmware is the one part of
the boot the machine cannot improve for you. On this board it is the largest phase of the boot by
some margin, and nothing below it can start until it is done.

| setting | why |
|---|---|
| **Quiet boot** (the vendor logo) — off | Drawing a logo means bringing up the display before anything needs it, and it hides the firmware's own progress while it does. Turning it off both removes the work and lets you see where the time goes. |
| **Network boot / PXE option ROMs** — off, once installed | Every enabled ROM is initialised at power-on and torn down again at hand-off. Leave them on until the network install is finished; turn them off afterwards. |

Both are worth measuring rather than sensing, and the machine keeps the number for you. The
firmware writes its own elapsed time into an EFI variable before the boot loader starts:

```
$ doas cat /sys/firmware/efi/efivars/LoaderTimeInitUSec-4a67b082-0a4c-41cf-b6c7-440b29bb8c4f \
    | tail -c +5 | tr -d '\0'
9802453
```

Microseconds, from power-on to the loader's first instruction — 9.8 seconds on that machine, of
a 19.5 second boot. Read it before the change and after. Anything that moves that number is real;
anything that does not, is not, however different it feels.

`systemd-analyze` prints the same figure as its `firmware` term, alongside every phase that
follows it:

```
$ doas systemd-analyze
Startup finished in 9.802s (firmware) + 2.167s (loader) + 1.472s (kernel)
  + 2.794s (initrd) + 3.243s (userspace) = 19.537s
```

### Why it asks for a password

The two ports a firmware asks on — `69` and `547` — are privileged, so the last step needs root.
The download and the signature check happen as you, before that; only the verified binary is run
with privilege.

The target appears on the dashboard when it has booted and reported itself:

```
  MACHINE            PLATFORM   DISKS  PHASE         LAST SEEN   PROGRESS
▌ 52:54:00:12:34:56  qemu-aarch 1      booted 3/11   waiting 2m  ██████──────
```

It will wait there indefinitely. **Nothing is written to the disk until you launch the install**,
and a machine that is waiting has not been touched.

## Configure it

Press `⏎` on the machine. The pane shows what it reported about itself — cores, memory, whether it
has a TPM, whether its firmware will take a Secure Boot key, and each disk it found — and the
settings the install will use:

```
┌ configure ─────────────────────────────────────────────────────────┐
│▌hostname    -                                                      │
│ disk        /dev/nvme0n1                                           │
│ encrypt     yes                                                    │
│ secure boot yes                                                    │
│ user        -                                                      │
│ password    -                                                      │
│ ssh key     -                                                      │
│ shell       /usr/bin/fish                                          │
│ keymap      us                                                     │
│ subvol      @nerv                                                  │
└────────────────────────────────────────────────────────────────────┘
  ↑↓ field   ⏎ edit/toggle   i INSTALL   esc back
```

Set at minimum a **hostname** and an **account** — a user with either a password or an SSH key.
An account with neither is refused: it produces a machine nobody can log into.

The **keymap** is set once here and holds everywhere. Two namespaces name the same keys and they
do not agree: the kernel's virtual console calls Dvorak `dvorak`, while XKB has no layout by that
name at all — it is layout `us`, variant `dvorak`. The installer looks the console name up in
systemd's `kbd-model-map` and writes all three keys to `/etc/vconsole.conf`:

```
KEYMAP=dvorak
XKBLAYOUT=us
XKBVARIANT=dvorak
```

`KEYMAP` is what `systemd-vconsole-setup` applies to the kernel VT — early boot, emergency mode,
anything before a userspace terminal. `XKBLAYOUT` and `XKBVARIANT` are what the kmscon console and
any Wayland compositor read. Naming only the console layout to an XKB consumer does not fall back
to something sensible; it fails the whole keymap compile (`[XKB-822] Failed to compile keymap`) and
leaves you at a dead keyboard.

Which **profile** is installed is a setting of the installer rather than of the machine, on the `s`
page: `core`, `workstation`, `workstation-gui` or `dev`.

Press `i` to install. That is the only destructive action in this chapter, and it is the first
moment anything is written to the target.

## Watch it

The row tracks the install through eleven phases. It takes a few minutes, most of it transferring
and unpacking the system:

```
▌ 52:54:00:12:34:56  qemu-aarch 1      done 11/11    1s          ████████████
```

At `done 11/11` the disk is bootable and the machine **stays on the list**, still reporting. It has
not rebooted and will not until you say so.

## Reboot into it

Press `r`. The target takes the order on its next poll and boots the system you just installed:

```
  52:54:00:12:34:56: reboot sent; it goes down on its next poll
```

You do not need to change anything in the target's firmware first. The install put the new system's
boot entry ahead of the network entry it arrived on, so it boots from its own disk from here on.

Then log in over the network, with the account you configured:

```
$ ssh <user>@<hostname>
```

## Secure Boot, after the install

`secure boot yes` means the machine makes its own key, signs what it boots with it, and enrols
that key into the firmware. The firmware takes a new key only in **setup mode**, with no
platform key enrolled, so the installer asks it first: **a machine whose firmware already holds
a platform key is refused before anything is written to its disk**, with what to clear. The
configure pane shows the answer before you press `i`, as `secure boot ready (setup mode)` or
`secure boot keys enrolled: clear them to sign`.

If the firmware takes the check and then refuses the enrolment anyway, the install fails and
says so. By then the disk is written and bootable, so that costs you the exit status and not
the install: you can fix the cause and enrol afterwards with the command below.

One case is not a failure. A firmware that implements no Secure Boot at all has nothing to
enrol into, and the install says that and continues — there is no key you can give a board that
does not have the feature.

Enrolling does not by itself make the machine enforce. `SecureBoot` reads 0 until the firmware
re-evaluates it at the next boot, and only if Secure Boot is switched on in the firmware setup
menu.

Ask the machine itself:

```
$ doas nerv-install secureboot
firmware
  SetupMode        1 — no platform key, so key variables may be written directly
  SecureBoot       0 — not enforcing
  PK               absent
  KEK              2 certificates, this machine's: NO
  db               4 certificates, this machine's: NO

this machine
  key directory    /etc/nerv/secureboot
  db certificate   SHA256 5E:AD:0D:06:…
  esp              /efi
  artifact         /efi/EFI/Linux/nerv.efi
                     signed, and carries this machine's certificate
```

That is a machine trusting Microsoft's keys and not its own — an older install, or one whose
firmware has no Secure Boot. To enrol, or to run the writes again after fixing whatever the
firmware objected to:

```
$ doas nerv-install secureboot --enrol --yes
```

It writes db, then KEK, then PK. **PK is what leaves setup mode**, so it goes last: writing it is
the moment the firmware starts enforcing, and from then on the machine boots only what this key
signed.

> **Read this before you enrol: an enforcing machine cannot be netbooted.**
>
> db ends up holding this machine's key and nothing else — not Microsoft's, not the build
> host's. That is the point; it means no key exists anywhere that can boot your whole fleet.
> The netboot installer is signed by nobody for the same reason, so a machine that is
> enforcing refuses it:
>
> ```
> invalid signature detected
> ```
>
> That is the firmware working, not a broken image. **To reinstall an enrolled machine, clear
> its Secure Boot keys in the firmware menu first** — the entry is usually *Erase all Secure
> Boot settings*, *Delete PK* or *Reset to Setup Mode*. Switching Secure Boot off is not
> enough: it stops enforcement and leaves the keys, and the new install's key cannot go in
> while the old one is there. Then netboot and install as normal, and switch Secure Boot back
> on. One trip to the firmware per reinstall.
>
> It does not affect ordinary upgrades. A running machine updates into its other slot over the
> network and never netboots, so the firmware is not involved. Check the artifact lines say *carries this machine's certificate* first — the command
refuses outright if there is nothing signed on the ESP to boot.

If the firmware will not take them, the command says which variable it refused and how far it got,
and the certificates are on the ESP under `nerv/secureboot/` for a firmware key-management menu to
import by hand.

## If the install fails

The row turns red and names the phase it stopped in, and the machine is left alone — it does not
reboot, so the console keeps the reason. `r` is refused on a machine whose install failed, because
rebooting it would boot whatever was on the disk before.

Reconfigure and press `i` again. A launch applies to one install: a machine that boots the
installer again waits for a new one rather than repeating the last.

## What a virtual machine cannot show you

A VM is a complete rehearsal of everything above except the TPM. Encryption itself is real in a
guest — it is ordinary dm-crypt — but a machine unlocks itself with a TPM keyslot, and a guest
has no TPM unless one is arranged for it. So a virtual target is configured with `encrypt` off, and
that one path is only ever exercised on real hardware.
