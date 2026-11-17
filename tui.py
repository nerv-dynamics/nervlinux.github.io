#!/usr/bin/env python3
"""Put a terminal program's screen on a page as text, in its own colours.

    tmux capture-pane -e -p -t PANE > axon.ansi
    python3 tui.py axon axon.ansi --sub 'EVA-00=nerv-1' --sub ...

writes the capture, with the substitutions made, to src/tui/axon.ansi, and
renders it into every page's <pre data-tui="axon"> block. With no capture
file, it re-renders src/tui/NAME.ansi as it is. Then python3 build.py.

WHY TEXT, NOT A SCREENSHOT
  A capture is a few kilobytes, sharp at any zoom, in the site's own
  typeface, selectable and readable by a screen reader, and a new one is one
  command. A screenshot is none of those.

SUBSTITUTIONS
  A capture shows what was on screen: host names, device UUIDs, home paths.
  Nothing internal is published, so each one is replaced here, and a
  replacement must be exactly as long as what it replaces, because the
  screen is a grid and a shorter name would shift every column after it.
  Pad with spaces where that reads better ('/home/me/x=~/x      ').
  A substitution that matches nothing is an error, not a no-op: the screen
  changed, and whatever it now shows has not been checked.

COLOURS
  Programs on Nerv draw in 24-bit colour from the Myelin palette, so a span
  carries its colour inline. The default foreground and background are the
  dark terminal's, set on .term--tui, which stays dark in light mode
  because the programs chose their colours for a dark background.
"""

import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
STORE = ROOT / "src" / "tui"
PAGES = ROOT / "src" / "pages"

BASIC = ["#1e1e1e", "#ff9a9f", "#92c56c", "#e1af4a", "#6ebdff", "#dea0f1", "#05c9db", "#dfdfdf"]

SGR = re.compile(r"\x1b\[([0-9;]*)m")
OTHER = re.compile(r"\x1b\[[0-9;?]*[A-Za-ln-z]|\x1b[()][A-Za-z0-9]|\x1b[=>]")


def colour(params, i):
    """Read an extended colour at params[i] (5;n or 2;r;g;b); return (css, next index)."""
    if i < len(params) and params[i] == 2 and i + 3 < len(params):
        r, g, b = params[i + 1:i + 4]
        return f"#{r:02x}{g:02x}{b:02x}", i + 4
    if i < len(params) and params[i] == 5 and i + 1 < len(params):
        n = params[i + 1]
        if n < 8:
            return BASIC[n], i + 2
        if n < 16:
            return BASIC[n - 8], i + 2
        if n < 232:
            n -= 16
            v = [0, 95, 135, 175, 215, 255]
            return f"#{v[n // 36]:02x}{v[n // 6 % 6]:02x}{v[n % 6]:02x}", i + 2
        g = 8 + 10 * (n - 232)
        return f"#{g:02x}{g:02x}{g:02x}", i + 2
    return None, len(params)


def style_of(st):
    fg, bg = st["fg"], st["bg"]
    if st["rev"]:
        fg, bg = bg or "#1e1e1e", fg or "#dfdfdf"
    css = []
    if fg:
        css.append(f"color:{fg}")
    if bg:
        css.append(f"background:{bg}")
    if st["bold"]:
        css.append("font-weight:700")
    if st["dim"]:
        css.append("opacity:.6")
    if st["ital"]:
        css.append("font-style:italic")
    if st["ul"]:
        css.append("text-decoration:underline")
    return ";".join(css)


def render(text):
    st = dict(fg=None, bg=None, bold=False, dim=False, ital=False, ul=False, rev=False)
    out = []
    for line in text.rstrip("\n").split("\n"):
        runs = []  # [style, text]
        pos = 0
        line = OTHER.sub("", line)
        for m in list(SGR.finditer(line)) + [None]:
            chunk = line[pos:m.start()] if m else line[pos:]
            if chunk:
                s = style_of(st)
                if runs and runs[-1][0] == s:
                    runs[-1][1] += chunk
                else:
                    runs.append([s, chunk])
            if not m:
                break
            pos = m.end()
            params = [int(p) if p else 0 for p in m.group(1).split(";")] if m.group(1) else [0]
            i = 0
            while i < len(params):
                p = params[i]
                i += 1
                if p == 0:
                    st.update(fg=None, bg=None, bold=False, dim=False, ital=False, ul=False, rev=False)
                elif p == 1: st["bold"] = True
                elif p == 2: st["dim"] = True
                elif p == 3: st["ital"] = True
                elif p == 4: st["ul"] = True
                elif p == 7: st["rev"] = True
                elif p == 22: st["bold"] = st["dim"] = False
                elif p == 23: st["ital"] = False
                elif p == 24: st["ul"] = False
                elif p == 27: st["rev"] = False
                elif 30 <= p <= 37: st["fg"] = BASIC[p - 30]
                elif 90 <= p <= 97: st["fg"] = BASIC[p - 90]
                elif p == 39: st["fg"] = None
                elif 40 <= p <= 47: st["bg"] = BASIC[p - 40]
                elif 100 <= p <= 107: st["bg"] = BASIC[p - 100]
                elif p == 49: st["bg"] = None
                elif p in (38, 48):
                    c, i = colour(params, i)
                    st["fg" if p == 38 else "bg"] = c
        html_line = "".join(
            f'<span style="{s}">{html.escape(t, quote=False)}</span>' if s else html.escape(t, quote=False)
            for s, t in runs)
        out.append(html_line)
    return "\n".join(out)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    name, rest = argv[0], argv[1:]
    subs, src = [], None
    while rest:
        a = rest.pop(0)
        if a == "--sub":
            old, _, new = rest.pop(0).partition("=")
            if len(old) != len(new):
                sys.exit(f"tui: --sub {old!r} -> {new!r}: {len(old)} characters against {len(new)}; the screen is a grid")
            subs.append((old, new))
        else:
            src = pathlib.Path(a)
    store = STORE / f"{name}.ansi"
    if src:
        text = src.read_text()
        for old, new in subs:
            if old not in text:
                sys.exit(f"tui: --sub {old!r} matches nothing in {src}")
            text = text.replace(old, new)
        STORE.mkdir(parents=True, exist_ok=True)
        store.write_text(text)
    text = store.read_text()
    body = render(text)
    block = re.compile(r'(<pre class="[^"]*" data-tui="%s"[^>]*>).*?(</pre>)' % re.escape(name), re.S)
    hits = 0
    for page in sorted(PAGES.glob("*.html")):
        s = page.read_text()
        s2, n = block.subn(lambda m: m.group(1) + body + m.group(2), s)
        if n:
            page.write_text(s2)
            hits += n
            print(f"  {store.relative_to(ROOT)} -> {page.relative_to(ROOT)}")
    if not hits:
        sys.exit(f'tui: no page has a <pre ... data-tui="{name}"> block')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
