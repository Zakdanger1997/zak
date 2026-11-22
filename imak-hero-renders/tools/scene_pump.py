"""Hero 5: i.Mak IRFM 93-160 L flange-mounted helical geared motor on a progressive-cavity pump skid.
python3 tools/scene_pump.py [--preview] [--samples N] [--scale F]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import hero_lib as H

H.fresh()
mats = H.M()
H.world_dark(0.10, haze=0.002)
H.hall(mats, floor=60, ceiling_h=7.0, floor_mat="floor")
pump_m = mats["blue"]
# hall columns for depth
for i, (x, y) in enumerate(((-6, 6), (0, 6), (6, 6), (-6, 13), (0, 13), (6, 13))):
    H.box(f"col{i}", (0.3, 0.3, 7.0), mats["frame"], loc=(x, y, 3.5))
for i in range(2):
    H.box(f"bgbeam{i}", (24, 0.25, 0.5), mats["frame"], loc=(0, 6 + 5 * i, 5.6))
# pipework in the background
for i, (y, z) in enumerate(((5.5, 3.2), (5.5, 3.7), (5.8, 4.3))):
    H.cyl(f"pipe{i}", 0.08 + 0.02 * i, 22, mats["frame"], loc=(0, y, z), axis="X", seg=32)

# ---------------------------------------------------------------- skid
ZS = 0.16                       # top of the base frame
H.box("base_plate", (3.0, 0.9, 0.02), mats["frame"], loc=(0.2, 0, ZS - 0.01), bevel=0.003)
for s in (-1, 1):
    H.box(f"base_ch{s}", (3.0, 0.08, 0.14), mats["frame"], loc=(0.2, s * 0.41, ZS - 0.09))
for x in (-1.2, 0.2, 1.6):
    H.box(f"base_x{x}", (0.08, 0.82, 0.14), mats["frame"], loc=(x, 0, ZS - 0.09))
for x in (-1.25, 1.65):
    for s in (-1, 1):
        H.cyl(f"lift{x}{s}", 0.03, 0.12, mats["yellow"], loc=(x, s * 0.47, ZS - 0.09), axis="Y", seg=24)

# ---------------------------------------------------------------- gearmotor (flange on the -Y end)
# IRFM: output shaft along -Y, flange face at the -Y end; rotate so the pump runs along -X
u = H.load_unit("IRFM_93-160_L", mats, spin=-90)       # output now points -X
SH = 0.21                                                 # shaft height above the unit's feet plane
PED = ZS + 0.14                                           # pedestal top: motor support saddle height
u["parent"].location = (0.75, 0, PED)
bpy.context.view_layer.update()
AX = PED + SH                                             # pump axis height
XF = 0.75 - u["size"].y / 2                               # flange face x
# motor support saddle under the motor end
MB = AX - 0.175                                            # motor belly height (IEC 160 frame)
H.box("saddle_col", (0.22, 0.26, MB - ZS - 0.03), mats["frame"], loc=(0.75 + 0.34, 0, ZS + (MB - ZS - 0.03) / 2))
H.box("saddle_top", (0.30, 0.34, 0.03), mats["frame"], loc=(0.75 + 0.34, 0, MB - 0.015), bevel=0.003)
for s_ in (-1, 1):
    H.box(f"saddle_cheek{s_}", (0.30, 0.02, 0.10), mats["frame"], loc=(0.75 + 0.34, s_ * 0.165, MB + 0.03))
H.cyl("saddle_strap", 0.185, 0.04, mats["dark"], loc=(0.75 + 0.34, 0, AX), axis="X", seg=96, cap=False)

# ---------------------------------------------------------------- pump
# bearing housing / lantern bolted to the gearmotor flange
H.cyl("lantern", 0.15, 0.36, pump_m, loc=(XF - 0.18, 0, AX), axis="X", seg=96, chamfer=0.01)
H.cyl("lantern_fl", 0.19, 0.03, pump_m, loc=(XF - 0.015, 0, AX), axis="X", seg=96)
H.bolts("lfl", [(XF - 0.04, 0.165 * math.cos(math.radians(a)), AX + 0.165 * math.sin(math.radians(a))) for a in range(0, 360, 45)], mats["bolt"], r=0.011, h=0.014, axis="X")
H.box("lantern_foot", (0.30, 0.34, 0.03), pump_m, loc=(XF - 0.18, 0, ZS + 0.015), bevel=0.003)
H.box("lantern_ped", (0.22, 0.14, AX - 0.14 - ZS - 0.03), pump_m, loc=(XF - 0.18, 0, ZS + 0.03 + (AX - 0.14 - ZS - 0.03) / 2))
# suction casing with the inlet flange on top
XS = XF - 0.36 - 0.26
H.box("suction", (0.52, 0.40, 0.40), pump_m, loc=(XS, 0, AX), bevel=0.01)
H.cyl("inlet", 0.10, 0.22, pump_m, loc=(XS, 0, AX + 0.30), seg=64)
H.cyl("inlet_fl", 0.15, 0.03, pump_m, loc=(XS, 0, AX + 0.41), seg=64)
H.bolts("ifl", [(XS + 0.125 * math.cos(math.radians(a)), 0.125 * math.sin(math.radians(a)), AX + 0.43) for a in range(0, 360, 45)], mats["bolt"], r=0.009, h=0.012)
H.cyl("inlet_pipe", 0.10, 1.6, mats["dark"], loc=(XS, 0, AX + 0.43 + 0.8), seg=48)
H.cyl("inlet_elbow", 0.10, 0.6, mats["dark"], loc=(XS, 0.3, AX + 0.43 + 1.6), axis="Y", seg=48)
# stator tube with tie rods, outlet flange at the far end
LS = 1.45
H.cyl("stator", 0.085, LS, pump_m, loc=(XS - 0.26 - LS / 2, 0, AX), axis="X", seg=64, chamfer=0.006)
H.cyl("stator_fl1", 0.13, 0.035, pump_m, loc=(XS - 0.26 - 0.02, 0, AX), axis="X", seg=64)
H.cyl("stator_fl2", 0.13, 0.035, pump_m, loc=(XS - 0.26 - LS + 0.02, 0, AX), axis="X", seg=64)
for a in range(0, 360, 90):
    H.cyl(f"tie{a}", 0.012, LS, mats["steel"], loc=(XS - 0.26 - LS / 2, 0.11 * math.cos(math.radians(a + 45)), AX + 0.11 * math.sin(math.radians(a + 45))), axis="X", seg=12)
H.cyl("outlet_fl", 0.15, 0.035, pump_m, loc=(XS - 0.26 - LS - 0.04, 0, AX), axis="X", seg=64)
H.cyl("outlet_pipe", 0.085, 0.5, mats["dark"], loc=(XS - 0.26 - LS - 0.30, 0, AX), axis="X", seg=48)
H.cyl("outlet_elbow", 0.085, 1.4, mats["dark"], loc=(XS - 0.26 - LS - 0.50, 0, AX + 0.7), seg=48)
# stator support feet
for x in (XS - 0.26 - LS * 0.3, XS - 0.26 - LS * 0.85):
    H.box(f"stfoot{x}", (0.10, 0.22, 0.02), pump_m, loc=(x, 0, ZS + 0.01))
    H.box(f"stped{x}", (0.06, 0.10, AX - 0.085 - ZS - 0.02), pump_m, loc=(x, 0, ZS + 0.02 + (AX - 0.085 - ZS - 0.02) / 2))
# pressure gauge and a name plate
H.cyl("gauge_stem", 0.012, 0.12, mats["steel"], loc=(XS - 0.26 - LS + 0.12, 0, AX + 0.14), seg=16)
H.cyl("gauge", 0.05, 0.03, mats["dark"], loc=(XS - 0.26 - LS + 0.12, 0, AX + 0.22), seg=48)
H.cyl("gauge_face", 0.045, 0.004, H.mat("gauge face", (0.9, 0.9, 0.88), 0.0, 0.3), loc=(XS - 0.26 - LS + 0.12, -0.016, AX + 0.22), axis="Y", seg=48)

# ---------------------------------------------------------------- lights & camera
target = Vector((0.45, 0.0, AX))
H.light_area("key", (1.9, -2.6, 2.6), target, 1200, 2.0, (1.0, 0.95, 0.88))
H.light_area("fill", (-2.4, -2.8, 1.2), target, 320, 4.0, (0.9, 0.93, 1.0))
H.light_area("rim", (0.2, 2.6, 2.8), target, 1600, 1.2, (0.75, 0.85, 1.0))
H.light_area("top", (0.3, 0, 5.0), target, 120, 3.0, (1, 1, 1))
H.light_area("hall", (0, 8, 6.5), (0, 8, 0), 900, 10.0, (0.85, 0.9, 1.0))
H.camera((2.55, -2.35, 1.05), (0.15, -0.05, AX - 0.05), lens=40, fstop=4.0, focus=(0.6, -0.2, AX), shift=(-0.04, 0.0))
H.render("hero_pump_irfm93", exposure=-0.4)
