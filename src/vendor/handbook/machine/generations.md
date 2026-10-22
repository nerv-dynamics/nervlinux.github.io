# Generations

The system lives in slots, and an update never touches the one you are running. It builds a new slot beside it, proves that slot boots to a login, and puts it on trial: if it never completes a boot, the machine goes back to the one before by itself, and `cage rollback` goes back on your word.

## What a slot is

A slot is a whole system: `/usr`, `/etc` and `/var`, with its own kernel and initrd sealed into one signed boot image. Slots sit side by side on the same encrypted disk, as btrfs snapshots of each other, so a new one costs no space until it changes.

Your home directory is not in any slot. `/home` lives beside them and every slot mounts the same one, so booting another slot changes the system and never your files.

`cage` is the one command that manages them. On its own it opens a dashboard of every slot, its kernel and its boot state; `?` lists the keys. The rest of this chapter uses its verbs, which ask for `doas` themselves when they need it.

## Seeing the slots

```
$ cage list
SLOT             ROLE      KERNEL   ARTIFACT   BOOT-COUNTER         FLAGS
@home            foreign   ?        none       -
@nerv            stable    7.2.8    uki        blessed              booted,default
@nerv-rescue     rescue    7.2.8    uki        blessed
@swap            foreign   ?        none       -
```

| role | |
| --- | --- |
| `stable` | the default: what the machine boots when nothing is on trial |
| `preferred` | a slot on trial, booted ahead of the default |
| `rescue` | the slot made at install, never updated — see [The rescue slot](#the-rescue-slot) |
| `staging` | a slot that is neither: an older system, or one being built |
| `foreign` | not a system: `@home` and `@swap`, which every slot shares |

`blessed` means the slot has completed a boot, or never needed to prove one. `3 tries left` means it is on trial. `booted` marks the slot you are running.

## `cage update` or `dnf`

**Updating the system is always `cage update`.** `dnf` installs and removes packages, and refuses `dnf upgrade` with a pointer here. [Software](software.md) has what each kind of package allows, and what happens to a package installed while an update waits for its reboot.

## Updating

```
$ cage update
:: snapshot @nerv → @nerv-20261017-1226
...
:: the gate: booting the new slot and driving a real login…
:: validate PASS — …
:: promoted @nerv-20261017-1226 → preferred [nerv-20261017-1226+3.efi], falling back to [nerv.efi]
::   boot-counted (3 tries left): if it never completes a boot, systemd-boot falls back to the default slot on its own
:: @nerv-20261017-1226 is promoted and boots at the next reboot. If it never completes a boot, the machine falls back to @nerv by itself.
```

In order, it:

1. snapshots the slot the machine boots into a new one, named for the date and time
2. runs `dnf upgrade` inside the new slot
3. seals it: builds its initrd and signs its boot image
4. boots that image in a virtual machine and logs in to it, as a person would
5. promotes it, so it boots at the next reboot, on trial

The running system is never changed, and nothing reboots. If anything fails, the new slot is left for you to look at and the machine still boots what it booted before. When there is nothing to upgrade, `cage update` says so and leaves no slot behind.

Reboot when it suits you:

```
$ doas reboot
```

## When an update is waiting

The lower tmux bar watches the two things that only change with a reboot: the kernel and the NVIDIA driver.

| the bar's left end | |
| --- | --- |
| the LAN address, in blue | the machine runs what it will keep running |
| `↑ L 7.2.10  N 610.60`, in red | a newer kernel or driver is in the repositories |
| `⟳ L 7.2.10`, in amber | one is installed in the next slot and waits for a reboot |

The repositories are asked a few minutes after boot and every six hours after that. To ask now:

```
$ cage updates
```

## The first boot of a new slot

A promoted slot boots on trial, with three tries. It is blessed the first time it comes all the way up, and from then on it boots like any other.

**If it never completes a boot** — a kernel that hangs, a system that never starts — every attempt spends a try. After three, the machine boots the default slot by itself, the one you were running before the update. Nothing needs to be typed, and the failed slot is left on the disk.

The slot you updated from stays the default until the next update proves its successor. That update makes today's slot the default, so the machine always has a slot that has booted to fall back to.

## Rolling back

```
$ cage rollback
:: rolled back: nerv-20261017-1226.efi is no longer preferred; the machine boots nerv.efi
```

The next reboot runs the slot you had before the last update. This works whether the newer slot failed or simply turned out to be worse: it stays on the disk, and `cage promote <slot>` brings it back.

With nothing on trial, `cage rollback` returns the default to the slot it replaced.

## Trying a change

To make a change you may want to undo — a package you are unsure of, an experiment with the system — put it in a slot of its own and boot that once:

```
$ cage try -- dnf install some-package
...
:: staged + boot-once @try-4211. reboot to test, then `cage promote @try-4211` if good.
```

The next reboot runs the new slot, one time. Whatever happens in it, the reboot after returns to your usual system. If you want to keep it, promote it:

```
$ cage promote @try-4211
```

`cage try --validate -- …` also boots it in a virtual machine first, as `cage update` does.

## What follows you to the next slot

A new slot is a copy of the system at the moment it was made. `/home` is not in any slot, so your files need nothing. Changes you make to `/etc` and `/var` after an update is staged are carried to the new slot when the machine shuts down, and a package you install goes straight into it: [After an update, before the reboot](software.md#after-an-update-before-the-reboot) has the rules.

Anything elsewhere in the system — `/opt`, `/srv`, `/root` — stays in the slot it was written to. Keep your work in `/home`.

## The rescue slot

The installer makes `@nerv-rescue`, a copy of the system as it was installed. No update touches it, it has no boot counter, and nothing cleans it up: it is the floor under every other slot.

To bring it up to date with the system you run now:

```
$ cage rescue --rebuild
```

The new rescue slot is built and sealed before the old one is removed, so the machine is never without one.

## Cleaning up

Every update leaves the previous slot on the disk. `cage gc` keeps the two most recent of those and shows what it would remove:

```
$ cage gc
  would remove: @nerv-20261003-0912 (nerv-20261003-0912.efi)
:: dry-run — pass --yes to actually delete the above.
$ cage gc --yes
```

It never removes the running slot, the default, a slot on trial or the rescue slot.
