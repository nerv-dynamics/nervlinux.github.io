# The Nerv Handbook

The published manual: what this machine does and how to use it. Read [`DISCIPLINE.md`](DISCIPLINE.md) before adding a chapter.

**This is the public tree.** `docs/` is the private one and is never published — mechanism, measurements, and rejected alternatives live there. The line between them is one sentence: *publish what the reader gets, keep how we got there private.*

## Status of this table of contents

A slot below with no link is a chapter that has not been written yet, because the thing it describes is not released. The website lists only the chapters that exist.

Chapter count is a health metric. It rises when the machine learns something new, not when someone has an idea.

## Structure

Two kinds of chapter, and the split is what keeps the manual from drifting into five copies of the same explanation:

- **Ideas** (Part II) explain one part of the machine, exactly once. Everything else links to it.
- **Uses** (Part III) are organised by what you are trying to do. Goals, steps, expected output, links — and no machinery.

## Part I — This machine

| | |
| --- | --- |
| [**Why an operating system, still**](machine/why-an-operating-system-still.md) | The argument. What Unix asserted and why it fit the machine it was built for, what changed about the machine, and the duty that is still unserved. The position this whole system is an answer to. |
| **What Nerv is** | What you get, and what it costs. The chapter to read before deciding whether this machine is for you. |
| [**Install**](machine/install.md) | From a bare box to an encrypted, attested workstation, over the network. |
| [**The first hour**](machine/the-first-hour.md) | The shell and the userland, where things live, and how to change a setting so it survives an update. |
| [**Software**](machine/software.md) | Installing and removing programs, Nerv's own and Fedora's, and how an update treats them and your changes to them. |
| **The desktop** | Umbriel, Noctalia and foot, for machines that install one. |

## Part II — Five ideas

| | |
| --- | --- |
| [**Generations**](machine/generations.md) | Every update is a transaction: built beside the running system, proved, kept — or it rolls itself back. |
| **The compute fabric** | One boundary governs compute: your GPU, someone else's across the network, memory, and where programs run. Every program is a client, and everything is accounted. GPUs on several machines work together through the standard NCCL library. |
| **What the machine remembers** | The log, the facts, and `why`: the questions your machine can answer about itself and about your data — and when it will decline to answer. |
| **Yours and not yours** | Your work, rebuildable residue, and unexplained bytes — and what follows you to the next machine. |
| **The chain of trust** | What is verified between power-on and a prompt, and precisely what that does not defend against. |

Five is the budget. A sixth idea requires retiring one.

## Part III — Ways of using it

| | |
| --- | --- |
| **AI development** | Models, capabilities, and building against the machine's own store and fabric. |
| **Gaming** | Steam, titles built for x86, and borrowing a faster GPU from across the room. |
| **Running the world's software** | Fedora packages, containers, k3s — anything built for glibc. |
| **Offloading and fleets** | Putting work on other machines, and several boxes acting as one. |
| **Building your own** | Packaging software for your machine, and owning the stack. |

## Part IV — When it breaks

| | |
| --- | --- |
| **Recovery** | Rollback, the rescue slot, the morning it will not boot, the forgotten passphrase. Written for someone having a bad day. |
| **Asking why** | From a symptom to a cause, using the machine's own record. |

## Part V — Reference

Every Nerv tool documents itself: `<tool> --help` lists every flag, and `tldr <tool>` shows the commands you use most.

## Two reading orders

**You own the machine:** Install → The first hour → Software → whichever Part III chapter you bought it for, following links backward into Part II when something needs explaining.

**You are deciding whether to:** What Nerv is → Generations → then try it on your own machine, if you want to: apply an update, then roll it back. Then The chain of trust.
