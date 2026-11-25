# The MAGI store format

This page specifies format 1 of a MAGI store, the files MAGI's engine keeps on disk for each store, byte by byte: every file, every encoding, every hash with its exact key, every catalogue entry, and what a reader must refuse. Format 1 is frozen, and the page is written for someone building a reader or a verifier of a store without MAGI's code. [What MAGI promises](magi-contract.md) says what the format guarantees a program, and [MAGI's limits](magi-limits.md) has the sizes it holds to.

## Conventions

Every integer is little-endian unless a section says otherwise; key encodings and history-view keys are big-endian, and say so. Offsets in a layout are bytes from the start of the structure.

| notation | meaning |
| --- | --- |
| `u8`, `u16`, `u32`, `u64` | an unsigned integer of that width, little-endian |
| `i64` | a signed 64-bit integer, two's complement, written as a `u64` |
| `[N]` | N raw bytes |
| `blob` | a `u32` length, then that many bytes |
| `str` | a `blob` holding UTF-8; a reader refuses one that is not UTF-8 |
| `leb` | an unsigned LEB128 number (below) |
| `time` | 24 bytes: a 16-byte boot id, then a `u64` of nanoseconds since that boot |
| `‖` | concatenation |
| `H(x)` | BLAKE3 of `x`, 32 bytes |
| `K(k, x)` | BLAKE3 in keyed-hash mode, key `k` (32 bytes), of `x`, 32 bytes |
| `le64(n)` | `n` as 8 little-endian bytes |
| `be64(n)` | `n` as 8 big-endian bytes |

**LEB128.** Seven bits a byte, least significant group first, the top bit set on every byte but the last. Only the shortest form is valid: a final byte of `0x00` after another byte is refused, so a number has exactly one encoding. A number is at most ten bytes, and in its tenth byte only the lowest bit may be set; each use below also names the largest value it takes, and a reader refuses a number above it. `300` is `ac 02`.

**Zigzag.** A signed difference `d` is stored as the unsigned `(d << 1) ^ (d >> 63)` (arithmetic shift), and read back as `(z >> 1) ^ -(z & 1)`. Differences are computed with wrapping 64-bit arithmetic.

**BLAKE3** is the standard function, with 32-byte output, in its hash and keyed-hash modes only. Every key below is 32 ASCII bytes, written here between quotes exactly as stored; `\0` is a zero byte.

| name | key |
| --- | --- |
| LINK | `"engram format v7: a block's link"` |
| GROUP | `"engram format v7: group header.."` |
| COMMIT | `"engram format v7: commit digest."` |
| GENESIS | `"engram format v7: stream genesis"` |
| HIST | `"engram format v8: history file\0\0"` |

**CRC-32C** is the Castagnoli CRC (reflected polynomial `0x82f63b78`, initial value and final XOR `0xffffffff`): CRC-32C of `"123456789"` is `0xe3069283`.

## A store

A store is one flat directory. Every name below uses 16 lower-case hexadecimal digits for a number. A reader ignores any name it does not know.

| file | what it is | a reader |
| --- | --- | --- |
| `log-<offset>.seg` | a log segment, named for the log offset of its first group | needs it |
| `checkpoint` | the folded catalogue at a batch boundary, and the root of the tables | needs it, if there is one |
| `tab-0000000000000000-<file>.run` | a sorted run of the store's one keyed space, which holds every state stream's and view's table | needs it to read state and views |
| `hist-<stream>-<segment>` | one history stream's blocks from one log segment, filed out of the log | needs it |
| `hidden-<offset>.side` | what a block holding a redacted record needs beside it to verify, named for the block's log offset | needs it to verify that block |
| `map-<segment>` | where each stream's blocks lie in one segment | may ignore it, and walk the segment |
| `blob-<hash>` | a file taken in, its bytes as they were, named by their BLAKE3 hash in 64 hexadecimal digits | needs it to read the bytes a `span` names |
| `checkpoint.tmp`, `hist-<stream>-<segment>.tmp` | a file being written when the writer stopped | ignores it; a writer removes it |
| `text-*`, `vec-*`, `cols-*`, `graph-*` | search, vector, column and graph indexes | not part of format 1 |

**The log** is one sequence of bytes, addressed by a **log offset**, cut into segment files. A segment named `log-X.seg` begins with a 128-byte header, and the byte at position `p` of the file, for `p ≥ 128`, is at log offset `X + p − 128`: headers take no log offsets. Segments hold groups of batches, each group whole within one segment. The segments a store keeps are in log order, and a segment the writer reclaimed leaves a gap; after the checkpoint's offset, every segment begins exactly where the one before it ends.

**What is derived.** The text, vector, column and graph indexes (`text-*`, `vec-*`, `cols-*`, `graph-*`) are built from the log and are not part of format 1: a reader may ignore them, and a writer may delete them at any time, which costs only the time to build them again. Block maps are part of format 1 but hold nothing the log does not; a reader may ignore them. Everything else is needed.

**Blobs.** A blob is written whole and never changed: its name is the BLAKE3 hash of every byte it holds, which a reader can check. A record's `span` field names bytes of a blob ([Typed records](#typed-records)), and a writer refuses a record whose span names a blob it does not hold or runs past its end. A writer removes a blob that no record names; a blob named by a redacted record only is removed by the redaction. A store with blobs uses the SPANS feature.

**One writer.** A store has one writer, which appends groups to the last segment, writes the other files whole beside it, and replaces the checkpoint by writing `checkpoint.tmp`, syncing it, renaming it over `checkpoint` and syncing the directory. A reader never writes.

## Features and revision

Every file of format 1 begins with `ENGRAM1` and a letter for its kind, except a table run, whose footer begins with it:

| magic | file |
| --- | --- |
| `ENGRAM1L` | a log segment |
| `ENGRAM1C` | the checkpoint |
| `ENGRAM1H` | a history file |
| `ENGRAM1T` | a table run (its footer) |
| `ENGRAM1S` | a sidecar |

A segment header, the checkpoint and a history file carry a **revision**, a `u32`, which is `1` and stays `1`. A reader refuses a file of any other revision: a revision above 1 is a store written by a later, incompatible format, which the reader leaves untouched.

**Features.** What a later writer adds to format 1, it adds as a **feature**: one bit, named before any writer sets it and never reused. Features are four bytes, two `u16` fields:

```text
0  u16  incompatible: a reader that does not know one of these refuses the store
2  u16  read-compatible: a reader that does not know one of these reads the store, and writes nothing to it
```

Features are sticky. Every segment header and every checkpoint carries every feature the store has used, so a store uses the union of the features in its checkpoint and in the headers of every segment from the checkpoint's on. A reader computes that union before it reads anything else, refuses the store if an incompatible bit is set that it does not know, and treats the store as read-only if a read-compatible bit is set that it does not know.

| bit | kind | name | meaning |
| --- | --- | --- | --- |
| `1 << 0` | read-compatible | SIGNED | the store holds signed stream heads (entry 13). Reserved: no writer of format 1 sets it yet. |
| `1 << 0` | incompatible | SPANS | a type the store carries has a `span` field, and the store holds blobs |
| `1 << 1` | incompatible | VECTORS | the store declares a vector view (plan 14) |
| `1 << 2` | incompatible | ALIASES | the catalogue holds an alias (entry 15), and the checkpoint carries the aliases |
| `1 << 3` | incompatible | RESOLUTIONS | the store declares a resolution (plan 15) |
| `1 << 4` | incompatible | RETIRES | the store has retired a stream (entry 16, gap code 4), and the checkpoint carries what it keeps of each retired stream |

A writer sets SPANS, VECTORS, ALIASES, RESOLUTIONS and RETIRES when the catalogue first holds what they name, and writes a checkpoint carrying them before it answers. No other bit is defined; a store that uses no feature has four zero bytes.

**A store from before the freeze.** A segment that begins `ENGRAM\0\0`, or a checkpoint that begins `ENGRAMCK`, belongs to a store written before format 1. A reader refuses it by name, giving the revision it holds at bytes 12..16, and does not treat it as damage. The way across is `magi export` with the MAGI that wrote the store and `magi import` with a MAGI of format 1 ([What MAGI promises](magi-contract.md#updates-and-rollbacks)).

## Log segments

A segment opens with a 128-byte header:

```text
  0  [8]   "ENGRAM1L"
  8  [4]   features
 12  u32   revision: 1
 16  u64   the log offset of the segment's first group: the number in its file name
 24  [16]  store id
 40  u64   the anchor's batch: the number of the last batch before the segment
 48  u64   the anchor's catalogue entry: the number of the last catalogue entry before it
 56  [32]  the anchor's commit digest: the commit chain's digest after that batch
 88  [32]  the anchor's catalogue link: the catalogue chain's link after that entry
120  [8]   the first 8 bytes of H(bytes 0..120)
```

The anchor says where the commit chain and the catalogue chain stand where the segment begins, so every group in a segment can be checked even after the segments before it are gone. The first segment of a store is at offset 0, and its anchor is batch 0, entry 0, the commit genesis and the catalogue genesis ([The chains](#the-chains)).

A reader checks a header in this order: a pre-freeze magic is refused by name; then the magic and the 8-byte check, either failing being damage; then the revision; then the features; then that bytes 16..24 equal the file name's offset. Every segment of a store holds the same store id.

After the header come groups, back to back. The last segment may end in zero bytes after its last group: a writer writes zeros ahead of the log, and where they begin, the log ends. A group never begins with a zero byte.

## Groups

A group is one write by the writer: one or more batches, each committed whole. It is linked once into the commit chain.

```text
  0  [4]  "EGRP"
  4  u32  group length, header to trailer inclusive
  8  u64  the group's own log offset
 16  u64  the number of its first batch
 24  u32  batches, at least 1
 28  u32  blocks
 32  u64  durable: the log offset the log was durable to when the group was written
 40  [8]  the first 8 bytes of K(GROUP, bytes 0..40)
 48       blocks, back to back
          the tape
          [32] trailer: the commit digest
```

**The tape** follows the last block and runs to the trailer. Per batch, in order:

```text
[16]  the batch's commit time: boot id
u64   the batch's commit time: nanoseconds
leb   spans
      per span: leb block index (below the group's block count), leb records (at least 1, at most 2^32 − 1)
```

The spans deal each batch's records out of the group's blocks in the order they were written, across streams: a span `(b, n)` is the next `n` records of block `b`. Over the whole tape, each block is dealt exactly its record count, and its records are dealt in their order within it. The tape ends exactly at the trailer.

**What makes a group valid.** Its header's check verifies; bytes 8..16 equal the offset where it lies; its length is at least 80 and fits where it lies; it has at least one batch; every block parses ([Blocks](#blocks)); the tape is as above and ends exactly at the trailer; its first batch is one more than the last batch before it (batches are numbered from 1); `durable` is no greater than the group's own offset; the trailer equals the commit digest ([The chains](#the-chains)); every block links into its stream; and every record and catalogue entry in it is one the fold accepts ([Folding the catalogue](#folding-the-catalogue), [State streams](#state-streams)). A group's batches stand or fall together: a reader applies none of a group until all of it is checked.

## Blocks

A block is one stream's records within one group. It is the unit of framing and of hashing.

```text
  0  u32   block length, header included
  4  u8    kind: 1 records, 2 catalogue entries
  5  u8    flags: 0x01 times, 0x02 tokens, 0x80 hidden
  6  u16   boots in the boot table
  8  u64   stream: 0 for the catalogue
 16  u64   the sequence number of its first record (for the catalogue, its first entry number)
 24  u32   records, at least 1
 28  u32   bytes of the record table
 32  [32]  seed
 64  [32]  link
 96        boot table: 16 bytes a boot
           record table
           payloads, back to back
```

**The record table** holds, per record, in order: `leb` payload length; then, with flag `0x01`, `leb` boot index (into the boot table) and `leb` zigzag nanoseconds from the record before (the first from 0); then, with flag `0x02`, `leb` zigzag token from the record before (the first from 0). A record's sequence number is the block's first plus its index in the block.

A reader refuses a block whose length is below 96 or past its group; whose kind is not 1 or 2; that sets a flag other than `0x01`, `0x02` and `0x80`; that has no records, or more records than its record table has bytes; whose boot table and record table run past it; whose boot table is empty with flag `0x01` or non-empty without it; whose record names a boot it does not have; or whose record table and payloads do not account for every byte exactly. A catalogue block (kind 2) is always stream 0 and a records block (kind 1) never is. A catalogue block carries neither times nor tokens.

**What a writer sets.** A stream witnessed by its source (declaration field 12) has its blocks written with flag `0x01`; a stream declared with an idempotency source has them written with flag `0x02`. A payload is at most 16 MiB. A writer starts a new block for a stream once a block's payloads reach 64 KiB, or its boot table holds 65,535 boots; a reader does not depend on where blocks are cut.

**A record's time** is its own, from the record table, when its block has flag `0x01`; otherwise it is its batch's commit time, from the tape of the group it was written in. A record's **token** is its value from the record table with flag `0x02`, and 0 without it.

**The seed** is 32 bytes the writer chooses for each block. A reader never derives it; it is not covered by the link, and a hidden block's seed is zero.

## The chains

A store has three kinds of chain: one per stream over its blocks, one for the catalogue (stream 0) over its blocks, and the commit chain over groups.

**A block's leaves and link.** For a block of `n` records with seed `s`, for `i` from 0 to `n − 1` (the index within the block, not the sequence number):

```text
nonce_i = K(s, le64(i))
leaf_i  = K(nonce_i, payload_i)
link    = K(LINK, prev ‖ head ‖ boot table ‖ record table ‖ leaf_0 ‖ … ‖ leaf_(n−1))
```

`head` is the block's bytes 0..32 with bit `0x80` of byte 5 cleared: the link covers neither the seed nor the hidden flag. The boot table and record table are exactly as stored. The link is stored at bytes 64..96.

`prev` is the stream's link before the block: the link of the stream's previous block, wherever it lies. A stream's first block chains from its **genesis**:

```text
stream genesis    = K(GENESIS, the stream's Declare entry, as its catalogue payload: 0x01 ‖ u64 id ‖ declaration)
catalogue genesis = H("engram v0 catalogue genesis" ‖ store id)
```

The quoted strings here are ASCII, without a terminator, followed by the 16-byte store id.

**The commit chain.** A group's trailer is:

```text
commit = K(COMMIT, prev commit ‖ group bytes 0..48 ‖ link of block 0 ‖ … ‖ link of the last block ‖ tape)
commit genesis = H("engram v0 commit genesis" ‖ store id)
```

`prev commit` is the trailer of the group before it, or the commit genesis before the store's first group. The header bytes 0..48 include the header's own 8-byte check.

## Hidden blocks and sidecars

A record is **redacted** in place. In every copy of its block, the writer first makes durable a sidecar named `hidden-<offset>.side`, where `offset` is the block's log offset, then zeroes the block's seed and the redacted record's payload (its length stays), and sets flag `0x80`. The link covers neither the seed nor the flag, so the chain stays whole; nothing left confirms a guess at what the record held.

```text
 0  [8]   "ENGRAM1S"
 8  u64   the log offset of the block it belongs to
16  u32   records: the block's record count
20        per record: u8 1 if redacted, 0 if not; [32] its leaf if redacted, its nonce if not
end [32]  H(every byte before)
```

A sidecar is `20 + 33 × records + 32` bytes. A reader refuses one shorter than 52 bytes, whose magic or checksum fails, whose length does not match its count, whose flag byte is neither 0 nor 1, that names another block, or whose count is not its block's.

**A hidden block verifies** through its sidecar: leaf `i` is the stored leaf for a redacted record, and `K(nonce_i, payload_i)` for any other, with the nonce taken from the sidecar; then the link is checked as for any block. A hidden block without its sidecar does not verify. Redacting a second record of a block rewrites the sidecar whole, keeping the first.

## The catalogue

Stream 0 is the **catalogue**: the store's own record of what streams exist, what types they are read by, what boots it knows and what each stream covers. Each catalogue block's records are entries, numbered from 1 across the whole store, chained like any stream from the catalogue genesis. An entry's payload is a tag byte and its fields, and a reader refuses an unknown tag or bytes after an entry's end.

| tag | entry | fields after the tag |
| --- | --- | --- |
| 1 | Declare | `u64` id, declaration |
| 2 | Open | `u64` stream, `time` at |
| 3 | Close | `u64` stream, `time` at, `u8` gap |
| 4 | Scar | `u64` stream, `u64` from, `u64` to, `time` at, `[32]` digest |
| 5 | Type | type |
| 6 | Mark | `u64` stream, `time` from, `time` to, `u8` hole, `u8` has count, `u64` count (0 without one) |
| 7 | none | never written; refused |
| 8 | Boot | `[16]` boot id, `u64` rank |
| 9 | Fill | `u64` view, `u8` source, `u64` through |
| 10 | Floor | `u64` view, `time` at |
| 11 | FillKey | `u64` view, `u8` source, `blob` after, `u8` done |
| 12 | Filed | `u64` stream, `u64` segment, `[32]` digest |
| 13 | Signed | `u64` stream, `u64` through, `u8` scheme, `blob` signature. Reserved: no writer of format 1 writes it. |
| 14 | Redacted | `u64` stream, `u64` seq, `time` at, `u64` block |
| 15 | Alias | `str` prefix, `str` to |
| 16 | Retired | `u64` stream, `str` name, `time` at |

A one-byte boolean is true when it is not zero. The gap codes of a Close:

| code | the interval ended because |
| --- | --- |
| 0 | the writer said it was stopping |
| 1 | the writer was meant to start and did not |
| 2 | the engine stopped with the interval open, and closed it when it came back |
| 3 | the writer's connection ended without its saying it was stopping |
| 4 | the stream was retired |

What each entry means:

- **Declare** creates stream `id`, as its declaration says. Ids are given in order from 1.
- **Open** and **Close** begin and end a coverage interval: a span during which the stream's writer was attached and the engine witnessed everything it sent.
- **Scar** says records `from..=to` of the stream are gone, by retention or by its retirement. `digest` is the link after record `to` (the last block holding it), from which the chain resumes, and `at` is that record's time, below which the stream no longer answers.
- **Type** is a type, or a new version of one, that the store carries: every typed stream is read by its store's own types.
- **Mark** is said by the writer of a source-witnessed stream: `[from, to)` on the source's clock is complete, or, with `hole`, a hole, holding `count` records if the source counted them. A `to` of `u64::MAX` nanoseconds is the end of its boot. On a view, a mark is the engine's own: a hole where the view dropped what it held.
- **Boot** gives a boot its rank among the store's boots. Ranks order boots; a rank is never 0 and never changes.
- **Fill** and **FillKey** record how far a history view declared over existing records has been fed what one of its sources held: through sequence `through`, or for a source that is itself a view, through row key `after`, and all of it once `done`. `source` is the source's place in the plan.
- **Floor** says a history view over its cap forgot its rows before `at`.
- **Filed** says the stream's records written in segment `segment` are now in its history file for that segment, whose digest is `digest` ([History files](#history-files)).
- **Signed** would say the stream's chain through record `through` is signed with `signature` under `scheme`. A store holding one sets the SIGNED feature.
- **Redacted** says record `seq` of the stream, of time `at`, in the block at log offset `block`, is redacted: hidden in place wherever that block lies. It says only that it was.
- **Alias** says that from here on, a reader's name beginning with `prefix` stands for the same name with `to` in place of the prefix. Only reads follow an alias; a write names the stream it writes. A later Alias of the same prefix replaces it, and none removes it.
- **Retired** says stream `stream`, named `name`, is retired at `at`: from here on it is no stream, its name is free, and a stream declared under the name later is another, with its own id. A retirement's batch holds, for each stream it retires, a Close with gap 4 if the stream's last interval is open, then for a history stream holding records a Scar from its floor to its head, then the Retired entry; and nothing but such entries, the boot entry a writer's first commit in a boot carries, and the entries a writer adds for history views over their caps.

### The stream declaration

A declaration is a sequence of tagged fields, each a `u8` field id and its value, in ascending id order, ended by a `0` byte. No length precedes it, so a reader decodes every field, a plan included, to find where it ends. A reader refuses a field id it does not know, rather than skip it, and refuses a declaration missing any of fields 1 to 10.

| id | field | value |
| --- | --- | --- |
| 1 | name | `str`: `<namespace>/<name>` |
| 2 | kind | `u8`: 0 history, 1 state, 2 view |
| 3 | writer | `u32` uid, `str` program |
| 4 | signing | `u8` 0 unsigned; or `u8` 1 and `str` key (reserved: no writer of format 1 declares one) |
| 5 | trust | `u8`: 0 native, 1 upstream, 2 patched, 3 parsed, 4 inferred |
| 6 | retention | `u64` byte cap, `u64` record cap (0: none) |
| 7 | consumer | `str` |
| 8 | idempotency | `u8` 0 none; 1 sequence; or 2 and `str` the external cursor it is derived from |
| 9 | durability | `u8`: 0 lazy, 1 group, 2 sync |
| 10 | schema | `str`: a type `<package>.<type>`, or `bytes` for records nothing types |
| 11 | plan | a view's plan ([Plans](#plans)); present on a view and only on a view |
| 12 | witness | `u8`: 0 the engine, 1 the source. Written only when it is 1; absent, it is 0. |

A **history** stream is append-only records. A **state** stream is changes to keys ([State streams](#state-streams)). A **view** is written by nothing: the engine derives it from its sources by its plan, and declares it with idempotency none and schema `bytes`.

### Plans

A plan is a `u8` tag and its fields. Within a plan:

- `ids` is a `u32` count, then that many `u16` field ids;
- `pairs` is a `u32` count, then that many pairs of `u16` (a left field id, a right field id);
- `keep` is `u8` 0, keeping the record whole, or `u8` 1 and `ids`, keeping those fields (an empty list keeps nothing);
- `pred?` is `u8` 0 for none, or `u8` 1 and a predicate; any other byte is refused.

| tag | plan | fields after the tag |
| --- | --- | --- |
| 1 | index | `str` source, `ids` fields |
| 2 | filter, keeping the whole record | `str` source, predicate |
| 12 | filter | `str` source, predicate, `keep` |
| 3 | project | `str` source, `ids` fields |
| 4 | join, keeping both records whole | `str` left, `u16` field, `str` right |
| 13 | join | `str` left, `u16` field, `str` right, `keep` of the left, `keep` of the right |
| 5 | history filter | `str` source, `pred?`, `ids` fields |
| 9 | history filter that derives fields | `str` source, `pred?`, `ids` fields, `u32` count, then per derived field: `str` name, `u16` map field it reads, `str` map key, `str` type (`text`, `bytes`, `u64` or `i64`) |
| 6 | band join | `str` left, `str` right, `pairs` on, `u64` δ in nanoseconds, `ids` left fields, `ids` right fields |
| 7 | antijoin | `str` left, `str` right, `pairs` on, `u64` δ in nanoseconds, `ids` fields |
| 8 | count | `str` source, `ids` by, `u64` window width in nanoseconds, `pred?` |
| 10 | text search | `str` source, `u32` count, then per field: `u16` field, `u8` weight; then `ids` key fields |
| 11 | edges | `str` source, `u16` from field, `u16` to field |
| 14 | vectors | `str` source, `u16` field, a `vec<f32,N>` or `vec<f16,N>` with N at most 65,536 |
| 15 | resolution | `u32` count (1 to 16), then that many `str` sources; `u16` island and `u16` value field of one end, then of the other; `pred?` |

Plans 1 to 4, 12 and 13 are over typed state streams; 5 to 9 over typed history streams or history views; 10 and 14 over a typed history stream; 11 over a typed history or state stream; 15 over typed state streams of one type, whose island fields are `text`. A text search, edges, vectors or resolution view holds no rows: its index is derived, outside format 1, and only its declaration is in the store. A text search's field is `text` or `span`; a span's bytes are searched as UTF-8, each sequence that is not read as U+FFFD.

A **predicate** is a `u8` tag, nested at most 64 deep:

| tag | predicate | fields after the tag |
| --- | --- | --- |
| 1 | the field is present and compares so to the constant | `u16` field, `u8` comparison (0 `=`, 1 `≠`, 2 `<`, 3 `≤`, 4 `>`, 5 `≥`), constant |
| 2 | the field is present | `u16` field |
| 3 | and | predicate, predicate |
| 4 | or | predicate, predicate |
| 5 | not | predicate |

A **constant** is a `u8` kind and a value: 1 bool (`u8`), 2 signed integer (`i64`), 3 unsigned integer (`u64`), 4 float (`u64`: an `f64`'s bits, or an `f32`'s bits zero-extended), 5 text (`str`), 6 bytes (`blob`), 7 time (`[16]` boot, `u64` nanoseconds), 8 blob (`[32]`). Any other kind is refused. Floats compare by their bit patterns as unsigned integers.

### Types and schemas

A **type** entry, and each type the checkpoint carries, is:

```text
str  name: <package>.<type>
u32  version: 1 for the first; each later one is one more
str  the schema text
u8   origin: 0 installed by a package, 1 declared by a program
u32  owner uid
str  owner program
```

A store takes a type's version 1 only if its schema parses, and version `n + 1` only if version `n` is the latest it holds, the origin and owner are the same, and the new schema **extends** the old: every old field is still there with the same id, name, type and optionality, every new field is optional, and the key is unchanged. So every record written under an earlier version decodes under the latest, and a reader reads every record by the latest version the store carries.

**The schema text** is one field a line, `<id> <name> <type>`, and at most one line `key <name>, <name>…` naming the key fields in key order. Text after `#` is a comment, and blank lines are ignored. Ids are decimal, from 1, strictly ascending down the file. A name is lower-case ASCII letters, digits and `_`, unique in the schema. A type ending in `?` may be absent. A key field is required, a scalar, and not a float. A schema declares at least one field.

```text
# geofront.artifact: one RPM in a repository
key file
1 file     text
2 name     text
3 epoch    u32
7 size     u64
9 disturl  text?
```

The types: `bool`, `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32`, `u64`, `f32`, `f64`, `text`, `bytes`, `time`, `blob`, `span`, `list<T>`, `map<K,V>` (K a scalar), and `vec<f32,N>` or `vec<f16,N>` (N at least 1). Lists and maps nest at most 32 deep. The scalars are every type but lists, maps, vectors and `span`. A `blob` is a content hash and nothing more; a `span` names bytes the store holds ([Blobs](#a-store)).

### Typed records

A typed record is its present fields in strictly ascending id order, each a `leb` field id (at most 65,535) and its value:

| type | value |
| --- | --- |
| `bool` | `u8` 0 or 1 |
| `i8`…`i64`, `u8`…`u64` | the integer, little-endian, at its width |
| `f32`, `f64` | the float's bits, little-endian, at its width |
| `text`, `bytes` | `leb` length (at most 2^32 − 1), then the bytes; `text` is UTF-8 |
| `time` | `[16]` boot id, `u64` nanoseconds |
| `blob` | `[32]`: a content hash |
| `list<T>` | `leb` count, then the items |
| `map<K,V>` | `leb` count, then the pairs, keys strictly ascending |
| `vec<f32,N>`, `vec<f16,N>` | N values of 4 or 2 bytes, little-endian; no count |
| `span` | `[32]` a blob's hash, `u64` offset, `u32` length; offset plus length below 2^64 |

The encoding is canonical, so equal records are equal bytes. A reader refuses a field id the schema does not have, a field out of order or repeated, a required field missing, a `bool` that is not 0 or 1, text that is not UTF-8, map keys out of order, and a number not in its shortest form.

**A key** orders as bytes, never by collation. A keyed type's key is each key field's value in key order, each encoded as:

| type | in a key |
| --- | --- |
| `bool` | one byte, 0 or 1 |
| signed integers | 8 bytes, whatever the width: `be64(value as u64 ^ 2^63)` |
| unsigned integers | 8 bytes, whatever the width: `be64(value)` |
| `text`, `bytes` | the bytes, each `00` written `00 ff`, then `00 00` |
| `time` | the 16-byte boot id, then `be64(nanoseconds)` |
| `blob` | the 32 bytes |

### Folding the catalogue

A reader folds the catalogue entry by entry, in order, into the state the checkpoint also carries ([The checkpoint](#the-checkpoint)). The fold of a store with no checkpoint starts with no streams, no types, no boots, next id 1, entry 0 and the catalogue genesis. An entry the fold refuses makes its group invalid.

| entry | accepted when | effect |
| --- | --- | --- |
| Declare | `id` is the next id, no stream has the name, and the name begins with no aliased prefix | the next id moves on; a new stream with head 0, head link and floor link its genesis, floor 1, and nothing else; a history view gets one fill per plan source, as below |
| Type | as in [Types and schemas](#types-and-schemas) | the type's latest version is this |
| Boot | the boot has no rank yet, the rank is not 0, and no boot has the rank | the boot is ranked; boots are kept in rank order |
| Open | the stream exists and its last interval is closed, or it has none | a new interval from `at`, opened at this entry's number, closed at 0 |
| Close | its last interval is open | that interval ends at `at` for the gap, closed at this entry's number |
| Scar | `from` is the stream's floor, `from ≤ to ≤` head | segment uses whose last record is at most `to` go from the front; the floor becomes `to + 1`, its link `digest` and its time `at`; redactions at or below `to` go; a closed interval goes if it closed before `at` in `at`'s boot, and a mark goes if it ends before `at` in `at`'s boot |
| Mark | the stream is a history stream witnessed by its source, `from` and `to` are in one boot with `from` before `to`, and only a hole has a count; or the stream is a view and the mark is a hole within one boot | see below |
| Fill | the source's fill is by sequence, and `through` is above where it stood and at most its end | the fill stands at `through` |
| FillKey | the source's fill is by key and not done, and `after` is above where it stood, or equal to it with `done` set | the fill stands at `after`, done if `done` |
| Floor | the stream is a view | the stream's floor time becomes `at`, and its intervals and marks below it go as for a Scar |
| Filed | the stream is a history stream with an unfiled segment use for `segment` | that use is filed, with `digest` |
| Signed | `1 ≤ through ≤` head | nothing is kept |
| Redacted | a history stream with floor `≤ seq ≤` head, or a state stream with `1 ≤ seq ≤` head; never a view; not already redacted | the redaction is added, in sequence order |
| Alias | `prefix` and `to` each end in `/` and are at least two bytes; they differ; `to` does not begin with `prefix`; no stream's name begins with `prefix`; no other aliased prefix begins `prefix` or is begun by it; `to` is not an aliased prefix and begins with none other than `prefix` | `prefix` is aliased to `to` |
| Retired | the stream exists and is named `name`; its last interval is not open; a history stream's floor is above its head | the stream leaves the streams for the retired ones, as below |

Every entry about a stream refuses a stream that does not exist, and a retired stream does not.

**A retired stream** is kept as the stream it was, with its floor its head plus one, its floor link its head link, its floor time its head time (if it has a head), no segment uses and no redactions, and with `at` and the segment the entry was written in. A view declared over it still reads it: a view's sources are the streams of their names that were declared before the view, retired or not, so a stream declared later under the same name is not one of them. A writer forgets a retired stream once the segment its Retired entry was written in is reclaimed and no stream's plan names it; ids are never given again, so none is mistaken for it. Every accepted entry moves the catalogue's entry number on by one.

**A Mark** that is complete, after a last mark that is complete too, in the same boot, with `from` within the last mark's span (`last.from ≤ from ≤ last.to`), extends the last mark: its `to` becomes the later of the two, and it is learned again at this entry's number. Any other mark is added, learned at this entry's number.

**A history view's fills**, made when it is declared, one per source in plan order: a source that is a view gets a fill by key, with `after` empty, done only if the same source appears earlier in the plan; any other source gets a fill by sequence ending at the source's head, standing at the head if the same source appears earlier in the plan and at its floor less one if not.

**A record** of stream `s` with sequence `q` and token `t`, in a segment starting at offset `g`, is accepted when `s` exists, is not 0, and `q` is its head plus one; when, for a stream declared without idempotency, `t` is 0; and when, for a stream with idempotency, `t` is 0 or above the stream's last token. Then the head becomes `q`, the head time the record's time, and the last token `t` if `t` is not 0. If the stream's last segment use is for segment `g`, its records go up by one, its bytes by the payload's length, and its last sequence and time become the record's; otherwise a new segment use for `g` is added with one record, the payload's bytes, and the record's sequence and time.

**After each group**, for each block, the bytes it spends beyond its payloads (its length less their sum) are added to its stream's last segment use; then each stream's head link, and its last segment use's link, become the link of its last block in the group, and the catalogue's head link the link of the last catalogue block.

A catalogue entry's number is its block's first number plus its index, and must be the catalogue's last number plus one.

## State streams

A state stream's record is one change to one key:

```text
blob  key
u64   expect: u64::MAX for no condition; 0 for a key that must not exist; otherwise the version the key must be at
u8    change, then its fields:
        1  put     blob value
        2  del
        3  merge   merge
        4  merge into a field   u16 field id, merge
        5  redact
```

A merge is a `u8` and its fields:

| id | merge | fields | folds the stored value `old` (absent: none) into |
| --- | --- | --- | --- |
| 1 | add | `i64` n | `old + n`, `old` an 8-byte `i64` (absent: 0); an overflow is refused |
| 2 | max | `i64` n | the larger of `old` and `n` (absent: `n`) |
| 3 | min | `i64` n | the smaller (absent: `n`) |
| 4 | union | `u32` count, then count `blob` | the set `old` with each element added; a set is `u32` count, then its elements as `blob`, strictly ascending |
| 5 | append | `blob` bytes | `old` followed by the bytes (absent: empty) |
| 6 | latest | `u64` stamp, `blob` bytes | `le64(stamp) ‖ bytes`, unless `old`, whose first 8 bytes are its stamp, has a later stamp, in which case `old` |

A reader refuses an unknown change or merge, and bytes after the record.

**How a record folds.** Each key holds a **version**, the sequence number of the record that last changed it, and its bytes. A record of sequence `q` with an `expect` other than `u64::MAX` requires the key's version to equal it, an absent key being at version 0. Then:

- **put** stores the value. On a typed stream the value must decode whole under the stream's type, and if the type is keyed, the key computed from the value must equal the record's key.
- **del** and **redact** remove the key.
- **merge** folds into the whole value of an untyped stream's key, as the table above says; on a typed stream it is refused.
- **merge into a field** applies only to a typed stream, to a key that exists, and to a field that is not a key field. Into a signed integer field, add, max and min are taken in `i64`; into an unsigned one, in a wider range and the result must be a `u64`; either way the result must fit the field's width. Union adds into a `list<text>` or `list<bytes>` and keeps the list sorted and without duplicates. Append extends a `text` (the bytes must be UTF-8) or `bytes` field. Latest is refused. An absent optional field folds from add's 0, max's and min's `n`, an empty list or empty bytes. The record is encoded again canonically.

A key whose value changes is at version `q`. A stream's **live bytes** are the sum, over its keys, of key length plus 8 plus value length, and a change that grows them past the stream's byte cap is refused. A change the fold refuses was never written: a log that holds one is damaged.

A **redact** record is written only by a redaction, never by a program. Folding it also adds the record itself to the stream's redactions, with its time and its block's log offset. Every earlier record of the key still on disk is named by a Redacted entry in the same batch.

## The checkpoint

The checkpoint is the folded catalogue at a batch boundary, and the root of the tables there. A reader starts from it and replays only the log after it.

```text
[8]   "ENGRAM1C"
[4]   features
u32   revision: 1
[16]  store id
u64   offset: the log offset replay resumes from
u64   batch: the number of the last batch before it
[32]  the commit digest after that batch
time  when that batch was committed
...   the folded catalogue, below
u32   block maps, then per map: u64 segment, u64 length of its valid bytes, u64 the log offset it maps to
...   with ALIASES only: u32 aliases, in prefix order, then per alias: str prefix, str to
...   with RETIRES only: u32 retired streams, in ascending id, then per stream: the stream as
      the folded catalogue lays one out below, time at, u64 the segment its retirement was written in
[32]  H(every byte before)
```

A reader refuses a checkpoint whose magic is not `ENGRAM1C` (and names a pre-freeze one), whose checksum fails, whose revision is not 1, whose features have an incompatible bit it does not know, or with bytes after its end. The folded catalogue:

```text
u64   the id the next declaration takes
u64   the catalogue's last entry number
[32]  the catalogue chain's link there
u32   streams, then per stream, in ascending id:
  u64    id
  ...    its declaration
  [32]   genesis
  u64    head: its last sequence number
  [32]   head link: the link of its last block
  time   head time: its last record's time
  u64    last token
  u32    coverage intervals, then per interval:
           time  from
           u8    0xff while open; otherwise the gap code, then time to
           u64   the entry number that opened it
           u64   the entry number that closed it, 0 while open
  u32    marks, in the order learned, then per mark:
           time from, time to, u8 hole, u8 has count, u64 count (0 without one), u64 the entry number that learned it
  u64    floor: the first sequence number it still answers for
  [32]   floor link: the link its floor's block chains from
  u8     0 with no floor time; or 1, then time floor time
  u32    segment uses, in log order, then per use:
           u64   segment: the log offset of the segment its records were written in
           u64   records
           u64   bytes: their payloads, and every byte their blocks spend beyond them
           u64   last sequence
           time  last time
           [32]  last link: the link of its last block in that segment
           u8    0 while in the segment; or 1, then [32] its history file's digest
  u64    live bytes of its table (a state stream's or a view's)
  u64    live bytes of its held table (a history view's)
  u32    fills, one per plan source of a history view, then per fill:
           u8 0, u64 through, u64 end       (by sequence)
           u8 1, blob after, u8 done        (by key)
  u32    redactions, in ascending sequence, then per redaction:
           u64 seq, time at, u64 the block's log offset
u32   types, in name order, each at its latest version, as a Type entry holds one
u32   boots, in rank order, then per boot: [16] boot id, u64 rank
u8    0 with no tables yet; or 1, then blob: the tables' root
```

A reader refuses a checkpoint that names a segment use past its own offset; a block map that is not of the log before its offset or not in log order; a stream whose head is `u64::MAX`, whose floor is more than one past its head, whose segment uses are out of log or sequence order, or one of whose segment uses holds a record past its head; and a redaction list out of order, or naming a record above the head or below the floor (for a state stream, below 1); and a retired stream whose id is not below the next id, or is a stream's. A segment-use, fill or table-root kind byte other than those above is refused.

**At a checkpoint, state streams and views are folded.** Every state stream's and view's table as of the checkpoint's offset is in the runs the root names, so each such stream's floor is its head plus one, its floor link its head link, its floor time its head time, and it has no segment uses: none of its records before the offset needs replay. A stream with a head forgets its intervals and marks below its floor time, as a Scar does. A stream declared after the checkpoint has nothing in a run yet.

## Tables

Every table of a store is in **one keyed space**: every state stream's table, every view's, and every history view's held table. The space is stored as a list of immutable sorted runs, newest first, that the checkpoint's table root names.

**Keys and values.** A table's key is stored as its table's id, `be64`, then the key; a stored key is at most 520 bytes, so a table's key is at most 512. A table's id is its stream's id, or, for a history view's held table, the view's id with bit 63 set. Every stored value is a `u64` version, then the value's bytes; a stored value is at most 64 KiB.

**The root** is the table root's blob from the checkpoint:

```text
u64  next file number: every run it names is below it
u32  runs
     per run, newest first: u64 file number
```

Run `F` is the file `tab-0000000000000000-<F>.run`. To find a key, a reader asks the runs newest first: the first run that holds an entry for the stored key decides, and a tombstone there means the key is absent. To scan, a reader merges the runs in key order, the newest entry for a key winning and tombstones dropped. A reader opening a store to read only never removes a run; a writer removes, on open, any run the root does not name.

### Table runs

A run is written once and never changed.

```text
pages 0 .. d          data pages: leaf pages of entries in stored-key order, tombstones included,
                      and before a leaf, the overflow pages of the values too large for it
pages d .. d+f        fence pages: branch pages holding each leaf's first key and its page number
then                  the bloom filter: w little-endian u64 words
last 128 bytes        the footer
```

The footer:

```text
  0  [8]   "ENGRAM1T"
  8  u64   d: data pages, at least 1
 16  u64   f: fence pages
 24  u64   w: bloom words, a positive multiple of 8
 32  u64   entries, tombstones included
 40  u32   bloom probes: 7
 44  u8    the pages' checksum: 1, CRC-32C
 45  [3]   zero
 48  [32]  H(the bloom words, as stored)
 80  [40]  zero
120  [8]   the first 8 bytes of H(le64(F) ‖ footer bytes 0..120), F the run's file number
```

A reader refuses a run whose footer check or magic fails, whose byte 44 is not 1, whose length is not `(d + f) × 4096 + 8w + 128`, whose probes are not 7, or whose bloom hash fails.

**A page** is 4096 bytes:

```text
   0  u8    kind: 1 leaf, 2 branch, 3 overflow
   1  u8    zero
   2  u16   entries
   4  u32   zero
   8        entries, back to back: u16 key length, u16 value length, key, value
4088  u32   CRC-32C of le64(F) ‖ le64(page number) ‖ page bytes 0..4088
4092  [4]   zero
```

Bytes after the last entry are zero. A value length of `0xffff` is a tombstone, with no value. A value length of `0xfffe`, allowed only in a leaf, marks an **overflow entry**: its 12 value bytes are a `u64` first overflow page and a `u32` value length, and the value is in that many consecutive overflow pages from there, 4080 bytes each, a page's bytes 8..4088, the last page's unused bytes zero. An overflow page has no entries. A writer puts a value in overflow pages when 4 bytes plus its key and value are over 1024, and writes them just before the leaf that names them. The checksum binds a page to its run and its place, so a page in the wrong place fails as a flipped bit does.

**Fences.** The branch pages, in order, hold one entry per leaf: the leaf's first stored key, and its page number as an 8-byte `u64` value. Page numbers strictly ascend and are below `d`, and the last is `d − 1`. A key lies in the last leaf whose first key is at most it. A leaf is never empty.

**The bloom filter** answers that a stored key is certainly absent. The filter is `w / 8` blocks of 8 words (512 bits). For a stored key `k`, with all arithmetic wrapping on 64 bits, `M = 0x9e3779b97f4a7c15`, and `rotl`, `rotr` rotating:

```text
h = 0x243f6a8885a308d3 ^ (len(k) × M)
for each whole 8-byte chunk c of k:    h = rotl((h ^ le_u64(c)) × M, 29)
the remaining 0..7 bytes, zero-padded to 8 as r:    h = (h ^ le_u64(r)) × M
h ^= h >> 32;  h ×= 0xd6e8feb86659fd93;  h ^= h >> 29

block = (h × blocks) >> 64, as a 128-bit product
x = rotl(h, 29) ^ (h >> 17)
7 times:  bit = x & 511;  x = rotr(x, 9)
```

Each of the 7 bits is set in the block: bit `b` is bit `b % 64` of word `block × 8 + b / 64`. A key is possibly present only if all 7 are set. A writer sizes the filter at `max(1, ⌈entries × 10 / 512⌉)` blocks.

### What the tables hold

**A state stream's table** holds each live key under the stream's key, its value the key's version and bytes ([State streams](#state-streams)).

**A state view's table** holds the view's rows, each value a version (the sequence number of the source change that last wrote the row, or 0 for a row written when the view was declared) and its bytes:

| plan | a row's key | its bytes |
| --- | --- | --- |
| index | the fields' values as a key, in plan order, then the source's key | empty |
| filter | the source's key, for a record the predicate holds for | the record whole, or the kept fields as a typed record |
| project | the source's key | the record with only those fields, as a typed record |
| join | the left record's join field as a key, then the left's key | the left half, then the right half |

A join row's left half is `blob` the kept fields of the left record (the whole record when it keeps it whole), absent when it keeps nothing of the left. Its right half is `u8` 0 when no right record has the join value as its key, or `u8` 1 then `blob` the kept fields of that right record, and absent when it keeps nothing of the right. The right stream is keyed by one field, of the join field's type.

**A history view's table** holds the rows it has emitted. Every key begins with a time: the boot's rank, `be64`, then the nanoseconds, `be64`. An **identity** is a `u16` big-endian length and that many bytes: a stream record's is its sequence number, `be64`; a view row's is its key after the time. Every value has version 0.

| plan | a row's key | its bytes, as a typed record of the row type |
| --- | --- | --- |
| history filter | the source record's time, its identity | the kept fields under their own ids, and derived fields numbered from `0x8000` in plan order |
| band join | the left's time and identity, then the right's nanoseconds (`be64`, same boot) and identity | the left's fields, then the right's, numbered 1, 2, … in plan order and named `l_…` and `r_…` |
| antijoin | the left's time and identity | the left's kept fields under their own ids |
| count | the window's start time, then the `by` fields' values as a key | field `n + 1`, `count` (`u64`), and field `n + 2`, `trust` (`u8`: the least trusted class counted), for `n` by fields; the by fields are numbered 1 to `n` and are read from the key |

A record's time in a history view is its time with the boot replaced by the boot's rank, so a record whose boot the store has not ranked is in no history view. A row is encoded under its row type partially: a field absent from the source is absent from the row. The held table (id with bit 63 set) is the view's own working state, rows waiting on what is not yet known; a reader of the view's rows may ignore it.

**Keeping views current past the checkpoint.** A state stream's table at the checkpoint is completed by replaying its records after the checkpoint, by the rules in [State streams](#state-streams). A view's table at the checkpoint is its rows there; the rows after it follow from its sources' records by the view's plan, and when a history view's row is emitted depends on what the store knows of its sources' completeness. This page specifies how rows are stored, not when a writer emits or withdraws them; a reader that needs a view's rows past the checkpoint either derives them itself from the plan, or asks MAGI.

## History files

A history stream's blocks from one closed segment can be copied out of the log, byte for byte, into a history file, so that the segment can be reclaimed while the stream still retains them. The file is `hist-<stream>-<segment>`, and a Filed entry records its digest in the stream's segment use.

```text
  0  [8]   "ENGRAM1H"
  8  [4]   features: none
 12  u32   revision: 1
 16  [16]  store id
 32  u64   stream
 40  u64   segment: the log offset of the segment the blocks were written in
 48  u32   blocks
 52  u32   bytes of the directory
 56  u16   boots in the boot table
 58  [6]   zero
 64  [32]  prev: the link the first block chains from
 96  [32]  digest = K(HIST, bytes 0..96 ‖ boot table ‖ directory)
128        boot table: 16 bytes a boot
           directory
           the blocks, verbatim and in order
```

**The directory**, per block, in `leb`: the block's log offset less the previous block's (the first block's less `segment`; after the first, never 0). Then, for a block without flag `0x01`, whose records take their batch's time, its **time runs**: a count (at least 1, at most the block's records); and per run, the record index it starts at less the previous run's (the first run's 0, every later one's above 0), a boot index, and zigzag nanoseconds from the previous run's, counting across the whole file from 0. Record `i` of such a block has the time of the last run starting at or before `i`.

Each block keeps its log offset as its address: its sidecar is still named for it, and its link and leaves are the ones the log had. A reader refuses a file of another revision, with an unknown incompatible feature, whose zero bytes are not zero, whose directory runs past it, whose digest fails, whose blocks are not the stream's record blocks with consecutive sequence numbers, or whose directory and blocks do not account for every byte. The file is the one the catalogue names only if its digest is the digest in the Filed entry, and its stream, segment and store id are the ones expected. Its first block chains from `prev`, and each later block from the one before it.

The tape that held a filed record's batch time stays behind in the segment; the directory's time runs carry it instead, and the catalogue's chain holds the directory's digest.

## Block maps

A segment's block map, `map-<segment>`, says where each stream's record blocks lie in it, so a reader need not walk the segment. Each checkpoint appends one chunk to the map of every segment it covers, mapping the groups between where the map ended and the checkpoint's offset, and records the map's valid length and the offset it maps to. Bytes past that length are never read. A map holds no link: a block read through it is checked against the link of the block before it, as a walk would.

Per chunk:

```text
  0  [4]   "EMAP"
  4  u32   chunk length, header to checksum inclusive
  8  u64   from: where the chunk before ended (the first chunk's: the segment's offset)
 16  u64   to: the log offset it maps to
 24  [16]  store id
 40  u32   groups
 44  u16   boots in the boot table
 46  [2]   zero
 48        boot table: 16 bytes a boot
           per group, leb: its offset less where the last group ended (the first, less from), its length, its record blocks
             per record block, leb: stream; zigzag first sequence less one past that stream's last block in the chunk
               (or less 0); records; offset within the group; length; then one byte:
               1  its records carry their own times
               2  they take their batch's time, not noted here (a reader takes it from the group's tape)
               0  they take their batch's time, noted here as time runs: a count, and per run the record index it
                  starts at less the previous run's in the block, a boot index, and zigzag nanoseconds from the
                  chunk's previous run's (from 0)
end  [4]   CRC-32C of the chunk before it
```

A map is only a shortcut. A map whose chunk fails its checksum, names another store, does not start where the one before it ended, or does not reach the offset the checkpoint says it maps to is set aside, and the segment is walked.

## Opening a store

A reader opens a store as the writer recovers it, and changes nothing.

1. List the directory. If there is a `checkpoint`, decode it; replay starts at its offset, in the last segment beginning at or before it, and the catalogue, commit digest, batch number and last commit time start as it says. With no checkpoint, replay starts at offset 0, which a segment must begin at, from the genesis of each chain and an empty catalogue. A checkpoint with no segment is damage; no segment and no checkpoint is no store.
2. Compute the store's features from the checkpoint and the headers of every segment from replay's on, and refuse or read only by them ([Features and revision](#features-and-revision)).
3. Open the tables at the checkpoint's root, if a reader needs state or views.
4. For each segment from replay's on, check its header. Where replay starts at a segment's beginning, its anchor must equal where the chains stand; each later segment must begin exactly where the one before it ended. Then read its groups in order, checking each whole before applying any of it ([Groups](#groups)), folding the catalogue entries and records batch by batch in tape order, and the state records into the tables.
5. Stop at the end of the valid log, as below.

**Where the log ends.** In the last segment, after the last valid group:

- **zeros to the end of the file** are where the log ends, and nothing is lost;
- otherwise, the reader looks at every byte position after the end for a group header: four bytes `EGRP` whose 8-byte check verifies. If any claims the log was durable past where the valid log ends, the store is **damaged**, and refused: a torn write only reaches bytes that were never synced;
- otherwise the bytes after the end are a **torn tail**: a write that never finished, none of it ever acknowledged as durable. A reader reports it and ignores it; a writer cuts it away when it opens the store.

In any segment but the last, an invalid or short group is damage, and the store is refused. A last segment whose header does not check and which is no longer than 128 bytes, after another segment, was created and never written, and holds nothing. A store whose only segment is offset 0, with no checkpoint, whose header does not check and which is no longer than 128 bytes, is not a store yet.

**What a reader refuses.** A store of a revision other than 1, or from before the freeze; an incompatible feature it does not know; a segment whose header does not check, names another offset, or belongs to another store; a segment that does not continue the chains or the log before it; damage anywhere but a torn tail; a group that does not close the commit chain, or whose blocks do not link into their streams; a catalogue entry or record the fold refuses; a hidden block without a sidecar that verifies; and a history file that is not the one its Filed entry names. A reader never takes damaged bytes for data.

**Reading a stream's records.** A stream's retained records are those from its floor to its head. Its segment uses list where they are, in order: a use still in its segment is read from the segment's groups, each record's time from its block or its batch; a filed use is read from the history file, each record's time from its block or the file's time runs. Every block read is checked against its leaves (through its sidecar when hidden) and links from the block before it, from the use before's last link, from the history file's `prev`, from the genesis for record 1, or from the floor link for the floor's block. A redacted record is read as redacted, with no payload.

## Verifying a store

`engram verify DIR` checks every byte of the log, every history file and every sidecar a store holds, beyond what opening it checks. An independent verifier does the same:

1. **Open the store** as above.
2. **Every segment against its chains.** For every segment the store holds, including those before the checkpoint, check its header, then check every group in it from the header's anchor: it parses, closes the commit chain, its first batch follows the last, every block of stream 0 is a catalogue block and every catalogue block is stream 0, and each catalogue block's first entry number follows the last and links from the catalogue chain. Where one segment begins exactly where the one before it ends, the chains where the first ends must equal the second's anchor. The last segment must end where opening ended, at the same batch, commit digest, entry number and catalogue link.
3. **Every stream's chain, through every copy on disk.** Walk every record block, in log order: for each segment offset, held either as a segment or as history files, first the segment's blocks of every stream not filed for that segment, then each history file for that segment. Retained or not, every block still on disk is checked, but a retired stream's, which no stream answers for. For each stream, a block's first sequence must be one past the last block seen, unless a segment the store no longer has lies between them. Each block must link from the link before it, when that is known: the previous block's, when it is the very next sequence; the history file's `prev` for a file's first block, which must agree with the previous block's when both are known; the stream's genesis for record 1; the floor link for the floor's block, which must agree with the previous block's link when that is known. Hidden blocks verify through their sidecars. The one block that cannot be checked against the one before it is the first block still on disk of a stream whose earlier blocks are gone; the next block's link still pins it.
4. **Every head.** For every stream whose head is at or above its floor, the last block on disk must end at the head, and its link must be the head link the catalogue holds.

It reports the streams, the records at or above their floors and how many of them are redacted, the segments, the history files, and the log's end offset, batch count and commit digest: two stores that are copies of one agree on the last three. A torn tail is reported, not counted as damage.

`engram verify` does not read the table runs; each run is checked by its footer, its bloom hash and every page's checksum when it is read. A verifier that wants the tables checked too opens every run the checkpoint's root names and checks those, the fences, and every data page.

## Exports

`magi export DIR` writes a store as plain files: JSON, one value per line, with each type's schema beside it.

```
DIR/store.json            the store: its id, its last commit, the boots it knows and their order
DIR/types.jsonl           each type: name, version, whether a package installed it or a program declared it, its owner
DIR/types/NAME.schema     its fields
DIR/streams.jsonl         each stream: its name, its writer, the flags magi declare takes to declare it again,
                          and what the store knew of it: its head, its floor, when its writer was attached, its source's marks
DIR/records/N.jsonl       its records, or a state stream's keys, one a line
```

A record is `{"seq", "time": {"boot", "ns"}, "token"}` and then its fields by name under `"record"`, or its bytes as `"text"` or `"hex"`. A redacted record says `"redacted": true` and nothing of what it held. A key is `"key_text"` or `"key_hex"`, its `"version"`, and its value the same way. Integers and floats are numbers, written exactly; text is a string; bytes are hex; a time is `{"boot", "ns"}`; lists and vectors are arrays; a map is an array of pairs. A stream's history and state streams come first, then its views, whose rows are not written: they come back when the view is declared again.
