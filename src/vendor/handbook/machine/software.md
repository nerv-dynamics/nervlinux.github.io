# Software

Installing and removing programs with `dnf`: Nerv's own packages and the whole of Fedora's, the three kinds of package and what each allows, where a package's settings live, and what happens to a package you install or a file you change once an update is waiting for its reboot.

## Two sources, one command

`dnf` installs from two places, and both are on from the start:

| | |
| --- | --- |
| **Nerv** | the system itself and the tools it ships, built by Nerv against its own C library, musl |
| **Fedora** | tens of thousands of packages more, Fedora's own builds, for glibc |

You do not choose between them. Ask for a program by its usual name and `dnf` takes Nerv's build when Nerv has one, and Fedora's when it does not:

```
$ doas dnf install fuzzel
Package      Arch    Version         Repository       Size
Installing:
 nerv-fuzzel aarch64 0:1.11.1-2.nerv nerv-stable 300.4 KiB
...
$ doas dnf install htop
Package     Arch    Version         Repository          Size
Installing:
 htop       aarch64 0:3.4.1-3.fc44  fedora         488.3 KiB
...
```

A Fedora program runs on the glibc runtime Nerv keeps beside musl, and its libraries live in `/usr/lib64`, apart from Nerv's in `/usr/lib`. The two never load each other's libraries, so a Fedora package can be installed and removed without touching anything Nerv ships.

Fedora's packages are signed by Fedora and checked against its keys before they are installed, as Nerv's are against Nerv's.

## Finding a package

```
$ dnf search ripgrep
$ dnf info htop
Name           : htop
Version        : 3.4.1
Release        : 3.fc44
Repository     : fedora
...
```

`Repository` says where a package comes from, and so does the release: `.nerv` is Nerv's build, `.fc44` is Fedora's. The first `dnf` you run without `doas` asks to import the repositories' signing keys; answer `y`.

## Installing and removing

```
$ doas dnf install htop
$ doas dnf remove htop
```

Removing a program removes it and whatever it alone brought in, and nothing else. A tool that came with your profile can be removed like any other.

## Three kinds of package

| kind | what it is | `dnf` |
| --- | --- | --- |
| **the base system** | `nerv-core` and what it requires: the shell, the libraries, the services that make the machine run | refuses to remove it |
| **the boot** | the kernel, the GPU driver, systemd, the initrd tools, cryptsetup and the platform package | refuses to change it; `cage update` does |
| **everything else** | the tools in your profile, and anything you install | installs and removes freely |

**The base system** is protected, because removing any part of it takes the rest with it. `dnf` stops before it changes anything:

```
$ doas dnf remove nerv-fish
Failed to resolve the transaction:
Problem 1: The operation would result in broken dependencies for the following protected packages: nerv-core
Problem 2: installed package nerv-core-1.0.0-24.nerv.noarch requires nerv-fish, but none of the providers can be installed
```

It is a warning, not a lock. `--setopt=protected_packages=` lifts it for one command, and `dnf` then lists everything that would go, which for any part of the base system is most of the machine.

**The boot** cannot change in a running system: a slot boots the kernel and initrd sealed into its own image, so a new kernel installed beside it would never run. `dnf` refuses before downloading anything, and names the way that works:

```
$ doas dnf install nerv-kernel
...
nerv: this transaction changes the boot path (nerv-kernel). A slot boots the kernel and initrd sealed into its own UKI, so this cannot be applied to a running or sealed slot.
      Run `cage update`: it builds a new slot, upgrades it, seals it, proves it boots and promotes it. Nothing has been changed.
```

## Updating

**Updating is `cage update`**, for Nerv's packages and Fedora's alike. It builds the new system beside the one you are running, so there is always one to go back to; [Generations](generations.md) is the whole of it.

`dnf upgrade` does not update this machine, and says so:

```
$ doas dnf upgrade
nerv: `dnf upgrade` does not update this machine; `cage update` does. It builds a new slot, upgrades it, seals it, proves it boots and promotes it, and the running slot stays there to go back to.
      Run `cage update`. Nothing has been changed.
```

## Where a package's settings live

A package puts its settings in `/etc`, and they are yours to edit. An update never overwrites a file you have changed: it keeps yours and writes its new default beside it as `.rpmnew`. [Where the defaults live](the-first-hour.md#where-the-defaults-live-and-how-to-change-one) has the details and the files Nerv ships.

Everything a package puts in `/usr` belongs to the package, and the next update replaces it. Change behaviour in `/etc`, or in your home directory, never in `/usr`.

## After an update, before the reboot

Once an update is staged, the machine has two systems: the one you are running, and the one it boots next. What you do in between goes where it will last.

**A package you install goes into the next system.** Anything installed into the running one would be gone after the reboot, so `dnf` sends it ahead and says so:

```
$ doas dnf install htop
nerv: this machine boots @nerv-20261017-1226 from now on, so this transaction goes there (/mnt/nerv-top/@nerv-20261017-1226).
      The running slot is unchanged; the change is live after the reboot.
...
```

The program appears after the reboot, not before. To use it now as well, reboot first.

**A file you change in `/etc` follows you.** Edit it in the running system as usual. When the machine shuts down, every change you made to `/etc` and `/var` since the update was staged is carried to the next system:

- a file you changed and the update did not is copied across
- a file the update changed and you did not keeps the update's version
- a file you both changed keeps the update's version, and yours is saved beside it as `<file>.cage-running`, to merge by hand

What was carried, and every conflict, is listed in the next system:

```
$ cat /var/lib/cage/carryover.log
```

Look for conflicts after the reboot:

```
$ find /etc -name '*.cage-running'
```

Logs, service state and databases in `/var` come with it. `/var/tmp` and `/var/cache` are not carried, and neither is anything outside `/etc` and `/var`. Your home directory needs nothing: every system mounts the same one.
