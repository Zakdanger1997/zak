"""Hero 2: i.Mak IRKM 93-160 L helical-bevel geared motor driving a vertical agitator on a
stainless process tank (wall-mounted bracket, output shaft down).
python3 tools/scene_agitator.py [--preview] [--samples N] [--scale F]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import hero_lib as H

H.fresh()
mats = H.M()
H.world_dark(0.12, haze=0.002)
H.hall(mats, floor=60, ceiling_h=8.0)
# extra: brushed stainless tank material with a little anisotropy, and a pale blue-grey painted bridge
tank_m = H.mat("tank stainless", (0.10, 0.105, 0.11), 0.9, 0.48, aniso=0.0, bump=(400, 0.03))
bridge_m = mats["frame"]

# ---------------------------------------------------------------- tank
RT, HT = 1.15, 2.3       # tank radius, shell height
ZB = 0.55                # bottom of shell (on legs)
H.cyl("shell", RT, HT, tank_m, loc=(0, 0, ZB + HT / 2), seg=160)
# dished top and bottom: shallow spheres clipped by the shell
for nm, zc, sgn in (("top", ZB + HT, 1), ("bot", ZB, -1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=RT * 1.9, segments=128, ring_count=64, location=(0, 0, zc - sgn * RT * 1.9 * 0.93))
    o = bpy.context.object
    o.name = "dish_" + nm
    o.data.materials.append(tank_m)
    bpy.ops.object.shade_smooth()
    bpy.ops.object.modifier_add(type="BOOLEAN")
    cutter = H.cyl("cut_" + nm, RT, 1.0, tank_m, loc=(0, 0, zc + sgn * 0.5), seg=160)
    cutter.hide_render = True
    cutter.hide_viewport = True
    o.modifiers[-1].operation = "INTERSECT"
    o.modifiers[-1].object = cutter
    o.modifiers[-1].solver = "EXACT"
# stiffening rings and legs
for z in (ZB + 0.4, ZB + HT - 0.4):
    H.torus("ring%.1f" % z, RT + 0.015, 0.03, tank_m, loc=(0, 0, z))
for i in range(4):
    a = math.radians(45 + 90 * i)
    x, y = (RT - 0.08) * math.cos(a), (RT - 0.08) * math.sin(a)
    H.cyl(f"leg{i}", 0.06, ZB + 0.45, tank_m, loc=(x, y, (ZB + 0.45) / 2), seg=32)
    H.box(f"legpad{i}", (0.22, 0.22, 0.015), tank_m, loc=(x, y, 0.0075))
# nozzles, manway, ladder
H.cyl("nozzle1", 0.08, 0.25, tank_m, loc=(RT + 0.1, 0.0, ZB + HT - 0.5), axis="X")
H.cyl("nozzle1f", 0.13, 0.03, tank_m, loc=(RT + 0.22, 0.0, ZB + HT - 0.5), axis="X")
H.cyl("nozzle2", 0.06, 0.25, tank_m, loc=(RT + 0.1, -0.5, ZB + 0.35), axis="X")
H.cyl("nozzle2f", 0.11, 0.03, tank_m, loc=(RT + 0.22, -0.5, ZB + 0.35), axis="X")
H.cyl("manway", 0.25, 0.12, tank_m, loc=(0.55, 0.0, ZB + HT + 0.17), seg=64)
H.cyl("manway_lid", 0.30, 0.03, tank_m, loc=(0.55, 0.0, ZB + HT + 0.24), seg=64)
H.cyl("drain", 0.05, 0.3, tank_m, loc=(0, 0, ZB - 0.25), seg=32)
for s in (-1, 1):                                   # ladder on the far side
    H.cyl(f"ladder{s}", 0.02, HT + 0.6, mats["galv"], loc=(-RT - 0.2, s * 0.25 + 0.6, ZB + HT / 2 + 0.2), seg=16)
for k in range(9):
    H.cyl(f"rung{k}", 0.012, 0.5, mats["galv"], loc=(-RT - 0.2, 0.6, ZB + 0.3 + k * 0.3), axis="Y", seg=12)

# ---------------------------------------------------------------- bridge and drive
ZT = ZB + HT + 0.06                                  # top of the shell flange
BZ = ZT + 0.12                                        # bridge top
for s in (-1, 1):                                     # two I-beams across the tank
    y = s * 0.33
    H.box(f"beam_web{s}", (RT * 2 + 0.5, 0.012, 0.18), bridge_m, loc=(0, y, BZ - 0.1))
    H.box(f"beam_top{s}", (RT * 2 + 0.5, 0.12, 0.012), bridge_m, loc=(0, y, BZ - 0.006))
    H.box(f"beam_bot{s}", (RT * 2 + 0.5, 0.12, 0.012), bridge_m, loc=(0, y, BZ - 0.194))
    for sx in (-1, 1):
        H.box(f"beam_sup{s}{sx}", (0.2, 0.2, 0.08), bridge_m, loc=(sx * (RT - 0.05), y, ZT + 0.02))
H.box("deck", (0.9, 0.9, 0.025), bridge_m, loc=(0, 0, BZ + 0.0125), bevel=0.003)

# IRKM 93-160 L: output hollow shaft along X at z=0.21 when on its feet, motor along +Y.
# rotate 90 deg about Y: output points down (-Z), feet face -X -> bolted to a vertical bracket plate.
u = H.load_unit("IRKM_93-160_L", mats)
R = Euler((0, math.radians(90), 0))
for o in u["objs"]:
    o.rotation_euler = (R.to_matrix() @ o.rotation_euler.to_matrix()).to_euler()
    o.location = R.to_matrix() @ o.location
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in u["objs"] for c in o.bound_box]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
# shaft axis (was x=0 after centring, y=-0.37, z=0.21) is now at x = 0.21, y=-0.37 ... re-derive from rotated shafts
ax = [s for s in u["shafts"] if abs(s["axis"].x) > 0.9 and s["r"] > 0.07]
sc = ax[0]["c"] - u["parent"].location          # local centre before rotation
sc = R.to_matrix() @ sc                          # after rotation
# place the parent so the shaft is on the tank axis and the unit sits just above the bridge deck
pz = BZ + 0.025 + 0.30 - mn.z
u["parent"].location = (-sc.x, -sc.y, pz)
bpy.context.view_layer.update()
feet_x = mn.x - sc.x                              # world x of the feet plane (faces -X)
# bracket: vertical plate under the gearbox feet only (the motor overhangs), on a welded pedestal
GY0, GY1 = mn.y - sc.y - 0.04, mn.y - sc.y + 0.40          # gearbox end of the unit (motor is at +Y)
gyc = (GY0 + GY1) / 2
gz0, gz1 = pz + mn.z - 0.05, pz + mx.z + 0.05
plate = H.box("bracket_plate", (0.03, GY1 - GY0, gz1 - gz0), bridge_m, loc=(feet_x - 0.015, gyc, (gz0 + gz1) / 2), bevel=0.003)
H.box("bracket_base", (0.50, GY1 - GY0, 0.03), bridge_m, loc=(feet_x - 0.25, gyc, BZ + 0.04), bevel=0.003)
H.box("bracket_col", (0.12, GY1 - GY0 - 0.06, gz0 - BZ - 0.055), bridge_m, loc=(feet_x - 0.09, gyc, (gz0 + BZ + 0.055) / 2))
for s_ in (-1, 1):
    H.box(f"bracket_rib{s_}", (0.30, 0.015, 0.25), bridge_m, loc=(feet_x - 0.17, gyc + s_ * ((GY1 - GY0) / 2 - 0.0075), gz0 + 0.12))
# agitator shaft through the hollow shaft, stuffing box on the deck, impellers inside (not visible, closed tank)
H.cyl("agit_shaft", 0.038, 1.2, mats["stainless"], loc=(0, 0, BZ + 0.1), seg=48)
H.cyl("stuffing_box", 0.11, 0.16, tank_m, loc=(0, 0, BZ + 0.025 + 0.08), seg=64, chamfer=0.008)
H.cyl("stuffing_fl", 0.16, 0.025, tank_m, loc=(0, 0, BZ + 0.025 + 0.17), seg=64)
H.bolts("stuff", [(0.13 * math.cos(math.radians(a)), 0.13 * math.sin(math.radians(a)), BZ + 0.025 + 0.19) for a in range(0, 360, 60)], mats["bolt"], r=0.009, h=0.012)
# foundation bolts on the bracket feet
H.bolts("feet", [(feet_x + 0.012, gyc + sy * 0.13, pz + (mn.z + mx.z) / 2 + sz * 0.11) for sy in (-1, 1) for sz in (-1, 1)],
        mats["bolt"], r=0.009, h=0.016, axis="X")

# hall columns and roof beams for depth
for i, (x, y) in enumerate(((-7, 7), (-1, 7), (5, 7), (11, 7), (-7, 15), (-1, 15), (5, 15), (11, 15))):
    H.box(f"col{i}", (0.3, 0.3, 8.0), bridge_m, loc=(x, y, 4.0))
for i in range(3):
    H.box(f"bgbeam{i}", (26, 0.25, 0.5), bridge_m, loc=(2, 7 + 4 * i, 6.3))
# a second, smaller tank far behind
H.cyl("shell2", 0.9, 2.0, tank_m, loc=(-3.6, 4.2, 1.5), seg=96)
H.cyl("shell3", 0.9, 2.0, tank_m, loc=(2.6, 5.0, 1.5), seg=96)

# ---------------------------------------------------------------- lights & camera
target = Vector((0.05, -0.15, pz + (mn.z + mx.z) / 2))
H.light_area("key", (2.4, -2.8, pz + 2.2), target, 1100, 1.6, (1.0, 0.95, 0.88))
H.light_area("fill", (-2.8, -2.6, pz + 1.0), target, 350, 4.0, (0.9, 0.93, 1.0))
H.light_area("rim", (-1.6, 2.6, pz + 4.2), target, 700, 1.0, (0.75, 0.85, 1.0))
H.light_area("top", (0, 0, pz + 4.5), target, 150, 3.0, (1, 1, 1))
H.light_area("hall", (2, 9, 7.5), (2, 9, 0), 1500, 10.0, (0.85, 0.9, 1.0))
cam_loc = Vector((1.75, -1.75, pz + 0.65))
H.camera(cam_loc, (0.1, -0.05, pz + 0.0), lens=45, fstop=4.0, focus=(0.05, -0.3, pz + 0.1), shift=(-0.04, 0.0))
H.render("hero_agitator_irkm93", exposure=-0.45)
