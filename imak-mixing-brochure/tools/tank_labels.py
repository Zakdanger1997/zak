#!/usr/bin/env python3
"""Write the page-6 tank figure block (image + leader lines + labels) into brochure.html.

Usage: python3 tools/tank_labels.py   (after compose_tank.py)
The block between <!-- tank figure --> and <!-- /tank figure --> is regenerated from
assets/tank-diagram.json, so labels follow the render if the camera or tank changes.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
J = json.load(open(os.path.join(ROOT, "assets", "tank-diagram.json")))

X0, Y0, W = 93.0, 33.0, 75.0          # figure position and width on the page (mm)
H = W * J["aspect"]
LX = X0 + W + 4.0                      # label column x (mm)
LABELS = [  # anchor key, label html
    ("drive", "<b>i.Mak agitator drive</b><br>MA 703 + IEC motor"),
    ("bridge_end", "<b>Bridge</b>"),
    ("coupling", "<b>Rigid coupling</b>"),
    ("shaft", "<b>Agitator shaft</b>"),
    ("wall", "<b>Tank wall</b>"),
    ("hydrofoil", "<b>Hydrofoil</b><br>axial impeller"),
    ("flow", "<b>Flow pattern</b>"),
    ("baffle", "<b>Baffle</b>"),
    ("turbine", "<b>Disc turbine</b><br>radial impeller"),
    ("leg", "<b>Support leg</b>"),
]


def mm(k):
    px, py = J[k]
    return X0 + W * px / 100, Y0 + H * py / 100


def main():
    items = sorted(((mm(k)[1], k, html) for k, html in LABELS))
    ys, last, last_two = [], -99, False
    for y, _, html in items:
        y = max(y, last + (7.8 if last_two else 5.4))
        ys.append(y)
        last, last_two = y, "<br>" in html
    lines, labs = [], []
    for (ay, k, html), ly in zip(items, ys):
        ax, _ = mm(k)
        lines.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{LX - 1.2:.1f}" y2="{ly:.1f}"/><circle cx="{ax:.1f}" cy="{ay:.1f}" r=".6"/>')
        labs.append(f'<div class="lab" style="left:{LX:.1f}mm; top:{ly - 1.6:.1f}mm;">{html}</div>')
    # load arrows on the shaft, just under the coupling
    sx, sy = mm("shaft")
    cx, cy = mm("coupling")
    fy = (sy + cy) / 2 + 1.5
    shaft_x = X0 + W * J["flange_front_top"][0] / 100
    arrows = (
        f'<path d="M{shaft_x + 1.2:.1f} {fy:.1f} L{shaft_x + 9:.1f} {fy:.1f}" stroke="#c8102e" stroke-width=".6" marker-end="url(#tar)"/>'
        f'<text x="{shaft_x + 9.8:.1f}" y="{fy + 1.1:.1f}" font-size="3.2" font-family="Barlow" font-weight="700" fill="#c8102e">F<tspan font-size="2.1" dy=".7">R</tspan></text>'
        f'<path d="M{shaft_x + 2.4:.1f} {fy + 3.2:.1f} L{shaft_x + 2.4:.1f} {fy + 9.5:.1f}" stroke="#c8102e" stroke-width=".6" marker-end="url(#tar)"/>'
        f'<text x="{shaft_x + 3.6:.1f}" y="{fy + 8.6:.1f}" font-size="3.2" font-family="Barlow" font-weight="700" fill="#c8102e">F<tspan font-size="2.1" dy=".7">A</tspan></text>'
    )
    block = f'''<!-- tank figure -->
  <img class="abs" src="assets/tank-diagram.png" style="left:{X0}mm; top:{Y0}mm; width:{W}mm;" alt="">
  <svg class="lines" width="210mm" height="297mm" viewBox="0 0 210 297">
    <defs><marker id="tar" viewBox="0 0 6 6" refX="5" refY="3" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#c8102e"/></marker></defs>
    <g stroke="#8e1b1e" stroke-width=".22" fill="#8e1b1e">{"".join(lines)}</g>
    {arrows}
  </svg>
  {"".join(labs)}
  <div class="cap" style="position:absolute; left:{X0 + 2}mm; top:{Y0 + H + 1.5:.1f}mm; width:{W}mm;">F<sub>R</sub> radial load and F<sub>A</sub> axial load from the impellers act on the output bearings of the drive in addition to the torque.</div>
  <!-- /tank figure -->'''
    p = os.path.join(ROOT, "brochure.html")
    s = open(p, encoding="utf-8").read()
    s, n = re.subn(r"<!-- tank figure -->.*?<!-- /tank figure -->", block, s, flags=re.S)
    assert n == 1, "markers not found"
    open(p, "w", encoding="utf-8").write(s)
    print("figure height", round(H, 1), "mm; labels", [round(y, 1) for y in ys])


if __name__ == "__main__":
    main()
