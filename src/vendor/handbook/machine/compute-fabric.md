# The compute fabric

One boundary governs compute: your GPU, someone else's across the network, memory, and where programs run. Every program is a client, and everything is accounted. GPUs on several machines work together through the standard NCCL library.

## Every program is a client

No program on a Nerv machine loads NVIDIA's driver. `libcuda.so.1` on the default library path is axon's, and so are `libvulkan.so.1`, `libnvidia-ml.so.1` and `libnccl.so.2`. Each takes the calls a program makes and forwards them to `axond`, the one process that answers for the GPU, which starts a worker holding the vendor's libraries for that session alone.

A program cannot tell the difference: the same binary, unmodified, with nothing to link against. What it gains is a boundary. A driver fault ends one session rather than the desktop beside it, the vendor's glibc libraries live in that worker and nowhere else, and every use of the GPU passes one place that knows who is using it.

On the same machine the boundary costs little. A session opens `/run/axon/sock` once to hand over a region of shared memory, and every call after that crosses through it, in under two microseconds a round trip.

## Who may use the GPU

`axond` asks the kernel who connected and admits members of the `video` group. Everything else on the machine is refused at the socket, before a worker starts.

A container gets the GPU by being handed the same socket; see [The GPU in a container](containers.md#the-gpu-in-a-container).

## Seeing what is running

`axon` on a terminal is the fleet view: every machine this one is enrolled with, its GPUs live, what is using them, the links between them, and this machine's CPU. `?` inside lists its keys, and one of them opens a shell on any GPU. Into a pipe, it is the same fleet as one plain table, and `--format=csv`, `json` or `tmux` give the telemetry scripts and the tmux bar read.

`nvidia-smi` is axon as well, and prints the vendor's own table byte for byte, so scripts written for it keep working. `btop`'s GPU panel reads the same telemetry.

## A GPU on another machine

`axon run --on` runs one program against a GPU in another machine. Nothing else on either machine is affected, and the program, its files and its environment stay here; only the GPU work moves.

```
$ ./driver_axpy
device: NVIDIA GB10
65536 elements correct
$ axon run --on z2 ./driver_axpy
axon: attached to NVIDIA A800 40GB Active (40441 MiB) at 172.16.0.226:18720
device: NVIDIA A800 40GB Active
65536 elements correct
```

The GPU must be one the program can drive. A CUDA program runs on NVIDIA GPUs, here or anywhere in the fleet, and not on an AMD one: axon moves the program's calls, not its meaning.

A target is a `host:port`, or a name from `~/.config/axon/targets`, one `name address` per line. `axon probe TARGET` asks a machine what it offers, and its exit status says whether it answered.

The network is in the way of a GPU in a way it is not of a disk, so what makes this affordable is the shape of the work. A program that records its kernels into a CUDA graph replays the whole pass in one round trip instead of one per launch, which is how inference engines already run a decode step. A kernel that does many operations per byte it moves gains the most: the GB10 runs double precision at a sixty-fourth of its single-precision rate, so a double-precision job is often faster on a data-centre GPU across the room than on the one under the desk.

A session from another machine survives the connection dropping. Its worker holds the session, and takes the client back once it proves the session's token.

## Serving this machine's GPU

```
$ axon serve --on THIS-MACHINE
```

opens this machine's GPU to the fleet. Every connection from another machine proves the fleet's key before anything else happens, and is sealed under the session's own keys after it. Which machines may reach which is decided by Plexus, which enrols them.

`axon serve` also works on a machine that is not running Nerv: it copies `axond` across and provisions it there, so a GPU in a workstation or a server can join the fleet.

## Several GPUs at once

```
$ axon run --on local,gpu2 ./train
```

gives the program one GPU on each target, as CUDA devices 0, 1 and so on, in that order; `local` is this machine. NCCL is axon's too: collectives between GPUs on different machines move over the fabric with one-sided RDMA writes, and the reduction runs on the GPU, in rank order, on the caller's stream. A program written for several GPUs with NCCL runs across machines as it is.

## Memory and limits

GPU memory on a GB10 is the machine's memory, so a limit on a program's memory holds its GPU memory too. Give work you do not trust yet a limit of its own, as [Running something risky on the GPU](the-first-hour.md#running-something-risky-on-the-gpu) shows; past it, an allocation is refused with an ordinary out-of-memory error, and nothing else on the machine notices.

## Where programs run

A program can run on another machine's processors as well as its GPU:

```
$ axon exec --on build1 -- make -j64
```

It is placed there once, when it starts, and never moves after that. It runs on this machine's system, not that one's: its `/usr` and `/etc` arrive file by file as they are opened, each one verified, so nothing needs installing on the other machine. Your home is served back to it over 9P by a process running as you, which the kernel confines to your home. Its terminal, its signals and its exit status are the program's own.

If the network drops, the program pauses at the point it needs this machine and carries on when the link returns, with its open files and locks intact. The other machine must run the same instruction set. A program built for this machine's Arm processors runs on another Arm machine, never on an x86 one, because it is the program's own machine code that runs there. Before it is placed, the processor features it was built for are checked against the other machine's, so a program never lands where it cannot run.

## Graphics

The desktop reaches the GPU the same way. Mesa on Nerv draws OpenGL through Zink, which is Vulkan, and Vulkan is axon's, so the compositor, a browser and a game are all sessions of the fabric, and a Vulkan program can run against a GPU on another machine as a CUDA one can.
