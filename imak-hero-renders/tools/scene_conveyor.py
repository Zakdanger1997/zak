"""Hero 1: i.Mak IRAM 93-160 L helical geared motor driving a belt conveyor head pulley.
python3 tools/scene_conveyor.py [--preview] [--samples N] [--scale F]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import bmesh
from mathutils import Vector, Euler
import hero_lib as H

H.fresh()
mats = H.M()
H.world_dark(0.25, haze=0.0025)
H.hall(mats, floor=60, ceiling_h=7.5)

# ---------------------------------------------------------------- conveyor geometry
BW = 0.8              # belt width
XH, XT = 1.5, -7.0    # head / tail pulley x
ZC = 0.75             # pulley centre height
RP = 0.25             # pulley radius
TB = 0.014            # belt thickness
YF = BW / 2 + 0.07    # frame side plate y


def belt():
    pts = []
    n = 24
    for i in range(n + 1):                      # head arc, from top (90deg) clockwise to bottom (-90deg)
        a = math.radians(90 - 180 * i / n)
        pts.append((XH + (RP + TB / 2) * math.cos(a), ZC + (RP + TB / 2) * math.sin(a)))
    for i in range(n + 1):                      # tail arc
        a = math.radians(-90 - 180 * i / n)
        pts.append((XT + (RP + TB / 2) * math.cos(a), ZC + (RP + TB / 2) * math.sin(a)))
    bm = bmesh.new()
    rows = []
    for x, z in pts:
        rows.append((bm.verts.new((x, -BW / 2, z)), bm.verts.new((x, BW / 2, z))))
    for i in range(len(rows)):
        a, b = rows[i], rows[(i + 1) % len(rows)]
        bm.faces.new((a[0], a[1], b[1], b[0]))
    bm.normal_update()
    o = H.obj_from_bmesh(bm, "belt", mats["rubber"])
    md = o.modifiers.new("solid", "SOLIDIFY")
    md.thickness = TB
    md.offset = 0
    H.smooth(o, 40)
    return o


belt()
# pulleys (rubber lagged drum + steel shaft)
for name, x in (("head_pulley", XH), ("tail_pulley", XT)):
    H.cyl(name, RP, BW + 0.1, mats["dark"], loc=(x, 0, ZC), axis="Y", chamfer=0.01)
    H.cyl(name + "_shaft", 0.045, BW + 0.1 + 0.5, mats["steel"], loc=(x, 0, ZC), axis="Y")
    for s in (-1, 1):                              # plummer block bearings
        y = s * (YF + 0.09)
        H.box(name + f"_pb{s}", (0.22, 0.12, 0.08), mats["frame"], loc=(x, y, ZC - 0.10), bevel=0.004)
        H.cyl(name + f"_pbh{s}", 0.085, 0.10, mats["frame"], loc=(x, y, ZC), axis="Y", chamfer=0.006)
        H.cyl(name + f"_pbc{s}", 0.055, 0.104, mats["bore"], loc=(x, y, ZC), axis="Y")
        H.bolts(name + f"_pb{s}", [(x - 0.08, y, ZC - 0.055), (x + 0.08, y, ZC - 0.055)], mats["bolt"], r=0.01, h=0.012)

# frame: side stringers (C-channel look: web + two flanges), cross members, legs
L = XH - XT + 0.9
XC = (XH + XT) / 2
for s in (-1, 1):
    y = s * YF
    H.box(f"stringer_web{s}", (L, 0.012, 0.24), mats["frame"], loc=(XC, y, ZC - 0.02))
    H.box(f"stringer_top{s}", (L, 0.08, 0.012), mats["frame"], loc=(XC, y - s * 0.034, ZC + 0.10))
    H.box(f"stringer_bot{s}", (L, 0.08, 0.012), mats["frame"], loc=(XC, y - s * 0.034, ZC - 0.14))
for i, x in enumerate([XT + 0.5 + k * 1.5 for k in range(6)]):
    H.box(f"cross{i}", (0.06, YF * 2, 0.06), mats["frame"], loc=(x, 0, ZC - 0.17))
    for s in (-1, 1):
        H.box(f"leg{i}{s}", (0.07, 0.07, ZC - 0.14), mats["frame"], loc=(x, s * (YF - 0.0), (ZC - 0.14) / 2))
        H.box(f"foot{i}{s}", (0.16, 0.16, 0.012), mats["frame"], loc=(x, s * YF, 0.006))
    H.box(f"brace{i}", (0.05, YF * 2, 0.05), mats["frame"], loc=(x, 0, 0.18))
# carrying idlers (flat) and return rollers
for k in range(1, 6):
    x = XT + 0.4 + k * 1.4
    H.cyl(f"idler{k}", 0.06, BW + 0.08, mats["galv"], loc=(x, 0, ZC + RP - TB - 0.06), axis="Y")
    for s in (-1, 1):
        H.box(f"idlerbr{k}{s}", (0.05, 0.03, 0.14), mats["frame"], loc=(x, s * (BW / 2 + 0.055), ZC + 0.11 + 0.05))
for k in range(1, 4):
    x = XT + 1.2 + k * 2.5
    H.cyl(f"ret{k}", 0.06, BW + 0.08, mats["galv"], loc=(x, 0, ZC - RP + TB + 0.06), axis="Y")
# side skirt / guard plate on the far side, yellow safety guard over the head drum
H.box("guard_top", (0.9, BW + 0.35, 0.01), mats["yellow"], loc=(XH + 0.08, 0, ZC + RP + 0.07))
H.box("guard_front", (0.01, BW + 0.35, 0.18), mats["yellow"], loc=(XH + 0.53, 0, ZC + RP - 0.02))
# discharge hopper under the head drum
H.box("hopper_back", (0.025, BW + 0.3, 0.45), mats["frame"], loc=(XH + 0.75, 0, 0.30))
for s_ in (-1, 1):
    H.box(f"hopper_side{s_}", (0.55, 0.025, 0.45), mats["frame"], loc=(XH + 0.48, s_ * (BW / 2 + 0.15), 0.30))
H.box("hopper_floor", (0.6, BW + 0.3, 0.025), mats["frame"], loc=(XH + 0.48, 0, 0.16), rot=(0, math.radians(-25), 0))
# hall columns and a second conveyor line far behind for depth
for i, (x, y) in enumerate(((-6, 6), (0, 6), (6, 6), (12, 6), (-6, 14), (0, 14), (6, 14), (12, 14))):
    H.box(f"col{i}", (0.3, 0.3, 7.5), mats["frame"], loc=(x, y, 3.75))
    H.box(f"colf{i}", (0.12, 0.3, 7.5), mats["frame"], loc=(x - 0.2, y, 3.75))
    H.box(f"colb{i}", (0.12, 0.3, 7.5), mats["frame"], loc=(x + 0.2, y, 3.75))
for i in range(3):
    H.box(f"bgbeam{i}", (26, 0.25, 0.5), mats["frame"], loc=(3, 6 + 4 * i, 5.8))

# ---------------------------------------------------------------- the drive
# IRAM 93-160 L: output shaft on the -Y end at z=0.21 above its feet; spin 180 so it points +Y
u = H.load_unit("IRAM_93-160_L", mats, spin=180)
out_z = 0.21
pedestal_top = ZC - out_z
ucy = -(YF + 0.09 + 0.06 + 0.10 + u["size"].y / 2)        # bearing block, coupling, unit
u["parent"].location = (XH, ucy, pedestal_top)
bpy.context.view_layer.update()
shaft_end_y = ucy + u["size"].y / 2
# pedestal: base plate on a welded stand
PX, PY = u["size"].x + 0.14, u["size"].y + 0.10
H.box("ped_plate", (PX, PY, 0.03), mats["frame"], loc=(XH, ucy, pedestal_top - 0.015), bevel=0.004)
H.box("ped_rim", (PX, PY, 0.10), mats["frame"], loc=(XH, ucy, pedestal_top - 0.08), bevel=0.004)
for sx in (-1, 1):
    for sy in (-1, 1):
        H.box(f"ped_leg{sx}{sy}", (0.09, 0.09, pedestal_top - 0.13), mats["frame"],
              loc=(XH + sx * (PX / 2 - 0.045), ucy + sy * (PY / 2 - 0.045), (pedestal_top - 0.13) / 2))
        H.box(f"ped_foot{sx}{sy}", (0.16, 0.16, 0.015), mats["frame"], loc=(XH + sx * (PX / 2 - 0.045), ucy + sy * (PY / 2 - 0.045), 0.0075))
    H.box(f"ped_bar{sx}", (0.07, PY - 0.09, 0.07), mats["frame"], loc=(XH + sx * (PX / 2 - 0.045), ucy, 0.14))
H.box("ped_bar_y", (PX - 0.09, 0.07, 0.07), mats["frame"], loc=(XH, ucy - PY / 2 + 0.045, 0.14))
# aggregate on the belt
H.rocks("aggregate", mats["rock"], XT + 1.2, XH - 0.35, -0.31, 0.31, ZC + RP, n=3200, rmin=0.012, rmax=0.034, heap=0.11)
# flexible coupling: two steel hubs and an orange elastomer spider in between
yc = (shaft_end_y + (-(YF + 0.09 + 0.06))) / 2
H.cyl("coup_hub1", 0.075, 0.07, mats["steel"], loc=(XH, yc - 0.05, ZC), axis="Y", chamfer=0.006)
H.cyl("coup_hub2", 0.075, 0.07, mats["steel"], loc=(XH, yc + 0.05, ZC), axis="Y", chamfer=0.006)
H.cyl("coup_spider", 0.068, 0.04, mats["yellow"], loc=(XH, yc, ZC), axis="Y")
H.cyl("coup_shaft", 0.030, 0.16, mats["steel"], loc=(XH, shaft_end_y + 0.02, ZC), axis="Y")

# anchor bolts on the unit feet (visual)
# ---------------------------------------------------------------- lights & camera
target = Vector((XH - 0.1, ucy + 0.1, ZC))
H.light_area("key", (XH - 1.2, ucy - 2.6, 3.0), target, 1300, 2.0, (1.0, 0.95, 0.88))
H.light_area("fill", (XH + 2.8, ucy - 2.2, 1.4), target, 300, 4.0, (0.9, 0.93, 1.0))
H.light_area("rim", (XH + 1.8, ucy + 2.4, 2.6), target, 1800, 1.2, (0.75, 0.85, 1.0))
H.light_area("top", (XH, ucy, 5.5), target, 500, 3.0, (1, 1, 1))
H.light_area("hall", (2, 8, 6.5), (2, 8, 0), 2800, 14.0, (0.85, 0.9, 1.0))
# camera: low 3/4 from the drive side, conveyor receding to the upper left
cam_loc = Vector((XH - 2.35, ucy - 1.05, 1.02))
H.camera(cam_loc, (XH + 0.05, ucy + 0.30, 0.70), lens=40, fstop=4.0, focus=(XH - 0.1, ucy, ZC), shift=(0.0, 0.02))

H.render("hero_conveyor_iram93", exposure=-0.45)
