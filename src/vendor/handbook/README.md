# The Nerv Handbook

The published manual: why the machine works the way it does, and how to do what you came to do. Read [`DISCIPLINE.md`](DISCIPLINE.md) before adding or changing a chapter.

**This is the public tree.** Mechanism, measurements and rejected alternatives are kept privately and never published. The line between them is one sentence: *publish what the reader gets, keep how we got there private.*

## How it is arranged

The handbook is a book. It follows a reader from deciding on the machine to running many of them, and every chapter has the same shape: what it teaches and what to read first, why the machine works this way, the procedures, and the reference ([Shape of a chapter](DISCIPLINE.md#shape-of-a-chapter)). A chapter may use something a later one explains; it says what it is in a clause and links ahead.

A chapter marked *(stub)* is an outline, and the website skips it until it is written. A chapter marked *(old shape)* is written, and not yet in the chapter shape; [Moving to this shape](#moving-to-this-shape) has the order.

## Preface

| | |
| --- | --- |
| [**Why an operating system, still**](machine/why-an-operating-system-still.md) | The argument. What Unix asserted and why it fit the machine it was built for, what changed about the machine, and the duty that is still unserved. The position this whole system is an answer to. |

## Part I — Getting started

| | |
| --- | --- |
| [**What Nerv is**](machine/what-nerv-is.md) | What you get, and what it costs. The chapter to read before deciding whether this machine is for you. *(old shape)* |
| [**Installing Nerv**](machine/install.md) | From a bare box to an encrypted, attested workstation, over the network, from Linux or Windows. *(old shape)* |
| [**The first hour**](machine/the-first-hour.md) | The console, the shell and the userland, help on the machine, becoming root, and where a setting lives so it survives an update. *(old shape)* |
| [**Installing software**](machine/software.md) | Programs with `dnf`, Nerv's own and Fedora's, the stable and testing channels, and trying testing in a slot of its own. *(old shape)* |
| [**The desktop**](machine/desktop.md) | Umbriel, Noctalia and foot, for machines that install one. *(old shape)* |

## Part II — Using the machine

| | |
| --- | --- |
| [**The GPU**](machine/compute-fabric.md) | axon: the one boundary every program goes through to reach a GPU, here or on another machine, and what it shows you about who is using it. |
| [**AI development**](machine/ai-development.md) | Serving a model with S2, and building against the machine's own store and fabric. *(old shape)* |
| [**Agents**](machine/agents.md) | yui: an agent in your terminal that sees only what you give it, and conversations the machine keeps. |
| [**Containers**](machine/containers.md) | Rootless podman, Nerv's two base images, which registries a machine pulls from, and the GPU inside a container. *(old shape)* |
| [**Games**](machine/gaming.md) | Steam, titles built for x86, nQuake, and borrowing a faster GPU from across the room. *(old shape)* |
| [**Building your own**](machine/building-your-own.md) | Packaging software for your machine, a repository of your own, and owning the stack. *(old shape)* |

## Part III — Keeping the machine

| | |
| --- | --- |
| [**Updates and generations**](machine/generations.md) | cage: every update built beside the running system, proved and put on trial, and the machine going back by itself when one fails. |
| [**Firmware**](machine/firmware.md) | Updating the board's own firmware from its vendor's releases: checked before, applied during a reboot you choose, and reported after. *(old shape)* |
| [**Power**](machine/power.md) | One power profile the whole machine follows, and what the defaults buy. *(old shape)* |
| [**Accounts and keys**](machine/accounts-and-keys.md) | The people on a machine, groups, security keys, and the passwords you keep. *(old shape)* |
| [**Security**](machine/chain-of-trust.md) | What is verified between power-on and a prompt, and precisely what that does not defend against. *(old shape)* |
| [**Your files**](machine/yours-and-not-yours.md) | Seele: your work, rebuildable residue and unexplained bytes, and what follows you to the next machine. *(old shape)* |
| [**The machine's record**](machine/what-the-machine-remembers.md) | MAGI: why the machine keeps a record of its own, who may write what, the journal it keeps, and how to read it. *(old shape)* |
| [**The journal**](machine/the-journal.md) | What every service, the kernel and the initrd said, kept for every boot in MAGI, and read for any boot, even with magid broken. |
| [**Experiments**](machine/experiments.md) | nerv-run and Balthasar: a run recorded with the machine it ran on, and claims about the machine tried by the control their shape demands. |

## Part IV — Many machines

| | |
| --- | --- |
| [**Networking**](machine/networking.md) | Wired and Wi-Fi, names, WireGuard, the firewall and SSH. *(old shape)* |
| [**Plexus**](machine/plexus.md) | Reaching your machines from anywhere: an organisation whose root only you hold, machines that join with one code, the fleet network, grants and relays. |
| [**Fleets**](machine/offloading-and-fleets.md) | Putting work on other machines, and several boxes acting as one. *(old shape)* |

## Part V — When it breaks

| | |
| --- | --- |
| [**Recovery**](machine/recovery.md) | Rollback, the rescue slot, the morning it will not boot, the forgotten passphrase. Written for someone having a bad day. *(old shape)* |
| [**Asking why**](machine/asking-why.md) | From a symptom to a cause, using the machine's own record. *(old shape)* |

## Part VI — Reference

| | |
| --- | --- |
| [**yui**](reference/yui.md) | Everything yui does that the Agents chapter leaves out: scripts, the board, the sandbox in full, the approver, the machine's policy, secrets and brokers, plugins, MCP servers, Telegram. |
| **The other programs** | One page for each of Nerv's own programs — cage, axon, plexus, S2, magi, geofront — with its screen, its keys and its commands. Planned; until then, `<tool> --help` lists every flag and `tldr <tool>` the commands you use most. |
| [**What MAGI promises**](reference/magi-contract.md) | What an answer from magid means for a record: durability at each level, crashes and power cuts, redaction, backup, export, updates and rollbacks, and every case in which something kept is lost. |
| [**MAGI's limits**](reference/magi-limits.md) | The sizes, counts and rates a store holds to, and what it refuses. |
| [**The MAGI store format**](reference/magi-format.md) | Format 1, frozen: every byte of a store, enough to read and verify one without MAGI. |
| **Glossary** | Slot, generation, grant, stream and the other words the handbook uses before the chapter that explains them. Planned. |
| [**Lineage**](machine/lineage.md) | Where Nerv's ideas came from — Unix, Plan 9, the BSDs, Arch, NixOS, Fedora, musl, id Software — and what each gave it. *(stub)* |

## Reading orders

**You own the machine:** Installing Nerv → The first hour → Installing software → Updates and generations → whichever Part II chapter you bought it for, following links back when something needs explaining.

**You are deciding whether to:** Why an operating system, still → What Nerv is → Updates and generations → then try it on your own machine: apply an update, then roll it back. Then Security.

## Moving to this shape

Each chapter moves to the shape in its own change, in this order: the chapters whose program has a terminal interface first, so their procedures go through it, then the longest.

1. Updates and generations (cage) — done
2. Plexus — done
3. The GPU (axon) — done
4. Agents (yui), with what is not for most readers moved to yui's reference page — done
5. The first hour, with what is not about the first hour moved to Keeping the machine
6. Games, with nQuake as one section of its own
7. AI development (S2), once its screen can be captured
8. The machine's record (MAGI), once its screen can be captured
9. The rest, in table order

When a chapter's file is renamed to match its title, the website keeps a page at the old address that sends the reader on.
