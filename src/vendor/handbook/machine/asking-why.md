# Asking why

From a symptom to a cause, using the machine's own record: a program that stopped, a service that will not start, something that was refused, and a machine that is slow.

## The journal, and MAGI

The journal is where the machine says what happened. journald keeps the boot that is running, and `journalctl` reads it; [MAGI](the-journal.md) keeps every boot, this one included, and `doas magi journal` reads them, with the same `-b`, `-u`, `-p` and `-g`. A question about an earlier boot is MAGI's alone.

## A program that stopped

What it said before it stopped, and anything the kernel said about it, is in this boot's journal:

```
$ journalctl -b -p warning
```

`umalloc` ends a program at the first sign of a heap bug, by design ([The allocator](the-first-hour.md#the-allocator)). To have it say what it found, run the program again with `umalloc_show_errors=1` in its environment.

## A service that will not start

```
$ systemctl status myservice
$ journalctl -b -u myservice
```

The first shows its state and its last lines; the second, everything it logged this boot. A service that failed on the previous boot is in `doas magi journal -b -1 -u myservice`.

## Something was refused

Three things on the machine refuse by design, and each says so in its own place:

- **SELinux** logs every denial: `journalctl -g 'avc: +denied'` names the process, what it tried to reach, and the rule's types.
- **The firewall** drops what nobody opened; `doas nft list table inet nerv` shows what is open ([The firewall](networking.md#the-firewall)).
- **The GPU** admits only members of `video`; `id` shows whether you are one ([Who may use the GPU](compute-fabric.md#who-may-use-the-gpu)).

## The machine is slow

```
$ btop
```

shows the processors, memory, disks, network and the GPU in one screen. `procs` sorts processes, `dust` shows where the disk went, and `axon` shows who is using the GPU, here and across the fleet. A program that is waiting on memory rather than computing shows as pressure: `cat /proc/pressure/memory`.
