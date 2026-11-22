# What the machine remembers

MAGI, the machine's own record: one service that keeps what Nerv's programs record and the machine's journal, knows which program wrote each record, shows any record changed after the fact, and knows where its record is complete.

## Why the machine keeps a record of its own

Every program keeps its history its own way: a log file, a directory of JSON, a SQLite database. SQLite is superb at what it is for, a program's own data in a file the program owns. But a file belongs to whoever can write it. Anything running as you can change a program's history and leave no mark, nothing can tell what a program recorded from what something else wrote in its name, and a question that crosses programs, such as what changed on this machine before a build started failing, has nowhere to be asked.

MAGI is that one place. It is a service, not a library: one daemon, `magid`, writes every store on the machine, and nothing else writes them. Everything below rests on that.

## Who writes what

- **One store per user.** Yours holds what your programs recorded, and only you can read it. Root's is the machine's own.
- **The kernel says who is writing.** magid asks the kernel for the user and the program at the other end of its socket, and never takes a program's word for its name.
- **A program writes only the streams it declared as its own.** Nothing writes a record as another program: not another program of yours, not a script, not an agent.

magid starts when something first connects to it. Idle, it sets no timer and wakes nothing, and a store nobody has used for five minutes is closed. Under the `saver` power profile it writes to the disk less often and closes stores sooner. Stopped, by `systemctl stop magid` or at shutdown, it finishes and answers what it had begun, tells every program still connected that it is stopping, and leaves every store closed: a program knows that each batch it was answered for is kept, and that nothing it asked after was done.

## What it keeps

A store holds **streams**, each with one writer. A history stream is a sequence of records, each kept as it was written. A state stream holds keys and their current values: a conversation's place, an index of packages.

- **A changed record shows.** Every record is chained by its hash to the one before it, so a record changed or removed after the fact is a break in the chain, and `engram verify` finds it.
- **A batch is all or nothing.** A program writes a batch of records at once, and after a power cut the store comes back at the end of a whole batch. Nothing half-written is ever read.
- **A rollback leaves a store alone.** A store a newer system wrote is opened by an older one only as far as it can be without being changed. If the older system can read it, it does, but writes nothing to it. If it cannot, it refuses the store and leaves it as it is, and going forward again finds it there.
- **Time is the boot and the clock within it.** A machine whose clock was wrong for a week still has that week in the right order, with the wall-clock time kept beside each record for what it is.
- **Records are typed.** A package installs the types of the records its programs write in `/usr/share/magi/schemas`. A field is added in a new version of a type, never renamed or changed, so a reader written today still reads next year's records.
- **Views are kept current.** A view is an index, a filter, a projection or a join over other streams, and it changes in the same batch as what it reads, so it is never behind. A program can watch one and be told when it changes.
- **Records can be found by their words.** A text view ranks a history stream's records by the words in their text, best first, optionally within the values of fields it keys, such as a project. What a search returns is exact as of the moment it is asked, and a record that was redacted is never among the answers.

Today the machine's journal is kept here, and so are yui's conversations ([Agents](agents.md#conversations)) and geofront's record of the packages in a repository it builds into ([Building your own](building-your-own.md#packaging-a-program)).

## The machine's journal

`magi-journal` takes the journal into root's store as journald writes it, as the stream `journal/entries`. It changes nothing about the journal, and `journalctl` reads it as before.

- **A structured entry is kept whole.** Nerv's own programs log their events as typed fields, and systemd logs its catalogued messages the same way.
- **Any other entry keeps everything but its text:** which program logged it, from which unit and as which user, at what priority, and when.
- **It holds 1 GiB,** and drops the oldest first.

**It knows where it is complete.** journald numbers every entry it receives, one after another, so a missing number is an entry that never reached the store. `magi-journal` records each run with no number missing as complete, and each gap as a hole with how many entries fell in it. A question asked over the journal can therefore be answered with where the answer is complete, and a span the record does not cover is never mistaken for one in which nothing happened.

## Reading it

`magi` talks to magid. On its own it reads your store; with `doas`, root's:

```
$ magi status
$ doas magi status
$ doas magi tail journal/entries -n 5
```

`status` lists every stream with its kind, its type and how many records it holds. `tail` prints a stream's last records with their time: the boot, and seconds into it.

```
$ doas magi facts journal/failed-units
```

says which units failed in each of the last three boots, and where the journal is complete enough to say so: a boot marked complete had no other failures.

| command | |
| --- | --- |
| `magi tail STREAM [-n N]` | a history stream's last records |
| `magi facts VIEW [--boots N]` | a history view's rows in each of the last boots (three unless told), and where each answer is complete |
| `magi get STREAM KEY` | one key of a state stream or a view |
| `magi range STREAM [--from K] [--to K]` | its keys, in order |
| `magi search VIEW WORDS [--where F=V]` | a text view's best records for the words, within a field's value |
| `magi schema [TYPE \| --installed]` | the types a store holds, or the ones packages installed |

A program, or a script of yours, declares a stream with `magi declare` and writes it with `magi append` or `magi put`. `magi --help` lists every command.

### Removing something recorded by accident

A password pasted into the wrong prompt, or a token a program logged, can be taken out of a history stream, whichever program wrote it:

```
$ magi redact STREAM SEQ
$ doas magi redact journal/entries 1048213
```

`SEQ` is the record's number, as `magi tail` shows it. When `magi redact` returns:

- **No file of the store holds any of it.** It is gone from the stream, from every view over the stream, and from every index that was kept of it: the words a search finds, the counts, the columns and the connections between records.
- **A scar takes its place.** The record still has its number and its time, so the chain around it still verifies and `engram verify` passes. Reading it says it was redacted, and nothing else.
- **The views do not know that instant any more.** A view over the stream answers that it has no knowledge at the record's time, rather than give a count that would tell what was there.

What it cannot reach is anything outside the store: a backup, a copy someone else made, or blocks the filesystem freed but has not yet overwritten. Only a history stream's records can be redacted: a state stream's value cannot be yet.

`engram` reads a store's files directly, with no daemon: a store copied off a machine, or one checked by hand. It never writes.

```
$ engram verify ./store
```

checks every record and every chain in it, and exits with 1 if anything is wrong.

## What comes next

The engine already keeps track of where every stream and every view is complete. What follows builds on that:

- **Facts,** derived from the record by declared rules, each naming the records and the rule it came from, and rebuilt from them when a rule improves.
- **Questions over the journal,** such as which units failed in the last three boots, answered with where the answer is complete. [Asking why](asking-why.md) moves to them as they arrive.
- **Claims,** a conclusion recorded with the measurement behind it and the test that would disprove it, dated to be checked again.
- **A fleet's record,** replicated between machines so they answer as one, with queries that run on the GPU.
