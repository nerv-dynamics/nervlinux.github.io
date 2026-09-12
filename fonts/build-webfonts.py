#!/usr/bin/env python3
"""Turn built Nerv typeface TTFs into subsetted WOFF2 for the web.

    python3 fonts/build-webfonts.py <dist-dir>

where <dist-dir> is the `dist/` of an Iosevka build run against
packages/nerv-fonts/files/private-build-plans.toml — see fonts/README.md for
how to produce one.

This is NOT part of `python3 build.py`. It runs when the typeface changes,
which is approximately never, and it needs fonttools; the site build needs
nothing. Its output is committed.

    pip install --user fonttools brotli

WHY SUBSET AT ALL
  A full Nerv face is ~5.6 MB and 37,573 glyphs, because Iosevka draws
  essentially everything. The site uses 106 distinct characters. Shipping the
  unsubsetted faces would be a 54 MB page.

WHY THIS RANGE
  The obvious "latin subset" is wrong here, and getting it wrong fails
  silently — a missing glyph is tofu on a page nobody thought to reload. What
  the site needs beyond latin: arrows, because every claim link ends in one;
  the shell prompt ornament, because the .term blocks draw a prompt with it;
  and box drawing plus block elements, because the handbook chapters draw
  boxes with them. Those are as load-bearing as the letters.

  So the range is not hand-guessed. verify() reads the characters the built
  pages actually contain and checks them against the cmap of each font it just
  wrote, so content needing a new glyph fails the build here instead of
  shipping a hole. The list IS the check.

  The entity trap, which cost one rebuild: scanning raw file text misses every
  character written as an HTML entity. `&#10095;` is seven ASCII bytes in the
  source and U+276F on the page, and the first version of this subset dropped
  it for precisely that reason. verify() unescapes before it counts.
"""

import html
import pathlib
import re
import subprocess
import sys

# Derived from the characters present in the built site, widened to whole
# blocks where a neighbour is plainly going to be needed next.
UNICODES = ",".join([
    "U+0000-00FF",                      # basic latin + latin-1
    "U+0131", "U+0152-0153",            # dotless i, oe
    "U+02BB-02BC", "U+02C6", "U+02DA", "U+02DC",
    "U+0304", "U+0308", "U+0329",       # combining marks
    "U+2000-206F",                      # punctuation: dashes, quotes, spaces
    "U+20AC", "U+2122",                 # euro, trademark
    "U+2190-2193",                      # arrows — used by every claim link
    "U+2212", "U+2215",                 # minus, division slash
    "U+23CE",                           # return symbol
    "U+276E-276F",                      # the shell prompt in .term blocks
    "U+2500-257F",                      # box drawing — the terminal blocks
    "U+2580-259F",                      # block elements — the cursor
    "U+FEFF", "U+FFFD",
])

# Keep shaping correct and nothing else. Notably no `liga`/`calt`: Iosevka's
# programming ligatures would turn `->` in a terminal block into an arrow
# glyph, which is wrong when the point is to show literal shell text.
FEATURES = "kern,ccmp,locl,mark,mkmk,rlig"

# (family dir, iosevka face file, output name, weight, style)
FACES = [
    # Display: a wider cut of Nerv Sans, headings only. See
    # fonts/nerv-display.plan.toml. Three weights because weight has to come
    # DOWN as size goes up: 300 carries the poster and the hero, 400 the page
    # titles, 600 the section headings. Nothing large is set at 600.
    ("nerv-display",   "normallightupright",    "nerv-display-300",  "300", "normal"),
    ("nerv-display",   "normalregularupright",  "nerv-display-400",  "400", "normal"),
    ("nerv-display",   "normalsemiboldupright", "nerv-display-600",  "600", "normal"),
    ("nerv-sans",      "normalregularupright", "nerv-sans-400",      "400", "normal"),
    ("nerv-sans",      "normalboldupright",    "nerv-sans-700",      "700", "normal"),
    ("nerv-sans",      "normalregularitalic",  "nerv-sans-400i",     "400", "italic"),
    ("nerv-sans-mono", "normalregularupright", "nerv-sans-mono-400", "400", "normal"),
    ("nerv-sans-mono", "normalboldupright",    "nerv-sans-mono-700", "700", "normal"),
    ("nerv-serif",     "normalregularupright", "nerv-serif-400",     "400", "normal"),
    ("nerv-serif",     "normalboldupright",    "nerv-serif-700",     "700", "normal"),
    ("nerv-serif",     "normalregularitalic",  "nerv-serif-400i",    "400", "italic"),
]

FAMILY_NAME = {
    "nerv-display":   "Nerv Display",
    "nerv-sans":      "Nerv Sans",
    "nerv-sans-mono": "Nerv Sans Mono",
    "nerv-serif":     "Nerv Serif",
}

HERE = pathlib.Path(__file__).parent


def used_characters(root):
    """Every character the built site can put on screen."""
    chars = set()
    for f in root.rglob("*.html"):
        if ".git" in str(f) or "vendor" in str(f):
            continue
        text = f.read_text(errors="replace")
        # Script and style are not content, and their punctuation would widen
        # the subset for glyphs no reader ever sees.
        text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
        chars |= set(html.unescape(text))
    # The handbook is authored upstream and rendered here, so its prose counts.
    for f in (root / "src" / "vendor").rglob("*.md"):
        chars |= set(f.read_text(errors="replace"))
    return {c for c in chars if c not in "\r\n\t"}


def verify(outputs, root):
    """Fail if the site uses a character the fonts we just wrote do not have."""
    from fontTools.ttLib import TTFont

    need = used_characters(root)
    bad = False
    for path in outputs:
        cmap = set()
        for table in TTFont(path, lazy=True)["cmap"].tables:
            cmap |= set(table.cmap)
        missing = sorted(c for c in need if ord(c) not in cmap)
        if missing:
            bad = True
            print(f"\n  {path.name}: {len(missing)} characters used by the site "
                  f"are not in this face:")
            for c in missing:
                print(f"      U+{ord(c):04X}  {c!r}")
    if bad:
        sys.exit("\nsubset is too narrow — widen UNICODES and re-run")
    print(f"\nverified: all {len(need)} characters the site uses are present "
          f"in all {len(outputs)} faces")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip().splitlines()[2].strip())
    dist = pathlib.Path(sys.argv[1]).expanduser().resolve()

    rows = []
    for fam, face, out, weight, style in FACES:
        src = dist / fam / "TTF-Unhinted" / f"{fam}-{face}.ttf"
        if not src.is_file():
            sys.exit(f"missing: {src}")
        dest = HERE / f"{out}.woff2"
        subprocess.run([
            sys.executable, "-m", "fontTools.subset", str(src),
            f"--unicodes={UNICODES}",
            f"--layout-features={FEATURES}",
            "--flavor=woff2",
            "--no-hinting",
            "--desubroutinize",
            "--drop-tables+=DSIG",
            # Keep the family name the build plan set: the whole point of the
            # typeface is that the page and the terminal say the same word.
            "--name-IDs=1,2,3,4,5,6,16,17",
            f"--output-file={dest}",
        ], check=True)
        rows.append((out, FAMILY_NAME[fam], weight, style,
                     src.stat().st_size, dest.stat().st_size))

    verify([HERE / f"{out}.woff2" for _, _, out, _, _ in FACES], HERE.parent)

    total = 0
    print(f"\n{'file':22} {'family':16} {'wt':>4} {'style':7} {'ttf':>9} {'woff2':>9}")
    for out, fam, weight, style, a, b in rows:
        total += b
        print(f"{out + '.woff2':22} {fam:16} {weight:>4} {style:7} "
              f"{a/1e6:8.1f}M {b/1024:8.1f}K")
    print(f"{'':58} total {total/1024:8.1f}K")


if __name__ == "__main__":
    main()
