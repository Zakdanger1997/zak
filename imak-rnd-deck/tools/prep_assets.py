#!/usr/bin/env python3
"""Assets for the technical restyle of 'Ar-Ge Departmanı Genel Eğitim Sunumu' (13.333 x 7.5 in, 1920x1080 px plates).

blueprint.png      light blueprint grid for the slide master
div_XX.png         dark industrial section dividers (grid + grayscale photo + corner marks), XX = 01..10, plus title/end
cutaway.png        IRK cutaway, background removed (anatomy slide)
gear_light.png     involute gear pair drawing (m=4, z=20/48) for the gear-geometry slide
Usage: python3 tools/prep_assets.py
"""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
W, H = 1920, 1080
HF = "/tmp/claude-0/hf/"
UNITS = "/home/user/zak/imak-anuga-video/assets/units/"
PW = "/tmp/claude-0/pptwork/assets/"


def grid(base, minor, major, step=24, big=120):
    im = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(im)
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=major if x % big == 0 else minor, width=1)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=major if y % big == 0 else minor, width=1)
    return im


def corners(im, col, m=34, L=46, w=3):
    d = ImageDraw.Draw(im)
    for x, y, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line([(x, y), (x + sx * L, y)], fill=col, width=w); d.line([(x, y), (x, y + sy * L)], fill=col, width=w)


# light blueprint for the master: very soft so the existing content stays readable
bp = grid((250, 251, 253), (238, 242, 246), (226, 233, 240))
corners(bp, (200, 30, 30), m=18, L=30, w=2)
bp.save(os.path.join(OUT, "blueprint.png"))


def dark_base():
    im = grid((18, 20, 22), (27, 31, 35), (36, 42, 48))
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-400, -300, W + 400, H + 300], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(220))
    im = Image.composite(im, Image.new("RGB", (W, H), (8, 9, 10)), v)
    return im


def gray(im, contrast=1.25, bright=0.85):
    g = ImageOps.grayscale(im.convert("RGB"))
    a = np.asarray(g).astype(np.float32)
    a = np.clip((a - 128) * contrast + 128, 0, 255) * bright
    return Image.fromarray(a.astype(np.uint8)).convert("RGB")


def photo_plate(src, name, x0=760):
    im = dark_base()
    p = Image.open(src).convert("RGB")
    k = max((W - x0 + 200) / p.width, H / p.height)
    p = p.resize((int(p.width * k), int(p.height * k)), Image.LANCZOS)
    p = gray(p).crop((p.width - (W - x0 + 200), (p.height - H) // 2, p.width, (p.height - H) // 2 + H))
    m = Image.new("L", p.size, 0)
    a = np.zeros((p.height, p.width), np.float32)
    ramp = np.clip(np.arange(p.width) / 420.0, 0, 1)
    a[:] = ramp
    m = Image.fromarray((a * 255).astype(np.uint8))
    im.paste(p, (x0 - 200, 0), m)
    finish(im, name)


def cutout_plate(src, name, box=(900, 120, 1850, 980), gray_it=True):
    im = dark_base().convert("RGBA")
    c = Image.open(src).convert("RGBA")
    c = c.crop(c.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
    k = min((box[2] - box[0]) / c.width, (box[3] - box[1]) / c.height)
    c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
    if gray_it:
        g = gray(c, 1.15, 0.95).convert("RGBA"); g.putalpha(c.getchannel("A")); c = g
    sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); sh.putalpha(c.getchannel("A").point(lambda v: int(v * .6)))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    x = box[0] + (box[2] - box[0] - c.width) // 2; y = box[1] + (box[3] - box[1] - c.height) // 2
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow); gd.ellipse([x - 60, y + c.height * .55, x + c.width + 60, y + c.height + 80], fill=(200, 20, 20, 90))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(60)))
    im.alpha_composite(sh, (x + 10, y + 30)); im.alpha_composite(c, (x, y))
    finish(im.convert("RGB"), name)


def finish(im, name):
    d = ImageDraw.Draw(im)
    corners(im, (230, 230, 230))
    d.line([(96, 980), (700, 980)], fill=(60, 66, 72), width=2)               # title-block rule
    for i in range(13):                                                      # scale ticks
        x = 96 + i * 50; d.line([(x, 980), (x, 968 if i % 2 == 0 else 974)], fill=(90, 96, 102), width=2)
    im.save(os.path.join(OUT, name))


cut = Image.open(HF + "5a5d9063-18b5-4d6a-9ca4-0a990c5f462c.jpg").convert("RGB")
if not os.path.exists(os.path.join(OUT, "cutaway.png")):
    from rembg import remove, new_session
    remove(cut, session=new_session("isnet-general-use"), post_process_mask=True).save(os.path.join(OUT, "cutaway.png"))
cutaway = os.path.join(OUT, "cutaway.png")

# gear drawing, light (original) and white-line version
G = json.load(open(PW + "gears.json")); DPI = 1920 / 13.333
def gears(white):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for k in ("wheel", "pinion"):
        g = Image.open(PW + f"gear_{k}.png").convert("RGBA"); s = int(G[k]["size"] * DPI); g = g.resize((s, s), Image.LANCZOS)
        im.alpha_composite(g, (int(G[k]["c"][0] * DPI - s / 2), int(G[k]["c"][1] * DPI - s / 2)))
    im.alpha_composite(Image.open(PW + "gear_annot.png").convert("RGBA").resize((W, H), Image.LANCZOS))
    if white:
        a = np.asarray(im).astype(np.float32)
        ink = (a[..., 0] < 120) & (a[..., 3] > 0)
        light = (a[..., 0] > 200) & (a[..., 1] > 200) & (a[..., 2] > 200)
        a[light, 3] *= 0.08                                # white gear fill -> barely visible on dark
        a[ink, :3] = 235
        im = Image.fromarray(a.astype(np.uint8))
    return im
gl = gears(False); gl.crop(gl.getbbox()).save(os.path.join(OUT, "gear_light.png"))
gw = gears(True)

title = dark_base().convert("RGBA"); title.alpha_composite(gw, (60, 0)); finish(title.convert("RGB"), "div_title.png")
plates = [("01", "cutout", UNITS + "industrial.png"), ("02", "cutout", cutaway), ("03", "gear", None), ("04", "photo", PW + "div_products.jpg"),
          ("05", "cutout", UNITS + "irc_a.png"), ("06", "photo", PW + "div_thanks.jpg"), ("07", "cutout", UNITS + "bevel_helical_b.png"),
          ("08", "cutout", os.path.join(OUT, "hx.png")), ("09", "photo", PW + "div_apps.jpg"), ("10", "cutout", "/tmp/claude-0/ig/en_groups.png")]
for n, kind, src in plates:
    name = f"div_{n}.png"
    if kind == "photo":
        photo_plate(src, name)
    elif kind == "gear":
        im = dark_base().convert("RGBA"); im.alpha_composite(gw, (120, 0)); finish(im.convert("RGB"), name)
    elif src and os.path.exists(src):
        cutout_plate(src, name, box=(1180, 90, 1660, 1000) if n == "10" else (880, 140, 1860, 960), gray_it=n != "10")
    else:
        finish(dark_base(), name)
end = dark_base().convert("RGBA"); end.alpha_composite(gw.transpose(Image.FLIP_LEFT_RIGHT), (-60, 0)); finish(end.convert("RGB"), "div_end.png")
finish(dark_base(), "dark.png")
print("ok")
