"""Social post (4:5): i.Mak IRC 93 hoist drive with motor on a hoist trolley, splined output shaft
and splined drum hub pulled slightly apart so the spline connection is the hero detail.
Renders 2160x2700; text/logo layout is added by tools/post_layout.py.
python3 tools/scene_irc_post.py [--preview] [--samples N] [--scale F]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import bmesh
from mathutils import Vector, Matrix
import hero_lib as H

H.fresh()
mats = H.M()
# deeper, less glossy red: real painted cast iron rather than a clear-coated show finish
mats["paint"] = H.mat("imak red", (0.52, 0.012, 0.012), 0.0, 0.52, coat=0.08, spec=0.38, bump=(900, 0.05))
H.world_dark(0.30, haze=0.003, tint=(0.85, 0.9, 1.0))
crane_m = H.mat("crane yellow", (0.72, 0.40, 0.02), 0.0, 0.42, coat=0.2, bump=(300, 0.02))
drum_m = H.mat("drum", (0.22, 0.22, 0.21), 0.85, 0.42, bump=(200, 0.03))
rope_m = H.mat("rope", (0.17, 0.16, 0.14), 0.9, 0.6, aniso=0.6)
spline_m = H.mat("spline steel", (0.75, 0.75, 0.74), 1.0, 0.22, aniso=0.3)
conc = mats["concrete"]
wall_m = mats["wall"]
frame = mats["frame"]


def prism(name, outer, inner, length, m, loc=(0, 0, 0)):
    """Extrude a ring profile (outer loop, optional inner loop with the same vertex count) along +X."""
    bm = bmesh.new()
    vo0 = [bm.verts.new((0, x, y)) for x, y in outer]
    vo1 = [bm.verts.new((length, x, y)) for x, y in outer]
    vi0 = [bm.verts.new((0, x, y)) for x, y in inner] if inner else None
    vi1 = [bm.verts.new((length, x, y)) for x, y in inner] if inner else None
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vo0[i], vo0[j], vo1[j], vo1[i]))
        if inner:
            bm.faces.new((vi0[j], vi0[i], vi1[i], vi1[j]))
            bm.faces.new((vo0[j], vo0[i], vi0[i], vi0[j]))
            bm.faces.new((vo1[i], vo1[j], vi1[j], vi1[i]))
    if not inner:
        bm.faces.new(list(reversed(vo0)))
        bm.faces.new(vo1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return H.obj_from_bmesh(bm, name, m, loc=loc)


def star(n, r1, r2, phase=0.0):
    """Square-toothed spline profile: n teeth, 4 points per tooth (outer r1, root r2)."""
    out = []
    for i in range(n):
        a0 = phase + 2 * math.pi * i / n
        w = math.pi / n * 0.45
        out += [(r2 * math.cos(a0 - w * 1.05), r2 * math.sin(a0 - w * 1.05)), (r1 * math.cos(a0 - w), r1 * math.sin(a0 - w)),
                (r1 * math.cos(a0 + w), r1 * math.sin(a0 + w)), (r2 * math.cos(a0 + w * 1.05), r2 * math.sin(a0 + w * 1.05))]
    return out


def circle(n, r):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# ---------------------------------------------------------------- hall
H.plane("floor", (80, 80), conc, loc=(0, 0, -6.5))
H.box("backwall", (60, 0.4, 14), wall_m, loc=(0, 14, 0.5))
for i in range(-4, 5):
    H.box(f"roofbeam{i}", (0.3, 30, 0.6), frame, loc=(i * 6, 2, 5.5))
H.box("roof", (60, 30, 0.1), wall_m, loc=(0, 2, 5.9))
sky_m = H.mat("skylight", (1, 1, 1), 0.0, 0.5, emit=((1.0, 0.97, 0.9), 1.2))
for i in range(-4, 4):
    H.box(f"sky{i}", (0.9, 26, 0.05), sky_m, loc=(i * 6 + 3, 2, 5.84))
for i in range(-4, 5):
    H.box(f"colA{i}", (0.35, 0.35, 12.5), frame, loc=(i * 6 + 2, -2.2, -0.25))
    H.box(f"colB{i}", (0.35, 0.35, 12.5), frame, loc=(i * 6 + 2, 13.5, -0.25))
H.box("runway2", (60, 0.3, 0.6), frame, loc=(0, 13.2, 0.9))
win_m = H.mat("window", (1, 1, 1), 0.0, 0.5, emit=((0.85, 0.92, 1.0), 1.1))
for i in range(-5, 6):
    H.box(f"win{i}", (3.6, 0.05, 1.6), win_m, loc=(i * 5 + 2.5, 13.78, 2.6))
    H.box(f"winb{i}", (3.6, 0.05, 1.0), win_m, loc=(i * 5 + 2.5, 13.78, -1.2))
H.box("girder2", (0.5, 14.4, 0.9), crane_m, loc=(3.5, 6.3, 1.9))
H.box("girder2b", (0.5, 14.4, 0.9), crane_m, loc=(4.6, 6.3, 1.9))

# ---------------------------------------------------------------- hoist trolley frame
WZ = 1.30                       # drum / output axis height
FY = 0.42                        # hoist frame beam y (behind the unit)
H.box("frame_beam", (2.9, 0.26, 0.28), crane_m, loc=(0.7, FY, WZ + 1.30), bevel=0.004)
H.box("frame_beam2", (2.9, 0.26, 0.28), crane_m, loc=(0.7, FY + 0.95, WZ + 1.30), bevel=0.004)
for x in (-0.65, 2.05):
    H.box(f"frame_x{x}", (0.26, 1.0, 0.22), crane_m, loc=(x, FY + 0.47, WZ + 1.30))
# gearbox hangs on a vertical plate welded under the beam
H.box("mount_plate", (0.03, 0.30, 1.40), crane_m, loc=(-0.23, 0.02, WZ + 0.46), bevel=0.003)
H.box("mount_gusset", (0.03, 0.26, 0.26), crane_m, loc=(-0.23, 0.02 + 0.15 + 0.13, WZ + 1.16 - 0.13))

# ---------------------------------------------------------------- IRC 93 (shaft face to +X) + motor
u = H.load_unit("IRC_93", mats, spin=-90)        # shaft face now looks to +X
out_z = 0.16
GZ = WZ - out_z
u["parent"].location = (0.0, 0.0, GZ)
bpy.context.view_layer.update()
in_c = Vector((0.16, -0.03, 0.50))               # input shaft centre after the spin (unit local)
out_c = Vector((0.01, 0.01, out_z))              # output shaft centre
FX = 0.21                                        # shaft face x
BX0, BX1 = 0.135, 0.355                          # input boss face .. motor front
H.cyl("bell", 0.105, BX1 - BX0, mats["paint"], loc=((BX0 + BX1) / 2, in_c.y, GZ + in_c.z), axis="X", seg=96, chamfer=0.008)
H.cyl("bell_fl0", 0.135, 0.022, mats["paint"], loc=(BX0 + 0.011, in_c.y, GZ + in_c.z), axis="X", seg=96)
H.cyl("bell_fl1", 0.16, 0.022, mats["paint"], loc=(BX1 - 0.011, in_c.y, GZ + in_c.z), axis="X", seg=96)
H.bolts("bellb", [(BX1 + 0.004, in_c.y + 0.145 * math.cos(math.radians(a)), GZ + in_c.z + 0.145 * math.sin(math.radians(a))) for a in range(0, 360, 45)], mats["bolt"], r=0.009, h=0.012, axis="X")
m = H.load_unit("IRAM_93-160_L", mats, spin=-90)  # motor end now points to +X
ZCUT = -157.0                                    # raw STEP z (mm): motor at z < -157
for o in m["objs"]:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, ZCUT), plane_no=(0, 0, 1), clear_outer=True)
    bm.to_mesh(o.data)
    bm.free()
MOTOR_FACE = 0.315                               # motor front face x (unit local): where the fins start
m["parent"].location = (BX1 - MOTOR_FACE, in_c.y, GZ + in_c.z - 0.21)

# ---------------------------------------------------------------- splined output shaft -> drum hub (pulled apart)
SX0 = FX - 0.02
SL = 0.26
NT = 24
prism("spline_shaft", star(NT, 0.040, 0.034), None, SL, spline_m, loc=(SX0, out_c.y, GZ + out_c.z))
H.cyl("spline_end", 0.030, 0.012, spline_m, loc=(SX0 + SL + 0.006, out_c.y, GZ + out_c.z), axis="X", seg=64, chamfer=0.004)
H.cyl("shaft_root", 0.046, 0.03, spline_m, loc=(FX + 0.015, out_c.y, GZ + out_c.z), axis="X", seg=64)
HX = SX0 + SL + 0.08                             # hub front face
prism("hub_boss", circle(4 * NT, 0.075), star(NT, 0.0415, 0.0355), 0.11, spline_m, loc=(HX, out_c.y, GZ + out_c.z))
prism("hub_flange", circle(4 * NT, 0.125), star(NT, 0.0415, 0.0355), 0.025, spline_m, loc=(HX + 0.085, out_c.y, GZ + out_c.z))
H.bolts("hubb", [(HX + 0.085 - 0.004, out_c.y + 0.105 * math.cos(math.radians(a)), GZ + out_c.z + 0.105 * math.sin(math.radians(a))) for a in range(0, 360, 45)], mats["bolt"], r=0.008, h=0.012, axis="X")
DX0 = HX + 0.11                                  # drum end plate
RD = 0.165
H.cyl("drum_plate", 0.20, 0.025, drum_m, loc=(DX0 + 0.0125, out_c.y, GZ + out_c.z), axis="X", seg=128)
H.cyl("drum", RD, 0.95, drum_m, loc=(DX0 + 0.025 + 0.475, out_c.y, GZ + out_c.z), axis="X", seg=128)
H.cyl("drum_plate2", 0.20, 0.025, drum_m, loc=(DX0 + 0.025 + 0.95 + 0.0125, out_c.y, GZ + out_c.z), axis="X", seg=128)
for i in range(46):
    H.torus(f"rope{i}", RD + 0.006, 0.0085, rope_m, loc=(DX0 + 0.05 + i * 0.0185, out_c.y, GZ + out_c.z), rot=(0, math.pi / 2, 0), seg=96, rseg=12)
for x in (DX0 + 0.05, DX0 + 0.05 + 45 * 0.0185):
    H.cyl(f"fall{x}", 0.0085, 3.0, rope_m, loc=(x, out_c.y - RD - 0.006, GZ + out_c.z - 1.5), seg=12)
H.box("ped_base", (0.22, 0.30, 0.03), crane_m, loc=(DX0 + 1.08, out_c.y, WZ - 0.34), bevel=0.003)
H.box("ped_col", (0.16, 0.18, 0.22), crane_m, loc=(DX0 + 1.08, out_c.y, WZ - 0.21))
H.cyl("ped_brg", 0.085, 0.11, mats["steel"], loc=(DX0 + 1.08, out_c.y, WZ), axis="X", seg=96, chamfer=0.006)
H.cyl("ped_shaft", 0.035, 0.10, spline_m, loc=(DX0 + 1.03, out_c.y, WZ), axis="X", seg=48)
H.box("ped_hanger", (0.16, 0.03, 1.16), crane_m, loc=(DX0 + 1.08, out_c.y + 0.10, WZ + 0.58))
H.box("ped_hanger2", (0.16, 0.42, 0.03), crane_m, loc=(DX0 + 1.08, out_c.y + 0.30, WZ + 1.15))

# ---------------------------------------------------------------- dust in the air
dust_m = H.mat("dust", (0.9, 0.85, 0.7), 0.0, 0.6)
rnd = random.Random(7)
bm = bmesh.new()
for i in range(110):
    x, y, z = rnd.uniform(-1.4, 1.8), rnd.uniform(-1.3, 0.6), rnd.uniform(WZ - 0.8, WZ + 1.3)
    r = rnd.uniform(0.0015, 0.0045)
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((x, y, z)))
H.obj_from_bmesh(bm, "dust", dust_m)

# ---------------------------------------------------------------- lights & camera
target = Vector((0.30, -0.05, GZ + 0.30))
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 1.5
sun.angle = math.radians(2.0)
sun.color = (1.0, 0.85, 0.65)
so = bpy.data.objects.new("sun", sun)
bpy.context.collection.objects.link(so)
so.rotation_euler = (math.radians(52), 0, math.radians(-35))
H.light_area("key", (1.6, -2.4, GZ + 1.9), target, 520, 1.4, (1.0, 0.94, 0.86))
H.light_area("fill", (-2.6, -2.0, GZ + 0.6), target, 150, 4.0, (0.85, 0.9, 1.0))
H.light_area("rim", (0.2, 2.8, GZ + 2.4), target, 1200, 1.2, (1.0, 0.8, 0.6))
H.light_area("spline_acc", (0.45, -0.9, GZ + 0.05), Vector((SX0 + SL / 2, out_c.y, GZ + out_c.z)), 60, 0.3, (1.0, 0.95, 0.9))
if os.environ.get("CAM") == "input":
    H.camera((0.25, -1.7, GZ + 0.55), (0.25, 0.0, GZ + 0.45), lens=50, fstop=8.0)
else:
    H.camera((-0.9, -2.2, GZ + 0.45), (0.32, 0.0, GZ + 0.30), lens=50, fstop=4.0, focus=(SX0 + SL / 2, out_c.y, GZ + out_c.z), shift=(0.0, 0.14))
# screen position of the spline (for the layout call-out)
from bpy_extras.object_utils import world_to_camera_view
import json
sc = bpy.context.scene
bpy.context.view_layer.update()
ndc = world_to_camera_view(sc, sc.camera, Vector((SX0 + SL * 0.55, out_c.y, GZ + out_c.z + 0.03)))
json.dump({"spline": [ndc.x, 1 - (ndc.y + sc.camera.data.shift_y)]}, open(os.path.join(H.PREVIEW_DIR if H.PREVIEW else H.OUT, "irc_post_raw.json"), "w"))
skip = os.environ.get("SKIP", "").split(",")
if "motor" in skip:
    for o in m["objs"]:
        o.hide_render = True
if "bell" in skip:
    for nm in ("bell", "bell_fl0", "bell_fl1"):
        bpy.data.objects[nm].hide_render = True
if os.environ.get("NORENDER"):
    for nm in ("IRC_93_paint", "bell", "bell_fl0", "bell_fl1", "spline_end", "IRAM_93-160_L_paint", "spline_shaft", "hub_boss"):
        o = bpy.data.objects[nm]
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        print("%-22s x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f" % (nm, min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts), min(p.z for p in pts), max(p.z for p in pts)))
    for nm in ("bell", "bell_fl0", "bell_fl1", "spline_end"):
        o = bpy.data.objects[nm]
        print(nm, "polys", len(o.data.polygons), "hide_render", o.hide_render, "cols", [c.name for c in o.users_collection], "vis", o.visible_get(), "mats", [x.name for x in o.data.materials], "scale", tuple(o.scale), "rot", tuple(round(a, 2) for a in o.rotation_euler))
    for sh in u["shafts"]:
        print("IRC shaft r=%.3f c=(%.3f %.3f %.3f) axis=(%.0f %.0f %.0f)" % (sh["r"], *sh["c"], *sh["axis"]))
else:
    H.render("irc_post_raw", w=2160, h=2700, exposure=-0.7)
