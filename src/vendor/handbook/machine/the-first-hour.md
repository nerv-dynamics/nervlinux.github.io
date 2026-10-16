# The first hour

What you have once you log in: the console and the shell, the tools that replace the ones you know, where the defaults live and how to change one so an update keeps your change, plus becoming root, swap, memory, and checking the machine is well.

## What you got

That depends on the profile you installed.

**`core`** is the machine and nothing else: `fish` as the login shell, the coreutils, `ssh`, `doas`, `ip`, `ping`, and busybox for the rest of POSIX — `sed`, `grep`, `awk`, `tar`, `gzip`, `vi`, `less`. It is a complete, usable Unix, and it is deliberately austere: no `neovim`, no `tmux`, no prompt beyond fish's own.

**`workstation`** is core plus the things a person uses every day: `neovim`, `tmux`, `git`, a prompt, and modern replacements for the classic tools. Everything below that names a tool describes workstation.

Check which you have:

```
$ rpm -q nerv-workstation
nerv-workstation-1.0.0-8.nerv.noarch       # installed
package nerv-workstation is not installed  # core only
```

## Help on the machine

Nerv ships no man pages. Every Nerv tool documents itself instead: `<tool> --help` lists every command and flag, and `tldr <tool>` shows the commands you use most. `tldr` covers the classic tools too, once its page cache has been downloaded with `tldr --update`.

```
$ cage --help
$ tldr cage
```

## The console

You log in on `kmscon`, on **tty1**. It is the only console: there is no getty behind it, so a boot lands on the login prompt rather than on a VT you have to switch to. It draws through DRM rather than the kernel's text console, in Nerv's own typeface, Ashinoko Sans Mono, and colour scheme, Myelin.

Switch virtual terminals with **Ctrl+Alt+F1** through **Ctrl+Alt+F12**. Plain Alt+F*n* does nothing here, because kmscon reads the keyboard itself. Ctrl+Alt is also what a Wayland compositor uses, so the chord is the same whatever is in front of you.

For a second shell you do not need another VT: `tmux` is installed on workstation, and the console starts inside it.

## The shell

The shell is `fish`, configured system-wide in `/etc/fish/conf.d/`. The files load in name order:

```
$ ls /etc/fish/conf.d/
05-nerv-path.fish     15-nerv-theme.fish   30-nerv-aliases.fish     50-nerv-prompt.fish  70-nerv-terminal-modes.fish
10-nerv-options.fish  20-nerv-colors.fish  40-nerv-navigation.fish  60-nerv-tmux.fish    nerv-editor.fish
```

| file | what it does |
| --- | --- |
| `05-nerv-path.fish` | sets `PATH`, including `/usr/sbin` |
| `10-nerv-options.fish` | shell options |
| `15-nerv-theme.fish` | the Myelin colour environment for tools that read their colours from a variable |
| `20-nerv-colors.fish` | fish's syntax colours and `LS_COLORS` |
| `30-nerv-aliases.fish` | the aliases below |
| `40-nerv-navigation.fish` | zoxide, fzf and atuin |
| `50-nerv-prompt.fish` | the starship prompt |
| `60-nerv-tmux.fish` | puts a local login inside tmux |
| `70-nerv-terminal-modes.fish` | resets the terminal after a remote session dies, so the mouse stops typing into your shell |
| `nerv-editor.fish` | `EDITOR`, `VISUAL` and `PAGER`, unless you have set them |

None of it affects scripts: each file applies only to interactive shells.

**Every alias depends on the tool being installed**, which is why one configuration serves both profiles:

```
command -q eza; and alias ls 'eza --icons=never'
command -q bat; and alias cat 'bat --style=plain --paging=never'
```

On `core` there is no `eza`, so `ls` is the real `ls`; on `workstation` it is `eza`. The binaries are never replaced: `command ls`, and any script that calls `ls`, gets the original.

## The tools that replace the ones you know

On workstation, these take the classic names:

| you type | you get | |
| --- | --- | --- |
| `ls`, `ll`, `la` | `eza` | listing, with git status |
| `cat` | `bat` | syntax highlighting, no pager |
| `vi`, `vim` | `nvim` | |
| `grep` | `rg` | searches file contents |
| `find` | `fd` | finds files by name |
| `sed` | `sd` | substitution, with ordinary regular expressions |
| `du` | `dust` | what is using the disk |
| `df` | `duf` | what is mounted and how full |
| `ps` | `procs` | processes |
| `top` | `btop` | the system monitor |
| `sudo` | `doas` | |

And these are installed under their own names:

| | |
| --- | --- |
| `jq` | query JSON |
| `delta` | how `git` shows you a diff |
| `xh` | HTTP requests |
| `hyperfine` | time a command properly, over many runs |
| `tldr` | short, example-first help pages |

`nvidia-smi` is not aliased: it is the real command and prints the vendor's own table.

## The prompt, history and jumping about

These are wired into the shell rather than run by you:

- **starship** draws the prompt, from `/etc/xdg/starship.toml`
- **atuin** keeps shell history — press `↑` and search it
- **zoxide** learns the directories you visit; `z <part-of-the-name>` jumps to one
- **fzf** provides the fuzzy pickers those use

## tmux

On workstation, logging in **at the machine** puts you in a tmux session named `nerv`, attaching to it if it already exists. Logging in over SSH does not, so a remote session is a plain shell.

The prefix is the default `C-b`. What is different:

| | |
| --- | --- |
| `C-b h` / `C-b v` | split into panes above and below / side by side |
| `Alt` + arrows | move between panes, no prefix |
| `Ctrl-Alt` + `←`/`→` | previous / next window, no prefix |
| `C-b j` / `C-b s` | join a pane from, or send a pane to, another window |
| `C-b r` | reload the configuration |

The mouse works: click a pane to focus it, drag a border to resize it.

There are two status bars.

The **upper** one starts with the machine's hostname, so on a desk with several of these you always know which machine a terminal is on. The hostname block turns yellow while tmux waits for a command after the prefix, and pink in copy mode, where keys scroll the pane instead of reaching the program in it. Then come the windows, and at the right edge the machine's uptime, temperature and power draw. There is no clock; every screen already has one.

The **lower** one starts with the machine's LAN address, the one you would `ssh` to. Then come the sessions, which you can click: the one you are in sits on a grey block. At the right are `CPU`, `GPU` and memory.

Both right-hand groups come from `axon --format=tmux --fields=…`, which you can also ask for other fields:

```
$ axon --format=tmux --fields=cpu,gpu,mem
$ axon --help              # the field list
```

`axon` on its own opens the full picture: every machine in the compute fabric, each GPU's load, memory, power and temperature as they change, and what is using them. `?` inside it lists the keys; `q` leaves.

On a GB10:

- **The temperature is one figure.** The CPU and GPU are one superchip, and their sensors read the same die.
- **The memory is one pool.** The CPU and the GPU share the same 121.6 GiB, so the used figure is for the whole machine.
- **GPU figures appear for members of the `video` group**, the group that may use the GPU at all. The account the installer creates is one; add another with `doas usermod -aG video <user>` and a fresh login.

## The editor

`nvim`, with a kickstart-based Lua configuration copied into your home when your account is created:

```
$ ls ~/.config/nvim/
colors  doc  init.lua  lsp  lua  nvim-pack-lock.json
```

`lsp/` holds one file per language server. The configuration is **yours**: it was copied, not linked, so edit it freely and nothing will overwrite it.

## Where the defaults live, and how to change one

| what | where |
| --- | --- |
| your editor config | `~/.config/nvim/` |
| your shell additions | `~/.config/fish/config.fish` |
| the system shell config | `/etc/fish/conf.d/*.fish` |
| the system tmux config | `/etc/tmux.conf` |
| the prompt | `/etc/xdg/starship.toml` |
| kernel and module hardening | `/etc/sysctl.d/`, `/etc/modprobe.d/` |
| how much swap the machine gets | `/etc/nerv/swap.conf` — see [Swap](#swap) |

**Edit any of them.** Every system file above is shipped `%config(noreplace)`: when an update brings a new default for a file you have changed, rpm keeps your version and writes the new one beside it as `.rpmnew`.

```
$ rpm -qf --qf '%{FILEFLAGS:fflags}\n' /etc/tmux.conf
cn
```

`c` is config, `n` is noreplace. After an update, look for what arrived:

```
$ find /etc -name '*.rpmnew'
```

Two files are always replaced by updates: `/etc/os-release`, which says what the machine is, and the CA bundle in `/etc/pki`, which has to track upstream to stay safe.

To **add** to the shell, put it in `~/.config/fish/config.fish`.

To **replace** one of the system files, put a file with the **same name** in `~/.config/fish/conf.d/`. fish loads `conf.d` by name and finds yours first:

```
$ echo "alias ls 'ls --color=auto'" > ~/.config/fish/conf.d/30-nerv-aliases.fish
```

That replaces the whole aliases file with yours, and no update touches it.

For tmux, `~/.config/tmux/tmux.conf` is read after the system file, so it adds to and overrides it.

## Becoming root

`doas`, not `sudo`:

```
$ doas systemctl restart sshd
$
```

**No password.** Your account is in `wheel`, and `/etc/doas.conf` is:

```
permit nopass keepenv :wheel
```

On a single-operator machine with an encrypted disk, a password prompt on every privileged command only stops someone who is already logged in as you. To require one, remove `nopass` in your own copy of the file, since this one belongs to its package.

## Swap

The machine has 16 GiB of swap, on by the time you log in:

```
$ swapon --show
NAME               TYPE SIZE USED PRIO
/var/swap/swapfile file  16G   0B   -1
```

It lives in its own btrfs subvolume, `@swap`, shared by every version of the system on the disk. Updates snapshot the running system, and btrfs cannot snapshot a subvolume holding an active swapfile, so **never create a swapfile anywhere else**.

`swappiness` is 10. Swap is a reserve for when something has gone wrong, not a tier the machine pages into routinely.

**To change the size**, put it in a file of your own:

```
$ printf 'NERV_SWAP_SIZE=32g\n' | doas tee /etc/nerv/swap.conf
$ doas swapoff /var/swap/swapfile && doas rm /var/swap/swapfile
$ doas nerv-swap
nerv-swap: creating a 32g swapfile at /var/swap/swapfile
nerv-swap: /var/swap/swapfile is on
```

No package ships `/etc/nerv/swap.conf`, so no update replaces it. The board's default lives in `/etc/nerv/platform`, which updates do replace, because it describes the hardware; a change made there is lost.

## The machine keeps its last memory

The GPU can never take the machine's last 2 GiB. A GPU allocation, or host memory pinned for the GPU, that would leave less is refused, and the program gets an ordinary CUDA out-of-memory error, exactly what a full GPU says. You can always still log in and stop whatever asked.

This covers what programs ask the GPU for. A program's own heap is ordinary memory, managed by the kernel.

## Running something risky on the GPU

Put work you do not trust yet — a benchmark, a probe, anything whose memory appetite you are still finding out — in `gpu-test.slice`:

```
$ doas systemd-run --slice=gpu-test --scope ./my-experiment
```

Inside the slice, memory is capped at 8 GiB, counting GPU memory, because on a GB10 they are the same memory. An allocation past the cap is refused with an ordinary out-of-memory error, and nothing outside the slice is disturbed. Only what you put in the slice is capped; your login session is not, so a model you mean to load is never refused.

## The allocator

Every program on the machine gets its memory from `umalloc`, a hardened build of mimalloc that is the C library's `malloc`. It is part of `libc`, like `printf`.

Heap bugs end with the program stopping, not with the program doing what an attacker wanted. Guard pages sit between heap regions, free lists are encrypted, and placement is randomised. Each of these kills the process the moment it happens: freeing the same pointer twice, freeing a pointer into the middle of a block, freeing an address that never came from `malloc`, overwriting a free-list link, and writing through a pointer after it was freed.

The compiler adds to it. Every package is built with `_FORTIFY_SOURCE=3`, a stack protector, branch protection and read-only relocations, so a `memcpy` past the end of a buffer of known size stops the program instead of corrupting it. Nerv supplies the fortified headers for musl itself.

`umalloc` guards its own bookkeeping; a program that overwrites its own data inside one valid allocation is outside what an allocator can see. A program with a latent heap bug stops instead of carrying on. Against glibc's allocator, `umalloc` is about 4% faster on one standard benchmark and 8% slower on another, a fraction of a percent of anything you will notice.

It reports what it is doing when you ask. mimalloc's options are read from the environment under either prefix, `umalloc_` or `mimalloc_`:

```
$ umalloc_verbose=1 ls
umalloc: process init: 0x428F0
v3.3.2 (built on Sep 19 2026, 15:15:36)
option 'show_errors': 0
...
```

`umalloc_show_stats=1` prints a summary at exit instead. Both write to standard error, so they never mix into a program's output.

## Checking the machine is well

Every package that ships a program also ships a check that exercises it, and `cage check` runs them all. It needs no privileges:

```
$ cage check
  n/a   nerv-bandwhich         n/a: capture needs CAP_NET_RAW; only argument parsing checked
  n/a   nerv-gping             n/a: pinging needs the network; only argument parsing checked

:: 76 ok, 0 failed, 2 n/a  (78 package checks in /usr/libexec/nerv/check)
```

It lists only what did not pass; `cage check --verbose` lists every check. A `FAIL` line names the package and says why. Run it first when something feels wrong, and last after changing anything.
