# Offloading and fleets

Putting work on other machines, and several boxes acting as one: the targets you name, serving a machine's GPU, running a program elsewhere, and what running a fleet for an organisation will add.

[The compute fabric](compute-fabric.md) explains the ideas this chapter puts to work. Which machines may reach which is [Plexus](plexus.md)'s job.

## Naming your machines

`~/.config/axon/targets` names the machines you use, one `name address` per line, so commands can say `--on gpu2` rather than an address:

```
$ cat ~/.config/axon/targets
gpu2     192.168.1.31:18720
build1   192.168.1.40:18720
default  gpu2
```

A command with no target uses `AXON_SESSION` if it is set, and the target named `default` if it is not. `axon probe gpu2` asks a machine what it offers, and `axon` on its own shows every machine in the fleet, live.

## Serving a machine's GPU

A fleet shares one key, which every machine proves before it is let in. Make it once, on the first machine:

```
$ doas axon fleet-key
```

and serve each machine's GPU to the fleet from the machine you are sitting at, as yourself rather than through `doas`:

```
$ axon serve --on gpu2
```

On a Nerv machine this gives its GPU service the fleet's key. A machine that does not run Nerv, a Linux workstation or server with an NVIDIA GPU, gets axon's GPU service copied across, installed and started, so its GPU joins the fleet as it is. `--dry-run` shows what would be done.

Every machine in a fleet holds the same key, so taking one machine out of the fleet means making a new key for the rest.

## Work on another machine

```
$ axon run --on gpu2 ./train
```

runs a program here against the GPU there: its files, its processors and its environment stay on this machine, and only the GPU work moves. `--on gpu2,build1` gives it one GPU on each.

```
$ axon exec --on build1 -- make -j64
```

runs the program on the other machine's processors and GPU, on this machine's system and with your home, and nothing needs installing there. It behaves as if it ran here:

- it gets your environment and your working directory,
- your terminal is its terminal, and what you type reaches it,
- `Ctrl-C` and the other signals reach it and every process it starts,
- its exit status is yours: the program's own, or 128 plus the signal that ended it. A failure of `axon exec` itself exits 255, as `ssh` does.

## Several machines as one

A program written for several GPUs with NCCL runs across machines as it is: give it one GPU on each with `axon run --on`, and its collectives move over the machines' ConnectX ports with RDMA. Machines joined by a cable between their ConnectX ports need nothing else ([The ConnectX ports](networking.md#the-connectx-ports)).

## Running a fleet

For an organisation, a fleet is more than a key: which teams may use which GPUs, which machines are enrolled, which generation each one runs, and what they report. A management plane that does this, self-hosted and able to run air-gapped, and supported generations that stay frozen and patched for an agreed period, are in development for organisations; [nervlinux.org/enterprise](https://nervlinux.org/enterprise/) describes them.
