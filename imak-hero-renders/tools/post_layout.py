"""Lay out the social post: headline top-left, i.Mak badge top-right, spline call-out,
white brand band at the bottom. Works at any size (everything scales with the width).
python3 tools/post_layout.py <raw_render.png> <out.jpg> [--lang tr|en]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = "/usr/share/fonts/opentype/inter"
LOGO = os.path.join(ROOT, "brand", "imak_logo.png")
RED = (205, 20, 25)
DARK = (32, 32, 36)

COPY = {
    "tr": {
        "h1": "Vinç Tahriğinde",
        "h2": "Güvenli Bağlantı",
        "sub": "IRC Serisi: tambura doğrudan oturan frezeli (kamalı) çıkış mili\nile boşluksuz, sıfır kayıplı güç aktarımı.",
        "call": "FREZELİ ÇIKIŞ MİLİ",
        "call2": "Tambur göbeğine doğrudan bağlantı",
        "site": "www.imakreduktor.com",
    },
    "en": {
        "h1": "Hoist Drives With",
        "h2": "A Secure Connection",
        "sub": "IRC Series: splined output shaft that seats directly in the\ndrum hub for backlash-free, loss-free power transmission.",
        "call": "SPLINED OUTPUT SHAFT",
        "call2": "Direct coupling to the drum hub",
        "site": "www.imakreduktor.com",
    },
}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), int(size))


def main(src, dst, lang="tr", spline_xy=None):
    c = COPY[lang]
    if spline_xy is None:
        meta = os.path.splitext(src)[0] + ".json"
        spline_xy = tuple(json.load(open(meta))["spline"]) if os.path.exists(meta) else (0.47, 0.595)
    im = Image.open(src).convert("RGB")
    W, H = im.size
    u = W / 1080.0                                  # design unit: 1 px at 1080 wide
    # darken the top for the headline and the bottom for the band transition
    grad = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        a = max(0.0, 0.78 - t * 1.9) if t < 0.42 else 0.0
        grad.putpixel((0, y), int(255 * a))
    grad = grad.resize((W, H))
    im = Image.composite(Image.new("RGB", (W, H), (8, 8, 10)), im, grad)
    draw = ImageDraw.Draw(im)

    # ---- headline
    x0, y = 70 * u, 118 * u
    f1 = font("InterDisplay-Light.otf", 76 * u)
    f2 = font("InterDisplay-Bold.otf", 80 * u)
    f3 = font("Inter-Regular.otf", 27 * u)
    draw.text((x0, y), c["h1"], font=f1, fill="white")
    y += 92 * u
    draw.text((x0, y), c["h2"], font=f2, fill="white")
    y += 108 * u
    for line in c["sub"].split("\n"):
        draw.text((x0, y), line, font=f3, fill=(235, 235, 235))
        y += 38 * u

    # ---- i.Mak badge, top right: white pennant with a pointed bottom
    logo = Image.open(LOGO).convert("RGBA")
    bw, bh = 225 * u, 150 * u
    bx, by = W - 60 * u - bw, 0
    badge = Image.new("RGBA", (int(bw), int(bh + 40 * u)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)
    bd.polygon([(0, 0), (bw, 0), (bw, bh), (bw / 2, bh + 40 * u), (0, bh)], fill=(255, 255, 255, 255))
    lw = int(bw * 0.84)
    lg = logo.resize((lw, int(lw * logo.height / logo.width)), Image.LANCZOS)
    badge.alpha_composite(lg, (int((bw - lw) / 2), int(bh / 2 - lg.height / 2 + 8 * u)))
    im.paste(badge, (int(bx), int(by)), badge)

    # ---- call-out on the splined shaft
    draw = ImageDraw.Draw(im)
    px, py = spline_xy[0] * W, spline_xy[1] * H
    fc = font("Inter-SemiBold.otf", 24 * u)
    fc2 = font("Inter-Regular.otf", 20 * u)
    lx, ly = px - 40 * u, py + 92 * u
    draw.line([(px, py), (px - 30 * u, ly - 18 * u), (lx, ly - 18 * u)], fill="white", width=int(3 * u))
    draw.ellipse([px - 7 * u, py - 7 * u, px + 7 * u, py + 7 * u], fill="white", outline=RED, width=int(3 * u))
    draw.ellipse([px - 16 * u, py - 16 * u, px + 16 * u, py + 16 * u], outline="white", width=int(2 * u))
    tw = draw.textlength(c["call"], font=fc)
    tw2 = draw.textlength(c["call2"], font=fc2)
    bw2 = max(tw, tw2) + 36 * u
    box = [lx - bw2, ly - 10 * u, lx, ly + 72 * u]
    draw.rounded_rectangle(box, radius=int(8 * u), fill=(255, 255, 255))
    draw.rectangle([box[0], box[1], box[0] + 8 * u, box[3]], fill=RED)
    draw.text((box[0] + 22 * u, ly - 4 * u), c["call"], font=fc, fill=RED)
    draw.text((box[0] + 22 * u, ly + 32 * u), c["call2"], font=fc2, fill=DARK)

    # ---- bottom brand band with an angled edge
    band_h = 135 * u
    poly = [(0, H - band_h - 36 * u), (W * 0.52, H - band_h), (W, H - band_h), (W, H), (0, H)]
    draw.polygon(poly, fill="white")
    draw.line([(0, H - band_h - 36 * u), (W * 0.52, H - band_h)], fill=RED, width=int(6 * u))
    lw = int(300 * u)
    lg = logo.resize((lw, int(lw * logo.height / logo.width)), Image.LANCZOS)
    im.paste(lg, (int(60 * u), int(H - band_h / 2 - lg.height / 2 + 8 * u)), lg)
    fs = font("Inter-Medium.otf", 30 * u)
    sw = draw.textlength(c["site"], font=fs)
    draw.text((W - 60 * u - sw, H - band_h / 2 - 12 * u), c["site"], font=fs, fill=DARK)
    draw.line([(W - 60 * u - sw, H - band_h / 2 + 30 * u), (W - 60 * u, H - band_h / 2 + 30 * u)], fill=RED, width=int(4 * u))

    im.save(dst, quality=94, subsampling=0) if dst.lower().endswith(".jpg") else im.save(dst)
    print("wrote", dst, im.size)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "tr"
    main(args[0], args[1], lang)
