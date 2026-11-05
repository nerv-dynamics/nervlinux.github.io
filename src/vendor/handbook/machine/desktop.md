# The desktop

Umbriel, Noctalia and foot, for machines that install one: getting a desktop, logging in, the keys you use, the shell around your windows, the browser, sound and the keyboard.

## Installing a desktop

The `workstation-gui` profile installs one, from the start or onto a console machine later:

```
$ doas dnf install nerv-workstation-gui
$ doas systemctl enable --now greetd.service
```

Nothing in it touches the boot path, so it installs into the running system without an update. Your account needs the `seat` group, which arrives with the desktop: `doas usermod -aG seat you`, then log in again ([Groups](accounts-and-keys.md#groups)).

## Logging in

The greeter takes over the first console and logs you in to an Umbriel session. Without it, log in on a free console, `Ctrl+Alt+F2`, and start one by hand:

```
$ umbriel-session
```

`Ctrl+Alt+F1` goes back to the first console. A session starts only at the machine itself, never over SSH, and only once the GPU service is running, since every window is drawn through it.

## Umbriel

Umbriel is the compositor: it draws the windows and decides where they go. Windows sit in columns on a strip that scrolls sideways, each new one opening at half the screen's width, and every display has its own workspaces.

| keys | |
| --- | --- |
| `Mod` alone | the launcher |
| `Mod+Return` | a terminal |
| `Mod+Q` | close the window |
| `Mod+Arrows`, `Mod+H/J/K/L` | move focus |
| `Mod+Shift+Left/Right` | move the column |
| `Mod+Shift+Up/Down` | move the window within its column |
| `Mod+R`, `Mod+Shift+R` | cycle the column's width |
| `Mod+F` | fullscreen |
| `Mod+T` | float the window |
| `Mod+O` | the overview of every workspace; the top-left corner opens it too |
| `Mod+1`…`9` | go to a workspace |
| `Mod+Shift+1`…`9` | send the window there |
| `Mod+Space` | the scratchpad |
| `Mod+Escape` | end the session |

`Mod` is the key with the logo on it. Umbriel reads its settings from `~/.config/umbriel/config.toml`, and from Nerv's own when you have none; copy Nerv's from `/etc/xdg/umbriel/config.toml` to start one. It applies a change the moment you save it. `umbriel outputs` lists the displays it drives.

## Noctalia

Noctalia is the shell around your windows: the bar, the launcher, notifications, the wallpaper and the lock screen. Its Settings panel changes it, and writes what you choose to `~/.config/noctalia/noctalia.toml`. It comes in Myelin, Nerv's colours, set in Nerv's own typeface, Ashinoko.

## foot

`foot` is the terminal, `Mod+Return` away. It reads `~/.config/foot/foot.ini` if you write one.

## Firefox

```
$ doas dnf install nerv-firefox
```

Nerv's Firefox runs on Nerv's own C library and allocator, with sponsored content, telemetry and DRM video switched off.

## Sound

PipeWire is the sound server, for every program, and starts with your session. `wpctl status` shows the outputs and inputs, and `wpctl set-default` picks one.

## The keyboard

The machine has one keyboard layout, for the console and the desktop alike, set in `/etc/vconsole.conf`:

```
KEYMAP=de
XKBLAYOUT=de
```

`nerv-keymap --list` shows the layouts; a change applies at the next login.

## What is still in progress

- **X11 programs.** The desktop is Wayland. Running programs that need X11 is in progress.
- **Screenshots and the clipboard from the command line.** No tools for them ship yet.
