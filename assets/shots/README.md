# Screenshots

Product photography for the landing page. These are **not** graded: a
screenshot of the system is already in the palette, because `css/palette.css`
and the running machine are generated from the same `palette.env`. Running one
through `grade.sh` would put it through the palette twice and leave it the only
image on the page that does not match the interface it is a picture of.

| file | ratio | size | what |
| --- | --- | --- | --- |
| `quake.jpg` | 16:9 | 2560×1440 | vkQuake in-game |
| `desktop.png` | 16:10 | 2880×1800 | niri, real work on screen |

Rules that make the difference between product photography and a screenshot:

- **Real output only.** Actual code, an actual `axon top`, an actual model
  loading. Never an empty window, never lorem ipsum, never a terminal showing
  `ls`.
- **Native resolution.** Capture at the panel's real pixel size and let the
  page scale it down. An upscaled screenshot is obvious and cheap-looking.
- **No desktop clutter.** No notifications, no half-open menus, no personal
  paths in a prompt if you would rather not publish them.
- **PNG, not JPEG.** Text and UI edges are exactly what JPEG handles worst.

Drop a file in, and it replaces the dashed placeholder slot in
`src/pages/index.html` automatically once the `<div class="slot">` is swapped
for the `<img>` the comment beside it shows.
