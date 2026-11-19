# Agents

yui puts an agent in your terminal: you talk to a model, and it reads files, edits them and runs commands to do what you ask, inside a sandbox that holds only what you give it. Conversations are kept by the machine, outlive the terminal, and pick up where they left off.

## Starting yui

yui comes with the workstation. On any other machine:

```
$ doas dnf install nerv-yui
```

Run it in the directory you want to work in. With no model named, it talks to this machine's S2:

```
$ yui
```

When S2 is not running, your first message brings up a card to start it. It shows the model, how much context fits in the memory that is free, and the command it will run. `y` starts it this once; `a` starts it from now on without asking. The footer says *loading S2's weights* until it answers, which takes seconds. A GPU that is already running a model is said to be busy, and nothing is started beside it.

The S2 that yui started runs until `ctrl+p`, then *Stop S2*, or until yui's background agent stops. An S2 you run yourself, as [AI development](ai-development.md#serving-a-model) shows, is used as it is and left alone.

Any server that speaks OpenAI's API works the same way:

```
$ yui --endpoint http://127.0.0.1:8000/v1 --model qwen3.8-27b
```

An `https://` endpoint is reached over TLS, and its certificate is checked against the machine's trusted certificates; `SSL_CERT_FILE` names a different file of them. A certificate that does not verify, or names another host, is refused.

A server that wants a key gets the one kept for it in `~/.config/yui/keys`, a file named for the server's host, and its port when it is not the scheme's own (80, or 443 for `https://`), holding the key alone:

```
$ mkdir -m 700 -p ~/.config/yui/keys
$ (umask 077; cat > ~/.config/yui/keys/10.0.0.5:8000)
```

It is kept the way an ssh key is: yui uses a key only you can read, in a directory only you can write, and refuses any other with the `chmod` that fixes it. A key goes only to the server it is named for. The agent never sees it: its tools run in a sandbox with a home of its own.

`ctrl+p`, then *Switch model*, changes the model in the middle of a conversation, and the conversation carries on.

## Conversations

`yui` in a directory opens the conversation last held there, with everything said in it on screen. `yui new` starts another. Nothing is written into the directory: the machine keeps conversations itself, in [MAGI](what-the-machine-remembers.md), where only you can read them.

`ctrl+s` lists every conversation, the most recently used first, with the last exchange of the one under the cursor. Choosing one moves yui into the directory it was held in. `yui sessions` prints the same list.

Close the terminal while the agent works and it carries on. The next `yui` opens on the conversation as it is, a question it asked you still waiting. Two terminals can open the same conversation: both show everything, and either can answer.

`yui ps` shows what every agent is doing: *working*, *needs-you* when a question waits for you, *done-waiting* when it has finished and waits for the next message, or *blocked* when its turn failed. With each comes since when, the machine, the directory and branch it works in, and what it waits on or what you asked it. An agent working when the machine stopped is shown blocked until you open its conversation again. `yui ps --follow` stays open and prints an agent's line again each time it changes.

The same state shows in two more places, as a glyph: a yellow ◆ for *needs-you*, a cyan ● for *working*, a green ○ for *done-waiting* and a red ✕ for *blocked*. In `ctrl+s` it comes before each conversation, and a blocked one says why. Inside tmux, each window carries one glyph per agent open in it, so you see every agent from whichever window you are in, and the terminal bell rings when an agent comes to need you. An agent another yui holds shows the state its own yui gives it.

An agent keeps a to-do list for the work in front of it, with its `todo` tool. Each task is to do, doing or done, and the agent writes the whole list each time it changes, so you see the list in the conversation as it stands. The list stays with the conversation: it is there again when the conversation is resumed, after a restart too. It also goes on the agent's card, so `yui ps` and the other agents see how far it has got and what it is doing now. A list holds up to 50 tasks of one line each.

## Agents talking to each other

Each agent can see the others and write to them. It lists them with `agents` (the same cards `yui ps` shows) and sends with `message`: a note, a question, a request, a reply or a done. Each message is addressed to one agent, on a thread, and can refer to issues, branches or paths.

A message never interrupts. It waits until the receiving agent's turn ends, then reaches the agent at the start of its next turn, all at once and labelled, in the conversation where you see it too. A question, a request or a reply to an agent with nothing to do starts its turn; a note or a done waits until it next works. An agent started by messages eight turns in a row stops and shows *needs-you* until you write to it.

Who sent a message is proven, so no agent can claim to be another. What it says is not trusted: a message is outside content to the agent receiving it, and a request carries no authority. Anything it asks for that needs your approval still shows a card. A message holds up to 256 KiB; past 4 KiB the agent sees the start and reads the rest when it needs it.

## What the agent may do

The agent works in a sandbox of its own. It sees the directory you started yui in, read-write; the system, read-only; and a home directory and a `/tmp` of its own, which last from one command to the next. It does not see your home directory, your other files, the machine's other programs, or the network, and it cannot use `doas`.

Inside the sandbox the agent needs no permission: it reads, writes and runs commands, and each change shows in the conversation as it is made.

A git repository's hooks and configuration stay read-only to the agent, so nothing it does runs the next time you commit. In a worktree, the agent sees the repository's history too, so it can commit. Started in your home directory, the agent sees none of it.

For anything more, a path elsewhere or the network, the agent asks, and the question appears as a card showing what it would reach and why:

| key | |
| --- | --- |
| `y` | allow it |
| `n` | refuse; type why, or nothing, and press enter |
| `e` | change what it would do, then press enter |
| `esc` | stop the agent |

`ctrl+p`, then *Sandbox*, lists what the agent can reach. Enter on a path takes it back; enter on the network gives it or takes it back. What you give is kept with the conversation.

What you type is yours to act on; text that came from elsewhere is not. Once a conversation holds outside content, a command that could reach the network is asked for again, the card saying why. A paste of eight lines or more counts as outside content: it usually came from a log, a page or a message. Typing and short pastes are yours. So does what a command prints while the agent has the network, since it could have fetched it from anywhere.

On a kernel that cannot make the sandbox, yui says so when the agent first acts, and asks before each write, each command and each read outside the directory. There, `a` on a card allows that tool for the rest of the conversation, until outside content arrives.

## An agent that approves for the others

The questions an agent asks are of two kinds. Some only you can answer: a path outside the sandbox, the network itself, a command where there is no sandbox. Others another agent may answer for you. Today that is one thing: reaching the network after outside content has arrived.

`ctrl+p`, then *Approver*, makes the conversation you are in the approver. Tell it in your own words what to allow. From then on, when another agent asks something an approver may answer, the question goes to the approver as well as up on that agent's card. The approver allows it, refuses it, or hands it to you. Its turn starts by itself, the asking agent shows *working* while it waits, and whichever of you answers first decides. If the approver ends its turn without deciding, or hands the question on, the asking agent shows *needs-you*. *Approver* again in the same conversation leaves no approver.

The approver never reads the other agent's text. That agent has read outside content, so what it wrote may carry instructions from whoever wrote that content. The approver sees what yui knows for itself: who asks, the task you gave that agent, the tool and why it needs asking, where the outside content came from, and the shape of each argument without its text. It may read the arguments if it must. Once it has, it has read outside content too, and it approves nothing more. The same goes for anything else outside it reads, so no agent may send it a message. An approver that has read outside content is passed over, the card saying why, and a conversation that already has cannot be made the approver.

An approver must be a conversation on S2 or another model yui talks to directly; a conversation on Claude cannot be one. Every answer to every question, yours and the approver's, is recorded with who gave it, for which agent, and on what.

## Claude

With Claude Code installed, yui talks to Claude:

```
$ yui --endpoint claude --model opus
```

Claude works with yui's tools and asks on yui's cards, like any other model, and the conversation resumes on Claude's side too: neither a resume flag nor a permissions flag is needed. A conversation moves between Claude and S2 with the model switcher.

## Tools and guards

Besides reading, writing and running commands, the agent has `nerv`, which answers what a model cannot know about this machine: which libc a program is built against, which package owns a file and whether it is Nerv's or Fedora's, which install profile brings a package in, and which slot is running.

Guards stop calls that would do the wrong thing here and tell the agent what to do instead: `sudo` becomes `doas`, another distribution's package manager becomes `dnf`, bash syntax in a `/bin/sh` command becomes its POSIX form, and the agent never reboots the machine. Your own guards go in `~/.config/yui/guards.json`, a list of rules; a rule names a tool, a field and a match, and what to say:

```
[
  {"id": "no-npm", "tool": "run", "field": "command", "word": "npm", "say": "This project uses pnpm."},
  {"id": "sudo", "off": true}
]
```

Any program can add tools of its own. One placed in `~/.config/yui/plugins` is started with yui's agents and speaks JSON, one message per line, on its standard input and output.

## Copy and paste

Drag across the conversation to copy; the text goes to your clipboard, over SSH and through tmux, without the frames around it. `ctrl+y` copies the agent's last answer, and `ctrl+p` copies the last code block or the last command's output. Hold shift to use your terminal's own selection instead.

A file dropped onto the terminal, or a pasted path, is attached to your message. A long paste is shown as a single line, `[paste 1 · 240 lines]`, and sent whole.

## Keys

| key | |
| --- | --- |
| `enter` | send; while the agent works, send when it finishes |
| `alt+enter` | a new line |
| `esc` | stop the agent |
| `ctrl+p` or `/` | commands |
| `ctrl+s` | conversations |
| `@` | attach a file |
| `shift+tab` | how hard the model thinks |
| `ctrl+t` | show the model's thinking |
| `ctrl+o` | open or close the last tool call; a click does the same |
| `ctrl+d` | leave; the agent carries on |
