# nervlinux.org

The Nerv Linux website. Static HTML and CSS, no dependencies, served by GitHub
Pages at <https://nervlinux.org>.

## Building

Pages are assembled from `src/layout.html` and `src/pages/*.html` by a single
script with no third-party imports:

```sh
python3 build.py
```

The output goes to the repository root (`index.html`, `system/index.html`, …)
and is committed. GitHub Pages serves it directly; there is no CI build step and
no `.nojekyll` processing to wait on.

Preview locally, with rebuild-on-save and browser reload:

```sh
python3 dev.py                  # http://localhost:8000, and on the LAN
python3 dev.py 9000             # another port
python3 dev.py --local          # loopback only
python3 dev.py --host 10.0.0.5  # one interface
```

It binds every interface by default and prints the address other machines
should use, so the site can be checked from a phone or another box — the only
way to find out whether the type and the hero actually survive a small screen.
Anyone who can reach the port can read this directory, so it belongs on a
trusted network; `--local` puts it back on the loopback.

`dev.py` runs the build, watches `src/`, `css/`, `assets/` and `fonts/`, and
reloads the open tab when any of them changes. The reload script is injected as
a page is served and never written to disk, so the committed HTML is exactly
what GitHub Pages gets. Stdlib only, like `build.py`.

To serve the committed output with nothing in the way:

```sh
python3 build.py && python3 -m http.server 8000
```

## Layout

```
build.py             assembles the site; --strict refuses unresolved placeholders
dev.py               preview server: rebuild on save, reload the tab, LAN-visible
sync.py              pulls myelin.css and handbook/ from ../nerv-linux
mdrender.py          markdown -> HTML for the handbook, stdlib only
grade.sh             puts an image into the Nerv grade

src/layout.html      the shell: head, masthead, footer, theme script
src/pages/*.html     one file per page, with a metadata comment at the top
src/vendor/          copies pulled from the OS tree by sync.py, not authored here

css/palette.css      GENERATED from src/vendor/myelin.css — do not edit
css/tokens.css       design tokens: type scale, spacing, contrast corrections
css/fonts.css        self-hosted Ashinoko @font-face rules
css/site.css         components

fonts/               Ashinoko, 8 faces subsetted to WOFF2, ~113 KB
fonts/build-webfonts.py   TTF -> subsetted WOFF2, verifies glyph coverage

assets/              logo lockups and favicon
assets/shots/        screenshots, never graded
assets/photos/       photography, always graded

docs/palette.md      Myelin: the roles, the ratios, and why the site is dark first
docs/type.md         the type system and how the webfonts are built
docs/voice.md        prose, colour meaning, capitals, display sizes
docs/grade.md        the image grade, measured
docs/imagery.md      art direction, the slots, and generation prompts
```

### Adding a page

Create `src/pages/<name>.html` starting with a metadata comment:

```html
<!--
title: Platforms
desc:  One-line description, used for <title> and the meta description.
slug:  platforms
nav:   platforms
-->
```

`slug` is the output directory; omit it for the front page. `nav` marks which
top-level nav item is current. Add the page to `NAV` in `build.py` if it belongs
in the primary navigation, and to the footer list in `src/layout.html`.

- **Colour comes from the OS, not from here.** `css/palette.css` is generated
  from `src/vendor/myelin.css`, which is nerv-theme's own export of the
  Myelin palette. `css/tokens.css` maps it onto the site's semantic names and
  states no colour of its own.

## Conventions

- **Maturity claims live only on `/status/`.** Every other page describes the
  system in plain present tense. One status table beats hedging in prose.
- **Colour must pass WCAG AA** — 4.5:1 for text and 3:1 for large text. For
  non-text, the 3:1 rule (WCAG 1.4.11) binds *controls and meaningful
  graphics*, not decoration: the hairline rules that carry the layout are
  decorative and sit well under it deliberately, while anything that is the
  visible edge of a control uses `--border-interactive`, which is measured
  against the surface it actually sits on. `docs/palette.md` has the ratios and
  a snippet for checking a new value.
- **No third-party requests.** Fonts are self-hosted; there is no analytics, no
  CDN, and no tracking.
