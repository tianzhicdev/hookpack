#!/usr/bin/env python3
"""Emit the 1200x630 social share card (A c44, B c21 pattern ported).

B's railsite ships an og:image built by the generator; my Pages carried
`twitter:card=summary` and NO og:image for 13+ cycles — the last social-meta
gap on my lane (my own c30/c37 candidate, demand = quiet cycle, no churn
elsewhere). Deterministic by construction: fixed fonts (DejaVu), fixed
palette, no timestamps, no dataset values — regenerating must produce
BYTE-IDENTICAL bytes (CI pins that).

Layout lesson taken from B c21 the hard way (their vision-QA caught two
eyeballed collisions): clearance is MEASURED with font.getlength and
ASSERTED at build time, never eyeballed. This build asserts all three
sharing rules: headline vs tile (same y-band), body vs tile (same y-band),
and the bottom-right URL footer vs the tile above it.

Palette mirrors index.html CSS vars (bg #0d1117, card #161b22, border
#30363d, acc #7ee787, dim #8b949e, fg #e6edf3) so the share card IS the site.

Run from the repo root: python3 scripts/build-og-image.py  -> og-image.png
Requires Pillow (hard dependency: a missing card is a FAIL, never a skip).
"""
import sys
from pathlib import Path

OG_IMAGE_NAME = "og-image.png"
SITE_URL = "https://tianzhicdev.github.io/hookpack/"

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    # Fail loud, never skip: the page WILL carry og:image, so a card that
    # silently fails to build is a 404 the moment someone shares the link.
    print("FAIL: Pillow is required to build og-image.png (no-skip policy)")
    sys.exit(2)


def font(path, size):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/" + path, size)


def main():
    root = Path(__file__).resolve().parent.parent
    W, H = 1200, 630
    BG, CARD, BORDER, FG, DIM, ACC = (
        "#0d1117", "#161b22", "#30363d", "#e6edf3", "#8b949e", "#7ee787")
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_big = font("DejaVuSans-Bold.ttf", 60)
    f_mid = font("DejaVuSans.ttf", 30)
    f_sml = font("DejaVuSans.ttf", 26)

    # right column: hook glyph (favicon motif, enlarged), vertically
    # centered against the text block (vision-QA c44: a top-right tile left
    # the bottom-right quadrant dead).
    gx, gy, TS = 880, 150, 240

    # left column: headline — measured clearance vs the tile (B c21 lesson)
    headline = ("Your hooks.", "Managed markers.", "Never clobbered.")
    hx, hy = 72, 96
    for line in headline:
        assert hx + f_big.getlength(line) <= gx - 12, \
            f"og-image headline '{line}' collides with the glyph tile"
    d.multiline_text((hx, hy), "\n".join(headline), font=f_big, fill=FG,
                     spacing=14)

    body = ("A zero-dependency git hooks manager in one",
            "Python file. Dispatchers carry managed markers,",
            "so hookpack never touches hooks it did not",
            "create. Install once, forget it works.")
    by0, leading = 392, 42
    assert by0 + leading * (len(body) - 1) + 34 <= H - 40, \
        "body block overruns the bottom margin"
    for i, line in enumerate(body):
        y = by0 + leading * i
        # tile spans gx..gx+TS vertically at gy..gy+TS; any body line that
        # shares that y-band must clear the tile's left edge
        if y < gy + TS:
            assert hx + f_mid.getlength(line) <= gx - 12, \
                f"og-image body line '{line}' collides with the glyph tile"
        else:
            assert hx + f_mid.getlength(line) <= W - 72, \
                f"og-image body line '{line}' overruns the right margin"
        d.text((hx, y), line, font=f_mid, fill=DIM)

    # footer: site URL, bottom-right (fills the quadrant the tile vacates)
    uw = f_sml.getlength(SITE_URL)
    ux = W - 72 - uw
    uy = H - 52
    body_bottom = by0 + leading * (len(body) - 1) + 34
    assert uy >= body_bottom, "footer URL collides with the body block"
    assert uy >= gy + TS + 12 or ux >= gx + TS, \
        "footer URL collides with the glyph tile"
    d.text((ux, uy), SITE_URL, font=f_sml, fill=ACC)

    # glyph: rounded tile + hook (same shape family as the data-URI
    # favicon: stem down, J-bend at the bottom, plain short tail at the
    # left end, ONE fletch chevron at the top — vision-QA c44: two arrow
    # heads read as a U-turn/swap symbol, not a hook).
    d.rounded_rectangle((gx, gy, gx + TS, gy + TS), radius=24,
                        fill=CARD, outline=BORDER, width=2)
    cx, top, bend_cy, rad = gx + 150, gy + 52, gy + 150, 44
    d.line((cx, top, cx, bend_cy), fill=ACC, width=10)          # stem
    d.arc((cx - 2 * rad, bend_cy - rad, cx, bend_cy + rad),
          0, 180, fill=ACC, width=10)                            # J-bend
    # tail length matches the favicon ratio (6/64 -> 22/240); vision-QA
    # c44: a long up-leg re-reads the glyph as a two-prong U-turn.
    d.line((cx - 2 * rad, bend_cy, cx - 2 * rad, bend_cy - 22),
           fill=ACC, width=10)                                   # plain tail
    d.line((cx, top, cx - 15, top + 15), fill=ACC, width=10)     # one fletch
    d.line((cx, top, cx + 15, top + 15), fill=ACC, width=10)

    out = root / OG_IMAGE_NAME
    img.save(out, "PNG", optimize=True)
    print(f"OK: wrote {out.name} ({out.stat().st_size} bytes, "
          f"{W}x{H}, deterministic)")


if __name__ == "__main__":
    main()
