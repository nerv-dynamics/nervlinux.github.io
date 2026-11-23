# What the machine remembers

MAGI, the machine's own record: one service that keeps what Nerv's programs record and the machine's journal, knows which program wrote each record, shows any record changed after the fact, and knows where its record is complete.

## Why the machine keeps a record of its own

Every program keeps its history its own way: a log file, a directory of JSON, a SQLite database. SQLite is superb at what it is for, a program's own data in a file the program owns. But a file belongs to whoever can write it. Anything running as you can change a program's history and leave no mark, nothing can tell what a program recorded from what something else wrote in its name, and a question that crosses programs, such as what changed on this machine before a build started failing, has nowhere to be asked.

MAGI is that one place. It is a service, not a library: one daemon, `magid`, writes every store on the machine, and nothing else writes them. Everything below rests on that.

## Who writes what

- **One store per user.** Yours holds what your programs recorded, and only you can read it. Root's is the machine's own.
- **The kernel says who is writing.** magid asks the kernel for the user and the program at the other end of its socket, and never takes a program's word for its name.
- **A program writes only the streams it declared as its own.** Nothing writes a record as another program: not another program of yours, not a script, not an agent.

magid starts at boot. Idle, it sets no timer and wakes nothing, and a store nobody has used for five minutes is closed. Under the `saver` power profile it writes to the disk less often and closes stores sooner. Stopped, by `systemctl stop magid` or at shutdown, it finishes what it had begun and closes every store.

What an answer from magid promises, across a crash, a power cut, an update and a rollback, and every case in which something kept is lost, is [What MAGI promises](../reference/magi-contract.md); the sizes and rates it holds to are [MAGI's limits](../reference/magi-limits.md).

## What it keeps

A store holds **streams**, each with one writer. A history stream is a sequence of records, each kept as it was written. A state stream holds keys and their current values: a conversation's place, an index of packages.

- **A changed record shows,** and a batch is kept whole or not at all ([What MAGI promises](../reference/magi-contract.md)).
- **Time is the boot and the clock within it.** A machine whose clock was wrong for a week still has that week in the right order, with the wall-clock time kept beside each record for what it is.
- **Records are typed.** A package installs the types of the records its programs write in `/usr/share/magi/schemas`. A field is added in a new version of a type, never renamed or changed, so a reader written today still reads next year's records.
- **Views are kept current.** A view is an index, a filter, a projection or a join over other streams, and it changes in the same batch as what it reads, so it is never behind. A program can watch one and be told when it changes.
- **Records can be found by their words.** A text view ranks a history stream's records by the words in their text, best first, optionally within the values of fields it keys, such as a project. What a search returns is exact as of the moment it is asked, and a record that was redacted is never among the answers.
- **Large searches can run on the GPU, and answer the same.** A search, or a retrieval by how near records lie to a vector, that reads enough to be faster on the GPU runs there once `doas /usr/libexec/magid profile` has measured, on this machine, from what size it is. Until then everything runs on the CPU. The answer is the same on either, to the last bit. Measure again after the GPU driver changes; a profile measured on another machine, or by another version of MAGI, is not used.

Today the machine's journal is kept here, and so are yui's conversations ([Agents](agents.md#conversations)), geofront's record of the packages in a repository it builds into ([Building your own](building-your-own.md#packaging-a-program)), and the runs and claims of [Experiments](experiments.md).

## The machine's journal

MAGI keeps the machine's journal, and nothing else does: every boot, from the initrd's first line to the last before the machine stops, as the stream `journal/entries` in root's store, with where it is complete. journald holds only the boot that is running. [The journal](the-journal.md) covers what it keeps and how to read it.

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
| `magi journal [-b N] [-u UNIT] [-p PRIORITY]` | the journal of any boot it holds ([The journal](the-journal.md)) |
| `magi tail STREAM [-n N]` | a history stream's last records |
| `magi facts VIEW [--boots N]` | a history view's rows in each of the last boots (three unless told), and where each answer is complete |
| `magi facts VIEW [KEY]` | a state view's rows whose key begins with KEY, each as the record it stands for |
| `magi get STREAM KEY` | one key of a state stream or a view |
| `magi range STREAM [--from K] [--to K]` | its keys, in order |
| `magi search VIEW WORDS [--where F=V]` | a text view's best records for the words, within a field's value, each with the words it holds |
| `magi retrieve --text VIEW WORDS [--vector VIEW FILE] [--current FILES]` | the same, ranked together with how near each record lies to a vector you provide, and only from files as they are now |
| `magi blob FILE` | takes a file into the store, for records to name its bytes |
| `magi schema [TYPE \| --installed]` | the types a store holds, or the ones packages installed |

A program, or a script of yours, declares a stream with `magi declare` and writes it with `magi append` or `magi put`. `magi --help` lists every command.

### The dashboard

`magi` alone at a terminal, or `magi tui`, opens a dashboard over your store, from `nerv-magi-tui`. Screens `1` to `7`:

- **Overview**: magid, and every stream.
- **Log**: a stream's records, with a `~~ hole` line wherever the store cannot say every record is there.
- **Facts**: a view's rows; `/` types what their keys begin with. `Enter` follows a row to its record, the record that took its file in, and the bytes.
- **Views**: each plan, and where it is complete.
- **Claims**: the claims of [Experiments](experiments.md), soonest due first.
- **Peers**: none; MAGI does not replicate between machines yet.
- **Ask**: a text view's plan, and a search.

`base_cmdline`, followed to its bytes:

```tui magi
 MAGI  1 Overview  2 Log  3 Facts  4 Views  5 Claims  6 Peers  7 Ask                 uid 1000  store 355f4c98
╭─ views with rows ──────── 6 ─╮╭─ provenance ──────────────────────────────────────────────────── Esc back ─╮
│ code.a/nerv-wip/names        ││ row of code.a/nerv-linux/names                                             │
│ code.a/nerv-wip/uncovered    ││ record in code.a/nerv-linux/facts                                          │
│ claim/unverified             ││   path="src/cage/src/cmdline.rs" start=1272 rule="definition.function"     │
│ claim/pending                ││   name="base_cmdline" end=1377 line=22 scope=""                            │
│ code.a/nerv-linux/names      ││   blob=0x7a34cac21365268eac85a4f66ecea7fcbfd84f34a06d5a11f7ecb8a63d27f5dd  │
│ code.a/nerv-linux/uncovered  ││   projector=0xb29c806d1046f194f2e427265700782bd923f5dd0c1974e494775cd484d6 │
│                              ││   2b9b lang="rust"                                                         │
│                              ││ taken in by code.a/nerv-linux/files                                        │
│                              ││   path="src/cage/src/cmdline.rs"                                           │
│                              ││   blob=0x7a34cac21365268eac85a4f66ecea7fcbfd84f34a06d5a11f7ecb8a63d27f5dd  │
│                              ││   size=13906 lang="rust" state="indexed"                                   │
│                              ││   projector=0xb29c806d1046f194f2e427265700782bd923f5dd0c1974e494775cd484d6 │
│                              ││   2b9b facts=128                                                           │
│                              ││   digest=0xc643166463166015fd2d22a9e93196d18e750c4869ab66a4f62d363bfadd8ae │
│                              ││   e                                                                        │
│                              ││   holds the blob this record was read from                                 │
│                              ││ bytes                                                                      │
│                              ││   src/cage/src/cmdline.rs [1272, 1377) of blob 7a34cac21365268e            │
│                              ││   Enter: magi-code show, if the file still holds them                      │
│                              ││                                                                            │
│                              ││                                                                            │
│                              ││                                                                            │
╰──────────────────────────────╯╰────────────────────────────────────────────────────────────────────────────╯
╭─ output ───────────────────────────────────────────────────────────────────────────────────────────────────╮
│ $ magi-code show src/cage/src/cmdline.rs 1272 1377 7a34cac21365268eac85a4f66ecea7fcbfd84f34a06d5a11f7ecb.. │
│ src/cage/src/cmdline.rs:22: bytes 1272..1377 of blob 7a34cac21365268eac85a4f66ecea7fcbfd84f34a06d5a11f7e.. │
│ pub fn base_cmdline() -> String {                                                                          │
│     base_cmdline_from(&read_opt("/proc/cmdline").unwrap_or_default())                                      │
│ }                                                                                                          │
│ - done in 0s                                                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
 1-7 screen  ↑↓ select  Enter open  Esc back  r region  / query  ? help  q quit
```

Each action runs the command the pane shows, as you would; `c` stops it. What you type is only a query; the dashboard writes nothing. `?` lists the keys.

### Starting a unit when something becomes true

systemd starts a unit when a socket is connected to, a path appears, a device is plugged in or a time comes. MAGI adds what a store knows: a view that holds a row is a file, and a path unit starts a unit on it. The unit says which fact it starts on; nothing that writes the store can name a unit, and nothing polls.

- **While a view holds at least one row,** `/run/magi/views/STORE/VIEW` exists, with the `/` in the view's name written `:`. `STORE` is your uid, or `system` for root's store.
- **It appears once the change is kept:** a batch written `group` or `sync` once it is on the disk, a `lazy` one once it is visible, and in either case before the program that wrote it is answered. It goes when the view is empty again.
- **Your store's directory is yours.** Only you, and root, can read it, and only magid writes it.
- **From boot.** magid opens every store as the machine starts, so a fact that was true before a reboot starts its unit again.

A user unit that does a job whenever one is due, with a view `jobs/due` declared as `filter jobs/tasks state == due`:

```ini
# ~/.config/systemd/user/jobs-due.path
[Path]
PathExists=/run/magi/views/%U/jobs:due
Unit=jobs-run.service

[Install]
WantedBy=default.target
```

`systemctl --user enable --now jobs-due.path` arms it, and `magi put jobs/tasks name=backup state=due` starts `jobs-run.service`. A unit is started again while the fact holds, so the job retires it when it is done, here with `magi put jobs/tasks name=backup state=done`. A system unit starts on root's store the same way, from `/run/magi/views/system/`.

### Asking about your source code

`magi-code` reads a source tree into your store: every function, type and module it defines, every call and import, and the function each one is in. It reads Rust and shell scripts by tree-sitter grammars and rule files, so the answers are what the code says, and nothing is guessed.

```
$ cd ~/Code/nerv-linux
$ magi-code index
3743 files in 4.4s: 2174 read (2171 indexed, 3 partial, 0 failed), 0 unchanged, 1569 not parsed, 0 gone
319492 facts written, 0 retracted, in code/nerv-linux/facts
not parsed, no grammar: 420 spec, 318 patch, 108 none, 107 c, 91 toml, 69 md, 53 conf, 48 cfg, ...
$ magi facts code/nerv-linux/names base_cmdline
160641 path="src/cage/src/cmdline.rs" start=1272 rule="definition.function" name="base_cmdline" end=1377 line=22 scope="" blob=0x7a34… projector=0xda4e… lang="rust"
172636 path="src/cage/src/seal.rs" start=24461 rule="reference.call-in-macro" name="base_cmdline" end=24473 line=493 scope="cmd_seal" blob=0xd0f2… projector=0xda4e… lang="rust"
…
```

Each line is one fact: the file and line, the byte range it was read from, the rule that found it, and in `scope` the function it is in. `base_cmdline,reference.call` asks for the calls alone. `blob` is the hash of the file's bytes when they were read, and `magi-code show PATH START END BLOB` prints that range and says whether the file still holds those bytes. A name is matched as it is written, so two functions of one name in different modules are both answered.

Run `magi-code index` again after a change: it reads only the files that changed, and a file's facts follow it, so an edited or deleted file leaves nothing stale behind. `magi facts code/NAME/uncovered` lists every file whose facts are not all in, and why: a language with no grammar, a syntax error the parse recovered from, or a file the parser could not read. A tree in git is read as `git ls-files` lists it.

New rules, or a new grammar from an update, never rewrite the facts you are reading: `magi-code index` reads the tree into a second copy beside them, and `code/NAME/` answers from the first. `magi-code diff` shows what changes: facts added and gone by rule, files that read worse, names no fact mentions any more. `magi-code promote` switches `code/NAME/` to the new copy, every stream at once; `magi-code rollback` switches back, until newer rules are read over the old copy. `magi-code status` shows both.

```
$ magi-code index --rules ~/my-rules
3763 files in 2.4s: 2192 read (2189 indexed, 3 partial, 0 failed), 0 unchanged, 1571 not parsed, 0 gone
297398 facts written, 0 retracted, in code.b/nerv-linux/facts: 297398 facts there
built beside the partition readers see, by other projectors: compare them with magi-code diff, and make it the one readers see with magi-code promote
$ magi-code diff
code.a/nerv-linux/ (live, version 50f187c7aaff) against code.b/nerv-linux/ (complete, version c65ce09734bd)
  files: 2572 read alike, 1191 read again, 0 only in code.a/nerv-linux, 0 only in code.b/nerv-linux
  facts: +0 added, -26378 gone, ~0 changed
    reference.call-in-macro      +0 -26378 ~0
  names no fact mentions any more: 243 PushKeyboardEnhancementFlags, a_flipped_bit_never_returns_wrong_data, …
$ magi-code promote
code/nerv-linux/ is code.b/nerv-linux/ now: version c65ce09734bd, 297398 facts, read from the same tree; code.a/nerv-linux/ stays as it was, for magi-code rollback
```

`magi-code retract BLOB`, the blob as a fact shows it, withdraws the facts of every file holding those bytes, and later runs leave them out while the file holds them. A name stays while another file still mentions it: retracting the file that defines a function keeps the function wherever it is called. `--undo` lets the next run read the file again.

`code/NAME/calls` is the tree as a graph, from each function to what it calls, and `magi reach` follows it through any depth: `--in` for what calls a function, `--depth N` to stop. Two trees are two islands: a call into a library read as another tree stops at the call. One rule joins them, `magi same code.same/ rule NAME code/A/ code/B/ BY`, and `magi-code link` writes a pair for each name the rule joins, without reading either tree again. A pair it cannot settle is asked, `magi same code.same/ ask`, and `yes` or `no` answers it.

```
$ magi same code.same/ rule magid-axon code/magi/ code/axon/ imported
$ magi-code link
  linked: 32 pairs
proposed: 7 (7 normalised-name); 7 wait for an answer: magi same code.same/ ask
$ magi reach code/magi/calls,code/axon/calls alloc --depth 1 --same code.same/identity
alloc: 13 reached, in 2 of 2 graphs
    0  code/magi/calls           alloc
    1  code/magi/calls           mem_alloc
    1  code/axon/calls           mem_alloc
…
```

The rules, and what each joins, are in [What MAGI promises](../reference/magi-contract.md#identity).

### Finding passages

A document can be kept in the store without copying it. `magi blob` takes the file in, and on a filesystem that can share a file's bytes (btrfs, as Nerv installs it) the store's copy shares them with the original and costs no space of its own. A record then names a passage by where it lies in that file. A text view searches the passages' words; a vector view finds the passages whose vectors lie nearest one you give it, if a program gave each passage a vector.

`magi retrieve` asks either view or both, ranked together, and prints for each passage why it was found: its place in each ranking, which of your words it holds and which it does not, and for a passage of a file, whether the file still holds it. No score is printed, since a number from one search means nothing beside a number from another. With `--current`, a passage of a file taken in again since is left out. Nothing on the machine makes vectors yet; finding passages by their words needs no model.

### Removing something recorded by accident

A password pasted into the wrong prompt, or a token a program logged, can be taken out of a history stream, whichever program wrote it, and a key of a state stream along with everything it ever held:

```
$ magi redact STREAM SEQ
$ doas magi redact journal/entries 1048213
$ magi redact STREAM --key KEY
```

`SEQ` is the record's number, as `magi tail` shows it; `KEY` is written as `magi get` takes it. When `magi redact` returns:

- **No file of the store holds any of it.** It is gone from the stream, from every view over the stream, and from every index that was kept of it: the words a search finds, the counts, the columns and the connections between records.
- **A scar takes its place.** The record still has its number and its time, so the chain around it still verifies and `engram verify` passes. Reading it says it was redacted, and nothing else.
- **The views do not know that instant any more.** A view over the stream answers that it has no knowledge at the record's time, rather than give a count that would tell what was there.
- **A redacted key is deleted.** Every change ever made to it is a scar, its name included, and so is the deletion itself. The key can be written again afterwards, and is then a key like any other.

What a redaction costs the views, and what it cannot reach, is [What MAGI promises](../reference/magi-contract.md#redaction).

### Backing up a store

```
$ magi backup ~/backups/store-monday
$ doas magi backup /srv/backups/journal
```

copies the store into a new directory as it is at that moment, while programs go on writing it; nothing waits for longer than the store takes to checkpoint. When it returns, the copy has been read back and verified, and its last line says where it ends:

```
DIR: FILES files, BYTES bytes; STREAMS streams, RECORDS records, BATCHES batches to offset END, commit DIGEST
```

- **The copy is a store.** Every record and every key in it is what the store held at that moment, and `engram verify` on it reports the same end and the same commit as the store reported then.
- **What it leaves out** is [What MAGI promises](../reference/magi-contract.md#backup): the indexes, which are built again, and anything after it, a redaction included.

To put a copy back, stop magid, move the store's directory aside, and move the copy into its place. A user's store is `/var/lib/magi/stores/UID`, and the system's is `/var/lib/magi/stores/system`.

### Taking the data out, and putting it in

```
$ magi export ~/exports/store
$ magi export ~/exports/monday --store ~/backups/store-monday
$ doas magi import ~/exports/store --store /var/lib/magi/import-1000
```

`magi export` writes everything a store holds as plain files any program can read: JSON, one value per line, with each type's schema beside it. It reads a backup it takes first, so the export is of one moment however busy the store is; `--store` exports a backup's directory instead.

What each file holds, and how each value is written, is [The MAGI store format](../reference/magi-format.md#exports).


`magi import DIR --store NEW` makes the store an export holds again, in the new directory `NEW`, with no daemon. It is the store it was to every reader: each stream declared by the program that declared it, each type owned by whoever owned it, each record at its sequence number, time and token, redacted where it was redacted, each key at its version, and what the store knew of when each stream was complete. What does not come across is [What MAGI promises](../reference/magi-contract.md#export-and-import).

To serve it, stop magid and move `NEW` into a store's place, as a backup is put back. The programs that wrote it then carry on where they were: each stream's next record is the one after its last, and the next token and the next version of a key follow on. Making a store's directory takes what writing one's files takes, so importing is root's, or magid's; nothing is ever imported through magid, and no program can write a record under another's name.

A backup is the store's own files, read by a MAGI that reads their format, which [The MAGI store format](../reference/magi-format.md) describes byte by byte; an export is plain JSON, so it is how a store moves to a MAGI whose format has changed.

`engram` reads a store's files directly, with no daemon: a store copied off a machine, a backup, or one checked by hand. It never writes.

```
$ engram verify ./store
```

checks every record and every chain in it, and exits with 1 if anything is wrong.

## What comes next

The engine already keeps track of where every stream and every view is complete. What follows builds on that:

- **Facts,** derived from the record by declared rules, each naming the records and the rule it came from, and rebuilt from them when a rule improves.
- **Questions over the journal,** such as which units failed in the last three boots, answered with where the answer is complete. [Asking why](asking-why.md) moves to them as they arrive.
- **A fleet's record,** replicated between machines so they answer as one, with queries that run on the GPU.
