"""Composite a transparent product render onto a photo background (4:5 post).
python3 tools/composite.py <photo.jpg> <render_rgba.png> <out.png> [--focus fx,fy] [--zoom Z] [--blur R]
       [--dark D] [--warm W] [--shadow S] [--grade]
  focus: which point of the photo (0..1) sits at the centre of the crop (default 0.5,0.5)
  zoom : crop zoom factor (>1 crops tighter)
  blur : background blur radius in px at 2160 wide (0 = none); dark: darken factor 0..1; warm: warm tint 0..1
The render is placed 1:1 (it was rendered at the output size). Its json sidecar (spline screen point) is copied.
"""
import json
import os
import shutil
import sys

from PIL import Image, ImageEnhance, ImageFilter

W, H = 2160, 2700


def arg(flag, default, cast=float):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


def main(photo, render, out):
    fx, fy = [float(v) for v in arg("--focus", "0.5,0.5", str).split(",")]
    zoom = arg("--zoom", 1.0)
    blur = arg("--blur", 0.0)
    dark = arg("--dark", 0.0)
    warm = arg("--warm", 0.0)
    bg = Image.open(photo).convert("RGB")
    # cover-crop to 4:5 around the focus point
    s = max(W / bg.width, H / bg.height) * zoom
    bw, bh = int(bg.width * s), int(bg.height * s)
    bg = bg.resize((bw, bh), Image.LANCZOS)
    cx, cy = int(fx * bw), int(fy * bh)
    x0 = min(max(cx - W // 2, 0), bw - W)
    y0 = min(max(cy - H // 2, 0), bh - H)
    bg = bg.crop((x0, y0, x0 + W, y0 + H))
    if blur:
        bg = bg.filter(ImageFilter.GaussianBlur(blur))
    if dark:
        bg = ImageEnhance.Brightness(bg).enhance(1 - dark)
    if warm:
        r, g, b = bg.split()
        r = r.point(lambda v: min(255, int(v * (1 + 0.10 * warm))))
        b = b.point(lambda v: int(v * (1 - 0.12 * warm)))
        bg = Image.merge("RGB", (r, g, b))
    fg = Image.open(render).convert("RGBA")
    if fg.size != (W, H):
        fg = fg.resize((W, H), Image.LANCZOS)
    # soft contact shadow under the product: blurred, offset alpha
    a = fg.split()[3]
    sh = a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.55))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(sh)
    comp = bg.convert("RGBA")
    comp.alpha_composite(shadow, (18, 40))
    comp.alpha_composite(fg)
    comp.convert("RGB").save(out)
    meta = os.path.splitext(render)[0] + ".json"
    if os.path.exists(meta):
        shutil.copy(meta, os.path.splitext(out)[0] + ".json")
    print("wrote", out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    # drop values that belong to flags
    vals = {sys.argv[i + 1] for i, a in enumerate(sys.argv) if a.startswith("--") and i + 1 < len(sys.argv)}
    args = [a for a in args if a not in vals]
    main(args[0], args[1], args[2])
