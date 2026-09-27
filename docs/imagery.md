# Imagery

How pictures get onto this site, and why they all look like they came from one
place. Read with [`grade.md`](grade.md), which is the mechanism.

## The one rule

**Every image goes through `./grade.sh`. Nothing is dropped in raw.**

Photography on a technology site reads as bolted-on when it is sourced from
five places and graded from none. What makes a generated image, a commissioned
photograph, a screenshot and a frame pulled from video read as one campaign is
not that they were shot together — it is that they all land on the same two
endpoints, which are the page's own background and body-text colours. The grade
is the campaign.

A corollary that matters when generating or commissioning: **do not ask for the
look.** Ask for good, neutral, hard-lit source material with a full tonal range
and let the grade do the colour work. An image that arrives already blue-black
and crushed cannot be graded — it can only be graded *again*, and it will sit
half a stop off from everything else forever.

## Art direction

The goth read comes from contrast, wardrobe and negative space. It does not
come from props, and it does not come from a colour filter.

| | |
| --- | --- |
| **Light shape** | One hard source, high and to one side, 45–60° off axis. Hard means small and undiffused: a bare bulb, a fresnel, a bounce through nothing, or direct sun through a window. No softbox wash, no ring light, no practical LEDs in frame. |
| **Exposure** | **Flat. Not contrasty.** See *Shooting for the grade* below; this is the one instruction that gets read backwards. |
| **Framing** | The hardware is in every frame, and the person is *doing something* — hands on keys, carrying the box, holding a cable, reading a wall of output. Tight or wide, never mid. |
| **Gaze** | Nobody looks at the camera. Nobody smiles at the camera. The subject is attending to the machine, and the viewer is a bystander. |
| **Wardrobe** | Black. Matte fabric, sharp silhouette, silver hardware. Visible tattoos and piercings are welcome; costume is not. These are people who work here, not people at a club. |
| **Set** | A real room — a desk with cable mess, a rack, a workshop bench. Not a white studio, not a glass-walled office, not a server room with blue LED strips. |
| **Screens** | Real output. Actual code, an actual `axon top`, an actual model loading. Never lorem ipsum, never a fake dashboard, never a glowing wireframe globe. |

### What will make it look like stock

The tells, in order of how badly each one hurts:

1. Someone looking at the camera and smiling.
2. A screen showing something that is not real software.
3. Soft, even, shadowless light.
4. A white or glass office.
5. More than two people in frame.
6. Anyone pointing at a monitor.

## Shooting for the grade

The single most common way to waste a shoot for this site is to shoot the look
you want instead of the material the grade needs. Those are different, and the
difference is measurable.

**Hard light, flat capture.** Two separate controls that get collapsed into
one:

- **Light shape is a lighting decision and you must get it right in camera.**
  Hard, directional light gives defined shadow edges, specular hits on
  aluminium, and modelling on a face. Soft diffuse light gives none of that,
  and no grade invents shape that was never lit. This is unrecoverable in the
  other direction.
- **Tonal contrast is a grading decision, so do not bake it in.** Expose to
  keep detail at both ends. The grade's job is to crush the shadows onto
  `#1e1e1e` and roll the highlights to `#dfdfdf`. Give it range to work with.

Measured, with the actual `grade.sh`, on one scene captured two ways and then
graded identically. Standard deviation in the bottom tonal quartile, which is
where the grade does its work:

| capture | shadow detail after grading | shadow mean |
| --- | --- | --- |
| flat, nothing clipped | **sd 12.45** | 43.6 |
| contrasty, shadows clipped in camera | sd 0.60 | 27.1 |

A **twentyfold** loss of shadow detail, and the crushed version lands at 27
rather than the intended 36, so it reads as a hole punched in the page rather
than as part of its surface. You can always crush later. You can never
un-crush.

### Practical settings

- **Shoot RAW.** The grade runs on 8-bit output, so hand it a 14-bit file
  developed to a deliberately flat 8-bit with the shadows intact.
- **Expose for the specular highlights.** On a dark set the highlights on the
  hardware are the only bright thing in frame and they carry the read. Clip
  them and there is nothing to roll off.
- **Keep a whisper of fill.** Not a fill light as such: a white wall or a
  bounce card well back is enough to keep noise out of the shadows. A lighting
  ratio that *looks* like 16:1 while still recording shadow detail is the
  target.
- **One colour temperature.** The grade desaturates to 40% and maps onto two
  endpoints. Mixed white balance survives that as muddy patches, and no single
  grade fixes a frame lit by a tungsten lamp and a daylight window at once.
  Gel everything to match or turn the other lights off.
- **Do not apply a look in camera.** No picture styles, no contrast presets,
  no in-camera monochrome.

If the flat file looks disappointing on the back of the camera, that is the
correct outcome. It is supposed to look like unexposed material until
`grade.sh` runs.

## The slots

Aspect ratios are fixed because the layouts are built against them. Generate at
or above the pixel size given; the grade script does not resize.

| slot | ratio | size | what it is |
| --- | --- | --- | --- |
| `hero.jpg` | 3:2 | 2100×1400 | Front page, right-hand panel of the hero. **See the masking constraint below.** |
| `who-1.jpg` | 3:2 | 1600×1066 | About page. A person and the machine, working. |
| `who-2.jpg` | 3:2 | 1600×1066 | About page, second frame. Different person, different distance. |
| `accent-1.jpg` | 4:5 | 1000×1250 | Portrait crop, used beside a claim. Hands and hardware, face partial or absent. |
| `accent-2.jpg` | 4:5 | 1000×1250 | As above. |
| `desktop.png` | 16:9 | 2560×1440 | **A screenshot, not a photograph.** niri, at native resolution, doing real work. |
| `quake.png` | 16:9 | 2560×1440 | **A screenshot.** vkQuake running, with the readout visible. |

The last two are not generated and not graded — a screenshot of the system is
already in the palette, because the system *is* the palette. That is the whole
point of generating `css/palette.css` from Myelin.

### The hero panel is masked, which constrains the composition

The hero photo fills the right **60%** of the hero at full height, and its
left edge is masked away so it dissolves into the grey gradient instead of
sitting in a box. The panel is roughly 1.2:1 at 1440px and wider than that on
a big monitor, which is why the source is landscape: an earlier version of
this slot was a tall narrow panel, and a full-height narrow frame forces a
vertical composition, which is the hardest kind to shoot well.

Consequences for whoever shoots or generates it:

- **Nothing load-bearing in the left third.** That part of the frame is
  progressively transparent and simply is not there. A face or a hand placed
  in it disappears.
- **Right-weighted composition.** The subject belongs in the right half. The
  left side should be falling into shadow anyway, which is what the art
  direction asks for regardless, so this costs nothing.
- **Cropped with `object-fit: cover`**, so the frame is trimmed top and bottom
  on a short viewport and at the sides on a wide one. Keep the subject away
  from all four edges.

The mask ramp was positioned by measurement rather than by even percentages:
against a checkerboard in this panel, alpha below roughly 0.2 is invisible on
this gradient, so a mask that spends its first third down there wastes it and
the photo reads as a narrow strip however wide the panel is.

Below 900px the panel is hidden entirely and the gradient carries the hero
alone, so this image is never the only thing communicating something.

## Generation prompts

Paste as-is. They are written to produce gradeable source: hard light, full
tonal range, no colour styling. Add "photographic, 35mm, shallow depth of
field, natural film grain" to any of them if the model is producing something
that looks illustrated.

**`hero.jpg` — 3:2 landscape, right-weighted**

> A cinematic editorial photograph of a woman in her late twenties in a black
> high-necked top, short black hair, silver ear jewellery, seated at a desk in
> a dark workshop, both hands on a mechanical keyboard, looking at a monitor
> out of frame. A small matte-black desktop computer sits beside her with
> cables running out of it. She occupies the right half of the frame; the left
> third is empty shadow with nothing in it. One hard light source from the
> upper right, deep falloff, neutral white balance, no colour grading, full
> tonal range. Shot on 35mm, f/2, natural grain. Documentary, not staged.

**`who-1.jpg` — 3:2**

> An editorial photograph of a tall man in his thirties, black clothing, long
> dark hair tied back, silver ear jewellery, standing at a workshop bench and
> lifting a small matte-black desktop computer with both hands. Industrial
> room, concrete and steel, cable reels and tools on the bench behind him. He
> is looking down at the machine, not at the camera. Single hard light from
> above and behind, deep shadows, neutral white balance, no colour grading.
> 35mm, f/2.8, natural grain.

**`who-2.jpg` — 3:2**

> An editorial photograph of two people working at a rack in a dim machine
> room, seen from behind and to one side. One kneels connecting a cable; the
> other stands holding a laptop open, reading. Both in black. Faces mostly
> hidden. The only light is one hard overhead source and the glow of a single
> monitor. Neutral white balance, no colour grading, full tonal range. 35mm,
> f/2, natural grain.

**`accent-1.jpg` — 4:5**

> A tight photograph of a pair of hands with black-painted nails and a silver
> ring typing on a mechanical keyboard, forearms showing dark tattoos, shot
> from above and slightly to the side. The rest of the frame is a dark desk
> with a cable and a coffee cup. One hard light source, everything else falls
> to black. Neutral white balance, no colour grading. 50mm, f/2, natural grain.

**`accent-2.jpg` — 4:5**

> A vertical photograph of a woman's profile in near-darkness, lit only from
> one side by the light of a monitor off-frame, black clothing, septum ring,
> looking intently at something below the frame. Most of the image is black.
> Neutral white balance, no colour grading, full tonal range. 85mm, f/1.8,
> natural grain.

## Workflow

```sh
# 1. generate or shoot. put the raw files anywhere; they are not committed.
# 2. compare candidates in the grade, before choosing:
./grade.sh --contact ~/raw/*.jpg          # writes contact-sheet.jpg

# 3. grade the ones you kept, into the repository:
./grade.sh ~/raw/hero-07.jpg assets/photos/hero.jpg

# 4. the defaults are provisional. They were set against a stock test image,
#    not against real material, so expect to move SAT and CONTRAST once the
#    first real frames exist:
SAT=50 CONTRAST=7 ./grade.sh ~/raw/hero-07.jpg assets/photos/hero.jpg
```

Raw sources are **not** committed. The graded result is the asset; the raw file
is a negative, and it lives wherever you keep negatives.

## Licence and provenance

Whatever the source, the obligation is the same: the site must be able to say
where a picture came from.

- **Generated** — fine, and the best option for control while there is nothing
  to photograph. Treat it as illustration. Do not caption it as if it were a
  photograph of this team or this hardware.
- **Commissioned** — the only way to get the actual machine in frame, and worth
  it once there is a machine worth photographing. Get a model release covering
  commercial use, because that is what a website is.
- **Stock** — heavily graded, and check the release. Free-stock coverage is
  thinnest exactly where this direction needs it: recognisable faces used
  commercially.

Record the origin of each file in `assets/photos/SOURCES.md` as it lands. A
picture nobody can account for is the one that has to come down later.
