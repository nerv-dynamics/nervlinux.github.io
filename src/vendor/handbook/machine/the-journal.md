# The journal

The machine's journal: what every service, the kernel and the initrd said, kept for every boot in MAGI, read with `journalctl` for the boot that is running and with `magi journal` for any boot at all.

## Synopsis

After reading this chapter, you will know:

- what the journal keeps of a boot, from the initrd to the last line before the machine stops;
- how to read an earlier boot, by unit, by priority and by time, and when magid itself is broken;
- what a power cut can cost, and what is no longer answered the way it was.

Before reading it, you should know:

- [The machine's record](what-the-machine-remembers.md): MAGI, its stores, and reading them with `doas`.

## Why it works this way

A log is worth most on the boot that went wrong, and that is the boot a log on disk is least likely to have whole: the end of a boot that hung, or the start of one that never got far enough to write anything.

So the machine keeps one copy of its journal, in one place, written once. journald holds the boot that is running in memory, and `magi-journal` takes each entry into root's MAGI store as journald receives it, as the stream `journal/entries`. It starts before any service and stops after every other program, so the boot it keeps begins at the initrd's first line and ends after the last unit has stopped. When magid is not running, before it starts, after it stops, or because it is what broke, the journal goes to disk in `/var/lib/magi-journal`, and magid takes it in when it comes back. No boot's log depends on magid having worked during it.

journald numbers every entry it receives, so the journal also knows where it is complete. A run with no number missing is marked complete, a gap is a hole with a count, and a boot held from its first entry is complete from the moment the boot began. A question asked of the journal is answered together with where the answer is complete, so a span the record does not cover is never mistaken for one in which nothing happened.

## What it keeps

- **Every entry, whole,** its message included: who logged it, from which unit and as which user, at what priority, when, and what it said. A single value over 64 KiB, such as a core dump carried in the journal, is left out and its length kept.
- **Every boot,** in root's store, up to 1 GiB, the oldest dropped first. The spool on disk holds at most 256 MiB.
- **A power cut loses at most what magid took in its last second,** and nothing logged at `crit` or worse: such an entry is on the disk before the next one is taken. journald's own files kept up to five minutes in memory.
- **This boot in memory as well:** journald holds up to 128 MiB of it, which is what `journalctl` and `systemctl status` read.

## Reading an earlier boot

```
$ doas magi journal --list-boots
$ doas magi journal -b -1 -p err
$ doas magi journal -b -1 -u myservice
$ doas magi journal -b -2 --since "2026-11-23 09:00" --until "2026-11-23 09:30"
```

`--list-boots` prints each boot the journal holds, its offset, its id, its first and last entry's time and how many entries it has. `-b` counts boots as `journalctl` does: `-b` alone is the last, `-b -1` the one before, `-b 1` the first held, or a boot's id. `-u` is a unit's own lines and systemd's lines about it, `-p` a priority and worse, `-t` a syslog identifier, `-g` lines whose message holds a text, ignoring case when the text is all lower case, and `-n` the last lines only. Times are UTC: `YYYY-MM-DD HH:MM:SS`, `@SECONDS`, or `-1h` before now.

What you see is one line an entry, the time, the host, the program and its process, and the message; a message of several lines is indented under its first.

```
$ doas magi journal --list-boots
   0 35e9bc4aae5d44b1baf6e2a16ebf0bc5 2026-11-23T14:10:44.892455Z 2026-11-23T14:11:17.248117Z     10000 entries
$ doas magi journal -n 1
2026-11-23T14:11:17.248117Z nerv01 jcost1093178[1093633]: jcost1093178 run 2 line 5000
```

## When magid is broken

The store is read from its files, with no magid:

```
$ doas magi journal --store /var/lib/magi/stores/0 -b -1 -p err
```

Whatever magid did not take before it broke is in the spool, `/var/lib/magi-journal`, as journald's own export format, a text file `grep` reads; magid takes it in first when it runs again. A boot of another slot is in that slot's own store: `--store` names that slot's `var/lib/magi/stores/0`.

## Checking the journal against journald

`--compare` takes entries in journald's export format and says which of them MAGI does not hold, or holds otherwise. For the boot that is running:

```
$ doas journalctl -D /run/log/journal -o export > /tmp/now.export
$ doas magi journal --compare /tmp/now.export
boot 35e9bc4aae5d44b1baf6e2a16ebf0bc5: 10000 entries; MAGI holds 10000 of them, 0 otherwise
every one of 10000 entries is in MAGI, as journald holds it
```

It exits 1 when any entry is missing, and names the first of them.

## What is answered differently

- **`journalctl -b -1`, and every earlier boot,** answer nothing: journald no longer has them. `magi journal` does.
- **`coredumpctl` lists only this boot's crashes.** The cores stay in `/var/lib/systemd/coredump` as before, and each crash's entry is in the journal: `doas magi journal -b -1 -u systemd-coredump` names the program, its signal and the core's file. `magi journal -o export` writes journald's export format, which `systemd-journal-remote` turns back into a journal file for `coredumpctl --file` and `journalctl --file`.
- **An account that may not read the system journal no longer reads its own services' lines** with `journalctl --user`: journald keeps one journal in memory, root's, and MAGI keeps it in root's store.
- **A failed slot's boots are in that slot's store,** not in the store of the slot the machine went back to: `magi journal -b -1` there shows that slot's own last boot, and the failed attempts are read with `--store` ([When magid is broken](#when-magid-is-broken)).
- **Journal files written before** stay where they are: `journalctl -D /var/log/journal` still reads them, and journald no longer adds to them or removes them. An entry of theirs without a message ID was taken into MAGI without its text, so those files hold the only copy of that text.

## Reference

| command | |
| --- | --- |
| `journalctl -b`, `systemctl status UNIT` | this boot, from journald's memory |
| `magi journal [-b N] [-u UNIT] [-p PRIORITY] [-t ID] [-g TEXT]` | any boot the journal holds |
| `magi journal [--since T] [--until T] [-n N]` | a span of it, or its last lines |
| `magi journal -o short\|short-monotonic\|cat\|export` | each line with the wall clock, seconds into its boot, the message alone, or journald's export format |
| `magi journal --list-boots` | the boots it holds |
| `magi journal --store DIR` | a store read from its files, with no magid |
| `magi journal --compare FILE` | which entries of an export MAGI does not hold |

Every option is in `magi --help` and `tldr magi`.
