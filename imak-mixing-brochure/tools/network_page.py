#!/usr/bin/env python3
"""Write the product-family "network" block on the back page (page 12) into brochure.html.

Products sit on three rows (industrial gear units, geared motors, compact units) joined by
red bus lines, scaled by image height so all renders share one visual scale per row.
"""
import os
import re

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TOP = 104.0                       # block top on the page (mm)
ROWS = [  # (baseline y in block mm, image height mm, [(asset, label html)])
    (40, 30, [("3d-ma.png", "<b>MA</b> monobloc"), ("3d-mk.png", "<b>MK</b> monobloc"),
              ("4dsm-hero.png", "<b>4DSM</b> agitator"), ("ipr.png", "<b>IPR</b> planetary")]),
    (80, 26, [("3d-irk.png", "<b>IRK</b>"), ("3d-ir.png", "<b>IR</b>"), ("3d-yp.png", "<b>YP</b>"),
              ("3d-irsd.png", "<b>IRSD</b>"), ("3d-irc.png", "<b>IRC</b> hoist")]),
    (113, 21, [("motor.png", "<b>Motors</b> IE2–IE4"), ("3d-s.png", "<b>S</b> aluminium"),
               ("3d-irnx.png", "<b>IRNX</b>"), ("3d-iro.png", "<b>IRO</b>")]),
]
X0, X1 = 20.0, 196.0              # usable width


def main():
    imgs, labs, lines, dots = [], [], [], []
    spine_x = 11.0
    for bi, (base, h, items) in enumerate(ROWS):
        widths = []
        for f, _ in items:
            w, hh = Image.open(os.path.join(ROOT, "assets", f)).size
            widths.append(h * w / hh)
        gap = (X1 - X0 - sum(widths)) / (len(items) - 1)
        x = X0
        bus_y = base - h * 0.42
        lines.append(f'<path d="M{spine_x} {bus_y:.1f} L{X1 - 4:.1f} {bus_y:.1f}"/>')
        for (f, label), w in zip(items, widths):
            imgs.append(f'<img class="abs" src="assets/{f}" style="left:{x:.1f}mm; top:{base - h:.1f}mm; height:{h}mm;" alt="">')
            labs.append(f'<div class="lab" style="left:{x + 1:.1f}mm; top:{base + 0.8:.1f}mm;">{label}</div>')
            dots.append(f'<circle cx="{x + w / 2:.1f}" cy="{bus_y:.1f}" r="1.1"/>')
            x += w + gap
    ys = [b - h * 0.42 for b, h, _ in ROWS]
    lines.append(f'<path d="M{spine_x} {ys[0]:.1f} L{spine_x} {ys[-1]:.1f}"/>')
    block = f'''<!-- product network -->
  <div class="abs" style="left:0; top:{TOP}mm; width:210mm; height:122mm;">
    <img class="ticks" src="assets/ticks-150x110-r.png" style="left:0; top:6mm; width:150mm; height:110mm;" alt="">
    <svg class="lines" width="210mm" height="122mm" viewBox="0 0 210 122">
      <g fill="none" stroke="#c8102e" stroke-width=".55" opacity=".9">{"".join(lines)}</g>
      <g fill="#c8102e">{"".join(dots)}<circle cx="{spine_x}" cy="{ys[0]:.1f}" r="1.3"/></g>
    </svg>
    {"".join(imgs)}
    {"".join(labs)}
  </div>
  <!-- /product network -->'''
    p = os.path.join(ROOT, "brochure.html")
    s = open(p, encoding="utf-8").read()
    if "<!-- /product network -->" in s:
        s, n = re.subn(r"<!-- product network -->.*?<!-- /product network -->", block, s, flags=re.S)
    else:  # first run: the old hand-placed block ends where the contact block starts
        i = s.index("<!-- product network -->")
        j = s.index('<div class="abs" style="left:15mm; top:232mm; width:62mm;', i)
        s, n = s[:i] + block + "\n\n  " + s[j:], 1
    assert n == 1
    open(p, "w", encoding="utf-8").write(s)
    print("network written")


if __name__ == "__main__":
    main()
