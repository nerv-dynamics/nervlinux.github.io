# What Nerv is

Nerv is a Linux distribution built from source for NVIDIA's Grace Blackwell machines. Like FreeBSD's base system, it is one tree, built together and versioned together; like Fedora, it is RPM-based and takes up new things early.

| | |
| --- | --- |
| C library | musl, with `umalloc` as its `malloc` |
| Toolchain | LLVM: clang and lld, with libc++ for C++ |
| Kernel | Linux, kept current |
| Init | systemd |
| `/bin/sh` | `dash` |
| Core utilities | uutils coreutils, and busybox for the rest of POSIX |
| Login shell | `fish` |
| Becoming root | `doas` |
| Packages | RPM and dnf5, Nerv's repository beside Fedora's |
| Root filesystem | btrfs, one subvolume per generation, on LUKS unlocked by the TPM |
| Boot | a signed unified kernel image |
| Mandatory access control | SELinux, enforcing, with a policy written for Nerv |
| Containers | podman, rootless |
| Console | kmscon |

## Where it departs

**musl, not glibc.** Everything Nerv builds links against musl. A program built for glibc runs from Fedora's packages, which install beside Nerv's own, or in a container. NVIDIA's driver libraries are the one piece of glibc code in the base system. See [Software](software.md).

**The GPU is the operating system's.** `libcuda.so.1` on a Nerv machine is axon, which forwards every driver call over a socket to the one process that holds the device. A program cannot tell the difference, a container gets the GPU by being handed that socket, and the GPU it reaches may be in another machine. `nvidia-smi` is axon too, and prints the vendor's table byte for byte.

**A program can run on another machine.** `axon exec --on MACHINE -- PROGRAM` places it on that machine's processors and GPU as it starts, and it never moves after that. It runs on the system it came from: its `/usr` and `/etc` arrive file by file as they are opened, and your home is served back to it over 9P by a process running as you. If the network drops, the program pauses at the point it needs its origin and carries on when the link returns, with its open files and locks intact. It is Plan 9's `cpu`, on Linux. See [The compute fabric](compute-fabric.md).

**The system is never changed in place.** `cage update` builds the next root in a new subvolume beside the running one, upgrades it, labels it for SELinux, builds its initrd, signs its boot image, boots it in a virtual machine where it can, and only then makes it the default. The new slot boots on trial and falls back by itself if it never comes up. `dnf` installs and removes software, but it does not update the machine. See [Generations](generations.md).

**Every process is in a domain.** SELinux enforces from the first boot, and nothing on the machine runs unconfined.

**The heap defends itself.** `umalloc` is a hardened allocator under every program, Firefox included: of the 33 heap attacks Nerv tests against, glibc's allocator lets 8 succeed and `umalloc` 1. See [The allocator](the-first-hour.md#the-allocator).

**No man pages.** Every Nerv tool documents itself with `--help`, and `tldr` covers the rest, the classic tools included.

## Standard underneath, modern at the prompt

Nerv ships every core utility in POSIX.1-2024. A script written to the standard runs as written, and the `core` profile is a complete Unix with nothing else on it.

At the prompt, the `workstation` profile gives the classic names to the tools that replaced them: `grep` is ripgrep, `find` is fd, `sed` is sd, `ls` is eza, `du` is dust. Each answers the same question its predecessor did, better. [The first hour](the-first-hour.md#the-tools-that-replace-the-ones-you-know) has the full table.

They are their own tools, with their own flags. Ripgrep already searches directories recursively, and its `-r` means *replace*:

```
$ grep -n TODO notes.txt
2:TODO: renew the certificate
$ grep -rn TODO notes.txt
n: renew the certificate
$ command grep -rn TODO notes.txt
2:TODO: renew the certificate
```

The new names are fish aliases, and only an interactive shell reads them: a script, a `doas` command and anything a unit runs get the POSIX tools. `command` reaches the classic tool from the prompt. To keep a classic name at your own prompt, change it in your own configuration, as [Where the defaults live](the-first-hour.md#where-the-defaults-live-and-how-to-change-one) describes; an update keeps your change.

## Daring to learn

Nerv expects you to learn new things. When people have thought hard about a tool and built a better one, Nerv ships the better one under the name you reach for, and the old habit gives way to a new one. Writing `sd old new` instead of `sed 's/old/new/'` is the small end of that. Generations instead of upgrades in place, a GPU governed like any other device, and tools whose output is a typed record rather than text to be parsed are the large end.

Like Fedora, Nerv takes up new things early, and it goes further than most distributions do. A tool is replaced when its successor is better at the same job, and `workstation` makes the change rather than leaving it as an option to find.

There is a line, and Nerv keeps to it. A new tool takes a classic name only when it answers the same question: `top` becoming `btop` is a better view of the same processes. `nvidia-smi` stays the vendor's own table, because a fleet-wide view is a different answer to a different question, and a name that means one thing at the prompt and another in a script cannot be trusted. The standard interfaces underneath stay where they are, so what changes is what you meet at the prompt, never what your scripts depend on.

## The machines it runs on

Nerv runs on machines built on NVIDIA's GB10, the Grace Blackwell chip in the DGX Spark and its siblings from other makers, and nothing else. One platform is what lets it treat the GPU as its own. RTX Spark and GB300 are on the roadmap. It installs over the network, from a second computer beside the one you are installing; see [Install](install.md).

## Licence

Nerv is open source under Apache-2.0, from the base system and its kernel patches to axon, cage and S2; patches to other projects keep those projects' licences. Every package is built from source, and nothing in Nerv calls home.
