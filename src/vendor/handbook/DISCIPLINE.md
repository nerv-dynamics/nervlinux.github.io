# The discipline for the handbook

What belongs in the published manual, what stays private, and how a chapter is shaped. This file
governs `handbook/`. Read it before adding a chapter.

## Two trees, and only one of them is published

| tree | audience | contains | published |
| --- | --- | --- | --- |
| `handbook/` | the operator | the surface: what the machine promises and how to use it | **yes** |
| `docs/` | us | the mechanism: why, how, the measurements, the rejected alternatives | **never** |

`docs/DISCIPLINE.md` governs the private tree; this file governs the public one. They are different
jobs, so they have different rules, and the vocabularies are allowed to differ — the internal tree
may call something an accelerator; the handbook does not.

**The disclosure line:**

> **Publish the promise and its conditions. Withhold the argument and the wounds.**

*"A hostile allocation pattern cannot wedge your machine"* is a promise — publish it. The pageblock
analysis that makes the sentence true is the argument — it stays private. A measured characteristic
may be published *with its conditions*; the method that produced it may not. Errata, postmortems,
rejected designs, and anything that reads as a recipe for reproducing what Nerv does are private.

The test a reviewer applies to a sentence: **does this tell a reader how to rebuild our advantage,
or only what to expect from it?**

Mechanically: **nothing in `handbook/` links into `docs/`.** The linter enforces it. A chapter that
needs a private document to make sense is a chapter that has not decided what it is.

## Three kinds of chapter

**Position chapters** state what the machine is an answer to. There is one part of them — Part I —
and they argue rather than instruct. They describe no surface and make no promise that could be
verified against a running machine, so a reader is owed the argument and nothing else.

## Two kinds of chapter

**Idea chapters** explain one promise of the machine, once. They are the only place a mechanism is
described. Their set is small and fixed — five — and a sixth requires retiring one.

**Use chapters** are organised by what a person is trying to do. They contain goals, steps, expected
output and links. **They may not contain guarantee statements or machinery paragraphs.**

That split is the whole structure, and it exists because task-organised manuals fail the same way
every time: each task re-explains the machinery, and the copies drift until one is wrong.

### One home

**A mechanism is explained in one place and cited everywhere else** — the public form of the private
tree's *a measurement lives in one place*.

Every guarantee has exactly one covering chapter. Zero is a documentation gap; two is a
contradiction waiting to be found by a reader. Today this is held in review — the machinery that
would check it mechanically is a ticket, not a paragraph here.

The standing temptation is a use chapter growing a "how this works" section. It has a sanctioned
outlet and no other: an **Underneath** box, exactly one sentence per idea cited, plus the link.

```
> **Underneath.** Containers reach the GPU through a socket rather than an injected driver.
> See [The compute fabric](../ideas/compute-fabric.md).
```

### The test that keeps idea chapters from becoming a subsystem manual

> **If an idea chapter's guarantees map one-to-one onto a single `area/*` label, it is a
> subsystem manual in a costume and the cut is wrong.**

Ideas span subsystems by construction. Generations spans cage, updates and packaging. The compute
fabric spans axon, kernel policy and the platform package.

## Front matter

Every chapter opens with it. Three keys, and each has a named consumer today:

```yaml
---
title:    Generations
kind:     position | idea | use
one-line: Every change to the system is a transaction — try it, prove it, keep it, or it
          rolls itself back.
---
```

`title` names the chapter. `kind` is what the one-home rule is checked against. `one-line` is the
self-identification the resident agent quotes when it answers with a citation, and what an index
is built from — the same mechanism `tools/gen-docs-index.sh` already runs over the private tree.

**A richer form was specified here before any chapter existed** — `covers:` checked against a
per-generation surface manifest, `argues:` binding a private document by content hash, and
`generation:` as a staleness stamp. It is a good design and it has no users, no manifest to check
against, and no chapter that needs it. Specifying it here made this file the thing the private
tree forbids: design-in-flight wearing current-state clothes. It is a deferral, so it is a ticket.
Add a key back when a chapter cannot be written without it.

## How a chapter is written

**For one operator.** Nerv addresses one person on one board, so a chapter is prescriptive: it
documents *the* way. Where an alternative exists it gets one sentence and no instructions. This is
coherence over completeness, applied to prose, and it is why chapters here are short where another
project's would be long.

**A guarantee carries its conditions and what would disprove it.** The private tree ends its
foundational document by naming what would falsify its own thesis; the handbook does the same in
public. A promise with no conditions is marketing, and this project does not ship that.

**The second reader is a model.** The resident agent indexes this handbook and answers the operator's
questions from it, with citations. That is not a metaphor, and it imposes real constraints:

- every fact stated once, in its home chapter — already the one-home rule, now with a second reason
- stable anchors; headings are an interface
- no *"as we saw above"*, no *"recall that"* — a chapter is read in fragments
- examples are command-and-expected-output pairs, so a quotation can be checked before it is made
- every chapter opens with the one-line self-identification in its front matter

**Pinned to a generation.** The handbook is built and published per generation, so it describes *this
machine*, exactly — not a floating average of the project. The build stamps the generation; a chapter
does not carry it by hand, because a hand-written stamp is a status field and status is the tracker's.

**Examples run where a harness exists.** Where a chapter's commands can be executed by an existing
harness, they are, and the transcript is the expected output. Adopt this per chapter. Do not build a
documentation-testing framework first.

## What does not go in

- **A chapter for anything not running on the canary.** The table of contents may carry the slot;
  the prose may not. A document exists because the thing it describes exists — that rule has no
  public exemption.
- **A Unix tutorial.** Another audience, another decade.
- **An option forest.** One way, documented.
- **Hand-written reference.** Part V is generated from the surface manifest. A paragraph restating a
  flag is a lint failure waiting to happen.
- **Screenshots.** Transcripts, which a diff can check.
- **A troubleshooting FAQ.** An accreting symptom list is a stale, unqueryable copy of what the
  machine's own record is being built to answer. The troubleshooting chapter of the future is a
  query surface; until it ships, Recovery covers the genuinely fatal cases and nothing else.
- **Contributing, community, history, roadmap.** The tracker exists.

Refusing these is what keeps this book at fifteen chapters where the conventional equivalent would
be forty. **The chapter count is a health metric**, and it should rise only when the machine learns
something new.
