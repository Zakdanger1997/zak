#!/usr/bin/env python3
"""Engineering-drawing gears for the cover: involute wheel (z=48) and pinion (z=20), module 4, as separate
square transparent PNGs centred on their axes (so PowerPoint can spin them), plus a static annotation layer.
Writes assets/gear_wheel.png, assets/gear_pinion.png, assets/gear_annot.png and assets/gears.json (placement)."""
import json
import math

from PIL import Image, ImageDraw, ImageFont

OUT = "/tmp/claude-0/pptwork/assets/"
DPI = 220                       # px per slide inch
M = 4.0                         # module (mm) – drawing scale: mm -> inches below
ZW, ZP = 48, 20
SCALE = 3.0 / (M * ZW / 2)      # wheel pitch radius = 3.0 in on the slide
PA = math.radians(20)
RED = (204, 6, 5)
INK = (52, 58, 66)
inv = lambda a: math.tan(a) - a
FONT = "/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf"


def outline(z, m, phase):
    r = m * z / 2; rb = r * math.cos(PA); ra = r + m; rf = r - 1.25 * m
    half = lambda R: math.pi / (2 * z) + inv(PA) - inv(math.acos(rb / max(R, rb)))
    r0 = max(rf, rb * 0.999)
    pts = []
    for k in range(z):
        c = phase + 2 * math.pi * k / z
        fl = [(r0 + (ra - r0) * i / 8) for i in range(9)]
        pts.append((rf, c - half(r0) - 0.002))
        pts += [(R, c - half(R)) for R in fl]
        pts += [(R, c + half(R)) for R in reversed(fl)]
        pts.append((rf, c + half(r0) + 0.002))
        nxt = c + 2 * math.pi / z - half(r0)
        for i in range(1, 6):
            pts.append((rf, c + half(r0) + (nxt - c - half(r0)) * i / 6))
    return [(R * math.cos(a), R * math.sin(a)) for R, a in pts], r, ra, rf


def gear_png(name, z, phase, color, fill, spokes):
    pts, r, ra, rf = outline(z, M, phase)
    s = SCALE * DPI                                   # px per mm
    half = int(ra * s) + 12
    S = 2
    im = Image.new("RGBA", (2 * half * S, 2 * half * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = half * S
    P = lambda x, y: (c + x * s * S, c - y * s * S)
    d.polygon([P(x, y) for x, y in pts], fill=fill, outline=color)
    d.line([P(x, y) for x, y in pts] + [P(*pts[0])], fill=color, width=int(4 * S), joint="curve")
    # web with lightening holes, hub, bore + keyway
    hub = r * 0.32
    if spokes:
        rin, rout = r * 0.42, rf - 2.2 * M
        for k in range(spokes):
            a0, a1 = 2 * math.pi * k / spokes + 0.16, 2 * math.pi * (k + 1) / spokes - 0.16
            arc = [P(rout * math.cos(a0 + (a1 - a0) * i / 40), rout * math.sin(a0 + (a1 - a0) * i / 40)) for i in range(41)]
            arc += [P(rin * math.cos(a1 - (a1 - a0) * i / 40), rin * math.sin(a1 - (a1 - a0) * i / 40)) for i in range(41)]
            d.polygon(arc, fill=(0, 0, 0, 0))
            d.line(arc + [arc[0]], fill=color, width=int(3 * S), joint="curve")
    bore = r * 0.16
    d.ellipse([P(-hub, hub), P(hub, -hub)], outline=color, width=int(3 * S))
    d.ellipse([P(-bore, bore), P(bore, -bore)], fill=(255, 255, 255, 255), outline=color, width=int(4 * S))
    kw = bore * 0.35
    d.rectangle([P(-kw, bore + kw * 0.9), P(kw, bore - 0.2)], fill=(255, 255, 255, 255), outline=color, width=int(3 * S))
    # dash-dot pitch circle
    n = 120
    for i in range(0, n, 2):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1.4) / n
        d.line([P(r * math.cos(a0), r * math.sin(a0)), P(r * math.cos(a1), r * math.sin(a1))], fill=color + (150,), width=int(2 * S))
    im = im.resize((2 * half, 2 * half), Image.LANCZOS)
    im.save(OUT + name)
    return 2 * half / DPI                              # image size in inches


# placement on the slide (inches): wheel centre, pinion up-left at 120 degrees
WC = (10.35, 4.75)
th = math.radians(122)                                 # direction wheel -> pinion (maths angle, y up)
a = M * (ZW + ZP) / 2 * SCALE                          # centre distance on the slide
PC = (WC[0] + a * math.cos(th), WC[1] - a * math.sin(th))
ww = gear_png("gear_wheel.png", ZW, th, RED, (204, 6, 5, 34), spokes=6)
wp = gear_png("gear_pinion.png", ZP, th + math.pi + math.pi / ZP, INK, (255, 255, 255, 235), spokes=0)

# static annotation layer: centre lines, centre-distance dimension, labels
W, H = int(13.333 * DPI), int(7.5 * DPI)
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
px = lambda x, y: (x * DPI, y * DPI)
f = ImageFont.truetype(FONT, int(0.17 * DPI))
fs = ImageFont.truetype(FONT, int(0.14 * DPI))


def dashdot(p0, p1, col=INK + (140,), w=2):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t = 0.0
    pat = [(0.35, True), (0.08, False), (0.05, True), (0.08, False)]
    k = 0
    while t < L:
        seg, on = pat[k % 4]; seg *= DPI
        if on:
            d.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * min(L, t + seg), y0 + uy * min(L, t + seg))], fill=col, width=w)
        t += seg; k += 1


for cx, cy, R in ((WC[0], WC[1], 3.3), (PC[0], PC[1], 1.55)):
    dashdot(px(cx - R, cy), px(cx + R, cy)); dashdot(px(cx, cy - R), px(cx, cy + R))
# centre line between axes + dimension with arrows, offset perpendicular
dashdot(px(*WC), px(*PC), RED + (170,))
nx, ny = math.sin(th), math.cos(th)                     # perpendicular (screen coords)
off = -0.85
A0 = (WC[0] + nx * off, WC[1] + ny * off)
A1 = (PC[0] + nx * off, PC[1] + ny * off)
d.line([px(*WC), px(WC[0] + nx * (off + 0.15), WC[1] + ny * (off + 0.15))], fill=INK + (160,), width=2)
d.line([px(*PC), px(PC[0] + nx * (off + 0.15), PC[1] + ny * (off + 0.15))], fill=INK + (160,), width=2)
d.line([px(*A0), px(*A1)], fill=INK + (200,), width=3)
ux, uy = (A1[0] - A0[0]) / a, (A1[1] - A0[1]) / a
for (bx, by), sgn in ((A0, 1), (A1, -1)):
    tip = px(bx, by)
    for s2 in (-1, 1):
        d.line([tip, (tip[0] + sgn * (ux * 0.16 - s2 * uy * 0.06) * DPI, tip[1] + sgn * (uy * 0.16 + s2 * ux * 0.06) * DPI)], fill=INK + (200,), width=3)
mx, my = (A0[0] + A1[0]) / 2, (A0[1] + A1[1]) / 2
lab = f"a = {M * (ZW + ZP) / 2:.0f}"
tw = d.textlength(lab, font=f)
d.text((mx * DPI + nx * 0.12 * DPI - tw / 2, my * DPI + ny * 0.12 * DPI), lab, font=f, fill=INK + (220,))
d.text(px(WC[0] - 2.75, WC[1] + 2.15), f"z = {ZW}   m = {M:.0f}", font=fs, fill=RED + (230,))
d.text(px(PC[0] - 1.75, PC[1] + 0.75), f"z = {ZP}", font=fs, fill=INK + (230,))
d.text(px(9.3, 0.25), f"i = {ZW / ZP:.1f}", font=fs, fill=INK + (200,))
im.save(OUT + "gear_annot.png")
json.dump({"wheel": {"c": WC, "size": ww, "period": 30.0, "dir": 1},
           "pinion": {"c": PC, "size": wp, "period": 30.0 * ZP / ZW, "dir": -1}}, open(OUT + "gears.json", "w"))
print("wheel", WC, ww, "pinion", [round(v, 2) for v in PC], wp)
