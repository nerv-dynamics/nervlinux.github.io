---
title:    Why an operating system, still
kind:     position
one-line: What Unix asserted, what changed about the machine underneath it, and the duty
          that is still unserved.
---

# Why an operating system, still

The argument this whole system is an answer to. It describes a duty, not a product — every
promise the rest of this book makes is discharging something claimed here, and if a promise
elsewhere cannot be justified against this chapter, one of the two is wrong.

Deliberately contains no solutions. What Nerv *does* about any of this is the rest of the book.

## What Unix asserted

Unix was not principally a set of tools. It was a claim about how a machine should be
addressed: **give every part of the computer one namespace and one calling convention, then
let the user compose.** Disks, terminals, tapes, pipes, processes — all files, all
`open`/`read`/`write`/`close`. That is why `cat` works on a serial port.

Four consequences, all deliberate:

- **Composition over capability.** A tool does one thing; the pipe supplies the rest.
- **The system is written in a language you have.** C and the compiler were in the box, so the
  machine could rebuild itself.
- **Text as interchange**, because in 1973 it was the only format every program could agree on.
- **The user drives with a language**, not a menu.

And it was a statement about a *specific machine*. Files and processes were the right
abstraction because the PDP-11 was one CPU, one memory, one disk, and some terminals. The
abstraction fit the hardware. That fit is the reason it worked, and noticing it is the reason
to re-examine it now.

## What the GNU project achieved

GNU set out to make Unix free and to make it run everywhere. That goal has a shape, and the
shape is correct for it: to replace every vendor's `ls` on every system, you must absorb every
vendor's `ls`, which means options accrete, behaviours are preserved for compatibility, and
portability outranks economy. An implementation carrying sixty flags is not bloat when its job
is to be a superset of sixty implementations. It is the job, done.

And the job is finished. Free Unix won so completely that it is now the unremarkable default —
the condition every system here is built on, this one included.

A goal that has been achieved stops constraining the next design. The obligation to run
everywhere, and to absorb everything that came before, is what GNU's shape is made of, and it
is the obligation a system built for known hardware no longer carries. That is not a criticism
of the shape; it is the handover.

**Completeness is the right value when you do not control the system. Coherence is the right
value when you do.**

## What changed: the machine

The hardware stopped looking like the thing files and processes described.

- **Compute is heterogeneous.** Cores of different capability and power, a GPU with
  its own scheduler, and increasingly other machines.
- **Memory is not one pool with one owner.** On unified-memory parts the GPU's memory
  *is* the host's, and two allocators with no way to negotiate share it.
- **The network is a tier**, not a peripheral.
- **Storage is a log**, not a block device with inodes.

But the deeper change is a pattern the system has been through before. **Hardware escapes the
process model, and the operating system's recurring duty is to bring it back.**

| escaped | returned as | the kernel primitive underneath |
| --- | --- | --- |
| mode-setting | the kernel sets modes; one compositor owns the device | KMS/DRM |
| the display | a compositor that owns the device and speaks a protocol | DRM leases, dma-buf |
| input | one library, driven by the compositor that owns the seat | evdev |
| audio | a daemon that owns the device and speaks a protocol | ALSA, then timer-based scheduling |
| bluetooth | a daemon that owns the adapter and speaks a protocol | the kernel BT stack |
| printing | a daemon that owns the device and speaks a protocol | USB/IPP transport |
| service state | an init that owns the lifecycle and speaks a protocol | cgroups |
| **compute** | **still outside** | |

Six times, the same shape. Each began as capability reached by linking a vendor library or
loading a vendor driver into someone else's address space — X's userspace mode-setting and
input drivers, OSS-era per-application device grabs, vendor print and Bluetooth stacks. Each
ended with **one process owning the device and speaking a protocol, and the kernel growing a
primitive underneath it.** Nobody planned the pattern; it is what the problem forces, because
a device that several processes address directly cannot be arbitrated, accounted, or explained
by anyone.

The row that is still empty is the one where that shape has not yet been applied.

A GPU today is reached by linking a vendor library. It is outside the namespace,
outside the scheduler, outside accounting, largely outside the system's own tracing, and
outside checkpoint except by vendor courtesy. One process can deny the device to every other
and the system cannot see it, arbitrate it, or explain it. That is fragmentation and
arbitration — the oldest operating-system problems there are — recurring in the one place the
operating system currently has no jurisdiction.

## The four duties

**1. Run the user's programs.** Schedule, isolate, account, trace, checkpoint — across *all
the compute the user owns*, which now includes the GPU and, where the boundary allows,
other machines. Everything below serves this. An operating system that cannot say what a
program is using, cannot stop it starving another, and cannot tell you why it failed is not
running that program; it is standing next to it.

**2. Know what is the user's.** The file namespace gave a uniform way to *address* bytes and
never a way to know what they *mean* or who put them there. A machine that cannot distinguish
the user's own work from reproducible output from unexplained residue cannot be cleaned,
audited, or moved.

**3. Know what happened.** A system that changes itself should be able to say what changed and
why. Unix logged text because text was the interchange format available; the record was
therefore prose, and prose is unqueryable.

**4. Be rebuildable.** C and the compiler were in the box. The modern form is that the system
is a composed, named, reproducible whole rather than the accumulated residue of every command
ever run against it.

## What follows

Principles, not mechanisms.

**Coherence over completeness.** Every element earns its place against the whole. Owning the
stack is what makes this available; refusing to use it is what wastes it.

**Correct from the beginning, or not yet.** A thing that works now and is shaped wrong is not
a step toward the thing that is shaped right. It is a thing that will have to be removed, and
by the time that is obvious something depends on it. "Get it working first" describes a
different artifact that happens to emit the same output — the path from it to the design is
usually demolition, not refinement.

This is not an argument for delay. It is an argument that the question *what is the right
shape* must be answered before the question *what makes this run*, because the second
question is much easier and will silently answer the first if allowed to. Where a stopgap is
genuinely necessary it is named as one and given an expiry, since an unnamed stopgap becomes
the design by default — and the record here is that this happens: a libudev stub was written
from scratch on a premise nobody had checked and later deleted; a network stack was
assembled live to get a box talking and then had to be described, in its own notes, as
"panic-configured, NOT the intended design".

**Typed records as interchange.** Text was the universal format because in 1973 it was the only
one. That constraint is gone. The interchange is a typed record with a stable schema, and text
is a *rendering* of it — the same argument Unix made, one representation later. A format that
cannot be read without guessing is prose wearing a schema's clothes.

**The operator surface is not the user surface.** Conflating them is what makes a general
distribution unadministrable. The shell is a user program and an excellent one; it is where you
*compose* the system's tools, not what they require. Testable form: **no tool may require a
shell, a display, or a human.** Every verb runs with stdin closed and no terminal, emits typed
output, and exits honestly. A human demanded as an *authentication factor* is a security
mechanism, not an interactive dependency; that exception is narrow and deliberate.

**A submission boundary is the unit of remoting.** What one machine can hand to another is
whatever is addressed through a queue coarser than the network is slow: command submission,
block I/O, starting a unit. What cannot be handed over is whatever is addressed at load/store
granularity, because no interface exists to intercept and no latency budget exists to hide.
The line is not which device — it is whether the interface is coarser than the wire. This is
why the GPU, swap, and service placement are the same problem, and coherent shared
memory is a different one.

**One operator.** A Nerv machine assumes a single person is responsible for it. Multi-user
time-sharing was Unix's answer to one expensive computer and many people; the situation
inverted. Stated so it is understood as a decision rather than an omission.

**Inference is never load-bearing.** A resident model may read what a person has no time to
read and propose what a person must still decide. It may not be required for the system to
boot, install, upgrade, repair, or explain itself. *The moment the OS cannot function without
inference, it stops being an operating system and becomes an appliance.*

## The role, and the thesis

A system built for one board and one operator cannot set a standard, and should not try. Every
return in the table above was standardized by people who arrived later and argued from a working
example that already existed: KMS before it was universal was one driver; cgroups before systemd
were one company's patches. The role available here is the other half of that arc — **be the
working example.** Ship the policy that has no standard yet, on the one machine where it can be
shipped whole, and leave the argument about generalising it to whoever wants to have it.

Stated as a thesis, so that it can be wrong: **a workload on the GPU should be a governed
process — scheduled, accounted, reclaimable, checkpointable, and attested — on hardware its
operator owns.**

And stated with its falsifier, because a promise with no conditions is marketing: if compute
returns to the process model through the vendor's door rather than the kernel's — if running
local models excellently never comes to require the operating system's cooperation — then the
thesis was wrong, and what remains is a coherent Unix and nothing more. That is the test. It is
written here to be checked, not defended.

## What this is not

Not an easy system, and not a hostile one — the difficulty budget is spent on the machine
being knowable, not on the user proving themselves. Not a Unix clone; the clone was built and
won. Not a collection of preferences: every choice here should be answerable with a measurement
or an argument, and where it is answerable with neither, that is recorded rather than defended.
