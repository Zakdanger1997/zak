"""Hero 3: the i.Mak product family on a dark reflective studio floor.
python3 tools/scene_lineup.py [--preview] [--samples N] [--scale F]
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
H.world_dark(0.08, haze=0.0)
H.plane("floor", (80, 80), mats["floor"])

# (name, spin degrees, x, y) - geared motors in front, industrial units behind, all facing the camera 3/4
UNITS = [
    ("IRAM_93-160_L", 35, -1.35, 0.10),
    ("IRKM_93-160_L", 20, -0.35, -0.10),
    ("YPM_93-160_L", 35, 0.55, 0.0),
    ("IRFM_93-160_L", 35, 1.50, 0.20),
    ("MK_703-G07", 125, -0.9, 1.6),
    ("MA_703-G00", 215, 0.6, 1.7),
    ("IRSDM_83-112_M", 35, 1.9, 1.4),
    ("IRNX_07", 35, 2.6, 0.9),
]
objs = []
for name, spin, x, y in UNITS:
    u = H.load_unit(name, mats, spin=spin, loc=(x, y, 0))
    objs.append(u)

target = Vector((0.45, 0.6, 0.3))
H.light_area("key", (3.0, -3.5, 3.8), target, 1600, 2.5, (1.0, 0.95, 0.88))
H.light_area("fill", (-4.0, -3.0, 2.0), target, 420, 5.0, (0.9, 0.93, 1.0))
H.light_area("rim", (-1.0, 5.0, 3.2), target, 2200, 2.0, (0.75, 0.85, 1.0))
H.light_area("rim2", (4.5, 4.0, 2.5), target, 1400, 1.5, (0.75, 0.85, 1.0))
H.light_area("top", (0.5, 0.5, 6.0), target, 350, 4.0, (1, 1, 1))
# a soft light strip behind the units, reflected in the floor
strip_m = H.mat("strip", (1, 1, 1), 0.0, 0.5, emit=((0.9, 0.95, 1.0), 0.7))


H.camera((1.0, -5.3, 1.65), (0.5, 0.6, 0.25), lens=46, fstop=5.6, focus=(0.3, 0.2, 0.25), shift=(0.0, 0.03))
H.render("hero_lineup_family", exposure=-0.4)
