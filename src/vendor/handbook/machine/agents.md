# Agents

yui puts an agent in your terminal: you talk to a model, and it reads files, edits them and runs commands to do what you ask, inside a sandbox that holds only what you give it. Conversations are kept by the machine, outlive the terminal, and pick up where they left off.

## Synopsis

After reading this chapter, you will know:

- how to start yui, on this machine's own model or on another;
- how conversations are kept, and how to run several agents at once and move between them;
- what an agent can reach on its own, how it asks for more, and why some questions come back;
- how an agent remembers, and what happens when a conversation grows longer than the model can read.

Before reading it, you should know:

- how to open a terminal and install a package ([The first hour](the-first-hour.md));
- that S2 is the machine's own model server. [AI development](ai-development.md) explains it; this chapter needs only its name.

Every detail this chapter leaves out, from the machine's policy file to MCP servers and Telegram, is in [yui](../reference/yui.md), the reference page.

## Why it works this way

An agent is a program that acts on what a model says. That is useful exactly to the extent that you can let it act, and you can let it act only if you know what it can reach. So yui does not run the agent as you. Each conversation's agent works in a sandbox of its own, holding the directory you started it in and nothing else of yours, and it asks before it reaches anything more. Each question you are asked is the edge of that sandbox, shown to you.

The second idea is where text comes from. What you type is yours to act on. A web page, a log, a pasted message or a reply from another agent is not: it may carry instructions from whoever wrote it. yui keeps track of when a conversation has read such outside content, and from then on asks again before anything could send data off the machine. That is the whole reason some questions come back after you have answered them before.

The rest follows from the agent being part of the machine rather than a tab in a browser. The model is this machine's S2 unless you name another, so a conversation is sent off the machine only when you choose an endpoint elsewhere, and then email and IP addresses are sent as handles. Conversations are kept by the machine itself, in [MAGI](what-the-machine-remembers.md), so they survive the terminal, a restart and a model switch. And there is one memory, the one you decide on: an agent's notes reach a conversation only once they are on.

## Starting yui

yui comes with the workstation. On any other machine:

```
$ doas dnf install nerv-yui
```

Run it in the directory you want to work in. With no model named, it talks to this machine's S2:

```
$ yui
```

When S2 is not running, your first message brings up a card to start it. It shows the model, how much context fits in the memory that is free, and the command it will run. `y` starts it this once; `a` starts it from now on without asking, in every conversation. The footer says *loading S2's weights* until it answers, which takes seconds. A GPU that is already running a model is said to be busy, and nothing is started beside it.

Any server that speaks OpenAI's API works too, and so does Claude, with Claude Code installed:

```
$ yui --endpoint http://127.0.0.1:8000/v1 --model qwen3.8-27b
$ yui --endpoint claude --model opus
```

A server that wants a key gets the one kept for it in `~/.config/yui/keys`, a file named for its host, readable by you alone; the agent never sees it ([Endpoints and their keys](../reference/yui.md#endpoints-and-their-keys)). Claude works with yui's tools and asks on yui's cards like any other model ([Claude](../reference/yui.md#claude)).

`ctrl+p`, then *Switch model*, changes the model in the middle of a conversation, and the conversation carries on. `ctrl+p`, or `/`, opens the commands palette, and most of what follows is a line in it.

## Conversations

`yui` in a directory opens the conversation last held there, with everything said in it on screen. `yui new` starts another. Nothing is written into the directory: the machine keeps conversations itself, in [MAGI](what-the-machine-remembers.md), where only you can read them.

`ctrl+s` lists every conversation, the most recently used first, with the last exchange of the one under the cursor. Choosing one moves yui into the directory it was held in.

Close the terminal while the agent works and it carries on. The next `yui` opens on the conversation as it is, a question it asked you still waiting. Two terminals can open the same conversation: both show everything, and either can answer.

Each conversation shows its state as a glyph: a yellow ◆ when a question waits for you, a cyan ● while it works, a green ○ when it has finished and waits for you, and a red ✕ when its turn failed. Inside tmux, every window carries one glyph per agent open in it, and the terminal bell rings when an agent comes to need you.

From a script: `yui ps` prints every agent's state, `yui show NAME` prints a conversation as text, and `yui send NAME TEXT` asks it something and prints the answer ([Conversations from a script](../reference/yui.md#conversations-from-a-script)). Everything `ctrl+p` changes is a command too: `yui context summarize at 80%`, `yui decide NAME allow`, `yui plugins telegram approve=none` ([Settings from a script](../reference/yui.md#settings-from-a-script)).

## Running several agents

Several agents can work at once, each in a conversation of its own, and one terminal follows all of them.

1. Start each one where its work is: `yui new` in each directory, or `tmux new-window 'yui open NAME'` to give a conversation a window of its own.
2. Press `alt+0`, or run `yui board`. The board shows every agent at once, one tile each: its state, where it works and on which branch, the last lines of what it is doing, and the question it waits on.
3. Answer a waiting question from its tile with `y` or `n`, or open the conversation with `enter`.
4. Move between agents without the board: `alt+1` to `alt+9` for the board's first nine, `alt+h` and `alt+l` for the one before and after, `alt+n` for the next that needs you, and `alt+b` back to the one before.

What you were writing to one agent waits in its composer until you come back. `p` on a tile pins it first, and `<` and `>` move it, so the numbers stay where you put them.

Agents can write to each other. A message waits until the receiving agent's turn ends; who sent it is proven, and what it says counts as outside content. An agent can also hand a task to a sub-agent, which appears on the board marked `↳` and can be opened and answered like any other ([Agents talking to each other](../reference/yui.md#agents-talking-to-each-other), [Sub-agents](../reference/yui.md#sub-agents)).

An agent keeps a to-do list for its work, and its tile says how far it has got: `2 of 5 done`. `alt+p` shows the list in a panel.

## What the agent may do

The agent works in a sandbox of its own. It sees the directory you started yui in, read-write; the system, read-only; and a home directory and a `/tmp` of its own, which last from one command to the next. It does not see your home directory, your other files, the machine's other programs, or the network, and it cannot use `doas`. A git repository's hooks and configuration stay read-only to it, so nothing it does runs the next time you commit.

Inside the sandbox the agent needs no permission: it reads, writes and runs commands, and each change shows in the conversation as it is made. For anything more, a path elsewhere or the network, it asks on a card that shows what it would reach and why:

| key | |
| --- | --- |
| `y` | allow it |
| `n` | refuse; type why, or nothing, and press enter |
| `e` | change what it would do, then press enter |
| `esc` | stop the agent |

`ctrl+p`, then *Sandbox*, lists what the agent can reach now, and enter on a line takes it back. yui's own files, its configuration and state and the socket its commands speak through, are never in the sandbox, whatever you grant ([The sandbox](../reference/yui.md#the-sandbox)).

Once a conversation holds outside content, a command that could reach the network is asked for again, and the card says why. A paste of eight lines or more counts as outside content, since it usually came from a log, a page or a message; typing and short pastes are yours. So does what a command prints while the agent has the network.

A question the agent asks you, rather than a permission, comes on a card with up to nine choices: a number answers it, and anything you type is your answer instead. A question is always yours to answer.

On a kernel that cannot make the sandbox, yui says so when the agent first acts, and asks before each write, each command and each read outside the directory. There, `a` on a card allows that tool from then on, and `ctrl+p`, then *Standing grants*, takes it back ([The sandbox](../reference/yui.md#the-sandbox)).

Three things go further than one conversation, and each has its section in the reference:

- **An approver.** Another conversation can answer the questions an agent may answer for you, so you are not asked each time an agent that read a page wants the network ([An agent that approves for the others](../reference/yui.md#an-agent-that-approves-for-the-others)).
- **The machine's policy.** `/etc/yui/policy`, owned by root, says what no agent on the machine may do, whoever approves it: tools denied, the network off, paths protected, the endpoints and MCP servers allowed ([Policy](../reference/yui.md#policy)).
- **Secrets.** An agent can use a token without ever holding it, through a broker you approve once ([Secrets and brokers](../reference/yui.md#secrets-and-brokers)).

## Memory

An agent can keep a short note for later conversations, under a title, for this project (its git repository) or for every project. Nothing of the notes is put in front of an agent: it is told how many it has, and searches them with its `recall` tool when its work calls for it.

A note is found only once it is on. `ctrl+p`, then *Memory*, lists the notes that hold here: `enter` on one turns it on or off, edits it, or deletes it. The first line of the palette chooses whether you turn notes on one at a time or they are on as they are written. Either way, a note written while the agent had read outside content waits for you.

An agent also searches this project's earlier conversations with its `history` tool, and reads the handbook on the machine with `nerv doc` before guessing how something on Nerv works ([Memory](../reference/yui.md#memory), [Earlier conversations](../reference/yui.md#earlier-conversations)).

## Long conversations

A conversation can go on longer than a model can read at once. Before it gets there, once a request fills 75% of what the model can read, yui has the model summarize it, beside the work and without stopping it. From then on the model is sent the summary in place of the conversation's start, the messages you wrote in it word for word, and the most recent part as it was. Your last message is always sent whole, and a line in the conversation says when it happens. The whole conversation is still kept, and `history` finds any of it.

`ctrl+p`, then *Context*, turns summarizing on or off, sets where it starts, from 50% to 90%, and switches the pruning that leaves out what a conversation no longer needs ([Long conversations](../reference/yui.md#long-conversations)).

## Giving the agent more

An agent's own tools read, write and run commands, fetch pages, and answer questions about this machine with `nerv`: which libc a program is built against, which package owns a file, which slot is running. Guards stop calls that would do the wrong thing here and say what to do instead: `sudo` becomes `doas`, and another distribution's package manager becomes `dnf`. Beyond that, an agent's tools come from three places, all set up from `ctrl+p`:

| | | |
| --- | --- | --- |
| **Plugins** | programs of your own that add tools, panels or a channel; *Plugins* sets each one up | [Tools and guards](../reference/yui.md#tools-and-guards) |
| **MCP servers** | a server's tools, declared in a file in `~/.config/yui/mcp`, run here in a sandbox of its own or reached at a URL | [MCP servers](../reference/yui.md#mcp-servers) |
| **terse** | holds the prose an agent writes to short, plain rules, once its *Checking* setting is on | [Plain writing](../reference/yui.md#plain-writing) |

`ctrl+p`, then *Tools*, lists every tool, plugin and server and switches each on or off, for the machine or for one conversation ([Switching tools](../reference/yui.md#switching-tools)).

A conversation can also be reached from a Telegram chat, through yui's `telegram` channel: make a bot, give yui its token under *Plugins*, then *telegram*, and allow the code the bot shows you. Grants never go through the chat ([Telegram](../reference/yui.md#telegram)).

## Reference

| key | |
| --- | --- |
| `enter` | send; while the agent works, send when it finishes |
| `alt+enter` | a new line |
| `esc` | stop the agent |
| `ctrl+p` or `/` | commands |
| `ctrl+s` | conversations |
| `alt+0` | the board; `alt+1` … `alt+9`, `alt+h`, `alt+l`, `alt+n` and `alt+b` move between agents |
| `alt+p` | the plugins' panels, shown or hidden |
| `@` | attach a file |
| `shift+tab` | how hard the model thinks |
| `ctrl+t` | show the model's thinking |
| `ctrl+o` | open or close the last tool call; a click does the same |
| `ctrl+y` | copy the agent's last answer |
| `ctrl+d` | leave; the agent carries on |

| command | |
| --- | --- |
| `yui` | the conversation last held in this directory |
| `yui new` | a new conversation here |
| `yui open NAME` | the conversation NAME names: its name, the end of it, or words of its title |
| `yui sessions` | every conversation, with its name |
| `yui ps [--follow]` | what every agent is doing |
| `yui board` | the board |
| `yui show NAME [--full] [--follow]` | a conversation as plain text |
| `yui send NAME TEXT` | ask a conversation, and print the answer |
| `yui model`, `sandbox`, `decide`, `plugins`, `context`, … | what `ctrl+p` changes, as commands ([Settings from a script](../reference/yui.md#settings-from-a-script)) |
| `yui mcp login NAME`, `yui mcp logout NAME` | sign in to an MCP server, and forget it |
| `systemctl --user enable --now yui` | keep yui's daemon running from login, for a channel |

| file | |
| --- | --- |
| `~/.config/yui/keys/HOST` | an endpoint's key, readable by you alone |
| `~/.config/yui/secrets/NAME` | a secret an agent uses through a broker |
| `~/.config/yui/brokers` | the brokers you approved |
| `~/.config/yui/mcp/NAME` | an MCP server |
| `~/.config/yui/plugins` | your own plugins |
| `~/.config/yui/settings` | the plugins' settings |
| `~/.config/yui/context`, `~/.config/yui/tools` | summarizing and pruning; the tools switched on or off |
| `/etc/yui/policy` | what no agent on this machine may do |

`yui --help` lists every command, `tldr yui` the ones used most, and [yui](../reference/yui.md) has everything else.
