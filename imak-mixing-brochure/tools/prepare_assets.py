#!/usr/bin/env python3
"""Turn raw i.Mak images into brochure-ready assets.

Usage:
    python3 tools/prepare_assets.py RAW_DIR

RAW_DIR holds the downloaded originals, named as in SOURCES (the WordPress media
library of imakreduktor.com saved as <year>_<month>_<file>, plus images extracted
from the i.Mak catalogue PDFs with `pdfimages -png -p`). Output goes to ../assets.

Operations:
  alpha  keep the image's own transparency, trim, resize
  key    remove a white studio background (flood fill from the border), trim, resize
  solid  keep only the opaque part of a transparent render (drops a soft floor plane)
  photo  plain photo: optional crop box (fractions), resize, save as JPEG
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")

# name: (source file in RAW_DIR, operation, max long edge px, crop box or None)
ASSETS = {
    # hero product: 4DSM vertical agitator / aerator unit
    "4dsm-hero":        ("wp/2020_08_12.-4DS-Series-2-1.png", "alpha", 1500, None),
    "4dsm-front":       ("wp/2020_08_12.-4DS-Series-3-1.png", "key", 1300, None),
    "4dsm-cad":         ("catimg/4DS-Ka-039-597.png", "key", 1200, None),
    "4dsm-exploded":    ("catimg/4DS-Ka-037-592.png", "key", 1200, None),
    # heavy-duty agitator drive: vertical MA monoblock with motor + oil cooler
    "ma-vertical":      ("wp/2020_08_MA703-1-1.png", "solid", 1200, None),
    "mk-unit":          ("wp/2020_09_MK603-UsttenExtruder-1.png", "alpha", 1000, None),
    "a-unit":           ("wp/2021_01_9.-A-Series-1.jpg", "key", 800, None),
    "ipr":              ("wp/2020_08_15.-IPR-Series-2.png", "alpha", 1200, None),
    # geared motors
    "ir":               ("wp/2021_01_1.-IR-Series-1.jpg", "key", 800, None),
    "irk":              ("wp/2020_08_2.-IRK-Series-e1597707082705-1.png", "alpha", 1200, None),
    "yp":               ("wp/2021_01_3.-YP-Series-1.jpg", "key", 800, None),
    "irsd":             ("wp/2021_01_7.-IRSD-Series-1.png", "key", 1100, None),
    "irs":              ("wp/2021_01_6.-IRS-Series-1.jpg", "key", 800, None),
    "s":                ("wp/2021_01_5.-S-Series-1.jpg", "key", 800, None),
    "irnx":             ("wp/2021_01_11.-IRN-Series-1.jpg", "key", 800, None),
    "irc":              ("wp/2021_01_4.-IRC-Series-1.jpg", "key", 800, None),
    "motor":            ("wp/2021_01_asenkron-motor-1.jpg", "key", 800, None),
    # cut-aways and exploded views
    "cut-irk":          ("wp/2021_10_IRK_Kesit-Poster-EN_V3-01-1.tif", "photo", 2000, (0.0, 0.155, 1.0, 0.69)),
    "cut-yp":           ("wp/2021_08_YP_Kesit-Poster-EN-V2-1-scaled.jpg", "photo", 1800, (0.0, 0.155, 1.0, 0.72)),
    "exploded-a":       ("catimg/A-Kata-083-1514.png", "key", 1200, None),
    # application and company photos
    "app-aerators":     ("wp/2021_05_Water-Full-1.jpeg", "photo", 1600, None),
    "app-waste":        ("wp/2026_01_waste-recyclage.jpg", "photo", 1400, None),
    "app-recycling":    ("wp/2026_07_Waste-treatment-article.jpg", "photo", 1024, None),
    "app-mining":       ("wp/2025_09_minning-1-scaled.jpg", "photo", 1800, None),
    "app-quarry":       ("wp/2026_01_mining1.jpg", "photo", 1080, None),
    "app-grain":        ("wp/2026_01_grain.jpg", "photo", 1080, None),
    "app-oilgas":       ("wp/2025_09_oil-and-gas-1.jpg", "photo", 1152, None),
    "app-pump-skid":    ("wp/2026_02_baede-tarihi-is-ortagimiza-ziyaret-1.jpeg", "photo", 1400, None),
    "factory-floor":    ("wp/2020_08_unnamed-1.jpg", "photo", 512, None),
    "factory-irkf153":  ("wp/2020_08_NEW-IRKF153-IMAK-Gearboxes-and-drives-scaled-1.jpg", "photo", 1800, None),
    "fair-hannover":    ("wp/2020_08_1-hannovermesse-2019-imak-reduktor-imakreduktor-gearbox-motors-scaled-1.jpg", "photo", 1800, None),
    "partner-za":       ("wp/2022_11_guney-afrika-imak-2-1.jpg", "photo", 600, None),
    "family":           ("wp/2026_02_dX0151Mq.jpg", "photo", 1376, None),
    # distributor photos of i.Mak installations (sources in SOURCES.md)
    "app-aerator-lagoon": ("social/distributor_uk_advanced_drives/ad_3995_heavy-duty-aerator-industrial-mixer-gearbox-manufacturer-supplier-uk-1.jpg", "photo", 1800, None),
    "app-4ds-pallets":  ("social/distributor_uk_advanced_drives/ad_3992_4DS-Aerator-gearboxes-for-water-treatment-plants-mixer-machines-uk-scaled.jpg", "photo", 1800, None),
    "app-tank-deck":    ("social/distributor_uk_advanced_drives/ad_3993_gearboxes-and-drives-for-water-treatment-plant-equipment-uk-man-ufacturer.jpg", "photo", 1108, None),
    "app-mixer-nl":     ("social/distributor_nl_atb/atb_imak-1000x600_orig.jpg", "photo", 1000, None),
    "app-aeration-basin": ("social/distributor_uk_advanced_drives/ad_2405_4DS-IMAK-Gearboxes-and-Drives-Solutions-for-Water-Treatment-Systems-mp4-image.png", "photo", 1280, None),
    "fair-win-eurasia": ("social/distributor_uk_advanced_drives/ad_2701_I-MAK-Reduktor-UK-Industrial-gearbox-supplier-Advanced-Drives-WIN-EURASIA-EXPO-3.jpg", "photo", 1200, None),
    "mk-red":           ("social/distributor_us_sipco/sipco_MK_RED.png", "key", 1300, None),
    "logo":             ("wp/2021_05_logo-FULL-1.png", "key", 1002, None),
}


def trim(im, pad=6):
    a = np.array(im.getchannel("A"))
    ys, xs = np.where(a > 8)
    if len(xs) == 0:
        return im
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, im.width)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, im.height)
    return im.crop((x0, y0, x1, y1))


def white_key(im, thr=238):
    """Make the white background connected to the border transparent, soft edge."""
    rgb = np.array(im.convert("RGB")).astype(np.int16)
    near_white = (rgb.min(axis=2) >= thr)
    lab, _ = ndimage.label(near_white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    # soft edge: grow background by 1 px, blur
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    a = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(a)
    return out


def _flatten(im):
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def resize(im, longest):
    s = longest / max(im.size)
    if s < 1:
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im


# product cut-outs whose red paint is moved to RAL 3020 (tools/ral.py); photos are left as they are
RAL_ASSETS = {"4dsm-hero", "4dsm-front", "ma-vertical", "mk-unit", "a-unit", "ipr", "ir", "irk", "yp",
              "irsd", "irs", "s", "irnx", "irc", "motor", "mk-red"}


def main(raw):
    os.makedirs(OUT, exist_ok=True)
    for name, (src, op, longest, box) in ASSETS.items():
        im = Image.open(os.path.join(raw, src))
        im.load()
        if op == "photo":
            im = im.convert("RGB")
            if box:
                w, h = im.size
                im = im.crop((int(box[0] * w), int(box[1] * h), int(box[2] * w), int(box[3] * h)))
            im = resize(im, longest)
            im.save(os.path.join(OUT, name + ".jpg"), quality=86, optimize=True, progressive=True)
        else:
            if op == "alpha":
                im = im.convert("RGBA")
            elif op == "solid":
                im = im.convert("RGBA")
                a = im.getchannel("A").point(lambda v: 255 if v > 200 else 0)
                im.putalpha(a.filter(ImageFilter.GaussianBlur(0.7)))
            else:
                im = white_key(im.convert("RGBA").convert("RGB") if im.mode != "RGBA" else _flatten(im))
            im = resize(trim(im), longest)
            if name in RAL_ASSETS:
                import numpy as np
                from ral import recolor
                im = Image.fromarray(recolor(np.array(im).astype("float32")).astype("uint8"), "RGBA")
            im.save(os.path.join(OUT, name + ".png"), optimize=True)
        print(f"{name:18s} {op:5s} {im.size[0]}x{im.size[1]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
