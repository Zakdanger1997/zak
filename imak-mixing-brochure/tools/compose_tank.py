#!/usr/bin/env python3
"""Seat the i.Mak agitator drive render on the tank's mounting flange.

Usage: python3 tools/compose_tank.py [--preview]
Reads  assets/tank-scene.png + assets/tank-points.json (from render_tank.py)
       assets/ma-vertical.png (i.Mak MA vertical agitator drive)
Writes assets/tank-diagram.png and assets/tank-diagram.json (label anchors in % of the image).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets")
PREVIEW = "--preview" in sys.argv
REAL = "drive3d" in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "tank-points.json")).read()

# Output flange of ma-vertical.png, measured on the image: bottom edge of the grey
# flange plate (front point) and its full width.
DRIVE_FLANGE_BOTTOM_Y = 720
DRIVE_FLANGE_X0, DRIVE_FLANGE_X1 = 50, 404
TOP_MARGIN = 0.03


def clean_shadow(im):
    """Drop the faint shadow-catcher haze, keep the contact shadow."""
    a = np.array(im).astype(np.float32)
    shadow = a[..., :3].max(axis=2) < 10
    al = a[..., 3]
    al[shadow] = np.clip((al[shadow] - 42) * 1.25, 0, 255)
    a[..., 3] = al
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def main():
    scene = Image.open(os.path.join(A, "tank-preview.png" if PREVIEW else "tank-scene.png")).convert("RGBA")
    pts = json.load(open(os.path.join(A, "tank-points-preview.json" if PREVIEW else "tank-points.json")))
    scene = clean_shadow(scene)
    if REAL:      # the real MA + motor are already part of the 3D render
        canvas, top_pad, x0_dummy = scene, 0, None
        return finish(canvas, pts, top_pad, None)
    drive = Image.open(os.path.join(A, "ma-vertical.png")).convert("RGBA")
    # cut off the shaft stub below the flange (it sits inside the pedestal)
    drive = drive.crop((0, 0, drive.width, DRIVE_FLANGE_BOTTOM_Y + 1))

    fl_w = pts["flange_right"][0] - pts["flange_left"][0]
    s = fl_w / (DRIVE_FLANGE_X1 - DRIVE_FLANGE_X0)
    drive = drive.resize((round(drive.width * s), round(drive.height * s)), Image.LANCZOS)
    fx = (DRIVE_FLANGE_X0 + DRIVE_FLANGE_X1) / 2 * s
    fy = DRIVE_FLANGE_BOTTOM_Y * s
    tx, ty = pts["flange_front_top"]
    ox, oy = round(tx - fx), round(ty - fy)

    # extend the canvas upwards if the drive sticks out of the top
    top_pad = max(0, -oy + round(scene.height * TOP_MARGIN))
    canvas = Image.new("RGBA", (scene.width, scene.height + top_pad), (0, 0, 0, 0))
    canvas.alpha_composite(scene, (0, top_pad))
    # soft contact shadow of the drive on the bridge plate
    from PIL import ImageDraw, ImageFilter
    sh = Image.new("L", canvas.size, 0)
    cx, cy, rx = tx, ty + top_pad, fl_w * 0.62
    ImageDraw.Draw(sh).ellipse((cx - rx, cy - rx * 0.16, cx + rx, cy + rx * 0.22), fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(fl_w * 0.08))
    canvas.alpha_composite(Image.merge("RGBA", (sh.point(lambda v: 0),) * 3 + (sh,)))
    canvas.alpha_composite(drive, (ox, oy + top_pad))

    return finish(canvas, pts, top_pad, (ox, oy, drive.width, drive.height))


def deepen_reds(arr):
    """Bring the red paint and flow arrows back to i.Mak red (the tank lighting washes them out)."""
    rgb = arr[..., :3] / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    red = (rgb[..., 0] == mx) & (mx - mn > 0.18) & (rgb[..., 0] > rgb[..., 1] * 1.5)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    new_sat = np.clip(sat * 1.45, 0, 0.97)
    new_v = mx * 0.86
    # rebuild colour keeping hue: channels scale between min and max
    k = (rgb - mn[..., None]) / np.maximum(mx - mn, 1e-6)[..., None]
    new_min = new_v * (1 - new_sat)
    out = new_min[..., None] + k * (new_v - new_min)[..., None]
    rgb = np.where(red[..., None], out, rgb)
    arr[..., :3] = rgb * 255.0
    return arr


def finish(canvas, pts, top_pad, drive_box):
    # crop tight to the equipment (not to the floor shadow) and fade the shadow out at the edges
    arr = np.array(canvas).astype(np.float32)
    solid = (arr[..., 3] > 6) & (arr[..., :3].max(axis=2) >= 10)
    ys, xs = np.where(solid)
    pad = round(canvas.width * 0.03)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, canvas.width)
    y0, y1 = max(ys.min() - pad // 3, 0), min(ys.max() + pad, canvas.height)
    arr = arr[y0:y1, x0:x1]
    h, w = arr.shape[:2]
    shadow = arr[..., :3].max(axis=2) < 10
    fx = np.minimum(np.arange(w), np.arange(w)[::-1]) / (w * 0.10)
    fy = np.minimum(np.arange(h), np.arange(h)[::-1]) / (h * 0.06)
    fade = np.clip(np.minimum(fx[None, :], fy[:, None]), 0, 1)
    arr[..., 3] = np.where(shadow, arr[..., 3] * fade, arr[..., 3])
    arr = deepen_reds(arr)
    out = Image.fromarray(arr.astype(np.uint8), "RGBA")
    W, H = out.size

    def rel(p, dy=top_pad):
        return [round((p[0] - x0) / W * 100, 2), round((p[1] + dy - y0) / H * 100, 2)]
    anchors = {k: rel(v) for k, v in pts.items() if k not in ("size",)}
    if drive_box:
        ox, oy, dw, dh = drive_box
        anchors["drive"] = rel((ox + dw * 0.72, oy + dh * 0.35), dy=top_pad)
    else:
        anchors["drive"] = anchors["drive3d"]
    anchors["aspect"] = round(H / W, 4)
    name = "tank-diagram-preview" if PREVIEW else "tank-diagram"
    out.save(os.path.join(A, name + ".png"), optimize=True)
    json.dump(anchors, open(os.path.join(A, name + ".json"), "w"), indent=1)
    print(name, out.size)


if __name__ == "__main__":
    main()
