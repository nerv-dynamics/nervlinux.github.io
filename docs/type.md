# Type

The site is set in the operating system's own letters. That is the one piece of
brand nobody can copy, and it is worth the trouble it costs.

## Where the typeface comes from

`nerv-fonts` in the OS tree builds four metrically related families from
`packages/nerv-fonts/files/private-build-plans.toml`, which **is** the design:
Iosevka is parametric, so a custom typeface is entirely a matter of which
variants, weights and metrics are selected, and that selection is in-tree.
Change a line, rebuild, and the system's letters change.

Lineage: Iosevka by Renzhi Li, by way of the Aporetic plan by Protesilaos
Stavrou. Both SIL OFL 1.1. Iosevka reserves no font name, which is why these
families may be called Nerv — see the licence note in the spec, and
`fonts/LICENSE-OFL.txt`, which ships with the webfonts because OFL requires it.

The site uses three of the four, plus one cut of its own. `Nerv Serif Mono` is
not on the web.

### Nerv Display

A wider cut of Nerv Sans, headings only. One parameter differs: width `shape`
goes from 525 to 600. Iosevka's normal width is 500 and extended is 600, so the
OS plan sits just above normal, which is correct for reading at 14px and too
narrow at 40px, where the sidebearings can no longer separate the letters and a
heading sets as one block.

The plan fragment is `fonts/nerv-display.plan.toml`. It belongs upstream in
`nerv-fonts` once the width is settled, at which point the site should consume
it like the others instead of carrying its own copy.

A second thing was wrong and is worth recording, because it was doing more
damage than the width: `h1`–`h3` carried `letter-spacing: -0.02em`, and the hero
`-0.022em`. That was tuned for IBM Plex, a wide humanist sans. Negative tracking
on a narrow quasi-proportional face is what made headings look crushed together.
Headings now sit at 0 and take their width from the display cut.

## The roles

| role | family | where |
| --- | --- | --- |
| Display, headings | **Nerv Display** | `h1`–`h3`, hero, claim headings |
| UI, nav, short copy | **Nerv Sans** | masthead, buttons, tiles, tables |
| Long-form reading | **Nerv Serif** | `.essay`, and every handbook chapter |
| Terminals, labels, data | **Nerv Sans Mono** | `.term`, `.crumb`, table heads, pills |

The split exists because **Nerv Sans is quasi-proportional and reads as a
technical face rather than a neutral one.** That is exactly right for a
headline, a label, or three lines of copy in a tile — it signals "this is a
machine" on every glyph, which is the brand doing its job for free. It is
exactly wrong for a column of six hundred words, where the same signal becomes
fatigue. So anything meant to be *read* rather than *scanned* goes to
`--font-serif`.

### An honest limit

**Nerv Sans and Nerv Serif are not a strong typographic contrast.** They are
metrically identical siblings from one parametric source, and the serif is a
slab variant; at body size the difference is a texture change, not the
sans/serif contrast a reader would get from pairing two unrelated faces. The
hierarchy on a long page therefore has to be carried by size, weight, measure
and leading, with the family change as reinforcement rather than as the signal.

This is a consequence of the whole typeface coming from one hand, which is the
property that makes it ours. It is a trade worth making, but it should be made
knowingly.

## Metrics

Measured against the IBM Plex the site used before, because the type scale in
`tokens.css` was tuned for Plex and had to survive the swap:

| | x-height | cap | ascent | descent | adv(n) |
| --- | --- | --- | --- | --- | --- |
| Nerv (all three) | 0.520 | 0.735 | 0.965 | −0.215 | 0.525 |
| IBM Plex Sans | 0.516 | 0.698 | 1.025 | −0.275 | 0.568 |

- **x-height is within 0.004**, so the type scale carried over untouched. No
  size compensation was needed anywhere.
- **Caps are 5% taller**, which gives headings slightly more presence than they
  had. Welcome, and the reason the hero needed no adjustment.
- **The font's own line box is ~9% tighter.** Every line-height on the site is
  an explicit multiple of font-size rather than `normal`, so nothing moved — but
  a new rule that relies on `line-height: normal` will set tighter than the rest
  of the site, and should not.
- **Set width is 8% narrower.** Measure is specified in `ch`, which scales with
  the font, so `--max-w-text: 68ch` is still 68 characters. Absolute widths are
  the thing to re-check, not relative ones.

## Building the webfonts

Occasional, manual, and not part of `build.py` — the typeface changes
approximately never, and the site build has no dependencies.

```sh
# 1. build the TTFs from the OS tree's plan (needs node; ~5 min on 48 cores)
#    Use the ttf-unhinted:: target: webfont:: and ttf:: shell out to
#    woff2_compress and ttfautohint respectively, and abort without them.
#    nerv-display needs the plan fragment in fonts/nerv-display.plan.toml
#    appended to private-build-plans.toml first.
npm run build -- ttf-unhinted::nerv-sans ttf-unhinted::nerv-sans-mono \
                 ttf-unhinted::nerv-serif ttf-unhinted::nerv-display --jCmd=16

# 2. subset to WOFF2 and write into fonts/
pip install --user fonttools brotli
python3 fonts/build-webfonts.py /path/to/Iosevka/dist
```

Ten faces, **140 KB total**, from 68 MB of unsubsetted TTF. A full Nerv face
is 37,573 glyphs because Iosevka draws essentially everything; the site uses
106 distinct characters.

### The subset is wider than "latin", deliberately

The obvious latin subset is wrong here and it fails *silently*. What the site
needs beyond latin: arrows, because every claim link ends in one; the shell
prompt ornament `U+276F`, which the `.term` blocks draw a prompt with; and box
drawing plus block elements, which the handbook chapters draw boxes with. Those
are as load-bearing as the letters.

`build-webfonts.py` verifies coverage against the cmap of each face it writes,
so content needing a new glyph fails the build instead of shipping tofu. One
trap is worth knowing: a scan of raw file text misses every character written
as an HTML entity. `&#10095;` is seven ASCII bytes in the source and U+276F on
the page, and the first version of this subset dropped it for that reason.

The range is derived from the characters present in the built pages, widened to
whole blocks where a neighbour is obviously next. It is authoritative in
`fonts/build-webfonts.py`; the copy in `css/fonts.css` is a comment.

To re-derive it after adding content:

```sh
python3 - <<'EOF'
import pathlib, unicodedata
chars = set()
for f in pathlib.Path(".").rglob("*.html"):
    if ".git" not in str(f): chars |= set(f.read_text(errors="replace"))
for c in sorted(c for c in chars if ord(c) > 0x7e):
    print(f"U+{ord(c):04X}  {c!r:8} {unicodedata.name(c,'?')}")
EOF
```

### Ligatures are off

`--layout-features` excludes `liga` and `calt`. Iosevka's programming
ligatures would turn `->` inside a terminal block into a single arrow glyph,
which is wrong when the point of the block is to show literal shell text.
