# The grade

The mechanism behind `./grade.sh`. For what to point a camera at, see
[`imagery.md`](imagery.md).

## What it is for

Every image on the site is mapped onto the same two endpoints: shadows land on
`--bg` (`#21252b`, the page ground) and highlights land on `--text`
(`#d7dce3`). An image graded this way is not merely darkened — it is made of
the same material as the page around it, so the edge between photograph and
interface stops being visible, and a set of pictures from unrelated sources
reads as one campaign.

## The pipeline

```
sRGB, auto-orient
  └─ -modulate 100,SAT          desaturate, keeping SAT% of the original
     ├─ branch A: duotone
     │    -colorspace gray      collapse to luminance
     │    -level LIFT%,100%     set the black point
     │    -sigmoidal-contrast   the S-curve: this is what produces falloff
     │    -clut gradient        map luminance onto SHADOW..HIGHLIGHT
     └─ branch B: the desaturated original
  └─ -compose blend MIX         A over B, MIX% of the way to the duotone
  └─ +noise Gaussian            GRAIN
```

## The knobs

| | default | what it does |
| --- | --- | --- |
| `SAT` | 100 | Saturation kept in the base image, before the duotone is blended over it. |
| `MIX` | 52 | How far toward the duotone. Sets both colour and endpoint accuracy. |
| `LIFT` | 6 | Black point, in percent. |
| `CONTRAST` | 8 | Sigmoidal contrast. The knob that produces deep falloff. |
| `PIVOT` | 34 | Where the S-curve pivots. Below 50 sends more of the frame dark. |
| `GRAIN` | 3 | Small and non-negotiable — clean images sit on a page like stickers. |

### SAT and MIX are not independent

The duotone branch is greyscale by construction, so colour survives only in the
`(100-MIX)%` of the base image blended back over it:

```
colour retained  ~=  SAT x (1 - MIX/100)
```

Two consequences. First, raising `SAT` alone does almost nothing at a high
`MIX`. Second, and more useful: a given look is reachable at more than one
setting, and the higher-`MIX` version is always better, because `MIX` is also
what holds the endpoints. `SAT=85 / MIX=42` and `SAT=100 / MIX=52` are
visually identical on the same frame, and the second lands blacks at 17
instead of 13.

**Raise `SAT` before you drop `MIX`.**

**The defaults are still provisional.** They were first set against
ImageMagick's `rose:` test image, which verified the mechanism and nothing
about the look, and then moved to the values above against a real placeholder
portrait. That frame is nearly monochrome to begin with, a grey seamless
backdrop and a black hoodie, so `SAT` there is almost entirely controlling
skin tone. Material with actual colour in it, wardrobe, a room, hardware, will
read far more saturated at the same number. Expect to set these again from the
real shoot, and use `--contact` to compare candidates in the grade.

## What MIX actually controls, measured

`MIX` trades colour retention against landing exactly on the endpoints. On a
full black-to-white ramp:

| MIX | shadow out | highlight out |
| --- | --- | --- |
| 42 | `13,15,18` | `238,240,243` |
| **52 (default)** | `17,19,22` | `234,236,240` |
| 62 | `20,22,26` | `230,233,237` |
| 80 | `26,29,34` | `223,227,232` |
| 100 | **`33,37,43`** | **`215,220,227`** |
| target | `33,37,43` = `#21252b` | `215,220,227` = `#d7dce3` |

The default no longer lands on the endpoints, and that is a deliberate trade:
a hero photograph that bleeds off the page edge can afford deeper blacks, and
the colour is worth more than the last few levels of endpoint accuracy. An
image sitting inline in the page flow, where the seam is visible on all four
sides, should be graded at a higher `MIX`.

At `MIX=100` the endpoints are exact, because the image is nothing but the
duotone, and there is no colour left at all. Push to 100 for a source with a
colour cast worth destroying, or for an image that has to sit inline without a
visible seam.

### The clamp that was tried and removed

The obvious way to guarantee the endpoints is to normalise the blend and then
`+level` it onto the two colours. It makes things measurably worse, because it
compresses a range the duotone step has already narrowed:

| | shadow out | highlight out |
| --- | --- | --- |
| with the clamp | `53,55,58` | `198,201,204` |
| without | `23,26,30` | `226,229,234` |

Darker shadows *and* duller highlights than asked for. `MIX` is the honest
control, and there is deliberately no clamp in the script.

## What is not graded

Screenshots. A screenshot of the system is already in the palette, because the
system is the palette — `css/palette.css` and the running machine's colours are
generated from the same Myelin export. Grading a screenshot would put it
*through* the palette twice and leave it the only image on the page that does
not match the interface it is a picture of.
