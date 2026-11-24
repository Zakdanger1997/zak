#!/usr/bin/env python3
"""Collage assets for the i.Mak presentation: paper, brush strokes, hand-drawn line, world map, round crops."""
import json
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = "/tmp/claude-0/pptwork/assets"
STORY = "/home/user/zak/imak-story-video/assets"
os.makedirs(OUT, exist_ok=True)
RED = (204, 6, 5)

# paper background 16:9
p = Image.open(f"{STORY}/paper.jpg").convert("RGB")
w, h = p.size
p.crop((0, 0, w, int(w * 9 / 16))).resize((2400, 1350), Image.LANCZOS).save(f"{OUT}/paper.jpg", quality=88)


def brush(name, W=1600, H=300, seed=1):
    rnd = random.Random(seed)
    S = 3
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    top, bot = [], []
    n = 120
    ph = [rnd.uniform(0, 6.28) for _ in range(6)]
    for i in range(n + 1):
        u = i / n
        x = (W * 0.02 + W * 0.96 * u) * S
        nt = 0.05 * math.sin(u * 7 + ph[0]) + 0.025 * math.sin(u * 23 + ph[1]) + 0.012 * math.sin(u * 61 + ph[2])
        nb = 0.05 * math.sin(u * 6 + ph[3]) + 0.025 * math.sin(u * 19 + ph[4]) + 0.012 * math.sin(u * 53 + ph[5])
        top.append((x, (H * 0.13 + nt * H) * S))
        bot.append((x, (H * 0.87 + nb * H) * S))
    pts = top + [(W * 0.995 * S, H * 0.35 * S), (W * S, H * 0.7 * S)] + bot[::-1] + [(0, H * 0.72 * S), (W * 0.01 * S, H * 0.3 * S)]
    d.polygon(pts, fill=RED + (255,))
    im = im.resize((W, H), Image.LANCZOS)
    im.save(f"{OUT}/{name}.png")


brush("brush1", seed=3)
brush("brush2", seed=7)


def loop_line(name, W=3000, H=300, loops_at=(), amp=0.03, width=7):
    """Hand-drawn red line along the middle with small loops at given x fractions."""
    S = 3
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = []
    r = H * 0.2
    cuts = sorted(loops_at)
    x = 0.0
    def base(xx):
        return H / 2 + math.sin(xx / W * 9) * H * amp
    for c in cuts + [None]:
        xe = W if c is None else c * W
        while x < xe:
            pts.append((x * S, base(x) * S)); x += 3
        if c is None:
            break
        y0 = base(x)
        for k in range(200):                     # full loop above the line, drifting forward
            th = 2 * math.pi * k / 199
            pts.append(((x + r * math.sin(th) + r * 0.35 * th / math.pi) * S, (y0 - r + r * math.cos(th)) * S))
        x += r * 0.7
    d.line(pts, fill=RED + (255,), width=width * S, joint="curve")
    im = im.resize((W, H), Image.LANCZOS)
    im.save(f"{OUT}/{name}.png")


# milestones at 1.55 + i*2.55 in on a 0.5..12.85 in line -> loops between them
xs = [1.55 + i * 2.55 for i in range(5)]
mids = [((a + b) / 2 - 0.5) / 12.35 for a, b in zip(xs, xs[1:])]
loop_line("timeline", loops_at=mids[1:3])

# world map (paper tone land), same projection as the story video
LON0, LON1, LAT0, LAT1 = -128.0, 152.0, -48.0, 72.0
W = 2800
S = W / (LON1 - LON0)
H = int((LAT1 - LAT0) * S)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
g = json.load(open("/tmp/claude-0/ne_land.geojson"))
for f in g["features"]:
    geo = f["geometry"]
    polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
    for poly in polys:
        for k, ring in enumerate(poly):
            pts = [((lon - LON0) * S, (LAT1 - lat) * S) for lon, lat in ring]
            d.polygon(pts, fill=(205, 191, 168, 255) if k == 0 else (0, 0, 0, 0))
im.save(f"{OUT}/world.png")
print("map", W, H)
