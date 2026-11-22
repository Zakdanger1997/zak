#!/usr/bin/env python3
"""Shift the red paint in an image to RAL 3020 Traffic Red (sRGB #CC0605), keeping shading.

Usage: python3 tools/ral.py image.png [more.png ...]     (edits the files in place)
Also imported by compose_tank.py and bearing_labels.py.

Saturated red pixels take RAL 3020's hue and saturation at their own brightness; the
less saturated a red pixel is (specular highlights, edges) the more of its original
colour is kept, so highlights stay white and shadows stay dark.
"""
import sys

import numpy as np
from PIL import Image

RAL3020 = np.array([204, 6, 5], dtype=np.float32) / 255.0
REF = RAL3020 / RAL3020.max()          # unit-brightness RAL colour


def recolor(arr):
    """arr: float32 HxWx3/4 in 0..255. Returns the same array with reds moved to RAL 3020."""
    rgb = arr[..., :3] / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    is_red = (rgb[..., 0] >= mx - 1e-6) & (rgb[..., 0] > rgb[..., 1] * 1.6) & (rgb[..., 0] > rgb[..., 2] * 1.6)
    w = np.clip((sat - 0.25) / 0.45, 0, 1) * is_red          # blend weight
    v = np.clip(mx * 0.97, 0, 1)
    target = REF[None, None, :] * v[..., None]
    rgb = rgb * (1 - w[..., None]) + target * w[..., None]
    arr[..., :3] = np.clip(rgb, 0, 1) * 255.0
    return arr


def main(paths):
    for p in paths:
        im = Image.open(p)
        mode = im.mode
        a = np.array(im.convert("RGBA")).astype(np.float32)
        a = recolor(a)
        out = Image.fromarray(a.astype(np.uint8), "RGBA")
        if mode != "RGBA":
            out = out.convert("RGB")
        out.save(p, optimize=True)
        print("RAL 3020:", p)


if __name__ == "__main__":
    main(sys.argv[1:])
