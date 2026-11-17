# Agents

yui puts an agent in your terminal: you talk to a model, and it reads files, edits them and runs commands to do what you ask, inside a sandbox that holds only what you give it. Conversations are kept by the machine, outlive the terminal, and pick up where they left off.

## Starting yui

yui comes with the workstation. On any other machine:

```
$ doas dnf install nerv-yui
```

Run it in the directory you want to work in, pointed at a model. S2 serving OpenAI's API on this machine, as [AI development](ai-development.md#serving-a-model) sets up, is the default:

```
$ yui
```

Any server that speaks OpenAI's API works the same way:

```
$ yui --endpoint http://127.0.0.1:8000/v1 --model qwen3.8-27b
```

`ctrl+p`, then *Switch model*, changes the model in the middle of a conversation, and the conversation carries on.

## Conversations

`yui` in a directory opens the conversation last held there, with everything said in it on screen. `yui new` starts another. Nothing is written into the directory: the machine keeps conversations itself.

`ctrl+s` lists every conversation, the most recently used first, with the last exchange of the one under the cursor. Choosing one moves yui into the directory it was held in. `yui sessions` prints the same list.

Close the terminal while the agent works and it carries on. The next `yui` opens on the conversation as it is, a question it asked you still waiting. Two terminals can open the same conversation: both show everything, and either can answer.

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

What you type is yours to act on; text that came from elsewhere is not. Once a conversation holds outside content, a command that could reach the network is asked for again, the card saying why. A paste of eight lines or more counts as outside content: it usually came from a log, a page or a message. Typing and short pastes are yours.

On a kernel that cannot make the sandbox, yui says so when the agent first acts, and asks before each write, each command and each read outside the directory. There, `a` on a card allows that tool for the rest of the conversation, until outside content arrives.

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
