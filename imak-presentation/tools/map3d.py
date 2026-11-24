#!/usr/bin/env python3
"""Artistic 3D world map for the 'Service centres' slide (style: white extruded map, tilted, on a light tech grid).

Writes assets/map3d.png (transparent, extruded + shadow), assets/map_bg.jpg (full-slide tech background) and
assets/map3d.json: the slide box of the map image and a homography so build_deck.py can place pins on it.
Countries with partners are tinted; service/mounting countries in RAL 3020 red; Türkiye darker.
"""
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = "/tmp/claude-0/pptwork/assets/"
G = json.load(open("/tmp/claude-0/ne_countries50.geojson"))
D = json.load(open("/home/user/zak/imak-story-video/assets/dealers.json"))
ALIAS = {"USA": "United States of America", "UK": "United Kingdom", "Czech Republic": "Czechia"}
MOUNT = {"United States of America", "South Africa"}
SERVICE = {"Egypt", "Ecuador", "Morocco", "Tunisia", "United Arab Emirates"}
partner_c = {ALIAS.get(d[1].split(", ")[-1], d[1].split(", ")[-1]) for d in D["international"] if d[0] != "EGASEN"}

LON0, LON1, LAT0, LAT1 = -128.0, 152.0, -48.0, 74.0
FW = 5600                                   # flat render width (px)
S = FW / (LON1 - LON0)
FH = int((LAT1 - LAT0) * S)
flat = lambda lon, lat: ((lon - LON0) * S, (LAT1 - lat) * S)

LAND = (250, 251, 252, 255)
BORDER = (196, 206, 216, 255)
TINT = (245, 205, 201, 255)
REDC = (204, 6, 5, 255)
TR = (150, 10, 9, 255)

top = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
d = ImageDraw.Draw(top)
mask = Image.new("L", (FW, FH), 0)
dm = ImageDraw.Draw(mask)
for f in G["features"]:
    p = f["properties"]
    if p["ADMIN"] == "Antarctica":
        continue
    name = p["ADMIN"]
    col = TR if name == "Turkey" or name == "Türkiye" else REDC if name in MOUNT | SERVICE else TINT if (name in partner_c or p["NAME"] in partner_c) else LAND
    geo = f["geometry"]
    polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
    for poly in polys:
        ring = [flat(lon, lat) for lon, lat in poly[0]]
        if len(ring) < 3:
            continue
        xs, ys = np.array(ring).T
        if abs(np.dot(xs, np.roll(ys, 1)) - np.dot(ys, np.roll(xs, 1))) / 2 < 900:
            continue
        d.polygon(ring, fill=col, outline=BORDER, width=3)
        dm.polygon(ring, fill=255)

# perspective: flat (u, v) -> output, top edge narrower (tilted table-top view)
OW, OH = 5200, 2500
src = [(0, 0), (FW, 0), (FW, FH), (0, FH)]
dst = [(520, 120), (OW - 520, 120), (OW - 40, OH - 260), (40, OH - 260)]


def homography(a, b):
    A, B = [], []
    for (x, y), (u, v) in zip(a, b):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        B += [u, v]
    h = np.linalg.solve(np.array(A, float), np.array(B, float))
    return np.append(h, 1).reshape(3, 3)


Hf = homography(src, dst)                    # flat -> out
Hi = np.linalg.inv(Hf)                      # out -> flat (PIL wants this)
coef = (Hi / Hi[2, 2]).flatten()[:8]
warp = lambda im: im.transform((OW, OH), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
wtop, wmask = warp(top), warp(mask)

# extrusion + soft shadow
DEPTH = 26
img = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
sh = Image.new("L", (OW, OH), 0)
sh.paste(wmask, (18, DEPTH + 40))
sh = sh.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.33))
img.paste(Image.new("RGBA", (OW, OH), (60, 78, 98, 255)), (0, 0), sh)
for k in range(DEPTH, 0, -1):
    shade = int(176 + 30 * (1 - k / DEPTH))
    layer = Image.new("RGBA", (OW, OH), (shade - 8, shade, shade + 10, 255))
    img.paste(layer, (0, k), wmask)
img.alpha_composite(wtop)
img.save(OUT + "map3d.png")

# background: cool light gradient + dotted grid + thin HUD lines (static)
BW, BH = 2400, 1350
y = np.linspace(0, 1, BH)[:, None]
x = np.linspace(0, 1, BW)[None, :]
r = np.sqrt((x - 0.55) ** 2 + ((y - 0.45) * 0.6) ** 2)
base = np.clip(1 - r * 0.55, 0, 1)
bg = np.stack([210 + 36 * base, 219 + 31 * base, 228 + 25 * base], -1)
bgi = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8))
bd = ImageDraw.Draw(bgi, "RGBA")
for gx in range(0, BW, 48):
    for gy in range(0, BH, 48):
        bd.ellipse([gx - 1.5, gy - 1.5, gx + 1.5, gy + 1.5], fill=(150, 168, 188, 110))
bd.line([(0, 1180), (BW, 1060)], fill=(150, 168, 188, 120), width=2)
bd.line([(BW - 140, 260), (BW - 140, 1100)], fill=(150, 168, 188, 120), width=2)
for k in range(0, 840, 24):
    bd.line([(BW - 150, 260 + k), (BW - 140 - (12 if k % 120 == 0 else 5), 260 + k)], fill=(150, 168, 188, 150), width=2)
bgi.save(OUT + "map_bg.jpg", quality=90)

# placement on the slide: map image box (inches)
MX, MY, MWI = 0.25, 1.35, 12.85
MHI = MWI * OH / OW
json.dump({"box": [MX, MY, MWI, MHI], "H": Hf.tolist(), "S": S, "lon0": LON0, "lat1": LAT1, "ow": OW, "oh": OH},
          open(OUT + "map3d.json", "w"))
print("map", OW, OH, "slide box", MX, MY, MWI, round(MHI, 2))
