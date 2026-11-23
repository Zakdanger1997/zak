#!/usr/bin/env python3
"""Turn the photos of the i.Mak company deck into collage cut-outs (white paper border, transparent
background) plus a paper background, for the collage-style company video.

Usage: python3 tools/prep_assets.py      (reads assets/pdf/*, writes assets/cut/*.png and assets/paper.png)
The deck images come out of `pdfimages -png -p assets/imak-company-deck.pdf assets/pdf/img` as RGB + soft-mask
pairs (hexagons). Two images that are vector or tiny in the deck are cropped from a 4368 px page render.
"""
import os

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.join(ROOT, "assets", "pdf")
OUT = os.path.join(ROOT, "assets", "cut")
BROCH = os.path.join(ROOT, "..", "imak-mixing-brochure", "assets")

# name: (rgb file, mask file)
HEX = {
    "factory1998": ("img-002-005.png", "img-002-006.png"),
    "barcode2012": ("img-002-009.png", "img-002-010.png"),
    "export2000": ("img-002-011.png", "img-002-012.png"),
    "turquality2024": ("img-003-022.png", "img-003-023.png"),
    "plant2023": ("img-003-032.png", "img-003-033.png"),
    "hudaco2019": ("img-003-034.png", "img-003-035.png"),
    "sipco2019": ("img-003-036.png", "img-003-037.png"),
    "egasen2021": ("img-003-038.png", "img-003-039.png"),
    "foundry2022": ("img-003-040.png", "img-003-041.png"),
}
RECT = {   # rectangular photos (their own white frame is trimmed off)
    "robot": "img-004-050.png", "geartest": "img-004-052.png", "factory": "img-004-054.png", "pour": "img-004-056.png",
    "s_agriculture": "img-005-064.png", "s_oilgas": "img-005-066.png", "s_water": "img-005-068.png",
    "s_mining": "img-005-070.png", "s_steel": "img-005-072.png", "s_food": "img-005-074.png", "s_cement": "img-005-076.png",
}


def paper_border(rgba, px=14, shadow=False):
    """Add a white paper border around the alpha shape (like a cut-out from a magazine)."""
    a = np.array(rgba.getchannel("A"))
    pad = px + 4
    big = Image.new("RGBA", (rgba.width + 2 * pad, rgba.height + 2 * pad), (0, 0, 0, 0))
    big.paste(rgba, (pad, pad), rgba)
    al = np.array(big.getchannel("A")) > 30
    grown = ndimage.binary_dilation(al, iterations=px)
    # slightly ragged outer edge, like scissors
    rng = np.random.default_rng(len(a))
    edge = grown & ~ndimage.binary_erosion(grown, iterations=2)
    jag = edge & (rng.random(edge.shape) < 0.35)
    grown = grown & ~jag
    base = Image.new("RGBA", big.size, (250, 247, 240, 0))
    ba = Image.fromarray((grown * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    base.putalpha(ba)
    base.alpha_composite(big)
    return base


def print_look(rgb, amount=0.18):
    """A touch of print: slightly lower saturation, warm paper tint, fine grain."""
    a = np.array(rgb.convert("RGB")).astype(np.float32)
    g = a.mean(axis=2, keepdims=True)
    a = a * (1 - amount) + g * amount
    a = a * np.array([1.02, 1.0, 0.96])
    a += np.random.default_rng(1).normal(0, 5, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def white_key(im, thr=232):
    rgb = np.array(im.convert("RGB")).astype(np.int16)
    near = rgb.min(axis=2) >= thr
    lab, _ = ndimage.label(near)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    out = im.convert("RGBA")
    out.putalpha(Image.fromarray(np.where(bg, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    return out


def trim(im, pad=4):
    a = np.array(im.getchannel("A"))
    ys, xs = np.where(a > 10)
    return im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, (rgb, mask) in HEX.items():
        im = print_look(Image.open(os.path.join(SRC, rgb)))
        m = Image.open(os.path.join(SRC, mask)).convert("L")
        m = m.point(lambda v: 255 if v > 128 else 0).filter(ImageFilter.GaussianBlur(0.7))
        im = im.convert("RGBA"); im.putalpha(m)
        paper_border(trim(im), 12).save(os.path.join(OUT, name + ".png"))
    for name, f in RECT.items():
        # these also carry a soft mask (clipped-corner shape); the white frame inside it is trimmed off
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        num = int(f[8:11]) + 1
        m = Image.open(os.path.join(SRC, f"{f[:8]}{num:03d}.png")).convert("L")
        a = np.array(im).astype(int)
        mm = np.array(m) > 128
        inner = mm & (a.min(axis=2) < 238) & (a.max(axis=2) > 18)
        ys, xs = np.where(inner)
        box = (xs.min() + 3, ys.min() + 3, xs.max() - 3, ys.max() - 3)
        im = print_look(im.crop(box)).convert("RGBA")
        im.putalpha(m.crop(box).point(lambda v: 255 if v > 128 else 0))
        paper_border(trim(im), 14).save(os.path.join(OUT, name + ".png"))
    # vector logo and tiny photo from the 4368 px page render
    g = Image.open(os.path.join(SRC, "crop_gearbox1983.png")).crop((130, 185, 665, 530))
    g = white_key(g, 225)
    a = np.array(g); red = (a[..., 0] > 120) & (a[..., 1] < 90)          # stray bits of the deck's red hexagon
    a[..., 3] = np.where(red, 0, a[..., 3]); g = Image.fromarray(a)
    trim(g).save(os.path.join(OUT, "gearbox1983.png"))
    lg = Image.open(os.path.join(SRC, "crop_logo1973.png")).crop((150, 100, 620, 570))
    trim(white_key(lg, 200)).save(os.path.join(OUT, "logo1973.png"))
    # today's i.Mak units (brochure studio renders from the official STEP models, RAL 3020)
    for n in ("3d-irkm", "3d-ma", "3d-mk", "3d-iram", "3d-irsdm", "3d-ypm"):
        p = os.path.join(BROCH, n + ".png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA")
            a = np.array(im); a[..., 3] = np.where(a[..., :3].max(axis=2) < 25, 0, a[..., 3]); im = Image.fromarray(a)
            trim(im).save(os.path.join(OUT, n.replace("3d-", "unit_") + ".png"))
    # paper background: warm off-white with grain and soft fibres
    W, H = 2200, 1300
    rng = np.random.default_rng(5)
    base = np.ones((H, W, 3), np.float32) * np.array([239, 233, 222], np.float32)
    n1 = ndimage.gaussian_filter(rng.normal(0, 1, (H, W)), 40) * 60
    n2 = rng.normal(0, 4.5, (H, W))
    fib = ndimage.gaussian_filter(rng.normal(0, 1, (H, W)), (0.6, 6)) * 9
    base += (n1 + n2 + fib)[..., None]
    Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save(os.path.join(ROOT, "assets", "paper.jpg"), quality=92)
    print("cut-outs:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
