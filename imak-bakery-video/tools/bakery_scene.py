#!/usr/bin/env python3
"""Clay-style 3D bakery line with real i.Mak drives (RAL 3020) – Cycles, one continuous camera move.

Usage: python3 tools/bakery_scene.py [--frames A-B] [--step N] [--samples N] [--res WxH] [--still F]
Frames -> render/line/####.png. Stations along +X: feeding (silo, screw, mixer), extruder, tunnel oven,
spiral freezer, linked by belt conveyors. Drives are the official i.Mak STEP models (step_parts.py meshes):
YPM 93 on the mixer, MK 703 on the extruder, IRSDM 83 on the oven conveyor, IRKM 93 on the spiral drum.
Camera timing is in CAM (seconds at 24 fps) and must match tools/timeline.py.
"""
import math
import os
import sys

import bpy  # noqa
import bmesh  # noqa
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PARTS = os.environ.get("PARTS", "/tmp/claude-0/cad/parts")
A = sys.argv[1:]
arg = lambda n, d: A[A.index(n) + 1] if n in A else d
SAMPLES = int(arg("--samples", 20))
RES = [int(v) for v in arg("--res", "1600x900").split("x")]
FPS = 24
TAU = math.pi * 2
BG = (0.016, 0.024, 0.036)          # dark slate (linear)
RAL3020 = (0.6038, 0.0018, 0.0015)

# --------------------------------------------------------------- materials
def mat(name, col, rough=0.55, metal=0.0, coat=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Specular IOR Level"].default_value = 0.3
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = 3.0
    return m


M = {}


def mats():
    M["clay"] = mat("clay", (0.80, 0.81, 0.82), 0.62)
    M["clay2"] = mat("clay darker", (0.62, 0.64, 0.66), 0.6)
    M["glass"] = mat("window", (0.25, 0.32, 0.38), 0.15, coat=0.5)
    M["belt"] = mat("belt", (0.18, 0.19, 0.20), 0.7)
    M["red"] = mat("RAL 3020", RAL3020, 0.42, coat=0.4)
    M["steel"] = mat("steel", (0.85, 0.86, 0.88), 0.2, 1.0)
    M["floor"] = mat("floor", BG, 0.9)
    M["dough"] = mat("dough", (0.80, 0.62, 0.36), 0.7)
    M["bun"] = mat("baked", (0.52, 0.24, 0.07), 0.55, coat=0.2)
    M["glow"] = mat("oven glow", (0.9, 0.4, 0.1), 0.5, emit=(1.0, 0.42, 0.12))


# --------------------------------------------------------------- helpers
def obj_done(o, m, bevel=0.0, smooth=False):
    o.data.materials.append(M[m] if isinstance(m, str) else m)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    if smooth:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    return o


def box(sx, sy, sz, loc, m="clay", bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj_done(o, m, bevel)


def cyl(r, h, loc, m="clay", axis="Z", verts=48, bevel=0.01):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.object
    if axis == "X":
        o.rotation_euler = (0, math.radians(90), 0)
    elif axis == "Y":
        o.rotation_euler = (math.radians(90), 0, 0)
    return obj_done(o, m, bevel, smooth=True)


def cone(r1, r2, h, loc, m="clay"):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=h, location=loc, vertices=48)
    return obj_done(bpy.context.object, m, 0.01, smooth=True)


def rod(a, b, r, m="clay"):
    a, b = Vector(a), Vector(b)
    d = b - a
    o = cyl(r, d.length, (a + b) / 2, m, verts=16, bevel=0)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


def legs(x0, x1, y0, y1, h, r=0.05):
    for x in (x0, x1):
        for y in (y0, y1):
            rod((x, y, 0), (x, y, h), r, "clay2")


def unit(name, loc, rot=(0, 0, 0), scale=1.0):
    """Import an i.Mak drive (paint/steel/bore meshes), RAL 3020 paint; STEP Y up."""
    objs = []
    for part, m in (("paint", "red"), ("steel", "steel"), ("bore", "steel")):
        f = os.path.join(PARTS, f"{name}_{part}.stl")
        if not os.path.exists(f) or os.path.getsize(f) < 200:
            continue
        bpy.ops.wm.stl_import(filepath=f, global_scale=0.001 * scale)
        o = bpy.context.selected_objects[0]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.data.materials.append(M[m])
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
        objs.append(o)
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for o in objs:
        o.parent = root
    root.rotation_euler = (math.radians(90) + rot[0], rot[1], rot[2])
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    c = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])
    root.location = Vector(loc) - Vector((c.x, c.y, min(p.z for p in pts)))
    return root


def mount(name, out_pt, out_ax, side_ax, w_pt, w_ax, w_side, scale=1.0):
    """Place an i.Mak unit so its output shaft (STEP mm point + axis) sits on a driven shaft in the world.
    side_ax (STEP) is turned to w_side (world) to fix the roll about the shaft."""
    from mathutils import Matrix
    objs = []
    for part, m in (("paint", "red"), ("steel", "steel"), ("bore", "steel")):
        f = os.path.join(PARTS, f"{name}_{part}.stl")
        if not os.path.exists(f) or os.path.getsize(f) < 200:
            continue
        bpy.ops.wm.stl_import(filepath=f, global_scale=0.001 * scale)
        o = bpy.context.selected_objects[0]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.data.materials.append(M[m])
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
        objs.append(o)
    def frame(a, b):
        a = Vector(a).normalized(); b = (Vector(b) - Vector(b).project(a)).normalized()
        return Matrix((a, b, a.cross(b))).transposed()
    R = frame(w_ax, w_side) @ frame(out_ax, side_ax).inverted()
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for o in objs:
        o.parent = root
    root.matrix_world = Matrix.Translation(Vector(w_pt) - R @ (Vector(out_pt) * 0.001 * scale)) @ R.to_4x4()
    return root


def motor(start, direction, length=0.55, r=0.14):
    """IEC motor in RAL 3020: flange, finned body, fan cover, terminal box; from start along direction."""
    d = Vector(direction).normalized(); a = Vector(start)
    q = d.to_track_quat("Z", "Y")
    def part(r_, l_, off, m="red", verts=40):
        o = cyl(r_, l_, a + d * (off + l_ / 2), m, verts=verts)
        o.rotation_euler = q.to_euler()
        return o
    part(r + 0.03, 0.04, 0.0)
    part(r, length * 0.7, 0.04, verts=24)
    for k in range(16):
        ang = TAU * k / 16
        side = (q @ Vector((math.cos(ang), math.sin(ang), 0))) * (r + 0.008)
        b = box(0.02, 0.02, length * 0.66, a + d * (0.04 + length * 0.35) + side, "red", 0.004)
        b.rotation_euler = q.to_euler()
    part(r * 0.95, length * 0.26, 0.04 + length * 0.7, "clay2")
    up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    box(0.16, 0.16, 0.12, a + d * (0.04 + length * 0.3) + up * (r + 0.06), "red", 0.01)


# --------------------------------------------------------------- machines
MOVERS = []          # (object, function(t) -> (location, rotation))


def conveyor(x0, x1, y, z, w=0.7, items=None, speed=0.35, item_mat="dough", gap=0.45, flat=True):
    """Belt conveyor along X between x0 and x1 at height z; products ride on it."""
    L = x1 - x0
    box(L, w, 0.06, ((x0 + x1) / 2, y, z), "belt", 0.01)
    box(L, 0.05, 0.16, ((x0 + x1) / 2, y - w / 2 - 0.03, z - 0.02), "clay2", 0.01)
    box(L, 0.05, 0.16, ((x0 + x1) / 2, y + w / 2 + 0.03, z - 0.02), "clay2", 0.01)
    for x in (x0, x1):
        cyl(0.05, w + 0.05, (x, y, z - 0.01), "clay2", axis="Y")
    n = max(2, int(L / 1.6))
    for i in range(n + 1):
        xx = x0 + 0.2 + (L - 0.4) * i / n
        rod((xx, y - w / 2, 0), (xx, y - w / 2, z - 0.05), 0.03, "clay2")
        rod((xx, y + w / 2, 0), (xx, y + w / 2, z - 0.05), 0.03, "clay2")
    if items is None:
        return
    rows = int(L / gap)
    for i in range(rows):
        for j, dy in enumerate((-0.18, 0.0, 0.18) if w > 0.5 else (0.0,)):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0, 0, 0), segments=20, ring_count=10)
            o = bpy.context.object
            o.scale = (1, 1, 0.55 if flat else 0.8)
            obj_done(o, item_mat, smooth=True)
            s0 = i * gap + j * 0.07

            def f(t, o=o, s0=s0, dy=dy):
                s = (s0 + speed * t) % (rows * gap)
                return (x0 + s, y + dy, z + 0.07), None
            MOVERS.append((o, f))


def feeding(X):
    """Flour silo, inclined screw conveyor, spiral mixer with YPM drive."""
    cyl(1.0, 3.6, (X + 0.6, 2.8, 3.4), "clay")
    cone(1.0, 0.18, 1.0, (X + 0.6, 2.8, 1.1), "clay")
    cone(1.03, 0.4, 0.4, (X + 0.6, 2.8, 5.4), "clay2")
    legs(X - 0.1, X + 1.3, 2.1, 3.5, 1.6)
    top, bot = Vector((X + 2.6, 1.5, 2.6)), Vector((X + 0.6, 2.8, 0.55))
    rod(bot, top, 0.16, "clay")                                                  # screw conveyor tube
    cyl(0.19, 0.08, top, "clay2").rotation_euler = (top - bot).to_track_quat("Z", "Y").to_euler()
    rod((X + 2.6, 1.5, 2.6), (X + 2.95, 0.95, 2.15), 0.12, "clay")               # discharge spout to the mixer
    dz = (top - bot).normalized()
    mount("IRAM_93-160_L", (0, 20, 467), (0, 0, 1), (0, 1, 0), top + dz * 0.04, -dz, (0, 0, 1), scale=0.8)
    # spiral mixer: base, bowl, column, head; IR inline geared motor vertical on the head drives the hook
    box(1.6, 1.6, 0.5, (X + 3.4, 0.4, 0.25), "clay2", 0.04)
    bowl = cyl(0.75, 0.85, (X + 3.4, 0.4, 0.95), "clay", verts=64)
    MOVERS.append((bowl, lambda t: (None, (0, 0, t * 0.9))))
    box(0.5, 0.5, 2.4, (X + 4.45, 0.4, 1.2), "clay", 0.04)
    box(1.5, 0.55, 0.45, (X + 3.9, 0.4, 2.25), "clay", 0.06)
    rod((X + 3.4, 0.4, 2.0), (X + 3.4, 0.4, 1.0), 0.05, "steel")
    mount("IRAM_93-160_L", (0, 20, 467), (0, 0, 1), (0, 1, 0), (X + 3.4, 0.4, 2.48), (0, 0, -1), (1, 0, 0), scale=0.8)
    return (X + 3.4, 0.4, 1.2)


def extruder(X):
    """Food extruder: frame, hopper, barrel with die; MK 703 gear unit + motor at the drive end."""
    box(6.0, 1.1, 0.7, (X + 3.0, 0, 0.35), "clay2", 0.04)
    box(5.0, 0.7, 0.35, (X + 3.4, 0, 0.88), "clay", 0.03)
    cyl(0.28, 4.2, (X + 3.6, 0, 1.35), "clay", axis="X", verts=48)
    for i in range(6):
        cyl(0.33, 0.12, (X + 1.8 + i * 0.7, 0, 1.35), "clay2", axis="X")
    cone(0.5, 0.18, 0.7, (X + 2.0, 0, 2.0), "clay")
    cyl(0.5, 0.35, (X + 2.0, 0, 2.5), "clay")
    cone(0.28, 0.12, 0.4, (X + 5.9, 0, 1.35), "clay2").rotation_euler = (0, math.radians(90), 0)
    box(1.5, 1.1, 0.7, (X - 0.76, 0, 0.35), "clay2", 0.04)                       # drive end of the frame
    mount("MA703-G00", (0, 0, 249), (0, 0, 1), (-1, 0, 0), (X + 1.5, 0, 1.35), (1, 0, 0), (0, 0, -1), scale=0.9)
    cx_in = X + 1.5 - 0.9 * (249 + 316) / 1000.0                                 # input shaft end (behind)
    zin = 1.35 - 0.9 * 0.497
    cyl(0.09, 0.14, (cx_in - 0.07, 0, zin), "clay2", axis="X")                    # coupling
    motor((cx_in - 0.14, 0, zin), (-1, 0, 0), length=0.75, r=0.17)
    return (X + 2.5, 0, 1.3)


def oven(X, L=11.0):
    """Tunnel oven with glowing windows; IRSDM drives the conveyor at the outlet."""
    box(L, 2.0, 1.5, (X + L / 2, 0, 1.25), "clay", 0.05)
    box(L - 0.4, 2.05, 0.18, (X + L / 2, 0, 0.62), "clay2", 0.02)
    for i in range(7):
        box(0.9, 0.04, 0.35, (X + 1.2 + i * 1.45, -1.02, 1.25), "glow", 0.01)
    for i in range(3):
        cyl(0.14, 1.0, (X + 2.0 + i * 3.6, 0.4, 2.45), "clay2")
    conveyor(X - 1.2, X + L + 1.4, 0, 0.62, w=1.4, items=True, speed=0.35, item_mat="bun", gap=0.5)
    xr = X + L + 1.4
    cyl(0.03, 0.35, (xr, -0.88, 0.61), "steel", axis="Y")                        # roller shaft extension
    mount("IRSDM_83-112_M", (0, 40, 202), (1, 0, 0), (0, 0, 1), (xr, -1.0, 0.61), (0, -1, 0), (1, 0, 0), scale=1.0)
    rod((xr - 0.05, -1.0, 0.4), (xr - 0.05, -1.0, 0.0), 0.025, "steel")          # torque arm
    return (X + L / 2, 0, 1.0)


def spiral(X):
    """Open spiral freezer: posts, rings and a 6-turn helical belt with products climbing; IRKM on the drum."""
    cx, cy, R, H = X + 2.2, 0, 1.9, 3.6
    for k in range(16):
        a = TAU * k / 16
        rod((cx + math.cos(a) * (R + 0.35), cy + math.sin(a) * (R + 0.35), 0), (cx + math.cos(a) * (R + 0.35), cy + math.sin(a) * (R + 0.35), H + 0.3), 0.04, "clay2")
    for z in (0.15, H + 0.3):
        bpy.ops.mesh.primitive_torus_add(major_radius=R + 0.35, minor_radius=0.05, location=(cx, cy, z), major_segments=64)
        obj_done(bpy.context.object, "clay2", smooth=True)
    drum = cyl(0.9, H, (cx, cy, H / 2 + 0.2), "clay", verts=64)
    MOVERS.append((drum, lambda t: (None, (0, 0, t * 0.25))))
    # helical belt as a swept ribbon
    turns, n = 6, 6 * 64
    bm = bmesh.new()
    rows = []
    for i in range(n + 1):
        a = TAU * turns * i / n
        z = 0.35 + (H - 0.4) * i / n
        rows.append([bm.verts.new((cx + math.cos(a) * r, cy + math.sin(a) * r, z)) for r in (1.0, R)])
    for i in range(n):
        bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
    me = bpy.data.meshes.new("helix"); bm.to_mesh(me)
    o = bpy.data.objects.new("helix", me); bpy.context.collection.objects.link(o)
    o.modifiers.new("t", "SOLIDIFY").thickness = 0.04
    obj_done(o, "belt")
    for p in o.data.polygons:
        p.use_smooth = True
    for i in range(70):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, segments=16, ring_count=8)
        b = bpy.context.object; b.scale = (1, 1, 0.55); obj_done(b, "bun", smooth=True)

        def f(t, i=i):
            u = ((i / 70) + t * 0.012) % 1.0
            a = TAU * turns * u
            z = 0.35 + (H - 0.4) * u + 0.08
            return (cx + math.cos(a) * 1.45, cy + math.sin(a) * 1.45, z), None
        MOVERS.append((b, f))
    dx, dy = cx, cy - R - 0.9
    box(0.9, 0.9, 0.45, (dx, dy, 0.225), "clay2", 0.03)
    mount("IRKM_93-160_L", (0, 27, 283), (1, 0, 0), (0, 0, -1), (dx, dy, 0.62), (0, 0, 1), (1, 0, 0), scale=0.9)
    sp = cyl(0.16, 0.05, (dx, dy, 0.82), "steel")
    rod((dx, dy, 0.82), (dx, dy, 0.6), 0.03, "steel")
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.03, location=(cx, cy, 0.82), major_segments=64)
    obj_done(bpy.context.object, "steel", smooth=True)
    for sgn in (-1, 1):
        rod((dx + sgn * 0.16, dy, 0.82), (cx + sgn * 0.9, cy - 0.35, 0.82), 0.018, "clay2")   # chain strands
    return (cx, cy, 1.8)


# --------------------------------------------------------------- scene
STATIONS = {}


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats()
    STATIONS["feeding"] = feeding(0.0)
    conveyor(5.0, 8.6, 0.4, 0.75, w=0.6, items=True, speed=0.3)
    STATIONS["extruder"] = extruder(9.0)
    conveyor(15.2, 19.0, 0, 0.62, w=1.0, items=True, speed=0.35)
    STATIONS["oven"] = oven(20.2)
    conveyor(33.0, 35.0, 0, 0.62, w=1.0, items=True, speed=0.35, item_mat="bun")
    STATIONS["spiral"] = spiral(35.5)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(20, 0, 0))
    obj_done(bpy.context.object, "floor")
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*BG, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
    sun.data.energy = 3.2; sun.data.angle = math.radians(8)
    sun.rotation_euler = (math.radians(42), 0, math.radians(-35))
    for loc, e, s in (((18, -18, 14), 9000, 14), ((18, 16, 10), 3500, 16), ((-10, 0, 8), 2500, 10)):
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object; l.data.energy = e; l.data.size = s
        l.rotation_euler = (Vector((18, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES; sc.cycles.use_adaptive_sampling = True; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.glossy_bounces = 2; sc.cycles.diffuse_bounces = 2
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = -0.2
    sc.render.fps = FPS


# camera: (time s, eye, target, lens). Overview between stations, like the reference.
OV = ((11.0, -24.0, 21.0), (19.5, 0.5, 0.0), 24)
CAM = [
    (0.0, (4.0, -28.0, 24.0), (18.5, 0.5, 0.0), 26),
    (4.5, *OV),
    (7.5, (-0.2, -7.6, 4.0), (3.2, 0.6, 1.5), 32),            # feeding
    (13.5, (0.6, -7.0, 3.6), (3.4, 0.6, 1.5), 32),
    (16.5, *OV),
    (19.5, (8.2, -5.6, 2.6), (11.0, 0.0, 1.1), 30),           # extruder
    (25.5, (8.9, -5.0, 2.3), (11.3, 0.0, 1.1), 30),
    (28.5, *OV),
    (31.5, (29.0, -6.4, 2.6), (32.3, -0.6, 0.6), 30),          # oven outlet with the IRSDM
    (37.5, (29.8, -5.8, 2.3), (32.5, -0.6, 0.6), 30),
    (40.5, *OV),
    (43.5, (33.5, -8.0, 3.6), (37.7, -1.6, 1.4), 30),         # spiral freezer
    (49.5, (34.6, -7.4, 3.2), (37.7, -1.4, 1.5), 30),
    (54.0, (12.0, -30.0, 27.0), (19.5, 0.5, 0.0), 24),        # pull back
]
DURATION = 54.0


def smooth(u):
    return u * u * (3 - 2 * u)


def cam_at(t):
    for (t0, e0, g0, l0), (t1, e1, g1, l1) in zip(CAM, CAM[1:]):
        if t <= t1:
            u = smooth(min(1, max(0, (t - t0) / (t1 - t0))))
            lerp = lambda a, b: Vector(a).lerp(Vector(b), u)
            return lerp(e0, e1), lerp(g0, g1), l0 + (l1 - l0) * u
    return Vector(CAM[-1][1]), Vector(CAM[-1][2]), CAM[-1][3]


def setup_camera():
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.sensor_width = 36
    return cam


def apply_frame(cam, f):
    t = f / FPS
    eye, tgt, lens = cam_at(t)
    cam.location = eye
    cam.rotation_euler = (tgt - eye).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens
    for o, fn in MOVERS:
        loc, rot = fn(t)
        if loc is not None:
            o.location = loc
        if rot is not None:
            o.rotation_euler = rot


def main():
    build()
    cam = setup_camera()
    sc = bpy.context.scene
    out = os.path.join(ROOT, "render", "line")
    os.makedirs(out, exist_ok=True)
    if "--still" in A:
        f = int(arg("--still", 0))
        apply_frame(cam, f)
        sc.render.filepath = os.path.join(ROOT, "render", f"still_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print("still", sc.render.filepath)
        return
    a, b = (int(v) for v in arg("--frames", f"0-{int(DURATION * FPS)}").split("-"))
    for f in range(a, b + 1, int(arg("--step", 1))):
        p = os.path.join(out, f"{f:04d}.png")
        if os.path.exists(p):
            continue
        apply_frame(cam, f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True)


if __name__ == "__main__":
    main()
