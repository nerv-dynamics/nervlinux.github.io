# What MAGI promises

What an answer from magid means for the record it was about: when it is kept, what a crash, a power cut, a redaction, a retirement, a backup or a move to another store does to it, and every case in which something kept is lost or something less is known. [What the machine remembers](../machine/what-the-machine-remembers.md) is the chapter on using MAGI; [MAGI's limits](magi-limits.md) has the sizes and rates, and [The MAGI store format](magi-format.md) the bytes on disk.

## A batch

A program writes a **batch**: any number of records, changes to keys, declarations and marks, sent together.

- **All or nothing.** A batch is kept whole or not at all. After any crash or power cut the store comes back holding exactly the batches before some point, every one of them whole: never part of a batch, and never a record nobody wrote.
- **In order.** Batches are kept in the order magid took them, which is the order of the store's commits. A batch sees every batch before it.
- **Refused alone.** A batch magid refuses changes nothing, and costs no other batch anything, even one sent in the same message.
- **Compare and set.** An append may name the head its stream must have; a change may name the version its key must be at, `0` for a key that must not exist. A batch whose condition does not hold is refused whole.
- **Idempotent where the stream says so.** On a stream declared with a source of tokens, every record carries one, and a record whose token is not above the stream's last is answered `Duplicate` and writes nothing. So a writer that resends after a crash keeps each record once.

## Durability

Every stream declares the least durability its batches carry, and a batch may ask for more. A batch is answered when what it asked for is true:

| durability | answered when | what a crash can take |
| --- | --- | --- |
| `lazy` | it is written, and every reader sees it | magid itself crashing or killed takes nothing. A power cut or a kernel crash can take the `lazy` batches of the last second (five seconds under the `saver` power profile), and nothing older. |
| `group` | an `fdatasync` covering it has returned; magid gathers the batches that arrive together under one | nothing answered |
| `sync` | the same, with no waiting to gather | nothing answered |

- **What was answered as durable is kept** across any crash and any power cut, on a disk that keeps what it says it synced.
- **A sync that fails is the failure of every batch it covered.** None of them is answered as kept, and the store is opened again from the disk before anything else is taken.
- **A program's buffered appends** (the client library's `append`, which sends what a program appends every millisecond) exist once they are sent: a program that dies within that millisecond loses what it had not sent, and a refusal of what it sent is told to no one. `commit` sends at once and answers with what magid did.
- **A clean stop loses nothing.** `systemctl stop magid` finishes and answers every request it had begun, syncs every store, `lazy` batches included, and tells each program still connected that it is stopping; every request answered was done, and the one refused and those after it were not. Each program's attachment to its streams is closed as `lost` at the stop.

## Crashes and power cuts

Opening a store after a crash replays what follows its last checkpoint, by the same rules that wrote it.

- **What was being written is dropped.** A batch whose bytes did not all reach the disk was never answered as durable, and is dropped whole.
- **Damage is never read as data.** A record, a block, a file or a chain that does not check is reported, and the store is refused, or the read that meets it is. A flipped bit or a lying disk can cost data; it never makes MAGI answer with data that is wrong.
- **Where the writer was attached is stated.** A writer attached when the machine went down has its attachment closed as `unclean`, at the store's last durable commit. After that point the store does not claim to know what the writer would have sent.

What the store cannot keep, stated plainly:

- **The last synced batch, damaged before a later one is written.** A bit that flips in the last group of batches the disk holds, before anything after it is written, cannot be told from a write that never finished, and that group is dropped, durable or not.
- **A disk that lies about syncing** can lose anything it claimed to keep. What is read is still never wrong.

**How this is tested, and how it is not.** Durability rests on the drive keeping what it said it flushed; MAGI cannot do better than the drive. The promises above are tested against a real kernel's block layer: every state a power cut could leave the disk in, on btrfs and on ext4, is rebuilt from a record of the writes and the flushes the kernel issued, and opened. They are not tested by cutting the power to a machine. A pull risks everything else on that machine, so no such test has been run, and what a particular drive does at a power cut is not something this page can promise.

## Tamper evidence

Every record is chained by its hash to the one before it in its stream, and every batch to the batch before it.

- **A record changed, removed or reordered shows**, to `engram verify` and to every read that passes it.
- **The chain is evidence, not a lock.** Whoever can write the store's files (root, or magid's own user) can rewrite a stream's chain from any point on, and nothing in the store tells. Signing a stream's head, which ties it to a key held elsewhere, is on the roadmap.
- **A stream whose oldest records retention let go** has its first record still on disk checked against the next, not against the ones before it, which are gone.

## Retention and what a stream forgets

A stream keeps what its declaration says, and the store says what it forgot.

- **A history stream** drops its oldest records once it holds more than its byte cap, or its record cap, without them. Records go a segment of the log at a time, so a stream holds up to one segment more than its cap until the next goes. What went leaves a **scar**: which records, and the time of the last. The stream answers from that time on, and a question about earlier says it is not known, not that nothing happened. The record of when its writer was attached goes with them: an attachment that ended before the scar is dropped, and so is what its writer said of its source before it.
- **A state stream** keeps each key's present value. Its earlier values are not history: once the store has folded them into the key's value, they are gone, and so is the record of a writer's attachment that ended before them. A change that would take it past its byte cap is refused; nothing is evicted.
- **A stream nothing writes any more** keeps what it holds until it is retired ([Retirement](#retirement)).
- **A history view** over its byte cap forgets its oldest rows, and below where it forgot it answers that it does not know.
- **A store at its budget** refuses what would take it past ([MAGI's limits](magi-limits.md#a-store)); no stream's records are evicted for another's.
- **Freed is not overwritten.** Records retention dropped, and earlier values of keys, leave the store's files; the filesystem may keep the blocks they were in until it reuses them.

## Views

A view changes in the same batch as what it reads, so it is never behind what it is over.

- **A view says where it is complete.** Where its sources are complete, so is it; where a source has a hole, so does the view, and it says so rather than answer as if nothing were there.
- **A source caught contradicting itself loses its claim.** A record arriving on a stream whose writer had marked that span of its source's clock complete, as having no such record, is kept, and the store no longer claims anything about that whole marked span: it becomes a hole, in the stream and in every view over it.
- **A view keeps what it declares.** A field a view did not declare is not in its rows.
- **A view declared over records already written is filled from them**, and answers as not yet known over what it has not reached.
- **A view built again holds what its sources hold now.** What a view had kept of records its sources have since let go does not come back when it is declared again or filled again.

## Files taken in

A file taken in with `magi blob` is held whole, named by the hash of its bytes.

- **A record names only what is held.** A record naming bytes of a file the store does not hold, or past its end, is refused, so every passage a record names can be read.
- **Its bytes cost no space where they can be shared.** On a filesystem that shares a file's bytes between copies, the store shares the original's, and `magi blob` says `shared`; elsewhere it says `copied`. Either way the store counts the whole length against its budget, since the original can be deleted.
- **Changing the original changes nothing in the store.** The store holds the bytes as they were taken in. A record found from them says whether the file at its path still holds them.
- **A file nothing names is let go** when the store is next opened, and magid logs it. One taken in and named by nothing yet is kept until then.

## Aliases

`magi alias PREFIX TO` makes every name beginning with PREFIX read as the same name beginning with TO, which is how a program rebuilds what it derived beside what you read and then switches you to it.

- **One switch moves every stream under the prefix at once.** A read before it sees the old streams and a read after it the new, never some of each.
- **Only reads follow an alias.** A write through one is refused and names the stream to write.
- **A switch can say what it replaces.** With `--expect NOW`, or `--new` for a prefix aliased to nothing, a switch whose prefix points elsewhere by then is refused and changes nothing.
- **A watch asked by an alias ends when the alias moves**, after every change to what it watched up to then, and says so. Watched again, it follows the new streams.
- **An alias is moved by the streams' writer**, on both sides of the switch, or by you through `magi alias`.
- **A store that holds an alias is refused by a MAGI that predates them**, by name rather than misread.

## Identity

A program names what it reads in a namespace of its own, an island: `code/magi/` for one tree, `code/axon/` for another. The same name in two islands is two things until something says otherwise, so a reach over two islands' graphs never crosses from one to the other by itself.

- **Two things become one only by a pair that counts.** A resolution (`same`, such as `code.same/identity`) reads pairs from the streams it names, and nothing else joins two islands.
- **You decide what counts.** A rule, `magi same NS rule NAME A B BY`, is yours, and `magi-code link` writes a pair for each name it joins, citing it. A pair a program guesses is a proposal, never read by a resolution, until you answer `yes`. `no` keeps a pair apart for good, whatever a rule says. A model's guess is only ever a proposal.
- **Your rules and answers are written by you.** magid lets only `magi` write them, so no other program can join two islands in your name.
- **Joining reads nothing again.** A rule added or taken back changes only the pairs; the facts of either tree are untouched, and the next reach answers by the pairs as they are.
- **A pair naming something no longer read joins nothing**, and joins again when it is read again.

`magi-code link` knows four rules:

| BY | joins a name that is |
| --- | --- |
| `imported` | defined in one tree, and used in the other only in files that import something only the first defines |
| `defined-once` | defined in one tree, and only used in the other |
| `same-blob` | defined in both, in files holding the same bytes |
| `same-path` | defined in both, in files of the same path, by its last three parts |

A name both define with nothing else in common stays two things, and is not asked about. A name is matched as it is written, so a rule joins what the names say: a name the other tree also takes from a library, such as `clone`, is joined with the rest.

## Redaction

[Removing something recorded by accident](../machine/what-the-machine-remembers.md#removing-something-recorded-by-accident) says what `magi redact` removes, and that the views over the stream no longer know the redacted record's instant. What else it costs, and what it cannot reach:

- **The record's batch-mates leave the views too.** On a stream whose records take their time from their batch, the other records of that batch share the instant, so they are withdrawn from the views with it. They stay in the stream.
- **A file's bytes go with the last record that names them.** Redacting every record that names bytes of a file taken in removes the file from the store before `magi redact` returns. While any other record still names it, it stays.
- **One place inside the store is not reached:** if the redacted value was the key through which one view was being filled from another, the store's catalogue can still hold it as that fill's position.
- **Outside the store, nothing is reached:** a backup taken before, an export, a copy someone else made, and the blocks the filesystem freed but has not yet reused.
- **A redaction is refused while a backup is being taken**, and says so. Run it again when the backup returns.
- **The store waits for it.** A redaction rewrites the store's tables, and batches that arrive meanwhile wait until it is done.

## Retirement

[Ending a stream](../machine/what-the-machine-remembers.md#ending-a-stream) says how. The streams named are retired together, or none is. A stream `magi retire` ends is no stream: a program writing to it is told no stream has that name, a writer attached to it is detached and the store says it was retired, and a stream declared under the name afterwards is a new one, empty. A view another view reads is retired after that view, or with it, named before it.

- **The views over it know nothing of it from then on.** A view says it does not know wherever the retired stream was its source, rather than answer as if nothing had been there, and a view of a state stream loses the keys it took from it. Neither reads a new stream declared under the name. What a view of a history stream had already found stays in it, as when a stream's retention lets records go.

- **Before it returns,** everything the stream held apart from the log is gone: its records filed out of the log, its searches, columns and connections, and every file taken in that only its records named, but for one taken in since magid last opened the store, which goes when magid next opens it.
- **Its records in the log go with the log.** The stretch being written now goes when the store begins the next; an earlier stretch that another stream still holds records in goes when that stream's retention lets them go. Until then they are in the store's files, and no read answers them.
- **It is not a redaction.** Nothing is zeroed. What must not be in the store's files at all is redacted first, then the stream retired.
- **A store at its budget still retires**, which is how it gets room back.
- **The store keeps a note of it** while any view reads it or any of the log may still hold its records: its name, when it was retired, and where its records ended. Then that goes too.
- **Outside the store, nothing is reached:** a backup taken before keeps the stream, and an export taken after does not have it.

## Backup

[Backing up a store](../machine/what-the-machine-remembers.md#backing-up-a-store) says how. A backup is the store at one moment, every record and key of it, verified before `magi backup` returns.

- **The indexes are not in it.** Searches, column scans and connections between records are built again from the copy when they are first asked, which takes the time building them takes.
- **What happens after is not in it**, a redaction included: a redaction made after a backup does not reach the backup.

## Export and import

[Taking the data out, and putting it in](../machine/what-the-machine-remembers.md#taking-the-data-out-and-putting-it-in) says how. An export holds every record, every key and every type exactly, floats to the bit; a store made again from it is the store it was to every reader, and its writers carry on where they were. What does not come across:

- **A view's rows.** A view is declared again in the new store and built from the records the export holds, so what it had kept of records its sources had already let go is not in it. A view's id is new.
- **The catalogue's length.** The new store's catalogue counts what the import itself wrote, one entry for each redaction repeated and each view declared again.
- **Files taken in come across whole**, in the export's `blobs` directory. An import without them refuses the records that name them, and leaves no store.
- **Retention while importing.** Nothing is evicted while the records go in; each stream's caps apply again from the store's next segment on.

## Updates and rollbacks

- **A rollback leaves a store alone.** A store a newer MAGI wrote is opened by an older one only as far as it can be without being changed: if it reads the store, it writes nothing to it; if it cannot, it refuses it and leaves it as it is, and going forward again finds it there.
- **The format is frozen.** Every MAGI that reads format 1 reads every format-1 store. What a later MAGI adds, it adds as a feature the store names, which an older MAGI refuses, or reads and writes nothing to.
- **A store from before the format froze is not read.** The first MAGI of format 1 sets such a store aside whole, as `/var/lib/magi/stores/UID.revN`, makes a new one in its place, and logs why. Nothing is deleted, but the new store starts empty: export each store before updating, and import the export afterwards. A store already set aside is exported with the earlier MAGI, from the generation before the update, with `magi export DIR --store` and its path.

## The machine's journal

[The machine's journal](../machine/what-the-machine-remembers.md#the-machines-journal) says what is kept of each entry. What is not:

- **The text of an entry with no message id.** Who logged it, from which unit, at what priority and when are kept; its words are not.
- **A field's value over 64 KiB**, such as a core dump. The entry records that the value was left out, and its length.
- **What journald never received.** The journal is complete relative to journald: what journald itself dropped, such as messages it rate-limited, is not counted as a hole.
- **Entries older than 1 GiB of journal**, which retention drops oldest first, with a scar.
