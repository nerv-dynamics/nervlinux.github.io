# What the machine remembers

MAGI, the machine's database of what it knows: everything observed on it, as a record that cannot be quietly changed, the facts that follow from that record, and answers that say exactly how far they can be trusted.

## Not ready yet

MAGI is in development and not on the machine yet. This chapter says what it is, so the rest of the handbook can point at it; it is written out in full when MAGI ships. Until then, the machine's record is the journal, and [Asking why](asking-why.md) shows how to read it.

## What it is

A machine already knows a great deal: which update it took and when, why a boot failed, what a service did before it stopped, what a measurement showed last month. Today that knowledge is text in log files, kept for a while and searched by hand, and a conclusion drawn from it lives in someone's notes with no date and no way to tell when it stopped being true.

MAGI keeps it as data. It is a database built on one idea: what was observed and what is believed are different things, and the second is always derived from the first. The same mechanism holds the machine's own history, a codebase, a mail spool or a plant's sensor readings, because they all have the same shape: things observed, folded into what they establish, read through views.

## Streams, events, facts and views

- **A stream** is where observations come from: one writer, with its own trust, retention and integrity. Each stream is a hash chain, so an entry changed or removed after the fact shows as a break.
- **An event** is one observation: this observer reported this, at this moment of this boot. Events are never changed. A correction is a new event that supersedes the old one.
- **A fact** is what the events establish: an entity, a property, a value, and the span of time it held. Facts are never written directly. Each is derived from events, names the events and the rules it came from, and can be rebuilt from them at any time.
- **A view** is a fold over facts, for reading, and names exactly what it was computed from, so a stale view is detected rather than trusted.

Time is recorded as the machine experienced it, the boot and the clock within it, and wall-clock time is worked out from that. A machine whose clock was wrong for a week still has a correct record of that week.

## How the facts are made

Rules that turn events into facts are deterministic and declared, and a new version of a rule rebuilds its facts from the record beside the old ones, then swaps them in at once, the way `cage` promotes a slot. Nobody ever reads a half-rebuilt world.

A language model can propose facts too, from prose or from code, through a separate component that can be removed without the rest of MAGI changing. What a model proposes is recorded as an event and checked by a deterministic rule before it becomes a fact, so a better rule improves old answers without running the model again.

## Answers with their limits

MAGI knows which streams it holds and over what time, and an answer reaches only as far as they do. A question the record does not cover gets an answer that says so, never a guess. An answer that rests on a source of lower trust carries that with it.

Some of what you know about a machine is a conclusion: this setting is needed, this driver is the fast one. MAGI records a conclusion as a claim, with the measurement behind it and the test that would disprove it. `nerv-run` wraps a command and records what it measured together with the conditions it ran under, the generation, the kernel command line and the settings that matter, and a claim carries a date to be checked again.

## Larger than one machine

The record replicates between machines, so a fleet answers as one, and queries over it run on the GPU. Every MAGI command emits typed records into a pipe and readable text on a terminal, and needs no shell, display or person to run.
