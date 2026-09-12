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
