#!/usr/bin/env python3
"""Crop the output-stage render and write the page-8 figure (dimensions, F_R, deflection, labels).

Usage: python3 tools/bearing_labels.py [--preview]
Reads assets/bearing-scene.png + bearing-points.json (render_bearing.py),
writes assets/bearing-diagram.png and the block between
<!-- bearing figure --> and <!-- /bearing figure --> in brochure.html.
"""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
A = os.path.join(ROOT, "assets")
PREVIEW = "--preview" in sys.argv
sys.path.insert(0, HERE)
from compose_tank import clean_shadow  # noqa: E402

Y0, HMAX = 186.0, 84.0           # figure top and height on the page (mm)
XC = 46.0                        # figure centre x (mm)
LX = 93.0                        # label column x (mm)
LABELS = [
    ("gear", "<b>Output gear</b>"),
    ("chamber", "<b>Gear unit housing</b><br>i.Mak red, cast iron"),
    ("brg_up", "<b>Upper bearing</b><br>tapered roller"),
    ("brg_lo", "<b>Lower bearing</b><br>tapered roller"),
    ("seal", "<b>Shaft seal</b>"),
    ("flange", "<b>Mounting flange</b>"),
    ("shaft", "<b>Agitator shaft</b>"),
    ("hub", "<b>Impeller hub</b>"),
]


def main():
    im = clean_shadow(Image.open(os.path.join(A, "bearing-preview.png" if PREVIEW else "bearing-scene.png")).convert("RGBA"))
    pts = json.load(open(os.path.join(A, "bearing-points-preview.json" if PREVIEW else "bearing-points.json")))
    arr = np.array(im).astype(np.float32)
    solid = (arr[..., 3] > 6) & (arr[..., :3].max(axis=2) >= 10)
    ys, xs = np.where(solid)
    pad = round(im.width * 0.02)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, im.width)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad * 2, im.height)
    arr = arr[y0:y1, x0:x1]
    h, w = arr.shape[:2]
    shadow = arr[..., :3].max(axis=2) < 10
    fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (h * 0.05), 0, 1)
    fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (w * 0.10), 0, 1)
    arr[..., 3] = np.where(shadow, arr[..., 3] * np.minimum(fx[None, :], fy[:, None]), arr[..., 3])
    out = Image.fromarray(arr.astype(np.uint8), "RGBA")
    name = "bearing-diagram-preview.png" if PREVIEW else "bearing-diagram.png"
    out.save(os.path.join(A, name), optimize=True)

    H = HMAX
    W = H * w / h
    X0 = XC - W / 2
    k = W / w

    def mm(p):
        return X0 + (p[0] - x0) * k, Y0 + (p[1] - y0) * k

    g = []
    # dimension a (left), dimension x (further left)
    (ax, ay1), (_, ay2) = mm(pts["a_top"]), mm(pts["a_bot"])
    bu, bl = mm(pts["brg_up_l"]), mm(pts["brg_lo_l"])
    dxa = min(ax, bu[0], bl[0]) - 4
    dxx = dxa - 7
    fz = mm(pts["force_at"])
    ext = lambda x1, y1, x2, y2: f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#6b6e73" stroke-width=".2"/>'
    g.append(ext(bu[0] - 1, bu[1], dxx - 1.5, bu[1]))
    g.append(ext(bl[0] - 1, bl[1], dxx - 1.5, bl[1]))
    g.append(ext(fz[0] - 2, fz[1], dxx - 1.5, fz[1]))
    dim = lambda x, ya, yb: (f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x:.1f}" y2="{yb:.1f}" stroke="#2a2b2e" stroke-width=".3" marker-start="url(#dm)" marker-end="url(#dm)"/>')
    g.append(dim(dxa, bu[1], bl[1]))
    g.append(dim(dxx, bl[1], fz[1]))
    g.append(f'<text x="{dxa - 1.2:.1f}" y="{(bu[1] + bl[1]) / 2 + 1.2:.1f}" font-size="3.6" font-family="Barlow" font-weight="700" fill="#2a2b2e" text-anchor="end">a</text>')
    g.append(f'<text x="{dxx - 1.2:.1f}" y="{(bl[1] + fz[1]) / 2 + 1.2:.1f}" font-size="3.6" font-family="Barlow" font-weight="700" fill="#2a2b2e" text-anchor="end">x</text>')
    # radial force
    ft = mm(pts["force_to"])
    g.append(f'<path d="M{fz[0] + 0.8:.1f} {fz[1]:.1f} L{ft[0] + 3:.1f} {fz[1]:.1f}" stroke="#c8102e" stroke-width=".7" marker-end="url(#fr)"/>')
    g.append(f'<text x="{ft[0] + 4.2:.1f}" y="{fz[1] + 1.3:.1f}" font-size="3.6" font-family="Barlow" font-weight="700" fill="#c8102e">F<tspan font-size="2.4" dy=".8">R</tspan></text>')
    # deflection line (exaggerated)
    d = " ".join(f"{mm(p)[0]:.2f},{mm(p)[1]:.2f}" for p in pts["deflection"])
    g.append(f'<polyline points="{d}" fill="none" stroke="#c8102e" stroke-width=".45" stroke-dasharray="1.2 .9"/>')
    last = mm(pts["deflection"][-1])
    g.append(f'<text x="{last[0] + 1.5:.1f}" y="{last[1] + 6.5:.1f}" font-size="2.7" font-family="Barlow" fill="#c8102e">deflection (exaggerated)</text>')

    items = sorted((mm(pts[key])[1], key, html) for key, html in LABELS)
    lines, labs, ly_prev, two = [], [], -99, False
    for ay, key, html in items:
        ly = max(ay, ly_prev + (7.6 if two else 5.2))
        axp = mm(pts[key])[0]
        lines.append(f'<line x1="{axp:.1f}" y1="{ay:.1f}" x2="{LX - 1.2:.1f}" y2="{ly:.1f}"/><circle cx="{axp:.1f}" cy="{ay:.1f}" r=".55"/>')
        labs.append(f'<div class="lab" style="left:{LX:.1f}mm; top:{ly - 1.6:.1f}mm;">{html}</div>')
        ly_prev, two = ly, "<br>" in html

    block = f'''<!-- bearing figure -->
  <img class="abs" src="assets/{name}" style="left:{X0:.1f}mm; top:{Y0}mm; height:{H}mm;" alt="">
  <svg class="lines" width="210mm" height="297mm" viewBox="0 0 210 297">
    <defs>
      <marker id="dm" viewBox="0 0 6 6" refX="3" refY="3" markerWidth="3.2" markerHeight="3.2" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6 z" fill="#2a2b2e"/></marker>
      <marker id="fr" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#c8102e"/></marker>
    </defs>
    {"".join(g)}
    <g stroke="#8e1b1e" stroke-width=".22" fill="#8e1b1e">{"".join(lines)}</g>
  </svg>
  {"".join(labs)}
  <!-- /bearing figure -->'''
    p = os.path.join(ROOT, "brochure.html")
    s = open(p, encoding="utf-8").read()
    s, n = re.subn(r"<!-- bearing figure -->.*?<!-- /bearing figure -->", block, s, flags=re.S)
    assert n == 1
    open(p, "w", encoding="utf-8").write(s)
    print("figure", round(W, 1), "x", H, "mm at x", round(X0, 1))


if __name__ == "__main__":
    main()
