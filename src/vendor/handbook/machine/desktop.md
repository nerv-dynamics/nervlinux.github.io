# The desktop

Umbriel, Noctalia and foot, for machines that install one: getting a desktop, logging in, the keys you use, the shell around your windows, the browser, X11 programs, sound and the keyboard.

## Installing a desktop

The `workstation-gui` profile installs one, from the start or onto a console machine later:

```
$ doas dnf install nerv-workstation-gui
```

Nothing in it touches the boot path, so it installs into the running system without an update. The graphical login comes with it and takes over the first console from the next boot; `doas systemctl start greetd.service` brings it up now instead. A session needs the `seat` group, which arrives with the desktop: the machine's administrators, the accounts in `wheel`, are put in it then, and any other account joins with `doas usermod -aG seat you` and logs in again ([Groups](accounts-and-keys.md#groups)).

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

`Mod` is the key with the logo on it. Umbriel reads its settings from `~/.config/umbriel/config.toml`, which a new account starts with; `/usr/share/umbriel/config.toml` is upstream's annotated example of every setting. It applies a change the moment you save it. `umbriel outputs` lists the displays it drives.

The pointer is Phinger, light on Nerv's dark surfaces, and the login screen uses the same one. `[input.cursor] theme` in your config picks another by the name of its directory under `/usr/share/icons`, such as `phinger-cursors-dark` or the left-handed `phinger-cursors-light-left`, and `size` sets how large it is drawn.

## Noctalia

Noctalia is the shell around your windows: the bar, the launcher, notifications, the wallpaper and the lock screen. Its Settings panel changes it, and writes what you choose to `~/.config/noctalia/noctalia.toml`. It comes in Myelin, Nerv's colours, set in Nerv's own typeface, Ashinoko.

## foot

`foot` is the terminal, `Mod+Return` away. The key runs `footclient`, which opens a window in a foot server that starts with your session, so the terminal is there at once. It comes in Myelin and Ashinoko from `/etc/xdg/foot/foot.ini`; a `~/.config/foot/foot.ini` of your own replaces that file entirely, and `include=/usr/share/foot/themes/myelin` in it keeps the colours.

## Firefox

Firefox comes with the desktop. Nerv's Firefox runs on Nerv's own C library and allocator, with sponsored content, telemetry and DRM video switched off.

## Files

Strata is the file manager: the launcher finds it as *Strata*, and `strata` starts it from a terminal. It browses in columns, icons or a list, with tabs, and previews documents, images, audio and source code beside the listing. Every preview is drawn in a sandbox that sees only the file it shows. Nothing indexes your files in the background: a search looks through the folder you are in, when you ask.

Other programs use it too. Firefox's Open and Save dialogs are Strata's, as are those of any program that asks the desktop for one, and "Show in folder" in a browser opens the folder in Strata.

## X11 programs

Programs written for X11 run on the desktop beside Wayland ones, in windows of their own. Every session has an X display, and programs started from it find it in `DISPLAY`:

```
$ echo $DISPLAY
:0
```

The X server is Xwayland. The session starts it when the first X11 program connects, and again if it stops. It draws with the GPU, and so does an X11 program using OpenGL. Nothing needs installing: it comes with the desktop.

## Sound

PipeWire is the sound server, for every program, and starts with your session. `wpctl status` shows the outputs and inputs, and `wpctl set-default` picks one.

## Icons

Programs draw Nerv's icons, Myelin: Lucide's line drawings in Myelin's colours, for places, kinds of file and common actions, with the Adwaita theme beneath them for everything else. `gtk-icon-theme-name` in `~/.config/gtk-4.0/settings.ini`, and in `~/.config/gtk-3.0/settings.ini`, picks another.

## The keyboard

The machine has one keyboard layout, for the console and the desktop alike. `nerv-keymap` sets both:

```
$ doas nerv-keymap de
$ doas nerv-keymap de:nodeadkeys     # an XKB layout and variant
$ nerv-keymap                        # what is set now
```

`nerv-keymap --list` shows the friendly names. The console changes at once; the desktop takes the new layout at the next login. Both are recorded in `/etc/vconsole.conf`.

## What is still in progress

- **Screenshots and the clipboard from the command line.** No tools for them ship yet.
- **The Trash, network locations and removable drives in Strata.** Strata shows the folders on your disks; it does not list these yet.
