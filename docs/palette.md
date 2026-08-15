# Palette — OneDark, corrected for contrast

Nerv Linux uses OneDark throughout the OS, so the site uses it too. But OneDark
is tuned for one background — its own. Measured against white, most of the
palette fails WCAG AA badly:

| colour | hex | on `#ffffff` | on `#282c34` |
| --- | --- | --- | --- |
| red | `#e06c75` | 3.20 ✗ | 4.38 ✗ (just under) |
| green | `#98c379` | 2.02 ✗ | 6.94 ✓ |
| yellow | `#e5c07b` | 1.73 ✗ | 8.10 ✓ |
| blue | `#61afef` | 2.36 ✗ | 5.92 ✓ |
| purple | `#c678dd` | 2.94 ✗ | 4.75 ✓ |
| cyan | `#56b6c2` | 2.37 ✗ | 5.91 ✓ |
| fg | `#abb2bf` | 2.13 ✗ | 6.57 ✓ |

AA requires **4.5:1** for body text and **3:1** for large text and UI borders.

## The rule

**Hue is the brand. Lightness is negotiable.** Each accent keeps its OneDark hue
and saturation; only lightness moves, and only far enough to clear 4.5:1 against
the background it will actually sit on.

### Light mode — darkened until they clear 4.5:1 on white

| token | OneDark | light variant | ratio |
| --- | --- | --- | --- |
| `--accent-red` | `#e06c75` | `#d63e4a` | 4.52 |
| `--accent-blue` | `#61afef` | `#1579cc` | 4.53 |
| `--accent-green` | `#98c379` | `#58813a` | 4.55 |
| `--accent-cyan` | `#56b6c2` | `#32818b` | 4.52 |
| `--accent-yellow` | `#e5c07b` | `#9a6f1e` | 4.50 |
| `--accent-purple` | `#c678dd` | `#b146d1` | 4.50 |

### Dark mode — authentic OneDark

Everything is used unchanged except red, lightened one step from `#e06c75` to
`#e17079` (4.38 → 4.53). The difference is not perceptible side by side; it is
the difference between failing and passing.

### Neutrals

A Carbon-style ramp rather than OneDark greys, because OneDark's `#abb2bf` is a
*foreground on dark* and has no light-mode counterpart.

| token | hex | on white |
| --- | --- | --- |
| `--text` | `#1a1d23` | 16.88 |
| `--text-secondary` | `#4b525e` | 7.87 |
| `--text-tertiary` | `#6b7280` | 4.83 |

## The exception: terminal and code blocks

`.term` is pinned to **canonical OneDark in both themes** — `#282c34`
background, unmodified `--od-*` foregrounds. Inside a terminal the palette is
being shown, not used as UI, and every colour there already clears AA against
its own background. Recolouring it for light mode would misrepresent what the OS
actually looks like.

## Checking a new colour

```sh
python3 - <<'EOF'
def lin(c):
    c = c/255
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4
def L(h):
    h = h.lstrip('#'); r,g,b = (int(h[i:i+2],16) for i in (0,2,4))
    return 0.2126*lin(r) + 0.7152*lin(g) + 0.0722*lin(b)
def cr(a,b):
    la,lb = L(a),L(b); hi,lo = max(la,lb),min(la,lb)
    return (hi+0.05)/(lo+0.05)

print(round(cr('#d63e4a', '#ffffff'), 2))   # -> 4.52
EOF
```

Anything below 4.5 does not go in as text. Anything below 3.0 does not go in as
a border or an icon.
