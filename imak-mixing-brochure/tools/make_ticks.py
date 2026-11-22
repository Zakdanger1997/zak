#!/usr/bin/env python3
"""Render the fine dashed-line background pattern as flat PNGs.

The pattern used to be built with CSS masks; some PDF viewers (iOS Quick Look)
ignore the resulting soft masks and draw solid black stripes. These PNGs have the
dashes and the fade baked in as plain grey-on-white pixels, so every viewer shows
the same thing.

Usage: python3 tools/make_ticks.py      -> assets/ticks-<w>x<h>-<fade>.png
"""
import os

from PIL import Image

PX_PER_MM = 10
PITCH, LINE = 1.25, 0.32      # mm: line every 1.25 mm, 0.32 mm wide
DASH, GAP = 1.6, 1.0          # mm: vertical dash and gap
TICK = (226, 227, 229)        # #e2e3e5 at full strength
SOLID = 0.3                   # first 30 % of the fade direction at full strength

# (width mm, height mm, fade direction): fade "r" = strong on the left, fades to the right
PATTERNS = [(170, 212, "r"), (120, 112, "l"), (100, 118, "r"), (150, 110, "r")]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def strength(t):
    """t = 0 at the strong edge, 1 at the faded edge."""
    return 1.0 if t <= SOLID else max(0.0, 1 - (t - SOLID) / (1 - SOLID))


def make(w_mm, h_mm, fade):
    W, H = round(w_mm * PX_PER_MM), round(h_mm * PX_PER_MM)
    im = Image.new("L", (W, H), 255)
    px = im.load()
    pitch, line = PITCH * PX_PER_MM, LINE * PX_PER_MM
    period, dash = (DASH + GAP) * PX_PER_MM, DASH * PX_PER_MM
    grey = sum(TICK) / 3
    for x in range(W):
        cov = min(max(line - (x % pitch), 0), 1)  # anti-aliased line edge
        if cov <= 0:
            continue
        t = x / W if fade == "r" else 1 - x / W
        a = strength(t) * cov
        v = round(255 - (255 - grey) * a)
        for y in range(H):
            if (H - 1 - y) % period < dash:
                px[x, y] = v
    name = f"ticks-{w_mm}x{h_mm}-{fade}.png"
    im.save(os.path.join(OUT, name), optimize=True)
    print(name, W, "x", H)


if __name__ == "__main__":
    for p in PATTERNS:
        make(*p)
