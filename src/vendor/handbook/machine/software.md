# Software

Installing and removing programs with `dnf`: Nerv's own packages and the whole of Fedora's, the three kinds of package and what each allows, the stable and testing channels, where a package's settings live, and what happens to a package you install or a file you change once an update is waiting for its reboot.

## Two sources, one command

`dnf` installs from two places, and both are on from the start:

| | |
| --- | --- |
| **Nerv** | the system itself and the tools it ships, built by Nerv against its own C library, musl |
| **Fedora** | tens of thousands of packages more, Fedora's own builds, for glibc |

You do not choose between them. Ask for a program by its usual name and `dnf` takes Nerv's build when Nerv has one, and Fedora's when it does not:

```
$ doas dnf install wireguard-tools
Package               Arch    Version               Repository       Size
Installing:
 nerv-wireguard-tools aarch64 0:1.0.20260223-2.nerv nerv-stable 108.5 KiB
...
$ doas dnf install htop
Package     Arch    Version         Repository          Size
Installing:
 htop       aarch64 0:3.4.1-3.fc44  fedora         488.3 KiB
...
```

A Fedora program runs on the glibc runtime Nerv keeps beside musl, and its libraries live in `/usr/lib64`, apart from Nerv's in `/usr/lib`. The two never load each other's libraries, so a Fedora package can be installed and removed without touching anything Nerv ships.

Fedora's packages are signed by Fedora and checked against its keys before they are installed, as Nerv's are against Nerv's.

## Programs from elsewhere

A program built for glibc that does not come from Fedora, a vendor's binary or the one an installer script unpacks, runs on the same glibc runtime as Fedora's packages. The runtime is a package of its own:

```
$ doas dnf install nerv-glibc-compat
```

Without it, such a program fails as though the file did not exist, although it is plainly there: what is missing is the glibc loader it names. The program must be built for Arm, `aarch64`, as everything on the machine is; a build for x86 does not run. A program that needs more of glibc's libraries than the runtime carries usually has them in Fedora, and `dnf provides` finds which package.

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
      Run `cage update`: it builds a new slot, upgrades it, seals it, tests it where it can and promotes it. Nothing has been changed.
```

**A service you install** -- a database, a CI runner, anything with a unit of its own -- runs confined, in a domain for software Nerv does not ship. It keeps its own files, uses the network, runs as its own users and builds what it builds; it is kept from the machine's keys and account secrets, its disks and the GPU's device nodes, and changes the installed system only the way you do, through `doas`. A service that expects one of those is refused, and the refusal is in the journal: `journalctl -g 'avc: +denied'`.

## Updating

**Updating is `cage update`**, for Nerv's packages and Fedora's alike. It builds the new system beside the one you are running, so there is always one to go back to; [Generations](generations.md) is the whole of it.

`dnf upgrade` does not update this machine, and says so:

```
$ doas dnf upgrade
nerv: `dnf upgrade` does not update this machine; `cage update` does. It builds a new slot, upgrades it, seals it, tests it where it can and promotes it, and the running slot stays there to go back to.
      Run `cage update`. Nothing has been changed.
```

## Stable and testing

Nerv's packages come on two channels, and a machine is on exactly one of them at a time:

| channel | |
| --- | --- |
| **stable** | the default, where every fresh install starts. Packages arrive in batches, each one moved here from testing after it has been tried. |
| **testing** | everything built from Nerv's main branch, usually within the hour of a change landing. You get fixes and new versions first, and you are the one who finds the problems. |

Both channels are signed, and `dnf` checks the signatures before it installs anything from either. The channel is unrelated to the `stable` role in `cage list`, which names the slot the machine boots by default.

### Which one you are on

The channel is a package. Exactly one of these two is installed:

```
$ rpm -q nerv-release-stable nerv-release-testing
nerv-release-stable-…
package nerv-release-testing is not installed
```

### Switching

Switching channels is swapping one package for the other. Like any change to the system, it goes into a new slot, never onto the running one, and that slot must pass the gate before it boots:

```
$ doas cage new
$ doas cage exec @<slot> -- dnf5 swap -y nerv-release-stable nerv-release-testing
$ doas cage seal @<slot>
$ doas cage validate @<slot> --login
$ doas cage boot @<slot>
$ doas reboot
```

`cage new` snapshots the running system into a new slot and names it. `cage validate --login` is the gate, the same one `cage update` runs: it boots the slot in a virtual machine and logs in to it, and it must pass. `cage boot` makes the slot the next boot only, so if it does not come up, the boot after it returns to the system you had. Once it has come up fine, keep it:

```
$ doas cage promote @<slot>
```

To go back to stable, swap the two names. Nerv never downgrades a package, so what you already have from testing stays installed until stable reaches or passes its version.

### Upgrading a few packages, not all of them

On testing you do not have to take everything at once. `cage update` takes ordinary `dnf` arguments after `--`:

```
$ doas cage update -- <package> [<package>…]
```

It makes a new slot, upgrades only the packages you name, seals it, runs the gate and promotes it, exactly as plain `doas cage update` does for everything.

An upgrade that touches the GPU driver deserves care. The gate runs in a virtual machine and cannot test the GPU, so upgrade the driver in a slot of its own, with nothing else, and reboot before you take anything more. If the new slot never completes a boot, the machine falls back to the one before by itself: [The first boot of a new slot](generations.md#the-first-boot-of-a-new-slot).

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
