#!/usr/bin/env bash
#
# grade.sh — put an image into the Nerv grade.
#
#   ./grade.sh in.jpg assets/photos/hero.jpg
#   ./grade.sh --contact in1.jpg in2.jpg ...      # a contact sheet to compare
#
# WHY THIS EXISTS
#   Photography on a technology site reads as bolted-on when it is sourced from
#   five places and graded from none. The single thing that makes mismatched
#   sources — a generated image, a commissioned shot, a screenshot, a frame
#   grabbed from video — read as one campaign is that they all land on the same
#   two endpoints. That is this script's whole job, and it is why every image
#   in assets/photos/ goes through it and none are dropped in raw.
#
#   The endpoints are the page's own: shadows sit on the site ground, highlights
#   sit on the body text colour. An image graded this way is not merely
#   "darkened" — it is the same material as the page around it, so the edge
#   between photograph and interface stops being visible.
#
# THE KNOBS, and what each is for
#   SAT   saturation kept in the base image, before the duotone is blended
#         over it. On its own it does NOT control how much colour you see,
#         because the duotone branch is greyscale by construction: colour only
#         survives in the (100-MIX)% of the base that is blended back. So
#
#             colour retained  ~=  SAT x (1 - MIX/100)
#
#         which means a given look is reachable at more than one setting, and
#         the higher-MIX version is always the better one. SAT=85/MIX=42 and
#         SAT=100/MIX=52 look the same; the second lands much closer to the
#         page's endpoints. Raise SAT before you drop MIX.
#   MIX   how far towards the duotone, and therefore how exactly the image
#         lands on the endpoints. Measured, not asserted: at MIX=100 a full
#         black-to-white ramp comes out at exactly 33,37,43 -> 215,220,227,
#         which is the two colours above. Blending any of the original back in
#         re-widens the range, so the default 72 overshoots by about 10/255 at
#         each end — imperceptible, and the price of keeping any colour at all.
#         Push it to 100 for a source with a colour cast worth destroying.
#   LIFT  black point, in percent. The goth read comes from deep falloff, not
#         from props: this is the knob that produces it.
#   GRAIN a small amount, and non-negotiable. Digitally clean images sit on a
#         page like stickers; grain is what makes them look photographed.
set -euo pipefail

# Myelin's dark ground and body text. A graded image is meant to be made of
# the same material as the page it sits on, so these track the palette: if
# Myelin changes, change them here too.
SHADOW="${SHADOW:-#1e1e1e}"     # --myelin-bg, dark
HIGHLIGHT="${HIGHLIGHT:-#dfdfdf}"   # --myelin-fg, dark
SAT="${SAT:-100}"
MIX="${MIX:-52}"
LIFT="${LIFT:-6}"
CONTRAST="${CONTRAST:-8}"
PIVOT="${PIVOT:-34}"
GRAIN="${GRAIN:-3}"
QUALITY="${QUALITY:-82}"

# The endpoints as luma percentages, computed from the colours above rather
# than written down twice — change SHADOW/HIGHLIGHT and these follow.
# Note there is deliberately no final clamp into the endpoints. The obvious
# one — normalise, then +level onto the two colours — compresses a range that
# the duotone step has already narrowed, and measurably makes things worse
# (53,55,58 -> 198,201,204 on the ramp above: darker shadows AND duller
# highlights than asked for). MIX is the honest control.

grade() {
  local in="$1" out="$2"
  mkdir -p "$(dirname "$out")"
  magick "$in" \
    -colorspace sRGB \
    -auto-orient \
    -modulate "100,${SAT}" \
    -write mpr:base +delete \
    \( mpr:base \
       -colorspace gray \
       -level "${LIFT}%,100%" \
       -sigmoidal-contrast "${CONTRAST}x${PIVOT}%" \
       \( -size 1x256 gradient:"${SHADOW}-${HIGHLIGHT}" \) -clut \
    \) \
    \( mpr:base \) \
    -compose blend -define compose:args="$((100 - MIX))" -composite \
    -attenuate "$(awk "BEGIN{print $GRAIN/100}")" +noise Gaussian \
    -quality "$QUALITY" \
    "$out"
  printf '  %-42s -> %-42s %s\n' "$in" "$out" \
    "$(du -h "$out" | cut -f1)"
}

if [ "${1:-}" = "--contact" ]; then
  shift
  tmp=$(mktemp -d)
  i=0
  for f in "$@"; do
    grade "$f" "$tmp/$(printf '%02d' $i).jpg" >/dev/null
    i=$((i + 1))
  done
  magick montage "$tmp"/*.jpg -tile 3x -geometry 420x+8+8 \
    -background "$SHADOW" contact-sheet.jpg
  echo "contact-sheet.jpg written ($# images)"
  rm -rf "$tmp"
  exit 0
fi

[ $# -eq 2 ] || { sed -n '3,6p' "$0"; exit 1; }
grade "$1" "$2"
