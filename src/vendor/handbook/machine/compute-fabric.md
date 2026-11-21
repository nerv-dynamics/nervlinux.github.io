# The GPU

How every program on a Nerv machine reaches a GPU: through axon, one boundary that answers for the GPU here and for any GPU in your fleet, knows who is using it, and keeps a driver fault inside the program that caused it. `axon` is also the program that shows you all of it, live.

## Synopsis

After reading this chapter, you will know:

- why no program on the machine loads NVIDIA's driver, and what that gives you
- who may use the GPU, and how to see who is
- how to run a program against a GPU in another machine, or on several GPUs at once
- how to open this machine's GPU to your fleet
- how to run a program on another machine's processors, and how graphics and video reach the GPU

Before reading it, you should know:

- how a program's memory is limited: [Running something risky on the GPU](the-first-hour.md#running-something-risky-on-the-gpu)
- for the parts across machines, Plexus, which decides which of your machines may reach which: [Plexus](plexus.md)

## Why it works this way

A GPU driver is the largest piece of code most machines run that nobody on them can read, and on an ordinary system every program that uses the GPU loads it into itself. A fault in it takes that program down, and often the desktop beside it; it brings its own C library into every process that touches it; and nothing on the machine can say, in one place, who is using the GPU and for what.

On Nerv, no program loads NVIDIA's driver. `libcuda.so.1` on the default library path is axon's, and so are `libcudart.so.13`, `libvulkan.so.1`, `libnvidia-ml.so.1`, `libnccl.so.2` and `libnvcuvid.so.1`. Each takes the calls a program makes and forwards them to `axond`, the one process that answers for the GPU, which starts a worker holding the vendor's libraries for that program's session alone. A program that brings its own CUDA runtime, as a PyTorch wheel does, loads it as it always did, and it runs over axon's driver.

A program cannot tell the difference: the same binary, unmodified, with nothing to link against. What it gains is a boundary. A driver fault ends one session rather than the desktop beside it, the vendor's glibc libraries live in that worker and nowhere else, and every use of the GPU passes one place that knows who is using it. On the same machine the boundary costs little: a session hands over a region of shared memory once, and every call after crosses through it, in under two microseconds a round trip.

And because a program's calls already cross a boundary, they can cross a network. The GPU in another machine is reached the same way as the one under the desk, which is what the rest of this chapter puts to work.

Plan 9 served every resource to programs over one protocol rather than through a library each; axon does that for the GPU.

## Who may use the GPU

`axond` asks the kernel who connected, and admits members of the `video` group. Everything else on the machine is refused at the socket, before a worker starts. `id` shows whether you are a member, and [Accounts and keys](accounts-and-keys.md) how to add someone.

A container gets the GPU by being handed the same socket: [The GPU in a container](containers.md#the-gpu-in-a-container).

## Opening axon

Run `axon` with no arguments:

```tui axon
 axon   1 machine · 1 answering · 1 GPU · 0% busy · 80.8 GiB free                                    every 2 s · ? keys
╭ GPUs ────────────────────────────────────────────────────────────────────────────────────────── best place first · o ╮
│     MACHINE GPU    BUSY                          FREE MEMORY           POWER TEMP  USING IT                          │
│ ▶ ● nerv-1 0 GB10            ▁▁▁▁▁▁▁▁▁▁▁▁▁   0% ▕███▍░░░░░░▏   81 GiB   5 W  46°  greeter                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭ nerv-1 · GPU 0 · NVIDIA GB10 ────────────────────────────────────────────────────────────────────────── this machine ╮
│  1 gpus   2 sessions   3 links   4 machine                                                                           │
│                                                                                                                      │
│ driver 620.70.06 · CUDA 13.5 · P8 · compute Default · persistence off · display off                                  │
│ GPU-00000000-0000-0000-0000-000000000000 · 0000000F:01:00.0                                                          │
│                                                                                                                      │
│ busy 0%   memory controller 0%                                                                                       │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                              ⢀⣀⣀⣀⣀⣀⣀ │
│                                                                                                                      │
│ memory 41.0 of 121.8 GiB  34%  · 80.8 GiB free                                                                       │
│                                                                                                                      │
│                                                                                                              ⢠⣴⣤⣶⣶⣶⣶ │
│                                                                                                                      │
│ power 5 W    ▆▇▇▆▇▆▇▇▇▇▇▇▇   temperature 46 °C    ▄▄▄▄▄▄▄▄▄▄▄▄▄                                                      │
│                                                                                                                      │
│ using it                                                                                                             │
│   greeter                                                                                                            │
│                                                                                                                      │
│ processes                                                                                                            │
│    PID  T    MEMORY  PROGRAM                                                                                         │
│   1138  C  32.5 MiB  /usr/libexec/axon/axon-vendor                                                                   │
│   1138  G  32.5 MiB  /usr/libexec/axon/axon-vendor                                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────↓ more─╯
 ⏎ use this GPU  r run…  x run there…  ↑↓ GPU  ←→ page  o order  ⇥ page  ? keys  q quit
```

- **The top line** sums up the fleet: how many machines and GPUs, how many answer, how busy they are, and how much memory is free.
- **The board** has every GPU of every machine, one row each, the best place for work first: the least busy, then the most memory free. Each row shows the GPU's use over the last minute, its free memory, its power and temperature, and who is using it: the people holding sessions on it, the machines they came from, and the programs on it. A machine that does not answer has one row, which says why. `↑` and `↓` move between GPUs; `o` lists them in the fleet's own order instead.
- **The page**, under the board, is the selected GPU and its machine in detail, in four pages: `1` the GPU, `2` the sessions using the machine's GPUs, `3` the links between machines, `4` the machine itself. `←` and `→` move between them, and `tab` gives the keyboard to the page, to scroll it.

`?` lists every key, and `q` leaves.

## Seeing what is using the GPU

1. Select one of the machine's GPUs, and press `2` for its sessions.
2. The page shows every program holding one of the machine's GPUs, with how much memory it holds; every session the machine is serving, with its user, where it came from and since when, including those from other machines; and, on this machine's page, every program here whose GPU calls cross axon, where they went, and what the crossing cost.

The GPUs page, `1`, shows each GPU's use, memory, power and temperature over the last minutes, and the processes holding a context on it.

From a script: `axon` into a pipe prints the same fleet as one plain table, and `--format=csv`, `json` or `tmux` give the telemetry scripts and the tmux bar read. `nvidia-smi` is axon as well, and prints the vendor's own table byte for byte, so scripts written for it keep working. `btop`'s GPU panel reads the same telemetry.

## Adding machines to the view

The fleet is this machine and the machines in `~/.config/axon/targets`, one `name address` per line, in that order. Press `e` to edit the file; the fleet is read again when you close it. A machine's address is usually its [Plexus](plexus.md) address.

From a script: `axon probe TARGET` asks a machine what it offers, and its exit status says whether it answered.

## A GPU on another machine

1. Select the GPU on the board, with `↑` and `↓`.
2. Press `enter`. A shell opens whose GPU programs run on the selected GPU.
3. Run the program as you would here. Leaving the shell, with `exit`, brings the board back.

For one program, `r` asks for its command line and runs it the same way; what it printed stays on the screen until you press `enter`.

Nothing else on either machine is affected. The program, its files and its environment stay on this machine; only its GPU work moves.

From a script:

```
$ ./driver_axpy
device: NVIDIA GB10
65536 elements correct
$ axon run --on gpu2 ./driver_axpy
axon: attached to NVIDIA A800 40GB Active (40441 MiB) at 192.0.2.10:18720
device: NVIDIA A800 40GB Active
65536 elements correct
```

The GPU must be one the program can drive. A CUDA program runs on NVIDIA GPUs, here or anywhere in the fleet, and not on an AMD one: axon moves the program's calls, not its meaning.

The network is in the way of a GPU in a way it is not of a disk, so what makes this affordable is the shape of the work. A program that records its kernels into a CUDA graph replays a whole pass in one round trip instead of one per launch, which is how inference engines already run a decode step. A kernel that does many operations per byte it moves gains the most: the GB10 runs double precision at a small fraction of its single-precision rate, so a double-precision job is often faster on a data-centre GPU across the room than on the one under the desk.

A session from another machine survives the connection dropping. Its worker holds the session, and takes the program back once it proves the session's token.

## Several GPUs at once

```
$ axon run --on local,gpu2 ./train
```

gives the program one GPU on each target, as CUDA devices 0, 1 and so on, in that order; `local` is this machine. NCCL is axon's too: collectives between GPUs on different machines move over the network with one-sided RDMA writes, and the reduction runs on the GPU, in rank order, on the program's stream. A program written for several GPUs with NCCL runs across machines as it is. [Fleets](offloading-and-fleets.md) puts several machines to work together.

## Serving this machine's GPU

```
$ axon serve --on THIS-MACHINE
```

opens this machine's GPU to the fleet. Every connection from another machine proves the fleet's key before anything else happens, and is sealed under the session's own keys after it. Which machines may reach which is decided by [Plexus](plexus.md).

`axon serve` also works on a machine that is not running Nerv: it copies `axond` across and provisions it there, so a GPU in a workstation or a server can join the fleet.

## Running a program on another machine's processors

```
$ axon exec --on build1 -- make -j64
```

runs a program on another machine's processors. It is placed there once, when it starts, and never moves after that. It runs on this machine's system, not that one's: its `/usr` and `/etc` arrive file by file as they are opened, each one verified, so nothing needs installing on the other machine. Your home is served back to it over 9P by a process running as you, which the kernel confines to your home. Its terminal, its signals and its exit status are the program's own. In axon, `x` places one command this way on the selected GPU's machine.

If the network drops, the program pauses at the point it needs this machine and carries on when the link returns, with its open files and locks intact. The other machine must run the same instruction set: a program built for Arm runs on another Arm machine, never on an x86 one. Before it is placed, the processor features it was built for are checked against the other machine's, so a program never lands where it cannot run.

## Memory and limits

GPU memory on a GB10 is the machine's memory, so a limit on a program's memory holds its GPU memory too. Give work you do not trust yet a limit of its own, as [Running something risky on the GPU](the-first-hour.md#running-something-risky-on-the-gpu) shows; past it, an allocation is refused with an ordinary out-of-memory error, and nothing else on the machine notices.

## Graphics

The desktop reaches the GPU the same way. Mesa on Nerv draws OpenGL through Zink, which is Vulkan, and Vulkan is axon's, so the compositor, a browser and a game are all sessions, and a Vulkan program can run against a GPU on another machine as a CUDA one can.

## Video

ffmpeg's NVDEC decoders, `h264_cuvid`, `hevc_cuvid` and the rest, reach the board's video engine through axon, with NVIDIA's own parser and decoder running in the worker:

```
$ doas dnf install nerv-axon-nvcuvid-musl
```

Decoded frames are the session's GPU memory, as they are with NVIDIA's library. A decode axon will not do is refused with an error that says why, never done some other way.

## Reference

The keys in axon:

| key | |
| --- | --- |
| `↑` `↓`, `k` `j` | select a GPU; scroll, on a page |
| `enter`, `s` | a shell whose GPU programs run on the selected GPU |
| `r` | run one command whose GPU programs run on the selected GPU |
| `x` | run one command on the selected GPU's machine, your home served from here |
| `o` | the best place for work first, or the fleet in its own order |
| `←` `→`, `1` `2` `3` `4`, `[` `]` | the GPU, sessions, links and machine pages |
| `tab`, `esc` | move between the board and the page; back to the board |
| `e` | edit the targets file |
| `c` | ask the machine's compute service again |
| `f` | read the fabric again |
| `m` | measure this machine's topology, after asking |
| `+` `-` | sample more or less often |
| `?`, `q` | every key; quit |

The commands, for scripts:

| command | |
| --- | --- |
| `axon` | the fleet view; into a pipe, a table (`--format=csv`, `json`, `tmux`) |
| `axon run --on TARGET[,TARGET…] PROGRAM` | run a program against GPUs elsewhere, or several at once |
| `axon exec --on TARGET -- PROGRAM` | run a program on another machine's processors |
| `axon serve --on MACHINE` | open a machine's GPU to the fleet |
| `axon probe TARGET` | ask a machine what it offers |
| `nvidia-smi` | the vendor's table, from axon |

`axon --help` lists every command and flag.
