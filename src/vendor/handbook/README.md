# The Nerv Handbook

The published manual: what this machine promises and how to use it. Read
[`DISCIPLINE.md`](DISCIPLINE.md) before adding a chapter.

**This is the public tree.** `docs/` is the private one and is never published — mechanism,
measurements, and rejected alternatives live there. The line between them is one sentence:
*publish the promise and its conditions, withhold the argument and the wounds.*

## Status of this table of contents

**It is a frame, not a claim.** A slot below with no link is a chapter that has not been written,
because the thing it would describe is not yet running on the canary. The frame exists so that a new
capability has an obvious home and so gaps are visible; the prose arrives when the machine does.

Chapter count is a health metric. It rises when the canary learns something new, not when someone
has an idea.

## Structure

Two kinds of chapter, and the split is what keeps the manual from drifting into five copies of the
same explanation:

- **Ideas** (Part II) explain one promise of the machine, exactly once. Every mechanism has one home
  here, and everything else cites it.
- **Uses** (Part III) are organised by what you are trying to do. Goals, steps, expected output,
  links — and no machinery.

## Part I — This machine

| | |
| --- | --- |
| [**Why an operating system, still**](machine/why-an-operating-system-still.md) | The argument. What Unix asserted and why it fit the machine it was built for, what changed about the machine, and the duty that is still unserved. No products, no verbs — the position this whole system is an answer to. **The website's Design page is built from this chapter.** |
| **What Nerv is** | The promises, what they cost, and what would disprove them. The chapter to read before deciding whether this machine is for you. |
| [**Install**](machine/install.md) | From a bare box to an encrypted, attested workstation, over the network. No USB stick. |
| [**The first hour**](machine/the-first-hour.md) | The shell and the userland, where things live, and how to change a setting so it survives an update. |

## Part II — Five ideas

| | |
| --- | --- |
| **Generations** | Every change to the system is a transaction: try it, prove it, keep it — or it rolls itself back. |
| **The compute fabric** | One boundary governs compute: your GPU, someone else's across the network, memory, and where programs run. Every program is a client, and everything is accounted. |
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

Generated per generation from the surface manifest — every verb, flag, exit code, config key and
event schema. Never hand-written, and therefore never stale.

## Two reading orders

**You own the machine:** Install → The first hour → whichever Part III chapter you bought it for,
following links backward into Part II when a promise needs explaining.

**You are deciding whether to:** What Nerv is → Generations → then run that chapter's demonstration
in a VM: apply an update, break the slot, watch the machine repair itself. Then The chain of trust.
