# The desktop

Umbriel, Noctalia and foot, for machines that install one: getting a desktop, logging in, the keys you use, the shell around your windows, the live background and the screensaver, the browser, X11 programs, sound, the power profile and the keyboard.

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

`Mod` is the key with the logo on it. Umbriel reads its settings from `~/.config/umbriel/config.toml`, which a new account starts with. That file includes `/usr/share/umbriel/config.toml`, upstream's annotated example of every setting, which carries the keys above, and anything you set in your own file wins over it; a `[keybinds]` entry there adds to the packaged ones. Umbriel applies a change the moment you save it. `umbriel outputs` lists the displays it drives.

An account whose `config.toml` predates the include has no keys at all, because a config file replaces Umbriel's built-in keys rather than adding to them. Adding these lines to the top of `~/.config/umbriel/config.toml` brings them back as soon as it is saved:

```
[include]
files = ["/usr/share/umbriel/config.toml"]
```

The pointer is Phinger, light on Nerv's dark surfaces, and the login screen uses the same one. `[input.cursor] theme` in your config picks another by the name of its directory under `/usr/share/icons`, such as `phinger-cursors-dark` or the left-handed `phinger-cursors-light-left`, and `size` sets how large it is drawn.

## Minimized windows

A window's own minimize button, or a click on its icon in the taskbar while it has the focus, hides it. Its icon stays in the taskbar, marked with a minus, and a click on that icon brings it back; right-click an icon for *Minimize* and *Restore*. A window in a column leaves the strip while it is minimized, and the columns beside it close up; it comes back in a column of its own, after the one you are working in. Pinned and fullscreen windows do not minimize.

## Noctalia

Noctalia is the shell around your windows: the bar, the launcher, notifications, the wallpaper and the lock screen. Its wallpaper is the one you see while the [live background](#the-live-background-and-the-screensaver) is off. It comes in Myelin, Nerv's colours, set in Nerv's own typeface, Ashinoko, and dark.

Nerv's settings for it are in `/etc/xdg/noctalia/nerv.toml`, which the shell reads first, for every account, old or new. What you choose in its Settings panel is saved in `~/.local/state/noctalia/settings.toml`, and anything you put in `~/.config/noctalia/` yourself, and both win over Nerv's. An update to the desktop reaches your account without touching either.

Umbriel's borders, title bars and overview wear the same colours, and change with them when the shell switches between dark and light. The shell writes them to `~/.config/umbriel/noctalia.toml`, which Umbriel's config includes when `"noctalia.toml"` is in the `files` list under `[include.optional]` in `~/.config/umbriel/config.toml`, as it is for every account the desktop made.

## The live background and the screensaver

The desktop's background is drift: a slow flight through a field of light, drawn on the GPU for every display, at most 24 frames a second and at half the display's resolution, which the compositor scales up. After five minutes without input the same flight comes to the front of every display as the screensaver, and the first key or click puts the desktop back; that key or click reaches no window. A program that asks the compositor to keep the display awake, as video players do and as the caffeine button on the bar does, keeps the screensaver away. The screensaver never locks the machine and never turns a display off.

`drift off` gives the background back to Noctalia's wallpaper, which then shows the frame that was on screen, saved at the display's full resolution; `drift on` brings the flight back. `drift pause` holds the background still on the frame it shows, and `drift resume` sets it moving again. Pausing and turning off apply to the background only: the screensaver flies regardless. Each choice outlasts a logout, and a paused background comes back on the frame it was paused on.

```
$ drift off
desktop=off motion=running screensaver=waiting outputs=1
$ drift status
desktop=off motion=running screensaver=waiting outputs=1
```

With the background off, the wallpaper is Noctalia's to change in its Settings like any other. The stills drift hands it are kept in `~/.local/state/drift/snapshots`, the latest for each display. While drift draws the background, the lock screen is plain black; with it off, the lock screen shows Noctalia's wallpaper. `systemctl --user mask drift` turns off both the background and the screensaver for your account.

| command | |
| --- | --- |
| `drift on`, `drift off` | the live background, or Noctalia's wallpaper showing its last frame |
| `drift pause`, `drift resume` | hold the background still, or set it moving |
| `drift toggle` | pause if moving, resume if paused |
| `drift status` | the state, as one line |

## Light and dark

The desktop is dark, and the shell's dark or light mode is every program's. Programs ask the desktop which one it is, through the desktop portal, and are told when it changes, so Browser and GTK 4 programs already open turn with the shell, in Myelin's accent colour for that mode. Choosing light, dark or automatic is done in Noctalia's Settings panel or the control center, and stays chosen.

Before the shell has said anything, at a first login or in a program started before it, everything is dark: the portal answers dark, and GTK's machine-wide settings in `/etc/xdg/gtk-3.0` and `/etc/xdg/gtk-4.0` choose the dark theme. The login screen, Luciole and foot start dark too. The shell writes the mode and the accent to `~/.local/state/nerv-portal-settings/appearance` whenever either changes.

To see what programs are told, ask the portal; `1` is dark and `2` is light:

```
$ busctl --user call org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop org.freedesktop.portal.Settings ReadOne ss org.freedesktop.appearance color-scheme
v u 1
```

## The bar

The bar runs along the top of every display.

| where | what |
| --- | --- |
| left | the launcher; your workspaces, by number; the taskbar, one icon for each window on this display; the workspace's layout, which opens a panel to change it and act on the focused window |
| middle | the date and time; what is playing, while something is |
| right | CPU, memory and GPU use; the privacy indicator, lit while a microphone, camera or screen share is in use; the tray; caffeine, which keeps the screen awake; the clipboard history; a screenshot; network; Bluetooth; volume; the battery, on a machine with one; brightness, on a display whose brightness can be set; the displays; notifications; the control center |

The GPU figure is the same one `axon` shows. Right-clicking an empty stretch of the bar opens the control center, and the shell's Settings changes what the bar holds.

## The tray

A program that keeps running without a window, such as Steam or a chat client, keeps an icon in the tray on the bar, in Myelin's colours. Closing its window leaves it there; click the icon to bring the program back, or right-click it for the program's menu.

## Displays

The displays button on the bar sets each display's resolution, refresh rate and scale, and turns one off; right-click it to arrange the displays by dragging them where they stand on your desk. A change applies at once and is already saved, to `~/.config/umbriel/outputs.toml`, which Umbriel's config includes. Keep `[output.*]` sections out of `~/.config/umbriel/config.toml`, where they would override that file.

## Plugins

The layout and displays buttons are Noctalia plugins, and they come installed with the desktop. Noctalia's plugin store is off: Settings → Plugins lists its two sources, *official* and *community*, and turning one on lets you browse it and install from it. The shell downloads nothing else at start either: its community templates and the calculator's currency exchange rates are off until you turn them on in Settings.

## foot

`foot` is the terminal, `Mod+Return` away. The key runs `footclient`, which opens a window in a foot server that starts with your session, so the terminal is there at once. It comes in Myelin and Ashinoko from `/etc/xdg/foot/foot.ini`; a `~/.config/foot/foot.ini` of your own replaces that file entirely, and `include=/usr/share/foot/themes/myelin` in it keeps the colours.

## Browser

Browser is the web browser that comes with the desktop: `browser` from a terminal, *Browser* in the launcher. It is built from Firefox's source, so pages work as they do in Firefox, and it runs on Nerv's own C library and allocator. It is not called Firefox, because Mozilla's name and logos belong to Mozilla's own builds.

It follows the desktop's [light or dark](#light-and-dark) scheme in Myelin's colours, and pages are shown in the same scheme; an open window changes when the shell does. About Browser opens over the window it came from. The window is two rows: the tabs, ending in the window's buttons, and the address bar with back, forward, reload, downloads and the extensions menu. Toolbars hide only in fullscreen. The interface is set in Ashinoko, and so is any page that does not choose its own fonts. A new tab is a blank page with the cursor in the address bar.

It starts where you left off: the last session's tabs come back, and each loads when you first look at it. Searches go to DuckDuckGo.

Video is decoded by the GPU's video engine: H.264, HEVC, VP8, VP9 and AV1, in 8 and 10 bits, which covers what YouTube and the other video sites serve, and the video of a call in VP8, VP9 or AV1. The frames go from the video engine to the screen without passing through the processor: the compositor draws each one itself, in the colours the video declares, so a film costs the processor a small part of what decoding it there would, high-resolution video plays smoothly, and nothing caps its frame rate. Seeking does not restart the video engine. A call whose VP9 carries several sizes at once is decoded by the processor. Tabs you are not looking at run on the machine's efficiency cores at a low clock, however busy their pages are; a tab playing sound is not slowed.

Video a site encrypts for DRM, as Vimeo and the subscription services do, plays once you allow it. Playing it takes Widevine, Google's DRM module, which is proprietary, so Browser has none until a site asks for it. Browser then asks whether to play DRM-controlled content; when you choose *Enable DRM*, it downloads Widevine from Google, checks that the download is the one Google signed, and plays the video once you reload the page. Widevine decrypts and decodes such video itself, on the processor. *Settings → General → Play DRM-controlled content* turns DRM off again and removes Widevine.

It sends nothing you did not ask it to, and fetches no plugin you did not ask for. Once DRM is on, it asks Google once a day whether Widevine has a newer version, naming the module, the platform and the architecture and nothing else. There is no telemetry, no studies or experiments, no crash reporting, no sponsored tiles or suggestions, and no Pocket. Tracking protection is on Strict, every page is loaded over HTTPS, and names are looked up by the system's own resolver. uBlock Origin is installed and on for every user; you can switch it off in *Settings → Extensions*, but not remove it. Browser never offers to save a password or to translate a page.

Every download asks where to go, in the desktop's file chooser. Sync is in *Settings → Sync*, for a Mozilla account, and nothing else asks you to sign in.

Browser uses the profile in `~/.mozilla/firefox`, or in `~/.config/mozilla/firefox` where a newer Firefox made it, so a profile from Firefox carries over as it is. Pages see Browser as Firefox, which is what its engine is.

## Files

Luciole is the file manager: the launcher finds it as *Luciole*, and `luciole` starts it from a terminal, `luciole ~/Downloads` in a folder. It browses in a grid, a list or columns, with tabs, windows and a split view, and draws thumbnails of images and the first page of PDFs beside the listing. It opens archives as folders and makes new ones. Thumbnails are drawn in helper processes with limits on their memory and time, so a broken file costs its thumbnail and never the window. Nothing indexes your files in the background: a search looks through the folder you are in, when you ask.

Other programs use it too. Browser's Open and Save dialogs are Luciole's, as are those of any program that asks the desktop for one, and "Show in folder" in a browser opens the folder in Luciole.

`Ctrl+,` opens its settings, which it keeps in `~/.config/luciole/`. Its colours are the desktop's: the shell writes them to `~/.config/luciole/colors.toml` whenever its palette changes.

## X11 programs

Programs written for X11 run on the desktop beside Wayland ones, in windows of their own. Every session has an X display, and programs started from it find it in `DISPLAY`:

```
$ echo $DISPLAY
:0
```

The X server is Xwayland. The session starts it when the first X11 program connects, and again if it stops. It draws with the GPU, and so does an X11 program using OpenGL. Nothing needs installing: it comes with the desktop.

## Sound

PipeWire is the sound server, for every program, and starts with your session. `wpctl status` shows the outputs and inputs, and `wpctl set-default` picks one.

## Power

The power profile button on the bar switches the machine's power profile, the same one `doas power PROFILE` sets from a terminal: power-saver, balanced, and performance where it changes something on that machine. Whoever is logged in at the machine may switch it; from anywhere else, it takes `doas power`.

A program may hold power-saver or performance while it runs, and the bar shows the held profile. The hold ends when the program lets go or exits, and the profile goes back to what it was. Choosing a profile yourself, on the bar or with `power`, ends every hold. `power` with no arguments says which profile is in force and why.

## GTK programs

GTK programs, GTK 3 and GTK 4 alike, come in Myelin and in Ashinoko Sans, dark or light with the shell. The shell writes their colours to `noctalia.css` and their settings to `settings.ini` in `~/.config/gtk-3.0` and `~/.config/gtk-4.0` whenever its palette or mode changes. A GTK 4 program already open turns with the shell, since it also asks the desktop for [light or dark](#light-and-dark); a GTK 3 program takes the new mode when it is next opened. `gtk.css` in the same folders is yours: it imports the colours, and CSS you add below that line applies on top of them.

`settings.ini` is the shell's and is written again on every change. To set something of your own there, copy `/usr/share/nerv-noctalia-config/gtk-settings.ini` into `~/.config/noctalia/`, edit the copy, and point the shell at it in `~/.config/noctalia/noctalia.toml`, which wins over Nerv's settings:

```
[theme.templates.user.gtk-settings]
input_path = "~/.config/noctalia/gtk-settings.ini"
```

## Icons

Programs draw Nerv's icons, Myelin: Lucide's line drawings in Myelin's colours, for places, kinds of file and common actions, with the Adwaita theme beneath them for everything else. A `gtk-icon-theme-name` line in your copy of the GTK settings template, as above, picks another.

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
- **The Trash, network locations and removable drives in Luciole.** Luciole shows the folders on your disks; it does not list these yet.
- **Thumbnails of videos.** Luciole shows a video as its icon.
