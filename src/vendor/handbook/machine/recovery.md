# Recovery

Rollback, the rescue slot, the morning it will not boot, the forgotten passphrase. Written for someone having a bad day: each section starts from what you see and ends with the machine working.

## Going back to yesterday

The machine boots, but something an update changed is wrong. Go back to the system you had before it:

```
$ doas cage rollback
rolled back: default = @nerv-20261101-0912
$ doas reboot
```

Nothing is lost by it. The update's slot stays where it is, so `cage promote` makes it the default again once it is fixed, and your home is the same in every slot. [Rolling back](generations.md#rolling-back) has the whole of it.

To try an older slot for one boot only, without changing the default, name it:

```
$ doas cage boot @nerv-20261028-1740
$ doas reboot
```

## The boot menu

The machine boots its default slot without showing a menu. To choose, hold **Space** as it starts, from power-on until the menu appears. It lists every slot, newest first, and the rescue slot.

Choosing a slot here boots it this once. Once it is up and working, make the choice stick with `doas cage rollback`, or `doas cage promote` and the slot's name.

## The rescue slot

The installer leaves a frozen slot beside the system: the one it installed, never updated, never boot-counted and never removed by `cage gc`. Whatever happens to the slots after it, it boots.

Choose it from the boot menu. Your home is there, as it is in every slot, and so is `cage`, so from the rescue slot you can see every slot and make any of them the default again:

```
$ cage list
$ doas cage promote @nerv-20261028-1740
$ doas reboot
```

The rescue slot is as old as the installation. Use it to get back to a working slot, not to work in. [The rescue slot](generations.md#the-rescue-slot) says how to replace it with a newer one.

## The morning it will not boot

Go through these in order.

**1. Wait five minutes.** A slot that an update has just made the default boots on trial. If it hangs, or comes up with a failed unit, the machine restarts it, and after three tries it boots the slot you had before, by itself. It may take one restart or three, and then you are back where you were yesterday. [The first boot of a new slot](generations.md#the-first-boot-of-a-new-slot) has the details.

**2. If it asks for a passphrase it never asked for before**, the TPM has refused to unlock the disk. That happens after a firmware update, when the TPM has been reset, or when the board has been replaced. Type the disk's recovery passphrase, the one the installer showed you, and the machine boots as usual. To have the TPM unlock it again, see [A forgotten passphrase](#a-forgotten-passphrase).

**3. If the screen stays black**, or the same failure repeats, power off, hold **Space** as it starts, and choose an older slot from [the boot menu](#the-boot-menu). If none of those boots, choose the rescue slot.

**4. Once it is up, ask why.** The journal of the boot that failed is the previous one:

```
$ journalctl -b -1 -p err
```

## A forgotten passphrase

The disk is unlocked by the TPM, so you only meet its passphrase when the TPM refuses. The installer makes the passphrase, shows it twice on the console, and keeps no copy anywhere: write it down when you install.

**With a fleet recovery key**, a lost passphrase is not the end. Set one up while every machine still boots:

```
$ doas cage escrow init
$ doas cage escrow enrol
```

`cage escrow init` makes one key for the whole fleet and shows it once, as a code to keep on paper, in a password manager or on a FIDO2 security key. `cage escrow enrol` gives this machine's disk a recovery key of its own, stored on the disk encrypted to the fleet key; run it on each machine. `cage escrow status` shows where a machine stands.

When a machine asks for a passphrase nobody has, read its recovery key with the fleet key:

```
$ doas cage recover --device /dev/nvme0n1p2
```

and type what it prints at the passphrase prompt. Once the machine is up, replace the key that has now been seen, and seal the disk to the TPM again:

```
$ doas cage escrow rotate --ask --tpm
```

**Without a fleet recovery key**, the passphrase and the TPM are the only ways in. A disk whose passphrase is lost and whose TPM no longer unlocks it cannot be opened, by you or by anyone else: nothing Nerv keeps anywhere can open it. That is what the encryption is for.

## Reinstalling without losing your work

Installing erases the whole disk, slots and home alike; nothing is kept. Copy your home to another machine first, for example:

```
$ rsync -a ~/ you@192.168.1.30:backup/
```

then install as on the first day, and copy it back. A machine with Secure Boot keys enrolled needs them cleared in its firmware before it will boot the installer; [Install](install.md) says how.
