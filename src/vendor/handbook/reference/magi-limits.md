# MAGI's limits

The sizes, counts and rates MAGI holds to, and everything it refuses, with what it says when it does. A limit here is a promise too: what is under it is taken, and what is over it is refused before anything is written, never cut short. [What MAGI promises](magi-contract.md) says what is kept; [What the machine remembers](../machine/what-the-machine-remembers.md) is the chapter on using it.

## A store

| | |
| --- | --- |
| stores | one per account in `/etc/passwd`, at `/var/lib/magi/stores/UID`, and the system's at `/var/lib/magi/stores/system`. A uid with no account is refused: *uid N is no account in /etc/passwd, and only an account has a store*. |
| a store's budget | 10% of the filesystem holding the stores, unless `/etc/magi/budgets` says otherwise: one `UID-or-user-or-* AMOUNT` a line, the amount in bytes with `K`, `M`, `G` or `T`, or a percentage. The file must be root's and writable by nobody else, or it is ignored. |
| at its budget | a batch that would pass it is refused, naming the budget and where it came from, and a batch that only closes a writer's attachment is still taken. Nothing is evicted to make room. A new stream's byte cap is held to what the budget has left. |
| writers | one: magid. Stores are not shared across machines, and one store is one unit of atomicity: a batch spans streams of one store, never two stores. |
| the format | format 1. A store from before the freeze is set aside, not read ([What MAGI promises](magi-contract.md#updates-and-rollbacks)). |

## Streams

| | |
| --- | --- |
| a name | `NAMESPACE/NAME`, lower-case letters, digits, `-`, `_` and `.`, with any number of `/`-separated parts after the first. Ids are the store's to give, never a program's. |
| a declaration | names every column: kind, writer, signing (`unsigned`), trust, retention, a consumer, idempotency, durability, schema, and a view's plan. One that leaves out a consumer, a byte cap or a writer's program is refused. |
| declared again | exactly as it is, it answers with the stream as declared and writes nothing; differing in anything, it is refused. |
| signing | only `unsigned` is taken; a key is refused until signing ships. |
| retention | a byte cap, required; a history stream may add a record cap of at least one. A state stream has no record cap: its byte cap bounds its live keys and their values, and a change past it is refused. |
| who writes it | only the program that declared it, as the kernel names it. A writer cannot send a state change of kind `redact`, which only a redaction writes. |

## Records and keys

| | |
| --- | --- |
| a history record | at most 16 MiB. Larger data belongs in a file the record names. |
| a key | at most 512 bytes. Keys are compared as bytes, never by a collation. |
| a state value | at most 65,528 bytes: 64 KiB less the 8 the store keeps beside it. |
| a record's time | on a stream the engine witnesses, the time of the batch that commits it; any other time is refused. On a stream its source witnesses, the source's time, required, in a boot the stream's writer has placed, and never after the batch that carries it. |
| a token | required on a stream declared with idempotency, refused on one declared without. One not above the stream's last is a duplicate, and writes nothing. |
| a merge | add, max and min on 64-bit signed integers (an add that overflows is refused, never wrapped); union into a sorted set of byte strings; append; latest by a writer's stamp. A merge the stored value cannot take is refused, and so is its batch. |
| a type | fields of `bool`, `i8` to `i64`, `u8` to `u64`, `f32`, `f64`, text, bytes, a time, a blob reference, lists, maps with a scalar key, and vectors of `f32` or `f16`, nested at most 32 deep. Key fields are required, scalar, and not floats. A new version adds fields and changes none. |

## Requests

| | |
| --- | --- |
| a message | at most 32 MiB, and at most 65,536 operations across its batches. |
| a read | at most 4,096 records, or 16 MiB of them, a call; a program reads on from the last sequence it was given. |
| a range | at most 4,096 keys a call, and it says whether more follow. |
| a history view by time | at most 4,096 rows a call, with a cursor to go on from. |
| a search | at most 1,024 hits, and at most 64 values required and 64 excluded. |
| a column scan | at most 16 columns to group by, 64 aggregates, 2²⁰ groups, and conditions nested 64 deep. Floats are not summed. |
| following a graph | at most 4,096 seeds and 2²⁰ rows answered. |
| an answer too large for one message | refused, never cut short. |
| a watcher | is cut off once 8 MiB of changes wait unread for it. A store holds at most 128 MiB of the views watches started from for watchers that have not read them; a watch past that is refused. |
| a backup | read 8 MiB at a time, at most 2²⁰ files. |

## Connections

| | |
| --- | --- |
| at once | 4,096 connections across every store, or fewer when magid's file-descriptor limit is lower. An eighth of them is kept for the system's store. |
| per account | an eighth of the users' share. |
| saying who it is | a connection that has not said `Hello` within 5 seconds is let go. |
| the system's store | reached only through its own socket, which the security policy opens to the journal's tail, the administrator and the system's own managers; no other service reaches it, root or not. |

## Rates and times

| | |
| --- | --- |
| a `lazy` batch | synced within a second, five seconds under the `saver` power profile. |
| a `group` or `sync` batch | answered when an `fdatasync` covering it returns. |
| a store nobody uses | closed after five minutes with no request, no watcher and no writer attached; fifteen seconds under `saver`. The next request opens it again. |
| idle | magid sets no timer, and wakes for nothing. |
| a reopened store | replays at most about the last 8 MiB of its log, whatever has been written. |
| a redaction | holds the store's writer while it rewrites the store's tables; batches that arrive meanwhile wait. |
| a backup | holds the writer only for a checkpoint. A redaction is refused while one is being taken. |

## What a store does not do

- **Write across stores.** A batch is atomic within one store, and nothing orders two stores' batches against each other.
- **Compress.** A store's files are not compressed by the filesystem; a mount that forces compression ignores that.
- **Sign.** Streams are declared `unsigned`; signing a stream's head is on the roadmap.
- **Replicate.** A store lives on one machine. A fleet's record is on the roadmap.
