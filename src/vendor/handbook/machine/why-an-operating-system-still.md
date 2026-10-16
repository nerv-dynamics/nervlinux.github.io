# Why an operating system, still

This chapter is about why we bothered to build an operating system at all, when perfectly good ones already exist. It is a bit of history and a bit of opinion, and it is the reasoning behind most of the decisions you will run into elsewhere in this handbook.

## What Unix asserted

It's easy to remember Unix as a collection of small tools and a terse shell, but at its heart it was a claim about how a computer should be addressed. Every part of the machine got one namespace and one calling convention, and the user was left to compose the rest. Disks, terminals, tapes, pipes and processes were all files, and all of them answered to `open`, `read`, `write` and `close`. That is why `cat` works on a serial port, and it remains one of the most elegant ideas in computing.

A handful of principles followed from it. Each tool was meant to do one thing, and the pipe connected them. The system was written in a language you already had, and in a fairly groundbreaking move, C and its compiler shipped in the box so the machine could rebuild itself. Text became the interchange format, mostly because in 1973 it was the only format every program could agree on. And the user drove the whole thing with a language rather than a menu. Coincidentally, that last one lines up remarkably well with what contemporary AI systems are good at.

It's worth remembering, though, that the original Unix was written for a specific machine. Files and processes were the right abstraction because a PDP-11 had one CPU, one memory, one disk and a few terminals. The abstraction fit the hardware, and that fit is a big part of why it worked so well. It is also the reason to go back and examine those assumptions, now that the hardware looks nothing like a PDP-11.

## What the GNU project achieved

GNU set out to make Unix free and to make it run everywhere, which turned out to be a demanding combination. To replace every vendor's `ls` on every system, GNU had to absorb every vendor's `ls`. Options accreted, old behaviour was preserved for compatibility, and portability won over economy almost every time. A tool with sixty flags was not bloated when its job was to stand in for sixty implementations.

And it worked. Free unix won so thoroughly that it is now the unremarkable default that practically every system, this one included, is built on. Once a goal has been achieved, it stops constraining whatever comes next. GNU carried the obligation to run everywhere and to absorb everything that came before it, and it carried it admirably, but it is an obligation we no longer need to carry ourselves.

## What changed: the machine

Meanwhile, the hardware quietly stopped looking like the thing files and processes were designed to describe. Compute is heterogeneous now, with cores of different sizes, a GPU with its own scheduler, and more and more often other machines on the network. Memory is no longer one pool with one owner. On unified-memory parts like the GB10, the GPU's memory is the host's memory, and two allocators with no way of negotiating with each other end up sharing it. The network behaves more like a tier of the machine than a peripheral, and storage behaves more like a log than a block device full of inodes.

The more interesting change, however, is a pattern we have seen before. Every so often a piece of hardware escapes the process model, and sooner or later the operating system has to bring it back.

| escaped | returned as | the kernel primitive underneath |
| --- | --- | --- |
| the display | the kernel sets modes, and one compositor owns the device and speaks a protocol | KMS/DRM, DRM leases, dma-buf |
| input | one library, driven by the compositor that owns the seat | evdev |
| audio | a daemon that owns the device and speaks a protocol | ALSA, then timer-based scheduling |
| bluetooth | a daemon that owns the adapter and speaks a protocol | the kernel BT stack |
| printing | a daemon that owns the device and speaks a protocol | USB/IPP transport |
| service state | an init that owns the lifecycle and speaks a protocol | cgroups |
| **compute** | **still outside** | |

In these six examples, each started out as a capability you reached by linking a vendor library, or by loading a vendor driver into somebody else's address space. Think of X's userspace mode-setting and input drivers, applications in the OSS era grabbing the sound card for themselves, or the vendor print and Bluetooth stacks. Each one ended with a single process owning the device and speaking a protocol, and the kernel growing a primitive underneath it. Nobody planned it that way. It is simply what the problem demands, because when several processes address a device directly, nobody can arbitrate between them or account for what they are doing.

There is one important piece of hardware where this has not happened yet. Today the GPU is reached by linking a vendor library, and it sits outside the namespace, the scheduler and the accounting, largely outside the system's own tracing, and outside checkpointing except where the vendor has been kind enough to allow it. One process can deny the device to every other process on the machine, and the system can neither see it happening nor explain it afterwards.

## The four duties

So what should an operating system actually do? It's in the eye of the beholder, but we think these four are important:

The first is to run the user's programs, which means scheduling, isolating, accounting for, tracing and checkpointing them across all the compute the user owns. Today that includes the GPU, and where the boundary allows it, other machines too. Everything else serves this duty. An operating system that can't tell you what a program is using, can't stop it from starving another one, and can't tell you why it failed isn't really running that program at all. It's more or less standing next to it.

The second is to know what belongs to the user. The file namespace gave us a uniform way to address bytes, but never a way to know what those bytes mean or who put them there. A machine that can't tell your own work apart from reproducible build output, or from residue nobody can explain, is very hard to clean up, audit or move somewhere else.

The third is to know what happened. A system that changes itself ought to be able to say what changed and why. Unix logged text because text was the interchange format of the day, which meant the record of what happened was prose, and prose is notoriously hard to query.

The fourth is to be rebuildable. Unix put C and the compiler in the box. Today the equivalent is a system that is a composed, named and reproducible whole, rather than the accumulated residue of every command anyone ever ran against it.

## What follows

A few convictions fall out of those duties, and they shape most of what you will find in Nerv.

The first is that a thing should be shaped correctly from the beginning, or not exist yet. Something that works today but has the wrong shape is not a step towards the right thing. It is something that will eventually have to be removed, and by the time that becomes obvious, something else depends on it. "Get it working first" usually produces a different artifact that happens to give the same output, and the road from there to the right design tends to be demolition. That is why we ask what the right shape is before we ask what makes it run, because the second question is far easier and will quietly answer the first one if you let it.

The second is that the interchange format should be a typed record with a stable schema, with text as one way of rendering it. Text was universal because in 1973 there was nothing else, and that constraint is long gone. In a sense this is the very same argument Unix made, just a few generations later.

The third is that the operator's surface and the user's surface are different things. Conflating the two is a big part of what makes a general-purpose distribution so hard to administer. The shell is a user program, and an excellent one, but it is where you compose the system's tools rather than something those tools depend on. In practice that means no tool in Nerv requires a shell, a display or a human. Every command runs with stdin closed and no terminal attached, emits typed output, and exits with an honest status. The one narrow exception is a human needed as an authentication factor, which is a security mechanism rather than an interactive dependency.

The fourth is that a submission boundary is the natural unit of remoting. What one machine can hand to another is anything addressed through a queue that is coarser than the network is slow, such as command submission, block I/O or starting a service. What can't be handed over is anything addressed at load/store granularity, because there is no interface to intercept and no latency budget to hide behind. So the line is not drawn around a particular device, but around whether its interface is coarser than the wire. That is why the GPU, swap and service placement turn out to be the same problem, while coherent shared memory is an entirely different one.

## The role, and the thesis

A system built for one board and one operator can't set a standard, and it shouldn't try. Every return in the table above was standardised by people who came later and argued from a working example that already existed. KMS was one driver before it was universal, and cgroups were one company's patches before systemd came along. The role we can play is the other half of that story, which is to be the working example. We ship the policy that has no standard yet, on the one machine where it can be shipped whole, and leave the argument about generalising it to whoever wants to have it.

Put as a thesis, it goes like this: a workload on the GPU should be a governed process, scheduled, accounted for, reclaimable, checkpointable and attested, on hardware its operator owns. If compute ends up returning to the process model through the vendor's door rather than the kernel's, then we were wrong, and what remains is a very coherent unix. We can live with that.

## What Nerv is

Inspired by FreeBSD, Fedora, and others that have carried the spirit of unix into the present, we hope that Nerv can serve as a test-bed for modern computing. In practice, that is a system built from scratch on musl and LLVM for NVIDIA's Grace Blackwell machines, in which the GPU is a device the operating system owns, and every layer, from the C library to the kernel, is something we can rebuild and explain.
