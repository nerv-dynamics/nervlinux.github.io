# The discipline for the handbook

How a chapter of the published manual is written, and what stays out of it. Read this before adding or changing a chapter.

## What the handbook is for

A person reads the handbook to learn why the machine works the way it does and how to do the things they came to do. It is a book, read in order by someone new and dipped into by someone who is not, in the tradition of the FreeBSD Handbook: chapters that follow a reader from installing the machine to running many of them, each with the same shape, each saying what it teaches and what it expects you to know.

It is not a list of features. Most of what a program can do belongs to the program's own reference, and the handbook links to it.

## Only the handbook is published

`handbook/` is written for the person using the machine: what it does and how to use it. It is published. Why and how — mechanisms, measurements, rejected alternatives — is kept privately and never published.

**Publish what the reader gets. Keep how we got there private.** A result goes in the handbook, stated plainly. The method behind it, errata, postmortems, rejected designs and anything that reads as a recipe for rebuilding what Nerv does stay private. Nothing in `handbook/` names or links to where they are kept.

## Voice

- **Present what you get.** Plain present tense: what the machine does, what you type, what you see. Not an argument, not a defence, and not our internal conversation.
- **Results, stated plainly.** No hedging qualifiers, no experiment write-ups. Keep a claim accurate in kind and leave off the conditions that only undersell it.
- **One way.** A chapter documents *the* way to do something. Where an alternative exists it gets one sentence and no instructions.
- **Only what runs today.** Something not yet released may be named as *on the roadmap*, in a sentence, matter-of-factly and without apology. It gets no instructions until it ships.
- **Credit where it is due.** Where Nerv takes an idea from another system, say so, in a sentence, as thanks rather than comparison. The lineage appendix collects them.
- **Unix and unix.** *Unix* is the Bell Labs system and the trademark; *unix* is the tradition it started.

## Shape of a chapter

Every written chapter has the same five parts, in this order:

1. **The first paragraph** says what the chapter is about, in a way that stands alone: the website shows it on the handbook index and in the page's description.
2. **Synopsis.** A section of exactly two lists: *After reading this chapter, you will know:* what the reader can do and understand at the end, and *Before reading it, you should know:* the chapters it builds on, as links. Nothing else goes in it.
3. **Why it works this way.** The idea behind the chapter, as what it gives you, in a few hundred words: the problem, the design, and what follows for the person at the keyboard. This is where a reader learns why something is good. It is not a defence, and it names no competitor.
4. **The procedures.** One section per thing a reader does, named for it (*Updating*, *Rolling back*). Each one is steps a person follows, then what they see when it worked. Where the program has a terminal interface, the steps go through it, and the command that does the same step follows as **From a script**.
5. **Reference.** The keys and commands of the chapter's program, as tables, and a link to the program's full reference. Never a copy of its options.

A short chapter may fold *Why it works this way* into its first paragraph. Nothing else is optional.

## Writing a procedure

- **Numbered steps for a sequence, prose for one action.** A step is one thing to do; what happens because of it goes in the next sentence, not the next step.
- **What you see.** Every procedure ends on what the reader sees when it worked: a capture of the screen, or a transcript.
- **Screens are text.** A terminal program's screen is a capture, never a picture: `tmux capture-pane -e -p` keeps its colours, and the capture goes in `handbook/tui/NAME.ansi`, with every host name, address, device ID and home path replaced by one exactly as long. The chapter shows it in a fence marked `tui NAME`, holding the same screen as plain text; the website draws the stored capture in its colours. A command's output is a transcript a reader can check against their own machine.
- **Labels as the program shows them.** A button, a menu item or a panel is written in bold, exactly as it appears: **Add machine**. Its key follows in code: **Add machine** (`a`). A path through the screens is joined with an arrow: **More** → **Fleet networking** → `enter`.
- **From a script.** Every step a terminal interface offers is also a command. Give it once, under the step, as `From a script:` and the command.
- **Notes and warnings, sparingly.** A blockquote that opens with a bold word is a box: `> **Note.**` for something worth knowing, `> **Warning.**` for something that loses work. One per section at most.

## Referring to other chapters

- **Forward is fine.** A chapter may use something a later chapter explains. Name it, say in a clause what it is, link it, and let the reader carry on: *"Plexus, which joins your machines into one private network, decides who may reach this port; [Plexus](machine/plexus.md) covers it."* The reader needs nothing more to continue.
- **By name, never by number.** Chapters are linked by their title, so moving one never breaks a sentence.
- **One fact, one home.** A fact is stated once, in the chapter it belongs to, and linked from everywhere else. Copies drift until one is wrong.
- **Headings are an interface.** They become anchors that other chapters and the website link to; rename one only with every link that points at it.
- **Read in fragments.** No *"as we saw above"*, no *"recall that"*. A section makes sense on its own.
- **A term the reader meets before its chapter** goes in the glossary.

## Keeping it a book

- **A feature is not a section.** A procedure goes in a chapter only if most of the chapter's readers will do it. Everything else goes in the program's reference: its `--help`, its tldr page, and its reference page here.
- **About 2,500 words a chapter.** `tools/lint-docs.sh` warns above 3,000. A chapter past that is two chapters, or carries a program's reference that belongs on its own page.
- **Chapter count is a health metric.** It rises when the machine learns something new, not when someone has an idea.
- **A stub is an outline.** A planned chapter starts as its heading, its first paragraph, the line `<!-- stub: … -->`, and its sections, each with one italic line on what goes there. The website skips a chapter while that line is in it; delete the line when the chapter is written.

## Form

- **No front matter.** The `# heading` is the title.
- **One line per paragraph.** No hard wrapping, in prose, lists, tables or blockquotes. Only code blocks keep their own line breaks.
- **The console and the desktop are separate.** Many machines never install a desktop, so the console chapters never assume one, and the desktop has its own chapter.

## What does not go in

- **A Unix tutorial.** Another audience.
- **An option forest.** `--help` and the tool's tldr page carry every flag; a chapter shows the commands you actually use.
- **A troubleshooting FAQ.** Recovery covers the cases that stop a machine; the rest belongs in the tracker.
- **Contributing and community.** The website and the tracker have them. Where the ideas came from is in the lineage appendix; how the project got here is not.
