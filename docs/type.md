# Type

The site is set in **Ashinoko**, the Nerv typeface. These are the operating
system's own letters: the same families the terminal, the console and the
desktop use. That is the one piece of brand nobody can copy, and it is worth
the trouble it costs.

## Where the typeface comes from

`nerv-fonts` builds Ashinoko from an in-tree Iosevka plan, which **is** the
design: Iosevka is parametric, so a custom typeface is entirely the selection
of variants, weights, widths and metrics recorded in that plan. Change a line,
rebuild, and the system's letters change.

Four families ship: **Ashinoko Sans**, **Ashinoko Sans Mono**, **Ashinoko
Serif**, **Ashinoko Serif Mono**. The site uses three; Serif Mono is not on the
web.

Lineage: Iosevka by Renzhi Li, by way of the Aporetic plan by Protesilaos
Stavrou. Both SIL OFL 1.1. Iosevka reserves no font name, which is why these
families may be renamed. `fonts/LICENSE-OFL.txt` ships with the webfonts
because the licence requires it.

## The roles

| role | family | where |
| --- | --- | --- |
| Display, headings | **Ashinoko Sans** | `h1`–`h3`, hero, claim headings |
| UI, nav, short copy | **Ashinoko Sans** | masthead, buttons, tiles, tables |
| Long-form reading | **Ashinoko Serif** | `.essay`, and every handbook chapter |
| Terminals, labels, data | **Ashinoko Sans Mono** | `.term`, `.crumb`, table heads, pills |

The split exists because **Ashinoko Sans is quasi-proportional and reads as a
technical face rather than a neutral one.** That is right for a headline, a
label, or three lines in a tile: it signals "this is a machine" on every glyph,
which is the brand working for free. It is wrong for six hundred words, where
the same signal becomes fatigue. So anything meant to be *read* rather than
*scanned* goes to `--font-serif`.

## The missing display cut

**Headings and body are currently the same family**, and that is a compromise,
not a design.

Ashinoko Sans is width `shape 525`. Iosevka's normal is 500 and extended is
600, so it sits just above normal, which is correct for reading at 14px and
tight at 32px, where the sidebearings can no longer separate the letters and a
heading sets nearly solid.

The site previously carried a custom wider cut at width 600, built locally for
headings only, which fixed this properly. It was retired when Ashinoko landed,
because a locally-built face under a name nobody else ships is worse than the
compromise.

**The real fix is a wider cut in `nerv-fonts`**: copy the `ashinoko-sans` plan,
change `widths.normal.shape` from 525 to 600, `menu` to 7, `css` to `expanded`,
and name it Ashinoko Display. Three weights are enough — 300 for the poster and
hero, 400 for page titles, 600 for section headings — because weight has to
come **down** as size goes up. Until then, `--tracking-tight` is positive and
headings pay for the width in spacing.

Never make that tracking negative. The site did once, inheriting `-0.02em` from
IBM Plex, a wide humanist sans; on a narrow quasi-proportional face negative
tracking is precisely what makes headings read as one block.

### An honest limit

**Ashinoko Sans and Ashinoko Serif are not a strong typographic contrast.**
They are metrically identical siblings from one parametric source, and the
serif is a slab variant; at body size the difference is a texture change, not
the contrast a reader gets from pairing two unrelated faces. Hierarchy on a
long page therefore rests on size, weight, measure and leading, with the family
change as reinforcement.

That is a consequence of the whole typeface coming from one hand, which is the
property that makes it ours. A trade worth making, knowingly.

## Metrics

Ashinoko is metrically identical to what preceded it, and close enough to IBM
Plex that the type scale in `tokens.css` needed no adjustment when the site
moved off Plex:

| | x-height | cap | adv(n) | glyphs |
| --- | --- | --- | --- | --- |
| Ashinoko (all four) | 0.520 | 0.735 | 0.525 | 37,573 mono / 48,318 proportional |
| IBM Plex Sans | 0.516 | 0.698 | 0.568 | — |

- **x-height within 0.004**, so the scale carried over untouched.
- **Caps 5% taller**, which gives headings more presence for free.
- **Set width 8% narrower.** Measure is specified in `ch`, which scales with
  the font, so `--max-w-text` is still the same character count. Absolute
  widths are what to re-check.
- **The font's own line box is ~9% tighter.** Every line-height on the site is
  an explicit multiple of font-size rather than `normal`, so nothing moved, but
  a new rule relying on `line-height: normal` will set tighter than the rest.

## Building the webfonts

`nerv-fonts` ships webfonts already, but unsubsetted: **23 MB** for the sixteen
faces, because Iosevka draws essentially everything and the site uses about a
hundred characters. So they are subsetted here.

```sh
pip install --user fonttools brotli
python3 fonts/build-webfonts.py ~/Downloads/Fonts/ttf
```

The argument is a directory of Ashinoko TrueType files named
`ashinoko-<family>-normal<weight><slope>.ttf`, as nerv-fonts ships them. Eight
faces out, **113 KB** total. Not part of `python3 build.py`: the typeface
changes approximately never, and the site build has no dependencies.

### The subset is wider than "latin", deliberately

Getting it wrong fails **silently** — a missing glyph is tofu on a page nobody
reloaded. Beyond latin the site needs arrows, because every claim link ends in
one; the shell prompt ornament `U+276F`, which the `.term` blocks draw a prompt
with; and box drawing plus block elements, which the handbook chapters draw
boxes with. Those are as load-bearing as the letters.

So the range is not hand-guessed. `verify()` reads the characters the built
pages actually contain and checks them against the cmap of every face it just
wrote, so content needing a new glyph fails the build instead of shipping a
hole.

**The entity trap**, which cost one rebuild: scanning raw file text misses every
character written as an HTML entity. `&#10095;` is seven ASCII bytes in the
source and U+276F on the page, and the first version of this subset dropped it
for exactly that reason. `verify()` unescapes before it counts.

### Ligatures are off

`--layout-features` excludes `liga` and `calt`. Iosevka's programming ligatures
would turn `->` inside a terminal block into a single arrow glyph, which is
wrong when the point of the block is to show literal shell text.
