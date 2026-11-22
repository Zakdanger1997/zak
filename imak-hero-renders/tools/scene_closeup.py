"""Hero 4: close-up of the IRKM 93-160 L helical-bevel geared motor, shallow depth of field,
dark background with room for a headline on the left. A second unit sits blurred behind.
python3 tools/scene_closeup.py [--preview] [--samples N] [--scale F]
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
H.world_dark(0.10, haze=0.0)
H.plane("floor", (80, 80), mats["floor"])

# hero unit: output hollow shaft along X at y=-0.37; spin so the output face looks to the camera
u = H.load_unit("IRKM_93-160_L", mats, spin=-28, loc=(0.0, 0.0, 0))
# a stub shaft in the hollow shaft, with a key
H.cyl("stub", 0.039, 0.42, mats["steel"], loc=(0.37 * math.sin(math.radians(-28)), -0.37 * math.cos(math.radians(-28)), 0.21), axis="X")
bpy.data.objects["stub"].rotation_euler = (0, math.pi / 2, math.radians(-28))
# second unit blurred in the background
H.load_unit("IRAM_93-160_L", mats, spin=55, loc=(-1.6, 1.4, 0))
H.load_unit("MA_703-G00", mats, spin=200, loc=(1.3, 2.3, 0))

target = Vector((0.12, -0.25, 0.22))
H.light_area("key", (1.4, -1.6, 1.6), target, 170, 1.2, (1.0, 0.95, 0.88))
H.light_area("fill", (-1.8, -1.4, 0.8), target, 50, 2.5, (0.9, 0.93, 1.0))
H.light_area("rim", (-0.8, 1.6, 1.4), target, 420, 0.8, (0.75, 0.85, 1.0))
H.light_area("rim2", (1.6, 1.2, 0.9), target, 200, 0.6, (0.75, 0.85, 1.0))
H.light_area("top", (0.2, 0.0, 3.0), target, 40, 2.0, (1, 1, 1))

H.camera((1.25, -1.55, 0.42), (0.02, -0.08, 0.24), lens=70, fstop=2.2, focus=(0.22, -0.42, 0.24), shift=(-0.07, 0.0))
H.render("hero_closeup_irkm93", exposure=-0.5)
