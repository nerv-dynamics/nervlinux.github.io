# Updates and generations

How Nerv updates itself without ever touching the system you are running: every update is a new slot, built beside the running one, proved to boot to a login, and put on trial, and a slot that fails sends the machine back to the one before by itself. `cage` is the program that does it, and the one you use to see and manage the slots.

## Synopsis

After reading this chapter, you will know:

- what a slot is, and what is kept outside every slot
- how to update the machine, and how to tell when an update waits for a reboot
- what happens on the first boot of a new slot, and when the machine goes back on its own
- how to roll back, try a change for one boot, and clean up old slots

Before reading it, you should know:

- how to open a terminal and use `doas`: [The first hour](the-first-hour.md)

## Why it works this way

An update that changes the system in place asks you to trust it twice: that every package it replaces works, and that the machine still boots once it is done. When either is wrong, you find out at the next reboot, on a system that is already changed, with the working one gone.

Nerv never updates the system you are running. An update copies it into a new slot, upgrades the copy, seals it into a signed boot image, and boots that image in a virtual machine, logging in as a person would, before the real machine ever sees it. Only then is it set to boot, on trial: it gets three tries to come all the way up, and if it never does, the machine boots the slot you had before, by itself, with nobody at the keyboard. The slot you updated from stays the default until its successor has proved itself, so there is always a system that has booted to go back to.

Two things follow for you. An update is never an emergency: it is built while you work, and takes effect at a reboot you choose. And going back is not a repair: the previous system is still there, whole, one key away.

The idea is older than Nerv: Solaris boot environments and NixOS generations got there first.

Ordinary programs do not wait for any of this. `dnf install`, `dnf remove` and `dnf upgrade` change the running system at once, as long as nothing in the boot path changes; an upgrade that reaches the kernel, the GPU driver, systemd, the initrd tools, cryptsetup or the platform package is refused with a pointer to `cage update`. [Installing software](software.md) has the details.

## What a slot is

A slot is a whole system: `/usr`, `/etc` and `/var`, with its own kernel and initrd sealed into one signed boot image. Slots sit side by side on the same encrypted disk, as btrfs snapshots of each other, so a new one costs no space until it changes.

Two things are in no slot, and every slot shares them:

- **your home directory**, `/home`, so booting another slot changes the system and never your files
- **the machine's own data**, `@data`, which holds `/var/log`: every slot writes the same journal, so `journalctl` on any slot shows what every slot logged

> **Note.** A machine installed before `@data` existed moves its logs there once, with `cage shared`. The journal moves whole, nothing written while it moves is lost, and running it again changes nothing.

## Opening cage

Run `cage` with no arguments:

```tui cage
 EVA    booted @nerv-20261117-1058   on trial @nerv-20261117-1159                           up 1h 9m  7.3.4  nerv-1
╭─ SLOTS ──────────────────────────────────────── 8 ─╮╭─ SLOT ────────────────────────────────────────────── stable ─╮
│   █ @home            foreign ?       ···· unsealed ││ @nerv-20261117-1058                                  stable  │
│   █ @nerv-20261108-. staging 7.3.3   ····  blessed ││ ──────────────────────────────────────────────────────────── │
│   █ @nerv-20261112-. staging 7.3.3   ····  blessed ││                                                              │
│   █ @nerv-20261116-. staging 7.3.4   ····  blessed ││ subvol     /mnt/nerv-top/@nerv-20261117-1058                 │
│ ▌ █ @nerv-20261117-. stable  7.3.4   bd··  blessed ││ modified   10d 17h ago                                       │
│   █ @nerv-20261117-. preferr 7.3.4   ··p·  3/3 try ││ kernel     7.3.4                                             │
│   █ @nerv-rescue     rescue  7.2.8   ····  blessed ││ artifact   nerv-20261117-1058.efi                            │
│   █ @swap            foreign ?       ···· unsealed ││ format     uki                                               │
│                                                    ││ integrity  signed  pcr11-policy                              │
│                                                    ││ size       38.5 MiB                                          │
│                                                    │╰──────────────────────────────────────────────────────────────╯
│                                                    │╭─ STORAGE ────────────────────────────────────────────────────╮
│                                                    ││ ESP  /efi           ██▋              19%  378 MiB / 2.0 GiB  │
│                                                    ││ ROOT /mnt/nerv-top  █▋               12%  436 GiB / 3.6 TiB  │
╰────────────────────────────────────────────────────╯╰──────────────────────────────────────────────────────────────╯
╭─ LOG ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ no output yet — pick a slot and press a verb key (? for help)                                                      │
│                                                                                                                    │
│                                                                                                                    │
│                                                                                                                    │
│                                                                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
 ↑↓ select  u update  n new  e exec  s / S seal  v validate  b boot  p promote  r rollback  t try  d delete
```

- **SLOTS**, on the left, lists every slot, with its role, its kernel and whether it has booted. `↑` and `↓` select one.
- **SLOT** shows the selected slot: when it was changed, its kernel, its boot image and whether that image is signed.
- **STORAGE** shows the boot partition and the disk.
- **LOG** shows the output of whatever cage is doing.
- The top line says which slot is running and which, if any, is on trial; the bottom line lists the keys, and `?` explains each one.

A key that changes what the machine boots, or removes anything, shows what it will do and waits: `y` or `enter` goes ahead, `esc` cancels. cage asks for `doas` itself when it needs it, from the dashboard and from the command line alike.

A slot's role says what the machine does with it:

| role | |
| --- | --- |
| `stable` | the default: what the machine boots when nothing is on trial |
| `preferred` | a slot on trial, booted ahead of the default |
| `rescue` | the slot made at install, never updated: [The rescue slot](#the-rescue-slot) |
| `staging` | neither: an older system, or one being built |
| `foreign` | not a system: `@home`, `@data` and `@swap`, which every slot shares |

`blessed` means the slot has completed a boot. `3/3 try` means it is on trial with three tries left.

From a script: `cage list` prints the same table.

## Updating

1. Press `u`. The review says what an update does; press `y`.
2. Watch **LOG**. cage snapshots the slot the machine boots into a new one named for the date and time, runs `dnf upgrade` inside it, seals it, boots it in a virtual machine and logs in, and sets it to boot next, on trial.
3. Reboot when it suits you.

When it worked, the last lines of the log say the new slot is promoted and boots at the next reboot, and **SLOTS** shows it as `preferred`, with three tries. The running system is unchanged, and nothing has rebooted. If any step fails, the new slot is left for you to look at and the machine still boots what it booted before. When there is nothing to upgrade, cage says so and leaves no slot behind.

From a script:

```
$ cage update
:: snapshot @nerv → @nerv-20261017-1226
...
:: the gate: booting the new slot and driving a real login…
:: validate PASS — …
:: @nerv-20261017-1226 is promoted and boots at the next reboot. If it never completes a boot, the machine falls back to @nerv by itself.
$ doas reboot
```

The virtual machine needs `nerv-qemu` and `nerv-aavmf`, which the `workstation`, `workstation-gui` and `dev` profiles carry. A `core` machine says so, skips that step, and puts the slot on trial untested.

## When an update is waiting

The lower tmux bar watches the two things that change only with a reboot, the kernel and the NVIDIA driver:

| the bar's left end | |
| --- | --- |
| the LAN address, in blue | the machine runs what it will keep running |
| `↑ L 7.2.10  N 610.60`, in red | a newer kernel or driver is in the repositories |
| `⟳ L 7.2.10`, in amber | one is installed in the next slot and waits for a reboot |

The repositories are asked a few minutes after boot and every six hours after that. To ask now: `cage updates`.

## The first boot of a new slot

A promoted slot boots on trial, with three tries. It is blessed the first time it comes all the way up, to multi-user with no unit failed, and from then on it boots like any other.

**If it never completes a boot** — a kernel that hangs, a system that never starts, a disk it cannot unlock, a unit that fails — every attempt spends a try. A boot on trial that is not blessed within five minutes restarts the machine, and a kernel that stops entirely is reset by the hardware watchdog, so a try is spent whether or not anyone is there. After three, the machine boots the default slot by itself. Nothing needs to be typed, and the failed slot is left on the disk with the journal of each attempt in its own store, which `doas magi journal --store` reads from the slot you are back on ([When magid is broken](the-journal.md#when-magid-is-broken)).

The five minutes are for a boot on trial only; a blessed slot waits at the passphrase prompt for as long as it takes. To keep a failed trial boot running while you look at it, stop its deadline: `doas systemctl stop nerv-trial-deadline.timer`.

The slot you updated from stays the default until the next update proves its successor. That update makes today's slot the default, so the machine always has a slot that has booted to fall back to.

## Rolling back

Press `r`. With a slot on trial, the review says it will stop trying it and boot the default again; with nothing on trial, that it will return the default to the slot it replaced. Press `y`, then reboot.

The newer slot stays on the disk either way. To bring it back, select it and press `p`.

From a script:

```
$ cage rollback
:: rolled back: nerv-20261017-1226.efi is no longer preferred; the machine boots nerv.efi
```

## Trying a change

For a change you may want to undo, such as a package you are unsure of or an experiment with the system, put it in a slot of its own and boot that once.

1. Press `t` and type the command, such as `dnf install some-package`, then `enter`.
2. The review says cage will make a new slot, run the command in it, seal it and arm it for the next boot only. Press `y`.
3. Reboot. The machine runs the new slot one time.
4. Whatever happens in it, the reboot after returns to your usual system. To keep the new one instead, select it and press `p`.

From a script:

```
$ cage try --validate -- dnf install some-package
:: staged + boot-once @try-4211. reboot to test, then `cage promote @try-4211` if good.
$ cage promote @try-4211
```

`--validate` also boots it in a virtual machine first. A whole channel can be tried the same way: [Trying testing without leaving stable](software.md#trying-testing-without-leaving-stable).

## What follows you to the next slot

A new slot is a copy of the system at the moment it was made. `/home` and `/var/log` are in no slot, so your files and the logs need nothing. Changes you make to `/etc` and `/var` after an update is staged are carried to the new slot when the machine shuts down, and a package you install then goes straight into it: [After an update, before the reboot](software.md#after-an-update-before-the-reboot) has the rules.

Anything elsewhere in the system, such as `/opt`, `/srv` or `/root`, stays in the slot it was written to. Keep your work in `/home`.

## The rescue slot

The installer makes `@nerv-rescue`, a copy of the system as it was installed. No update touches it, it has no boot counter, and nothing cleans it up: it is the floor under every other slot. [Recovery](recovery.md) says when to boot it.

To bring it up to date with the system you run now, press `R` and choose **rebuild**. The new rescue slot is built and sealed before the old one is removed, so the machine is never without one.

From a script: `cage rescue --rebuild`.

## Cleaning up

Every update leaves the previous slot on the disk. Press `g` to see what cleaning up would remove: every older slot but the two most recent. `G` removes them, after a review. To remove one slot, select it and press `d`.

Neither ever removes the running slot, the default, a slot on trial or the rescue slot; cage says why when you ask it to.

From a script:

```
$ cage gc
  would remove: @nerv-20261003-0912 (nerv-20261003-0912.efi)
:: dry-run — pass --yes to actually delete the above.
$ cage gc --yes
```

## Reference

The keys in cage:

| key | |
| --- | --- |
| `↑` `↓`, `j` `k` | select a slot |
| `tab` | move between the slots and the log |
| `u` | update |
| `r` | roll back |
| `t` | try a change for one boot |
| `p` | promote the selected slot: boot it from now on, on trial |
| `b` | boot the selected slot once |
| `n` | snapshot the selected slot into a new one |
| `e` | run a command inside the selected slot |
| `s`, `S` | seal the selected slot, with or without a boot counter |
| `v` | boot the selected slot in a virtual machine |
| `d` | delete the selected slot |
| `g`, `G` | show what cleaning up would remove; remove it |
| `R` | the rescue slot |
| `c` | cancel what is running |
| `?` | every key, explained |
| `q` | quit |

The commands, for scripts:

| command | |
| --- | --- |
| `cage list` | every slot, its role and its boot state |
| `cage update` | update into a new slot, gate it and put it on trial |
| `cage updates` | ask the repositories whether a kernel or driver update is waiting |
| `cage rollback` | stop the trial, or return the default to the slot it replaced |
| `cage try [--validate] -- COMMAND` | run a command in a new slot and boot it once |
| `cage promote SLOT` | boot a slot from now on, on trial |
| `cage gc [--yes]` | remove older slots |
| `cage rescue --rebuild` | rebuild the rescue slot from the running system |

`cage --help` lists every command and flag, and `tldr cage` the ones used most.
