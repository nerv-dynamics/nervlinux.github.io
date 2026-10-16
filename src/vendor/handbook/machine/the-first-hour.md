---
title:    The first hour
one-line: The shell you land in, the tools that replace the ones you know, where the
          defaults live, and how to change one so it survives an update.
kind:     use
---

# The first hour

You have logged in. This chapter is what is under your hands, and how to change it.

## What you got

Two answers, depending on which profile was installed.

**`core`** is the machine and nothing else: `fish` as the login shell, the coreutils, `ssh`,
`doas`, `ip`, `ping`, and busybox for the POSIX tail — `sed`, `grep`, `awk`, `tar`, `gzip`,
`vi`, `less`. It is a complete, usable Unix and it is deliberately austere. There is no
`neovim`, no `tmux`, no prompt beyond fish's own.

**`workstation`** is core plus the things a person uses: `neovim`, `tmux`, `git`, a prompt, and
a set of Rust replacements for the classic tools. Everything below that names a tool by name is
describing workstation.

Check which you have:

```
$ rpm -q nerv-workstation
nerv-workstation-1.0.0-4.nerv.noarch       # installed
package nerv-workstation is not installed  # core only
```

## The console

What you logged into is `kmscon`, on **tty1**, and it is the only console: there is no getty
behind it, so a boot lands on the login prompt rather than on a VT something has to switch to.
It renders through DRM rather than the kernel's text console, which is what lets it use Nerv's
own font and palette — Ashinoko Sans Mono, Nerv's typeface, and Myelin, its colour scheme.

Switching virtual terminals is **Ctrl+Alt+F1** through **Ctrl+Alt+F12**. Plain Alt+F*n* is the
kernel's chord and does nothing here: kmscon reads the keyboard itself and turns the kernel's
own key handling off on its VT. Ctrl+Alt is also what a Wayland compositor uses, so the chord
does not change depending on what is in front of you.

Nothing needs to be switched to for a second shell — `tmux` is installed on workstation, and
`60-nerv-tmux.fish` is one of the files below.

## The shell

`fish`, and it is configured system-wide rather than per user. The configuration is seven files
in `/etc/fish/conf.d/`, loaded in numeric order:

```
$ ls /etc/fish/conf.d/
05-nerv-path.fish   20-nerv-colors.fish     40-nerv-navigation.fish  60-nerv-tmux.fish
10-nerv-options.fish 30-nerv-aliases.fish   50-nerv-prompt.fish
```

Each one begins by returning unless the shell is interactive, so none of it affects scripts.

**Every alias is conditional on the tool being installed.** That is the whole reason one
configuration serves both profiles:

```
command -q eza; and alias ls 'eza --icons=never'
command -q bat; and alias cat 'bat --style=plain --paging=never'
```

On `core` there is no `eza`, so `ls` is the real `ls`. On `workstation` it is `eza`. Nothing
errors on the machine that lacks the tool, and nothing needs a per-profile config file.

The binaries are never replaced. `ls` is an alias, so `command ls` and any script calling `ls`
get the original.

## The tools that replace the ones you know

On workstation, these are aliased over their classic names:

| you type | you get | |
| --- | --- | --- |
| `ls`, `ll`, `la` | `eza` | listing, with git status |
| `cat` | `bat` | syntax highlighting, no pager |
| `vi`, `vim` | `nvim` | |

And these are new names, not aliases:

| | |
| --- | --- |
| `rg` | search file contents — the one to reach for |
| `fd` | find files by name |
| `sd` | substitute, in place of `sed s///` |
| `jq` | query JSON |
| `dust` | what is using the disk |
| `duf` | what is mounted and how full |
| `procs` | processes, in place of `ps` |
| `btop` | the system monitor |
| `delta` | how `git` shows you a diff |
| `xh` | HTTP requests |
| `hyperfine` | time a command properly, over many runs |
| `tldr` | the short version of a man page |

`tldr` matters more here than elsewhere: **Nerv ships no man pages and nothing to render them.**
`tldr` and `--help` are the documentation on the machine.

## The prompt, history and jumping about

Three tools are wired into the shell rather than run by you:

- **starship** draws the prompt, from `/etc/xdg/starship.toml`
- **atuin** replaces shell history — press `↑` and search it
- **zoxide** learns the directories you visit; `z <part-of-the-name>` jumps to one
- **fzf** provides the fuzzy pickers those use

## tmux

On workstation, logging in **at the machine** puts you inside a tmux session named `nerv` —
attaching to the existing one if it is there, creating it if not. Logging in over SSH does not,
so a remote session is a plain shell.

The prefix is the default `C-b`. What is different:

| | |
| --- | --- |
| `C-b h` / `C-b v` | split horizontally / vertically |
| `Alt` + arrows | move between panes, no prefix |
| `Ctrl-Alt` + `←`/`→` | previous / next window, no prefix |
| `C-b j` / `C-b s` | join a pane from, or send a pane to, another window |
| `C-b r` | reload the configuration |

The mouse works — click a pane to focus it, drag a border to resize.

There are two status bars, and they answer different questions.

The **upper** one opens with the machine's hostname, so on a desk with more than one of these
you can never mistake which box a terminal is on. The block changes colour rather than adding
words: yellow while the prefix key is pressed and tmux is waiting for a command, pink in copy
mode, where keys scroll the pane instead of reaching the program in it. Then the windows, and
at the right edge what the hardware is doing — how long the machine has been up, how hot it
is, and what it is drawing. There is no clock, on the grounds that every screen already has
one.

The **lower** one opens with the machine's LAN address — the one you would `ssh` to. Then the
sessions, which are clickable: the one you are in is on a grey block, the others on the bar
itself. At the right, `CPU`, `GPU` and memory.

Both right-hand groups come from `axon --format=tmux --fields=…`, which is also how you
can ask for something else:

```
$ axon --format=tmux --fields=cpu,gpu,mem
$ axon --help              # the field list
```

`axon` on its own opens the full picture: every machine in the compute fabric, each GPU's
load, memory, power and heat as it moves, and what is using them. `?` inside it lists the
keys; `q` leaves.

Three things about those figures are worth knowing, and all three are properties of the
board rather than choices about the bar. The **temperature is one figure** because a GB10
is a superchip: the ACPI thermal zones and the GPU's own sensor are the same die, about a
degree apart, so a CPU and a GPU temperature would be one fact printed twice. The
**memory is one pool** — the kernel's `MemTotal` and the GPU's `memory.total` are the same
121.6 GiB — so the used figure is of the whole machine, not of a card. And the GPU figures
are there only for a member of the `video` group, which is who may use the GPU at all; the account
the installer creates is one, and another is added with `doas usermod -aG video <user>` and a fresh
login.

## The editor

`nvim`, configured from a kickstart-derived Lua config seeded into your home the first time your
account is created:

```
$ ls ~/.config/nvim/
after  doc  init.lua  lsp
```

`lsp/` holds one file per language server. The config is **yours** — it was copied in at account
creation, not linked, so editing it is the intended way to change the editor and nothing will
overwrite it.

## Where the defaults live, and how to change one

Three places, and which you use decides whether your change survives.

| what | where |
| --- | --- |
| your editor config | `~/.config/nvim/` |
| your shell additions | `~/.config/fish/config.fish` |
| the system shell config | `/etc/fish/conf.d/*.fish` |
| the system tmux config | `/etc/tmux.conf` |
| the prompt | `/etc/xdg/starship.toml` |
| kernel and module hardening | `/etc/sysctl.d/`, `/etc/modprobe.d/` |
| how much swap the machine gets | `/etc/nerv/swap.conf` — see *Swap* below |

**Edit any of them.** Everything above is shipped `%config(noreplace)`: when an update carries a
new default for a file you have changed, rpm keeps your version and writes the new one beside it
as `.rpmnew`. Your edit is never silently replaced.

```
$ rpm -qf --qf '%{FILEFLAGS:fflags}\n' /etc/tmux.conf
cn
```

`c` is config, `n` is noreplace. After an update, look for what arrived:

```
$ find /etc -name '*.rpmnew'
```

Two things are deliberately **not** noreplace, and both would be a bug if they were:
`/etc/os-release` and the CA bundle in `/etc/pki`. The first is the machine's identity — an
edit that persisted would make it lie about what it is — and the second must track upstream,
because a CA bundle pinned to what you had last year is a vulnerability rather than a
preference.

To **add** to the shell, put it in `~/.config/fish/config.fish`.

To **override** one of the system drop-ins rather than add to it, put a file with the **same
name** in `~/.config/fish/conf.d/` — fish loads `conf.d` by basename and yours is found first:

```
$ echo "alias ls 'ls --color=auto'" > ~/.config/fish/conf.d/30-nerv-aliases.fish
```

That replaces the whole aliases drop-in with yours, permanently, and no update touches it.

For tmux, `~/.config/tmux/tmux.conf` is read after the system one, so it adds to and overrides
what is above without replacing the file.

## Becoming root

`doas`, not `sudo`:

```
$ doas systemctl restart sshd
$
```

**No password.** Your account was put in `wheel` at install time, and `/etc/doas.conf` is:

```
permit nopass keepenv :wheel
```

That is a deliberate choice and worth knowing rather than discovering: on a single-operator
machine with an encrypted disk, a password prompt on every privileged command defends against
someone who is already logged in as you. If that is not your threat model, remove `nopass` —
in your own copy of the file, since this one is owned by the package.

## Swap

The machine has 16 GiB of swap, on by the time you log in.

```
$ swapon --show
NAME               TYPE SIZE USED PRIO
/var/swap/swapfile file  16G   0B   -1
```

It sits in its own btrfs subvolume, `@swap`, and that placement is load-bearing rather than
tidy: btrfs refuses to snapshot a subvolume that holds an active swapfile, and every system
update snapshots the system you are running. A swapfile anywhere inside the system would
therefore break updates the moment it was switched on. **Do not create one there.** One
swapfile, in `@swap`, shared by every version of the system on the disk.

`swappiness` is 10, not the usual 60. Swap here is what the machine reaches for when something
has gone wrong, not a tier it pages into routinely.

**To change the size**, put it in a file of your own:

```
$ printf 'NERV_SWAP_SIZE=32g\n' | doas tee /etc/nerv/swap.conf
$ doas swapoff /var/swap/swapfile && doas rm /var/swap/swapfile
$ doas nerv-swap
nerv-swap: creating a 32g swapfile at /var/swap/swapfile
nerv-swap: /var/swap/swapfile is on
```

`/etc/nerv/swap.conf` is not shipped by any package, which is the point: there is nothing for
an update to replace, so the file is yours alone. The board's default lives in
`/etc/nerv/platform`, which **is** replaced by updates — it states what the hardware is, so it
has to be. Do not put your override there; it will be discarded.

## Nothing takes the machine's last memory

**The promise:** however much the GPU is asked for, the machine keeps 2 GiB to itself. An
allocation of GPU memory, or of host memory pinned for the GPU, that would leave less is
refused, and the program sees an ordinary CUDA out-of-memory — exactly what a full GPU says.
You stay able to log in and stop whatever asked.

**Its condition:** it covers what programs ask the GPU for. A program's own heap is ordinary
memory, and the kernel's to manage.

**What would disprove it:** the machine stalling for memory while GPU sessions hold it. That is a
bug worth reporting.

## Running something risky on the GPU

Work you do not trust yet — a benchmark, a probe, anything whose memory appetite you are still
measuring — goes in `gpu-test.slice`:

```
$ doas systemd-run --slice=gpu-test --scope ./my-experiment
```

**The promise:** an allocation inside that slice is refused rather than granted at the
machine's expense. CUDA reports an ordinary out-of-memory and the program can handle it or
die; nothing outside the slice is disturbed.

**Its conditions**, both of which matter:

- It applies only to what you put in it. Nothing else on this machine is capped, deliberately —
  a cap on your login session would also refuse a model you meant to load.
- The cap is 8 GiB, and it covers GPU memory as well as ordinary memory, because on this board
  they are the same memory.

**What would disprove it:** a program in the slice growing past 8 GiB. If you see that, the
accounting is not working and it is a bug worth reporting, not a limit worth raising.

## The allocator, and how to ask it what it is doing

Every program on this machine gets its memory from `umalloc` — a hardened build of mimalloc that
*is* the C library's `malloc`, rather than something a particular program was linked against. You
do not choose it and cannot avoid it; it is as much a part of `libc` as `printf`.

**The promise:** a large class of heap bugs — a double free, a write past the end of a block, a
free list an attacker has learned to steer — ends in the program dying rather than in the program
doing what the attacker wanted. Guard pages sit between heap regions, free lists are encrypted,
and placement is randomised.

Specifically, each of these kills the process at the moment it happens rather than being absorbed:
freeing the same pointer twice, freeing a pointer into the middle of a block, freeing an address
that never came from `malloc` (a stack variable, say), overwriting a free-list link, and writing
through a pointer after it was freed.

The compiler helps too. Every package is built with `_FORTIFY_SOURCE=3`, a stack protector,
branch protection and read-only relocations, so a `memcpy` past the end of a known-size buffer
stops the program rather than corrupting it. musl does not implement fortification itself — Nerv
supplies it as overlay headers — and before that was done, this machine had none of it, silently.

**Its conditions:**

- It protects against corruption of the *allocator's own* bookkeeping. A program that overwrites
  its own data inside one valid allocation is doing something the allocator cannot see.
- A program with a latent heap bug that used to run will now stop running. That is the feature,
  and it is the same trade every hardened allocator makes: the alternative is a program
  continuing on a heap whose shape somebody else chose.
- It costs a few percent, and the direction depends on the program: against glibc's allocator it
  is about 4% faster on one standard benchmark and 8% slower on another. Allocation is a small
  share of most programs' time, so this is a fraction of a percent of anything you will notice.
  The trade was made deliberately, measured rather than assumed, and is not configurable
  per-program.

It answers questions if you ask. Any of mimalloc's options can be set in the environment under
either spelling — `umalloc_` is the one that matches this system, `mimalloc_` keeps upstream's
documentation usable:

```
$ umalloc_verbose=1 some-program
umalloc: process init: 0xFDB17C
umalloc: reserved 1048576 KiB memory
...
umalloc: process done: 0xFDB17C
```

`umalloc_show_stats=1` prints a breakdown at exit instead of the whole verbose log. Both write to
standard error, so they will not corrupt a program's output if you are piping it somewhere.

**What would disprove it:** a program that writes past the end of a block and carries on as if
nothing happened. That is worth reporting.

## Checking the machine is well

Every package that ships a program also ships a check that exercises it, and `cage check` runs
them all. It needs no privileges:

```
$ cage check
  ok    nerv-fish              fish -c evaluates expressions and variables
  ok    nerv-ripgrep           rg finds a match
  n/a   nerv-tcpdump           capture needs CAP_NET_RAW
  ...
:: 34 ok, 0 failed, 5 n/a  (36 package checks in /usr/libexec/nerv/check)
```

A `failed` line names the package and prints why. That is the first thing to run when something
feels wrong, and the last thing to run after changing anything.
