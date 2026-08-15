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

Preview locally:

```sh
python3 -m http.server 8000
```

## Layout

```
src/layout.html      the shell: head, masthead, footer, theme script
src/pages/*.html     one file per page, with a metadata comment at the top
css/tokens.css       design tokens — palette, type scale, spacing
css/fonts.css        self-hosted IBM Plex @font-face rules
css/site.css         components
fonts/               IBM Plex Sans (variable) + Mono, latin subset, ~74 KB
assets/              logo lockups and favicon
docs/palette.md      how the OneDark palette was adapted, with contrast ratios
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

## Conventions

- **Maturity claims live only on `/status/`.** Every other page describes the
  system in plain present tense. One status table beats hedging in prose.
- **Colour must pass WCAG AA** — 4.5:1 for text, 3:1 for borders and large text.
  `docs/palette.md` has the ratios and a snippet for checking a new value.
- **No third-party requests.** Fonts are self-hosted; there is no analytics, no
  CDN, and no tracking.
