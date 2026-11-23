# yui

Everything yui does, for when [Agents](../machine/agents.md) is not enough: the files it reads, its commands for scripts, the rules a machine can set, and the tools, plugins, servers and channels an agent can be given. The chapter is where to start; this page is where to look something up.

## Endpoints and their keys

Without `--endpoint`, yui talks to this machine's S2. Any server that speaks OpenAI's API works the same way:

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

The S2 that yui started runs until `ctrl+p`, then *Stop S2*, or until yui's background agent stops. An S2 you run yourself, as [AI development](../machine/ai-development.md#serving-a-model) shows, is used as it is and left alone.

## Conversations from a script

`ctrl+s` lists every conversation, the most recently used first, with the last exchange of the one under the cursor. Choosing one moves yui into the directory it was held in. `yui sessions` prints the same list, with each conversation's name.

`yui show NAME` prints a conversation as plain text, for a script or an agent elsewhere: its last five messages and what ran between them, each output cut to a few lines. `--full` prints all of it, whole, and `--follow` stays and prints it as it goes on. `yui send NAME TEXT` asks it and prints the answer as it comes, until the turn ends, or until a question for you waits, which only you answer. What `send` asks counts as another agent's words, not yours: once it has written in a conversation, your standing grants no longer cover the agent's calls there.

`yui open NAME` opens the conversation NAME names: its name, the end of it, or words of its title, as long as only one conversation answers. Each terminal is a yui of its own, so one tmux window per conversation is `tmux new-window 'yui open build'`, `tmux new-window 'yui open review'`, and so on. Moving to another conversation in one window moves no other.

Close the terminal while the agent works and it carries on. The next `yui` opens on the conversation as it is, a question it asked you still waiting. Two terminals can open the same conversation: both show everything, and either can answer.

`yui ps` shows what every agent is doing: *working*, *needs-you* when a question waits for you, *done-waiting* when it has finished and waits for the next message, or *blocked* when its turn failed. With each comes since when, the machine, the directory and branch it works in, and what it waits on or what you asked it. An agent working when the machine stopped is shown blocked until you open its conversation again. `yui ps --follow` stays open and prints an agent's line again each time it changes.

The same state shows in two more places, as a glyph: a yellow ◆ for *needs-you*, a cyan ● for *working*, a green ○ for *done-waiting* and a red ✕ for *blocked*. In `ctrl+s` it comes before each conversation, and a blocked one says why. Inside tmux, each window carries one glyph per agent open in it, so you see every agent from whichever window you are in, and the terminal bell rings when an agent comes to need you. An agent another yui holds shows the state its own yui gives it.

## The board

`alt+0`, or `yui board`, shows every agent at once, one tile each: its state and since when, where it works and on which branch, the last lines of what it is doing, and the question it waits on, if one. `y` or `n` answers that question from the board; anything more, such as editing the call, opens the conversation with `enter`. On a narrow terminal the tiles become a list.

The board is the same in every yui, on any terminal: `p` pins a tile first, `<` and `>` move it, and `x` takes it off until its agent next works or needs you. The order numbers the agents for the keys that move between them, from the board or from inside a conversation:

| key | |
| --- | --- |
| `alt+0` | the board |
| `alt+1` … `alt+9` | the board's first to ninth agent |
| `alt+h` and `alt+l` | the agent before and after this one |
| `alt+n` | the next agent that needs you |
| `alt+b` | back to the agent shown before this one |

What you were writing to one agent, sent or not yet, waits in its composer until you come back. While another agent needs you, the footer says so.

An agent keeps a to-do list for its work with the `todo` tool. Each task is to do, doing or done, and the agent writes the whole list each time. The list stays with the conversation, after a restart too. `alt+p` shows it in a panel at the top right.

Its tile, `yui ps` and the other agents read how far it has got: `2 of 5 done`. A list holds up to 50 tasks of one line each.

## Agents talking to each other

Each agent can see the others and write to them. It lists them with `agents` (the same cards `yui ps` shows) and sends with `message`: a note, a question, a request, a reply or a done. Each message is addressed to one agent, on a thread, and can refer to issues, branches or paths.

A message never interrupts. It waits until the receiving agent's turn ends, then reaches the agent at the start of its next turn, all at once and labelled, in the conversation where you see it too. A question, a request or a reply to an agent with nothing to do starts its turn; a note or a done waits until it next works. An agent started by messages eight turns in a row stops and shows *needs-you* until you write to it.

Who sent a message is proven, so no agent can claim to be another. What it says is not trusted: a message is outside content to the agent receiving it, and a request carries no authority. Anything it asks for that needs your approval still shows a card. A message holds up to 256 KiB; past 4 KiB the agent sees the start and reads the rest when it needs it.

## Questions

An agent that needs your decision asks it on a card, with up to nine choices: a number answers, the arrows and `enter` choose, and anything you type is your answer instead. A reply that starts with a digit is begun with a space. Where several choices may be taken, a number or the space bar marks one and `enter` sends them all. From the board, the tile's number answers it. A question is yours: no approver is shown it, and no "always" covers it.

## Sub-agents

An agent can hand a task to a sub-agent and wait for its answer. The sub-agent is an agent of its own, on the board, its card marked `↳` with the name of the one that started it; you can open it and answer its cards. It is given the task and nothing else of the conversation, and the sandbox its parent had when it started, the network only if the parent had it. While it works, its parent's call shows what it is doing. Stopping the parent stops it. Sub-agents start sub-agents of their own two levels down and no further.

What a sub-agent answers is trusted as far as its own conversation: one that read a web page answers with outside content, and its parent's later sends are asked for.

## Memory

An agent can keep a short note for later conversations, under a title, for this project (its git repository) or for every project. Writing again under a title the project already has rewrites that note rather than adding another.

Nothing of the notes is put in front of an agent. It is told how many it has, and searches them with its `recall` tool when its work calls for it: by the words it expects in them, then reading one whole. A change reaches a conversation the next time it starts, or after it has been idle ten minutes, never halfway through.

A note is found only once it is on. `ctrl+p`, then *Memory*, lists the notes that hold here, with when an agent last read each: `enter` on one turns it on or off, edits it in the composer, its title on the first line (`ctrl+g` opens your editor), or deletes it. The first line of the palette chooses how notes are turned on: by you, one at a time, or as they are written. Either way, a note written while the agent had read outside content waits for you, and is marked so. Turning a note on, editing and deleting it, and the choice itself, are recorded as your decisions.

## Earlier conversations

An agent searches earlier conversations on this machine with its `history` tool: what was asked, said, run and answered there, found by its words, then read a few turns around a hit. It searches this project's conversations unless asked for every project's, and the turns of its own conversation that it is sent as a summary (below). What it reads counts as it did where it was said: a page fetched there is outside content here too.

## Long conversations

A conversation can go on longer than a model can read at once. Before it gets there, yui has the model summarize it, beside the work and without stopping it, once a request fills 75% of what the model can read. From the next request on, the model is sent the summary in place of the conversation's start, then the messages you wrote in that part word for word, newest first, as many as fit in 24 KiB, then the names it used (issues, merge requests, commits, paths, addresses), and then the most recent part of the conversation as it was, about 10,000 to 25,000 tokens of it. Your last message is always sent whole. A line in the conversation says when it happens.

You do not wait for a summary unless a request comes close to filling the model, at 92.5%, before the summary is written, or the model refuses a request as too long: then that request waits for it. If the model cannot write one, yui makes one from your messages, the names, and the previous summary. The next summary is written from the last one and what came after it. The whole conversation is still kept: `history` finds and reads any of it. The summary is kept with the conversation, so a conversation you come back to after a restart goes on from it.

How much a model can read is what its server says (`max_model_len`, as vLLM gives it); for a server that says nothing, yui takes 128K tokens. A conversation with Claude is summarized by Claude Code itself.

`ctrl+p`, then *Context*, turns summarizing on or off and sets where it starts, from 50% to 90%; a request then waits from seven tenths of the way from there to the whole window. Starting later summarizes less often, so less is lost to summaries, and sends longer requests in between. The same picker switches the pruning strategies, which leave out what a conversation no longer needs: a call's output repeated by a later one, the middle of a very large output, a failure a later call got past, earlier reasoning, a failed call's arguments, and a file's earlier reads once it was read or changed again. What is left out can be recalled whole. The choices are kept in `~/.config/yui/context` and hold for every conversation from its next turn.

## The handbook

This handbook is on the machine, in `/usr/share/doc/nerv/handbook`, as it stands for the software installed. An agent searches it with `nerv doc` and its words, and reads a section with `nerv doc read`, before guessing how something on Nerv works.

## The sandbox

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

On a kernel that cannot make the sandbox, yui says so when the agent first acts, and asks before each write, each command and each read outside the directory. There, `a` on a card allows that tool in the conversation from then on, after a restart too, but never once outside content has arrived.

`ctrl+p`, then *Standing grants*, lists every `a` you have given and that still holds: the tool, the conversation it holds in (every conversation, for starting S2), who gave it and since when. Enter on one takes it back. The next such call is asked for again, in a turn already under way too.

## An agent that approves for the others

The questions an agent asks are of two kinds. Some only you can answer: a path outside the sandbox, the network itself, a command where there is no sandbox. Others another agent may answer for you. Today that is one thing: reaching the network after outside content has arrived.

`ctrl+p`, then *Approver*, makes the conversation you are in the approver. Tell it in your own words what to allow. From then on, when another agent asks something an approver may answer, the question goes to the approver as well as up on that agent's card. The approver allows it, refuses it, or hands it to you. Its turn starts by itself, the asking agent shows *working* while it waits, and whichever of you answers first decides. If the approver ends its turn without deciding, or hands the question on, the asking agent shows *needs-you*. *Approver* again in the same conversation leaves no approver.

The approver never reads the other agent's text. That agent has read outside content, so what it wrote may carry instructions from whoever wrote that content. The approver sees what yui knows for itself: who asks, the task you gave that agent, the tool and why it needs asking, where the outside content came from, and the shape of each argument without its text. It may read the arguments if it must. Once it has, it has read outside content too, and it approves nothing more. The same goes for anything else outside it reads, so no agent may send it a message. An approver that has read outside content is passed over, the card saying why, and a conversation that already has cannot be made the approver.

An approver must be a conversation on S2 or another model yui talks to directly; a conversation on Claude cannot be one. Every answer to every question, yours and the approver's, is recorded with who gave it, for which agent, and on what.

## Policy

A machine can hold a policy: what no agent there may do, whoever approves it. It is one file, `/etc/yui/policy`, with one rule to a line and `#` starting a comment:

```
deny run grant                 # these tools are refused
network off                    # no sandbox has the network, and nothing is sent outward
protect ~/.ssh /srv/customers  # no grant, read or write reaches these
endpoint s2 https://llm.example.org/v1   # only these endpoints are used
mcp mcp.example.org tools.internal:8443  # only MCP servers at these hosts are used
memory manual                  # every note waits for you to turn it on
```

- `deny` names tools. The agent is not told of them, and a call to one is refused.
- `network off` keeps the network out of every sandbox, whatever was granted, and refuses every call that could send something off the machine.
- `protect` names paths, `~` meaning the user's home. Inside the sandbox they are not there, even within a granted directory, and a grant at or inside one is refused.
- `endpoint` names the endpoints a conversation may use: a URL, which also covers the paths under it, `s2` or `claude`. With no `endpoint` line, any may be used.
- `mcp` names the hosts whose [MCP servers](#mcp-servers) may be used, each a host, which covers every port, or `host:port`. A server at a URL elsewhere is not used, and *Tools* names the line that refuses it. With no `mcp` line, a server at any host may be used. Under `network off` none is.
- `memory manual` makes every note an agent writes wait for you to turn it on, whatever the *Memory* palette chooses.

What the policy forbids is refused before anyone is asked: no card, no approver, and `a` does not cover it. The refusal names the file and line, and repeats the line's comment, so write the reason there. Where yui cannot make a sandbox, `network off` and `protect` refuse every command and every plugin's tool, since nothing could hold them to it. `ctrl+p`, then *Policy*, shows the rules in force.

The file is followed only while root owns it and its directory and no one else can write either. With no file there is no policy. A file that cannot be followed, a rule misspelled or the file writable by others, stops every tool call, naming the file and line, until it is fixed; a typo never drops a rule silently. A change holds from the next call, with no restart. An agent cannot change the file: `/etc` is read-only in every sandbox.

On a machine an organisation manages, the file is the organisation's, written by whatever manages its fleet. Root on the machine can still change it.

## Secrets and brokers

An agent can use a secret without ever holding it. Keep each secret in its own file in `~/.config/yui/secrets`, named for the secret, the way ssh keeps a private key:

```
$ mkdir -m 700 -p ~/.config/yui/secrets
$ (umask 077; printf '%s\n' "$TOKEN" > ~/.config/yui/secrets/forge-token)
```

A secret others can read, or one in a directory others can write, is not used. The agent names a secret by its handle, `secret:forge-token`, and uses it through a broker: a short declaration of where the secret may go and what the agent may choose. yui, not the agent, puts the value in place.

```
# the forge's issues
http https://git.example.org/api/v4
secret forge-token header PRIVATE-TOKEN
allow GET /projects/*/issues
allow POST /projects/*/issues
```

```
# glab, which reads the token from its environment
program /usr/bin/glab
secret forge-token env GITLAB_TOKEN
args issue list -R *
```

An `http` broker is asked by yui itself; the agent chooses the method, a path the `allow` lines match (`*` is one part of the path, `**` any number) and a JSON body. A `secret` line puts the value in a named header or, with `bearer`, in `Authorization`. A `program` broker runs the program as you, without a shell, with the secret in a variable (`env NAME`) or on its input (`stdin`); the agent gives only the words after the program, matching an `args` line word for word, where `*` is one word that is not an option.

The agent proposes a broker with its `broker` tool. You approve it once, on a card only you can answer, which shows the secret, where it goes and what the agent controls; it is then kept in `~/.config/yui/brokers` and works in every conversation. A broker you write there yourself asks the same way on its first use. Changing a word of it asks again. The approval is a standing grant: `ctrl+p`, then *Standing grants*, takes it back. Using a broker reaches past the sandbox, so after outside content it is a question an approver may answer, and `network off` in the machine's policy refuses it. What a broker returns counts as outside content.

If a secret's value turns up in anything a tool returns, a file the agent read or a command's output, yui replaces it with the secret's handle before the agent or the record sees it, and says so. Values shorter than eight characters are not looked for. There is no broker for an ssh agent yet.

## Addresses sent elsewhere

An endpoint that is not on this machine is sent handles in place of email and IP addresses: `ada@example.org` becomes `‹email:1›` and `10.0.4.17` becomes `‹ip:1›`, the same handle for the same address throughout the conversation. What comes back has the addresses put back, so you read them, and the agent's commands run with them. The conversation you keep holds the real addresses. This machine's S2, `localhost` and the fleet's own addresses see everything; any other endpoint, one on your local network included, sees handles.

These are patterns. A version number shaped like an IP address is hidden too, and a name or anything written in prose is not hidden at all. A secret is treated more strictly: if you type or paste a secret's value, it is sent as its handle and yui says so, and a conversation that holds one anyway is sent to no endpoint. A conversation on Claude is not given handles.

## Claude

With Claude Code installed, yui talks to Claude:

```
$ yui --endpoint claude --model opus
```

Claude works with yui's tools and asks on yui's cards, like any other model, and the conversation resumes on Claude's side too: neither a resume flag nor a permissions flag is needed. A conversation moves between Claude and S2 with the model switcher.

Claude Code's own memory and its reading of `CLAUDE.md` files are off in a conversation here. Claude is told of yui's [memory](#memory) and searches it like any other model, so there is one memory, the one you decide on.

## Tools and guards

Besides reading, writing and running commands, the agent has `nerv`, which answers what a model cannot know about this machine: which libc a program is built against, which package owns a file and whether it is Nerv's or Fedora's, which install profile brings a package in, and which slot is running.

Guards stop calls that would do the wrong thing here and tell the agent what to do instead: `sudo` becomes `doas`, another distribution's package manager becomes `dnf`, bash syntax in a `/bin/sh` command becomes its POSIX form, and the agent never reboots the machine. Your own guards are a setting of the guards plugin (`ctrl+p`, then *Plugins*, then *guards*): a list of rules, where a rule names a tool, a field and a match, and what to say, and one of yui's own can be turned off:

```
[
  {"id": "no-npm", "tool": "run", "field": "command", "word": "npm", "say": "This project uses pnpm."},
  {"id": "sudo", "off": true}
]
```

Any program can add tools of its own. One placed in `~/.config/yui/plugins` is started with yui's agents and speaks JSON, one message per line, on its standard input and output.

A plugin is held like a command. Its own process, which sees each call before it runs, gets a sandbox of its own: the system read-only, a directory under yui's state, and no network. Each call of one of its tools runs inside the conversation's sandbox, seeing what the agent sees and reaching the network only when the agent was granted it; what it answers then counts as outside content, as a networked command's output does. Where yui cannot make a sandbox, a plugin runs as you, and its tools count as reaching outward.

A plugin is set up in the TUI. `ctrl+p`, then *Plugins*, lists each plugin that has settings, and enter on one shows them: on-off ones are switched, choices picked, text and secrets written in the composer (`enter` keeps it, an empty one goes back to the plugin's own, `esc` leaves it), and lists added to and taken from. yui keeps them in `~/.config/yui/settings`, readable by you alone, hands them to the plugin when it starts, and starts it again when one changes. A secret is never shown again, only whether it is set. What a plugin says is wrong with its settings is listed under them. A plugin reads nothing else of yours.

A plugin may also keep a little state for each conversation, draw a panel, and put one line on the agent's card. yuid keeps the state in magi and hands it back with each call. The plugin never reaches magi itself.

A panel is a title, a list and lines. yui draws it in its own colours and shows nothing else a plugin sends. `alt+p` shows or hides the panels, and `ctrl+p`, then *Panels*, chooses which. A plugin may read the agent's finished reply and ask for it again, once a turn at most, or warn you.

A plugin may also be a channel: a way to reach conversations from somewhere else, a chat service, say. yuid starts the channel apart from the plugin's own process, with the network and the plugin's directory, and keeps it running. Each chat it holds is a client of its own, seeing a conversation as a terminal does, but allowed less: it opens conversations, asks them, stops them, and answers the agent's questions and only the cards an approver agent could answer too. Grants, the policy and the sandbox stay with you, at the terminal, whatever the plugin is. A channel cannot change its own settings: it can only ask you to add a line to one, saying why, and the question waits under the plugin in *Plugins*, and in a line in each open conversation, until you allow or refuse it. While a channel is ready, yuid does not exit when the terminals close; to have it running from login, `systemctl --user enable --now yui`.

### Fetching pages

The `fetch` tool reads a web page as text. HTML becomes plain lines, and JSON and text arrive as they are. A conversation without the network asks you first, on a card, and `a` covers it from then on. What a page says counts as outside content. `network off` refuses every fetch.

### Plain writing

`terse` holds the prose an agent writes to short, plain rules. It checks prose files and the comments in code before a write lands, and the agent's replies. It skips code.

- A sentence of more than 20 words is a hint, and of more than 25, a fault. A paragraph of more than 4 sentences is a hint, and of more than 6, a fault.
- Faults: a progressive or perfect tense, a contraction, a semicolon and a phrasal verb such as `set up`. A long word with a short one, such as `utilize` for `use`, is a fault too.
- Hints: the passive, a hedge such as `probably`, and words that sell, such as `seamless`.

A fault refuses the write and lists what to fix, or asks for the reply again. To silence one fault, write `terse: off RULE reason` on its line or the line before.

terse checks nothing until it is turned on: `ctrl+p`, then *Plugins*, then *terse*, then *Checking*. Its *Rules* setting sets the rest, one thing a line:

```
off style/hedge           # a rule not checked
soft verb/perfect         # a fault made a hint
word in lieu of = instead # one more word
replies off               # replies not checked
```

Its words are Nerv's own; a `word` line adds one of yours.

## MCP servers

An MCP server gives yui's agents its tools. Declare one in a file of its own in `~/.config/yui/mcp`, named for the server. One that runs on this machine is declared by its program:

```
run /usr/bin/github-mcp-server stdio   # the program and its arguments
env GITHUB_HOST=github.example.org     # its environment
network                                 # it may reach the network
read ~/src/notes                        # what it may read
write ~/src/scratch                     # and write
auto search_code get_file_contents      # its tools that need no card
timeout 60                              # seconds a call may take
```

One served elsewhere is declared by its URL, and yui speaks to it over HTTP:

```
url https://mcp.example.com/mcp        # where it is served
token                                   # send it the key kept for its host
auto search                             # its tools that need no card
timeout 60                              # seconds a call may take
```

A file has `run` or `url`, never both. `env`, `network`, `read` and `write` are for a server that runs here, and a file with a `url` that names one is refused.

A server at a URL that wants a key is given the one kept for its host, the same file in `~/.config/yui/keys` an [endpoint's key](#endpoints-and-their-keys) is, when its file says `token`. One that signs you in with OAuth needs no line at all: run `yui mcp login NAME` once, NAME being the file's name.

```
$ yui mcp login github
Open this to sign in to github:

  https://github.example.com/login/oauth/authorize?response_type=code&client_id=…

The browser is sent back to http://127.0.0.1:41377/callback when you have signed in. If it is on another machine, that page will not load: paste its address here and press enter.
signed in to github
```

Open the address, sign in, and yui finishes when the browser comes back to it; a server waiting for the sign-in is started from yuid's next request. Over ssh, the browser is on your own machine and that last page does not load; copy its address from the browser and paste it into the terminal instead. The sign-in is kept in `~/.config/yui/keys/mcp/NAME`, readable by you alone, and yui renews it itself when it expires; it is used only for the URL it was made for. `yui mcp logout NAME` forgets it. `oauth` in the file says the server is not to be tried without a sign-in, and `client ID` gives the client ID to sign in as, for a server that does not register yui by itself. Until you have signed in, the server's tools are not offered, and *Tools* says to run `yui mcp login NAME`.

A server that runs here runs in a sandbox of its own: it sees the system, a directory of its own under yui's state, and what its file names, and nothing else of yours. It has the network only when its file says `network`, and never while the machine's policy says `network off`. A protected path is not there for it either. A server at a URL runs nowhere here, and sees nothing of the machine but the arguments of the calls made to it.

Its tools are offered as `server.tool`, and each asks on a card unless the file names it `auto`. What a server with the network answers counts as outside content, and what a server at a URL answers always does; once a conversation holds outside content, its calls to such a server go to the approver, as any send does. A call that runs past the file's `timeout`, or that you stop with `esc`, is cancelled at the server.

yuid follows the directory as it changes: a new file starts its server, a removed one stops it, and a changed one starts it again, all from the next request and with no restart. A server that runs here and stops is started again once; if it stops again it is left down, and *Tools* says so until its file changes.

The file is followed only while it is yours and no one else can write it. A line yui does not understand leaves that server down, naming the file and the line.

## Switching tools

`ctrl+p`, then *Tools*, lists every tool, each plugin and each MCP server with its tools, and whether each is on. Enter on one switches it on or off for this machine, or for this conversation only, which is kept with the conversation and overrides the machine. A tool switched off is not offered to the agent, and a call to it is refused, saying so. Switching a plugin or a server off switches all its tools off.

The machine's switches are kept in `~/.config/yui/tools`, `off NAME` or `on NAME` to a line, which you may also edit by hand; a change holds from the next request. What the machine's policy denies stays off, whatever is switched. `approve` cannot be switched off: the approver decides with it, so choose the approver instead.

## Telegram

A conversation can be reached from a Telegram chat, through yui's own `telegram` channel. Make a bot with Telegram's BotFather, then give yui its token: `ctrl+p`, then *Plugins*, then *telegram*, then *Bot token*. To have yuid running from login, so the bot answers with no terminal open:

```
$ systemctl --user enable --now yui
```

Write to the bot. It answers with a short code, and asks you whether you may talk: the question appears under *telegram* in *Plugins*, naming the Telegram account and the same code. Check that it is the code on your phone and allow it; a name in Telegram is whatever its owner typed, and the code is what ties the question to your chat. From then on that account may talk to yui, and the bot says so. Once someone may talk, strangers are not answered at all, unless *Strangers may ask* says *always*.

The other settings say where the chat goes:

| setting | what it says |
| --- | --- |
| *Conversation* | the conversation the chat is: its name, the end of it, or words of its title. Without it, the last one held in *Directory* |
| *Directory* | where a new conversation is started; your home directory without it |
| *Endpoint*, *Model* | what a new conversation talks to; this machine's S2 without them |
| *Cards in the chat* | `delegable`, the cards an approver agent could answer, or `none`; questions always |
| *Who may talk* | the Telegram accounts, a user id and a name a line; allowing a question adds one |

What you write in the chat is asked as if you typed it in the terminal, and the answer appears as it is written, with a line for each tool the agent runs. The terminal shows the same conversation, and the chat shows what was asked from the terminal. A message sent while the agent works goes when its turn ends. `/stop` ends the turn, `/new` starts a new conversation, `/open WORDS` opens the one the words name, and `/status` says which one this is. A reply too long for a few messages also comes as a file. A text file you send is read, as outside content, since anyone could have written it; voice notes and pictures are not read.

A question the agent asks comes with its choices as buttons, and whatever you write while it waits is your answer. A card the agent raises comes with *Allow*, *Always* and *Refuse* when it is one an approver agent could answer; any other says to answer it in the terminal. Telegram carries the chat and can read it, which is why grants never go through it. Only private chats are answered: a group the bot is added to is ignored.

## Copy and paste

Drag across the conversation to copy; the text goes to your clipboard, over SSH and through tmux, without the frames around it. `ctrl+y` copies the agent's last answer, and the commands (`ctrl+p`) copy the last code block or the last command's output. Hold shift to use your terminal's own selection instead.

A file dropped onto the terminal, or a pasted path, is attached to your message. A long paste is shown as a single line, `[paste 1 · 240 lines]`, and sent whole.

## Keys

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
| `ctrl+d` | leave; the agent carries on |

