# Voice

What the site is allowed to say, and how it looks while saying it. The
mechanics live elsewhere: [`type.md`](type.md) for the families and the build,
[`palette.md`](palette.md) for contrast ratios, [`grade.md`](grade.md) for
images. This file is the part that is a decision rather than a measurement.

## Prose

- **Serial comma, always.** "CPU, GPU, and memory are services."
- **Second person, and slightly casual.** "You can run a musl build of Quake on
  your ARM machine." Not "a musl build of Quake runs on the workstation." The
  site is addressed to a person who might use the thing, and the detached
  editorial register makes it sound like a press release about someone else's
  product.
- **No em dashes.** Use a comma, a colon, a full stop, or brackets.
- **Avoid the antithesis tic**: "it is not X, it is Y", "not a Z but a W". One
  or two in a page is writing; five is a mannerism, and it reads as generated.
- **Say the number, then the condition.** "3x" in the figure, "at peak" in the
  line under it. Never bury a qualifier inside the claim, and never drop one.
- **Present tense for what runs. A state table for what does not.** Uniform
  present tense across unfinished work is how a site gets caught.

## Colour

The palette's twelve roles come from `nerv-theme` and are documented in
[`palette.md`](palette.md). What each one *means* here:

| | meaning | where |
| --- | --- | --- |
| **Green** | **NVIDIA, and nothing else** | `.hl` in the hero headline |
| **Red** | Nerv's own mark, and the primary action | the logo, `.btn--primary`, the hero rule |
| **Cyan** | the machine speaking | `.readout`, eyebrow labels |
| **Yellow** | attention, something unfinished | `.pill--building`, the provisional badge |
| grey scale | everything else | all body copy |

**Green is the one to be strict about.** It was chosen because it is NVIDIA's
colour, so every additional thing it marks costs the one place it carries
meaning. A poster claim once borrowed it for emphasis; it has been taken back.
Emphasis in running text comes from size, weight, and position.

### The exception, stated so it does not look like drift

Green has a second, legitimate job as a **status** colour: green shipping,
yellow building, grey designed. That coexists with the brand meaning because
of a hard rule:

> **Green in running text means NVIDIA. Green in a status indicator means
> working.**

Status green only ever appears inside a pill or a status column, never in a
sentence. `.col-nerv` in the userland comparison table is the one borderline
case, marking the Nerv column of a two-column comparison; it reads as status
rather than brand, which is why it stays.

## Capitals

> **All-caps is for labels the interface applies. Never for language a person
> wrote.**

**Caps:**

- Column headers in data tables. They name a field, they are not prose.
- Status pills: `RUNNING`, `BUILDING`, `DESIGNED`.
- Eyebrow and category labels above a block.
- Breadcrumbs. A location, not a sentence.
- The `PROVISIONAL` badge. A warning from the build, not from the author.

**Never caps:**

- Headings, at any level.
- Body copy, captions, figure captions.
- Buttons. They instruct a person, so "What it does", never "WHAT IT DOES".
- Navigation.

### Machine output is lowercase, deliberately

The readout strip is monospace and **not** capitalised:

```
vkquake / vulkan / aarch64 musl / axon://win11pc.lan / radeon rx 9070
```

Hostnames, package names, and architectures are lowercase in reality, and
capitalising `axon://win11pc.lan` would misrepresent what the machine prints.
So case carries the distinction, and both are monospace:

> **Caps are a label about the machine. Lowercase mono is output from the
> machine.**

## Type sizes

**One display size**, `--t-display`. Every large statement uses it: the page
headline, a section's opening claim, the line over a screenshot.

There were briefly two, on the theory that a claim running the full column
wants more size than a headline constrained beside the hero photo. That is a
description of a layout constraint, not of a hierarchy, and it produced two
nearly-identical sizes that read as an accident rather than as a system. It was
also the wrong way round, since nothing on a page should outrank its `h1`.

Before that there were three, because a bespoke `clamp()` had been written per
component: 2.5rem, 2.15rem, and 2rem all doing versions of the same job.

A second step needs a reason that can be written down here.

## Measures

**Do not cap a measure by reflex.** A `ch` cap on a line meant to flow
manufactures exactly the line breaks the page is trying to avoid. It has done
so three times here: on the hero headline at 42ch, again at 30ch, and on the
poster's demonstration line at 60ch, which broke a 108-character sentence that
fits its column with 240px to spare.

- **A single sentence under a claim gets no cap.** One line at desktop width,
  wrapping on its own when the viewport is narrower.
- **A heading may take a short measure.** `.section-title` sits at 34ch, which
  is conventional typography, and deliberately wraps five headings across the
  site to two lines.
- **A column of body copy takes `--max-w-text`**, which is what it is for.
- **Where a layout already bounds the text**, as the hero photo's padding does,
  that is the cap. A second one narrows it twice, which is how "built from
  scratch on musl" lost its authored line break.
