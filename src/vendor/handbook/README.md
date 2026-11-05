# The Nerv Handbook

The published manual: what this machine does and how to use it. Read [`DISCIPLINE.md`](DISCIPLINE.md) before adding a chapter.

**This is the public tree.** Mechanism, measurements and rejected alternatives are kept privately and never published. The line between them is one sentence: *publish what the reader gets, keep how we got there private.*

## Status of this table of contents

A chapter marked is an outline: its sections, each with a line on what goes there, and no text yet. The website skips a stub until it is written.

Chapter count is a health metric. It rises when the machine learns something new, not when someone has an idea.

## Structure

Two kinds of chapter, and the split is what keeps the manual from drifting into five copies of the same explanation:

- **Ideas** (Part II) explain one part of the machine, exactly once. Everything else links to it.
- **Uses** (Part III) are organised by what you are trying to do. Goals, steps, expected output, links — and no machinery.

## Part I — This machine

| | |
| --- | --- |
| [**Why an operating system, still**](machine/why-an-operating-system-still.md) | The argument. What Unix asserted and why it fit the machine it was built for, what changed about the machine, and the duty that is still unserved. The position this whole system is an answer to. |
| [**What Nerv is**](machine/what-nerv-is.md) | What you get, and what it costs. The chapter to read before deciding whether this machine is for you. |
| [**Install**](machine/install.md) | From a bare box to an encrypted, attested workstation, over the network. |
| [**The first hour**](machine/the-first-hour.md) | The shell and the userland, where things live, and how to change a setting so it survives an update. |
| [**Software**](machine/software.md) | Installing and removing programs, Nerv's own and Fedora's, and how an update treats them and your changes to them. |
| [**Containers**](machine/containers.md) | Rootless podman, Nerv's two base images, which registries a machine pulls from, and the GPU inside a container. |
| [**The desktop**](machine/desktop.md) | Umbriel, Noctalia and foot, for machines that install one. |
| [**Networking**](machine/networking.md) | Wired and Wi-Fi, names, WireGuard, the firewall and SSH. |
| [**Accounts and keys**](machine/accounts-and-keys.md) | The people on a machine, groups, security keys, and the passwords you keep. |

## Part II — Five ideas

| | |
| --- | --- |
| [**Generations**](machine/generations.md) | Every update is a transaction: built beside the running system, proved, kept — or it rolls itself back. |
| [**The compute fabric**](machine/compute-fabric.md) | One boundary governs compute: your GPU, someone else's across the network, memory, and where programs run. Every program is a client, and everything is accounted. GPUs on several machines work together through the standard NCCL library. |
| [**What the machine remembers**](machine/what-the-machine-remembers.md) | MAGI, the machine's database of what it knows: an unforgeable record of what was observed, the facts derived from it, and answers that state their own limits. |
| [**Yours and not yours**](machine/yours-and-not-yours.md) | Seele. Your work, rebuildable residue, and unexplained bytes — and what follows you to the next machine. |
| [**The chain of trust**](machine/chain-of-trust.md) | What is verified between power-on and a prompt, and precisely what that does not defend against. |

Five is the budget. A sixth idea requires retiring one.

## Part III — Ways of using it

| | |
| --- | --- |
| [**AI development**](machine/ai-development.md) | Models, capabilities, and building against the machine's own store and fabric. |
| [**Gaming**](machine/gaming.md) | Steam, titles built for x86, and borrowing a faster GPU from across the room. |
| [**Offloading and fleets**](machine/offloading-and-fleets.md) | Putting work on other machines, and several boxes acting as one. |
| [**Plexus**](machine/plexus.md) | Reaching your machines from anywhere: your own authority, enrolment, and access that exists only where you grant it. |
| [**Building your own**](machine/building-your-own.md) | Packaging software for your machine, and owning the stack. |

## Part IV — When it breaks

| | |
| --- | --- |
| [**Recovery**](machine/recovery.md) | Rollback, the rescue slot, the morning it will not boot, the forgotten passphrase. Written for someone having a bad day. |
| [**Asking why**](machine/asking-why.md) | From a symptom to a cause, using the machine's own record. |

## Part V — Reference

Every Nerv tool documents itself: `<tool> --help` lists every flag, and `tldr <tool>` shows the commands you use most.

## Two reading orders

**You own the machine:** Install → The first hour → Software → whichever Part III chapter you bought it for, following links backward into Part II when something needs explaining.

**You are deciding whether to:** What Nerv is → Generations → then try it on your own machine, if you want to: apply an update, then roll it back. Then The chain of trust.
