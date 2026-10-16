# Install

Nerv installs over the network from any Linux machine you already have: one command turns that machine into the installer, and the GB10 you are installing boots from it, with no USB stick and nothing typed into the target.

Nerv installs on **GB10** machines. RTX Spark and GB300 are on the roadmap.

You need:

- the **target**, on the same network, set to boot from the network in its firmware
- the **operator machine**, any Linux box, with `curl` and `openssl`
- the target's disk, which **will be erased**

## Start the installer

One command. It fetches the installer, checks its signature against the key embedded in the script, and hands over:

```
$ curl -fsSL https://nervlinux.org/install.sh | sh
:: fetching http://repo.nervlinux.org/bin/nerv-install-x86_64
:: signature verified
:: netboot needs udp/69 and udp/547, so this last step asks for sudo
:: starting the installer
```

The script contains no install logic, so it is short enough to read in full before you run it: `curl https://nervlinux.org/install.sh` prints it. Everything it fetches is checked against the key printed in the script itself.

That includes the generation. Before anything is written to a disk, the installer checks the signature on the generation's manifest and **refuses a generation that does not verify**. There is no override.

The last step asks for `doas` or `sudo` because the two ports a firmware boots from, `69` and `547`, are privileged. The download and the signature check run as you; only the verified binary runs as root.

A dashboard opens. Its header shows the two ways a target can reach it — the first needs nothing set anywhere, the second is the pair of values a DHCP server asks for — and what a target that boots now will install:

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

Set the target to boot from the network and turn it on. On the same network segment that is all: the installer answers the target's own question about where to boot from, so there is nothing to configure on either machine and nothing to undo afterwards. Nothing is typed into the target either — no installer media, no kernel arguments, no console, and no boot entry to create in its firmware.

The target appears on the dashboard once it has booted and reported itself:

```
  MACHINE            PLATFORM   DISKS  PHASE         LAST SEEN   PROGRESS
▌ 4c:bb:47:12:34:56  gb10       1      booted 3/11   waiting 2m  ██████──────
```

It waits there indefinitely. **Nothing is written to the disk until you launch the install.**

### If the target is on another network, or its firmware has no IPv6

Then the network carries the answer, in two fields every DHCP server has, whether a home router or a corporate one:

| field | value |
|---|---|
| next-server, or *option 66* | the address the dashboard printed |
| boot filename, or *option 67* | `nerv-installer.efi` |

On a UniFi this is *Network → Advanced → Network Boot*; on dnsmasq it is `dhcp-boot`.

**A boot filename applies to the whole network**, so anything else that netboots while it is set also reaches this installer. Remove it when you are finished.

### Two firmware settings to change

The firmware is the largest phase of the boot on a GB10, and the one part the system cannot speed up for you. Two settings make it faster:

| setting | why |
|---|---|
| **Quiet boot** (the vendor logo) — off | Drawing the logo brings up the display before anything needs it and hides the firmware's own progress. Off, the work is gone and you can see where the time goes. |
| **Network boot / PXE option ROMs** — off, once installed | Every enabled ROM is initialised at power-on and torn down at hand-off. Leave them on until the install is finished, then turn them off. |

The firmware records its own elapsed time, in microseconds from power-on to the boot loader's first instruction, in an EFI variable:

```
$ doas cat /sys/firmware/efi/efivars/LoaderTimeInitUSec-4a67b082-0a4c-41cf-b6c7-440b29bb8c4f | tail -c +5 | tr -d '\0'
9802453
```

`systemd-analyze` shows the same figure as its `firmware` term, beside every phase that follows it:

```
$ doas systemd-analyze
Startup finished in 9.802s (firmware) + 2.167s (loader) + 1.472s (kernel) + 2.794s (initrd) + 3.243s (userspace) = 19.537s
```

Read it before a change and after.

## Configure it

Press `⏎` on the machine. The pane shows what the machine reported about itself — cores, memory, whether it has a TPM, whether its firmware will take a Secure Boot key, and each disk it found — and the settings the install will use:

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

Set at least a **hostname** and an **account**: a user with a password, an SSH key, or both. An account with neither is refused, because nobody could log into the machine.

The **keymap** is set once here and holds everywhere: on the console from early boot, and in any Wayland compositor. The console and XKB name layouts differently — the console's `dvorak` is XKB's layout `us`, variant `dvorak` — so the installer writes both to `/etc/vconsole.conf`:

```
KEYMAP=dvorak
XKBLAYOUT=us
XKBVARIANT=dvorak
```

`KEYMAP` is what the console uses from early boot; `XKBLAYOUT` and `XKBVARIANT` are what kmscon and any Wayland compositor read.

The **profile** is chosen on the installer's settings page, `s`:

| profile | what you get |
|---|---|
| `core` | the machine and a complete, austere Unix |
| `workstation` | core plus the tools a person works with every day |
| `workstation-gui` | workstation plus the desktop: a graphical login, Umbriel, Noctalia and a terminal |
| `dev` | core plus the musl LLVM toolchain and packaging tools, for a machine that builds Nerv packages |

Press `i` to install. It is the only destructive action in this chapter, and the first moment anything is written to the target.

## Watch it

The row tracks the install through eleven phases. It takes a few minutes, most of them spent transferring and unpacking the system:

```
▌ 4c:bb:47:12:34:56  gb10       1      done 11/11    1s          ████████████
```

At `done 11/11` the disk is bootable and the machine **stays on the list**, still reporting. It does not reboot until you say so.

## Reboot into it

Press `r`. The target takes the order on its next poll and boots the system you just installed:

```
  4c:bb:47:12:34:56: reboot sent; it goes down on its next poll
```

There is nothing to change in the target's firmware. The install puts the new system's boot entry ahead of the network entry it arrived on, so from now on it boots from its own disk.

Log in over the network with the account you configured:

```
$ ssh <user>@<hostname>
```

## Secure Boot

With `secure boot yes`, the machine makes its own key, signs what it boots with it, and enrols that key into the firmware.

The firmware accepts a new key only in **setup mode**, with no platform key enrolled. The configure pane shows which state the firmware is in before you press `i`: `secure boot ready (setup mode)`, or `secure boot keys enrolled: clear them to sign`. **A machine whose firmware already holds a platform key is refused before anything is written to its disk**, and the pane says what to clear.

If the firmware refuses the enrolment during the install, the install reports it as failed, but the disk is already written and bootable: fix the cause and enrol afterwards with the command below. A firmware with no Secure Boot at all has nothing to enrol into; the install says so and continues.

Enrolling does not make the machine enforce on its own. `SecureBoot` reads 0 until the next boot, and enforcement starts only if Secure Boot is switched on in the firmware setup menu.

The machine shows its own state:

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

That machine trusts Microsoft's keys and not its own. To enrol, or to retry after fixing whatever the firmware objected to, first check that the artifact line reads *carries this machine's certificate*, then:

```
$ doas nerv-install secureboot --enrol --yes
```

It writes db, then KEK, then PK. Writing **PK** ends setup mode, so it goes last: from then on the machine boots only what its own key signed. If the firmware refuses a variable, the command says which one and how far it got, and the certificates are on the ESP under `nerv/secureboot/` for the firmware's key-management menu to import by hand.

> **An enforcing machine cannot be netbooted.** Its db holds this machine's key and nothing else — not Microsoft's, not ours — so no key anywhere can boot your whole fleet. The netboot installer is signed by nobody for the same reason, and an enforcing machine refuses it with `invalid signature detected`.
>
> **To reinstall an enrolled machine, clear its Secure Boot keys in the firmware menu first.** The entry is usually *Erase all Secure Boot settings*, *Delete PK* or *Reset to Setup Mode*. Switching Secure Boot off is not enough: the old keys stay, and the new install's key cannot go in beside them. Netboot and install as usual, then switch Secure Boot back on.
>
> Updates are unaffected. A running machine updates into its other slot over the network and never netboots.

## If the install fails

The row turns red and names the phase it stopped in. The machine does not reboot, so its console keeps the reason, and `r` is refused, because rebooting would boot whatever was on the disk before.

Reconfigure and press `i` again. A launch applies to one install: a machine that boots the installer again waits for a new launch rather than repeating the last one.
