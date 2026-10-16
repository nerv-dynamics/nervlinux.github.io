# The discipline for the handbook

How a chapter of the published manual is written, and what stays out of it. Read this before adding or changing a chapter.

## Two trees, and only one of them is published

| tree | audience | contains | published |
| --- | --- | --- | --- |
| `handbook/` | the person using the machine | what the machine does and how to use it | **yes** |
| `docs/` | us | why and how: mechanisms, measurements, rejected alternatives | **never** |

`docs/DISCIPLINE.md` governs the private tree; this file governs the public one.

**Publish what the reader gets. Keep how we got there private.** A result goes in the handbook, stated plainly. The method behind it, errata, postmortems, rejected designs and anything that reads as a recipe for rebuilding what Nerv does stay in `docs/`. Nothing in `handbook/` links into `docs/`.

## Voice

- **Present what you get.** Plain present tense: what the machine does, what you type, what you see. Not an argument, not a defence, and not our internal conversation.
- **Results, stated plainly.** No hedging qualifiers, no experiment write-ups. Keep a claim accurate in kind and leave off the conditions that only undersell it.
- **One way.** A chapter documents *the* way to do something. Where an alternative exists it gets one sentence and no instructions.
- **Only what runs today.** Something not yet released may be named as *on the roadmap*, in a sentence, matter-of-factly and without apology. It gets no instructions until it ships.
- **Unix and unix.** *Unix* is the Bell Labs system and the trademark; *unix* is the tradition it started.

## Shape of a chapter

- **No front matter.** The `# heading` is the title. The first paragraph is the chapter's description: the website shows it on the handbook index and in the page's description, so it must stand on its own.
- **One line per paragraph.** No hard wrapping, in prose, lists, tables or blockquotes. Only code blocks keep their own line breaks.
- **One fact, one home.** A fact is stated once, in the chapter it belongs to, and linked from everywhere else. Copies drift until one is wrong.
- **Headings are an interface.** They become anchors that other chapters and the website link to; rename one only with every link that points at it.
- **Read in fragments.** No *"as we saw above"*, no *"recall that"*. A section makes sense on its own.
- **Examples are command and expected output.** A transcript, which a reader can check against their own machine, rather than a screenshot.
- **The console and the desktop are separate.** Many machines never install a desktop, so the console chapters never assume one, and the desktop has its own chapter.

## What does not go in

- **A Unix tutorial.** Another audience.
- **An option forest.** `--help` and the tool's tldr page carry every flag; a chapter shows the commands you actually use.
- **A troubleshooting FAQ.** Recovery covers the cases that stop a machine; the rest belongs in the tracker.
- **Contributing, community and history.** The website and the tracker have them.
