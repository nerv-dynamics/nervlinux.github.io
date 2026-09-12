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

A dashboard opens. Its header is the two ways a target can reach it — the first needs nothing
set anywhere, the second is the pair of values a DHCP server asks for:

```
  Nerv Linux - Netboot Server
  IPv6 - no configuration needed - [fd00:6e65:7276::1]
  IPv4 - set DHCP 66 to 10.0.0.5 and 67 to nerv-installer.efi

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
has a TPM, and each disk it found — and the settings the install will use:

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

## If the install fails

The row turns red and names the phase it stopped in, and the machine is left alone — it does not
reboot, so the console keeps the reason. `r` is refused on a machine whose install failed, because
rebooting it would boot whatever was on the disk before.

Reconfigure and press `i` again. A launch applies to one install: a machine that boots the
installer again waits for a new one rather than repeating the last.

## What a virtual machine cannot show you

A VM is a complete rehearsal of everything above except encryption. No emulator implements the
drive-native encryption Nerv uses, so a virtual target must be configured with `encrypt` off, and
that one path is only ever exercised on real hardware.
