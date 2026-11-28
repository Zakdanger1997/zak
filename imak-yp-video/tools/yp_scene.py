#!/usr/bin/env python3
"""i.Mak YP series "exploded movement" film (after a luxury-watch tourbillon reveal): the real YP 93 housing, split in
two, floats in a bright studio with its three helical stages, bearings, seals and bolts; everything flies together into
the finished gear unit, which then turns once for a hero view.

Usage: python3 tools/yp_scene.py [--frames A-B] [--step N] [--samples N] [--res WxH] [--still F]
Frames -> render/yp/####.png (RGBA, transparent background; tools/compose.py puts them on the studio gradient).

Geometry: housing = official i.Mak YP 93 STEP model from i-Guide (3b_model/YP/YP 93.step.rar), split into paint / bore /
steel meshes by imak-mixing-brochure/tools/step_parts.py (assets/yp93_*.stl, millimetres, Y up). Measured on it: input
shaft Ø38 on the axis x=0, y=0; hollow output Ø60 on x=0, y=-240; both along Z. The STEP is an envelope model with no
internals, so the gear train is modelled here after i.Mak's YP cutaway poster: three helical stages Z1/Z2, Z3/Z4, Z5/Z6
stacked from the input down to the hollow output shaft. Gear sizes are illustrative, not catalogue data.
"""
import math
import os
import sys

import bpy  # noqa: E402
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "..", "imak-bakery-video", "tools"))
import scenekit as K  # noqa: E402  materials, lights, camera, render settings (reads --samples / --res from argv)

A = sys.argv[1:]
arg = lambda n, d: A[A.index(n) + 1] if n in A else d
FPS = 24
END = 20 * FPS                    # 0-480: exploded drift, assembly, hero turn
MM = 0.001
S_SPLIT = 30.0                    # housing split plane, z (mm)


def srgb(c):
    return K.srgb(c)


# ------------------------------------------------------------------ materials
def mats():
    M = {}
    M["paint"] = K.paint_mat("i.Mak red", (176, 18, 22), rough=0.24, coat=1.0, cast=0.25, peel=0.2)
    M["bore"] = K.metal_mat("machined", (160, 162, 165), 0.3, scratch=0.05)
    M["gear"] = K.metal_mat("case-hardened gear", (128, 130, 134), 0.28, scratch=0.06)
    M["flank"] = K.metal_mat("ground flank", (190, 193, 198), 0.16, aniso=0.3, scratch=0.04)
    M["steel"] = K.metal_mat("bright steel", (222, 224, 228), 0.1, aniso=0.4, scratch=0.03)
    M["race"] = K.metal_mat("bearing race", (210, 212, 216), 0.08, scratch=0.02)
    M["rubber"] = K.plain("seal rubber", (22, 22, 24), 0.55)
    M["zinc"] = K.metal_mat("zinc bolt", (178, 180, 176), 0.3, scratch=0.05)
    return M


# ------------------------------------------------------------------ geometry helpers (mm, axis = Z)
def obj_from_bm(bm, name, mat, smooth=40):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(smooth))
    o.select_set(False)
    return o


def ring_verts(bm, r, z, n, phase=0.0):
    return [bm.verts.new((r * math.cos(phase + i * 2 * math.pi / n), r * math.sin(phase + i * 2 * math.pi / n), z)) for i in range(n)]


def bridge(bm, a, b, flip=False):
    n = len(a)
    for i in range(n):
        q = (a[i], a[(i + 1) % n], b[(i + 1) % n], b[i])
        bm.faces.new(q[::-1] if flip else q)


def tube(r_in, r_out, z0, z1, mat, name, n=96):
    bm = bmesh.new()
    o0, o1 = ring_verts(bm, r_out, z0, n), ring_verts(bm, r_out, z1, n)
    i0, i1 = ring_verts(bm, r_in, z0, n), ring_verts(bm, r_in, z1, n)
    bridge(bm, o0, o1); bridge(bm, i1, i0); bridge(bm, i0, o0); bridge(bm, o1, i1)
    return obj_from_bm(bm, name, mat)


def solid(r, z0, z1, mat, name, n=64):
    bm = bmesh.new()
    a, b = ring_verts(bm, r, z0, n), ring_verts(bm, r, z1, n)
    bridge(bm, a, b)
    bm.faces.new(a[::-1]); bm.faces.new(b)
    return obj_from_bm(bm, name, mat)


def gear(r, width, z0, mat, name, module=3.0, helix=14.0, hand=1, bore=None):
    """Helical spur gear about Z: tooth profile on the pitch radius r, twisted along the face width."""
    teeth = max(10, int(round(2 * r / module)))
    ra, rf = r + module, r - 1.25 * module
    prof = []
    for k in range(teeth):
        a0 = k * 2 * math.pi / teeth
        p = 2 * math.pi / teeth
        for f, rr in ((0.0, rf), (0.12, rf), (0.30, ra), (0.50, ra), (0.68, rf), (0.88, rf)):
            prof.append((rr, a0 + f * p))
    steps = 6
    twist = hand * width * math.tan(math.radians(helix)) / r
    bm = bmesh.new()
    rings = []
    for s in range(steps + 1):
        z = z0 + width * s / steps
        tw = twist * s / steps
        rings.append([bm.verts.new((rr * math.cos(a + tw), rr * math.sin(a + tw), z)) for rr, a in prof])
    for s in range(steps):
        bridge(bm, rings[s], rings[s + 1])
    if bore:     # caps with a bore: bridge the tooth ring to an inner circle on each face
        n = len(prof)
        for ring, z, flip in ((rings[0], z0, True), (rings[-1], z0 + width, False)):
            inner = [bm.verts.new((bore * math.cos(a), bore * math.sin(a), z)) for _, a in prof]
            for i in range(n):
                q = (ring[i], ring[(i + 1) % n], inner[(i + 1) % n], inner[i])
                bm.faces.new(q[::-1] if not flip else q)
        ib0 = [v for v in bm.verts if abs(v.co.z - z0) < 1e-6 and abs(math.hypot(v.co.x, v.co.y) - bore) < 1e-6]
    else:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from_bm(bm, name, mat, smooth=25), teeth


def bearing(r_in, r_out, width, z0, M, name):
    parts = []
    t = (r_out - r_in) * 0.28
    parts.append(tube(r_out - t, r_out, z0, z0 + width, M["race"], name + "_outer"))
    parts.append(tube(r_in, r_in + t, z0, z0 + width, M["race"], name + "_inner"))
    rb, rm = (r_out - r_in) * 0.24, (r_in + r_out) / 2
    nb = max(8, int(2 * math.pi * rm / (rb * 2.6)))
    for k in range(nb):
        a = k * 2 * math.pi / nb
        bpy.ops.mesh.primitive_uv_sphere_add(radius=rb, location=(rm * math.cos(a), rm * math.sin(a), z0 + width / 2), segments=20, ring_count=10)
        s = bpy.context.object; s.data.materials.append(M["steel"]); bpy.ops.object.shade_smooth()
        parts.append(s)
    cage = tube(rm - rb * 0.5, rm + rb * 0.5, z0 + width * 0.2, z0 + width * 0.8, M["zinc"], name + "_cage", n=64)
    parts.append(cage)
    return join(parts, name)


def bolt(length, d, M, name):
    head = solid(d * 0.85, 0, d * 0.65, M["zinc"], name + "_h", n=6)
    shank = solid(d / 2, -length, 0, M["zinc"], name + "_s", n=24)
    return join([head, shank], name)


def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    return o


def import_stl(path, name, mat):
    bpy.ops.wm.stl_import(filepath=path)
    o = bpy.context.selected_objects[0]
    o.name = name
    o.data.materials.clear(); o.data.materials.append(mat)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_auto_smooth(angle=math.radians(32))
    return o


def split(o, z):
    """Cut a mesh at the plane z=const into two objects (back z<z0, front z>z0), no caps."""
    front = o.copy(); front.data = o.data.copy(); bpy.context.scene.collection.objects.link(front)
    for ob, keep_back in ((o, True), (front, False)):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, z), plane_no=(0, 0, 1), clear_outer=keep_back, clear_inner=not keep_back)
        bm.to_mesh(ob.data); bm.free()
    front.name = o.name + "_front"; o.name = o.name + "_back"
    return o, front


# ------------------------------------------------------------------ build
PARTS = []   # (object, assembled location (mm), exploded offset (mm), exploded rotation (rad xyz), spin axis rate, order 0..1)


def part(o, off, rot=(0, 0, 0), order=0.5, spin=0.0):
    o.parent = ROOTO
    PARTS.append(dict(o=o, loc=Vector(o.location), off=Vector(off), rot=Vector(rot), base=Vector(o.rotation_euler), order=order, spin=spin))


def build():
    global ROOTO
    M = mats()
    ROOTO = bpy.data.objects.new("yp_root", None)
    bpy.context.scene.collection.objects.link(ROOTO)
    ROOTO.rotation_euler = (math.radians(90), 0, 0)       # STEP Y-up -> Blender Z-up
    ROOTO.scale = (MM, MM, MM)

    P = lambda n: os.path.join(ROOT, "assets", f"yp93_{n}.stl")
    paint = import_stl(P("paint"), "housing", M["paint"])
    bore = import_stl(P("bore"), "bores", M["bore"])
    steel = import_stl(P("steel"), "input_shaft", M["steel"])
    for o in (paint, bore, steel):           # stl import applies its own axes: undo to raw STEP coordinates
        o.rotation_euler = (0, 0, 0); o.scale = (1, 1, 1); o.location = (0, 0, 0)
    pb, pf = split(paint, S_SPLIT)
    bb, bf = split(bore, S_SPLIT)
    hb = join([pb, bb], "housing_back")
    hf = join([pf, bf], "housing_front")
    part(hb, (0, 0, -260), (0.0, 0.18, 0), order=0.0)
    part(hf, (0, 40, 620), (0.0, -0.25, 0.06), order=0.95)
    part(steel, (0, 0, -420), (0, 0, 0), order=0.2, spin=0.5)

    # shaft axes (x, y) mm and the three stages (pinion r, wheel r, z0, width)
    S = [(0, 0), (38, -72), (-34, -150), (0, -240)]
    st = [(17, 63, -120, 30), (27, 78, -40, 40), (33, 64, 60, 52)]
    z_back, z_front = -150, 200
    zoff = {0: 120, 1: 260, 2: 420}
    for k, (rp, rw, z0, w) in enumerate(st):
        (xa, ya), (xb, yb) = S[k], S[k + 1]
        pin, _ = gear(rp, w, z0, M["flank"], f"Z{2 * k + 1}", hand=1)
        whe, _ = gear(rw, w, z0, M["gear"], f"Z{2 * k + 2}", hand=-1, bore=rw * 0.32)
        pin.location = (xa, ya, 0); whe.location = (xb, yb, 0)
        dz = zoff[k]
        part(pin, (-30 + 20 * k, 30, dz + 60), (0.3, -0.2, 0), order=0.30 + 0.1 * k, spin=0.9)
        part(whe, (40 - 25 * k, -20, dz), (-0.25, 0.3, 0), order=0.25 + 0.1 * k, spin=-0.5)
    # intermediate shafts + output hollow shaft
    for k, (x, y) in enumerate(S[1:3], 1):
        sh = solid(14 + 4 * k, z_back + 10, z_front - 40, M["steel"], f"shaft{k}")
        sh.location = (x, y, 0)
        part(sh, (20 * k, -10, 540 + 40 * k), (0.4, 0.2, 0), order=0.15 + 0.05 * k, spin=0.3)
    hollow = tube(30, 42, z_back - 26, 238, M["steel"], "hollow_shaft")
    hollow.location = (0, -240, 0)
    part(hollow, (0, -60, 760), (0.2, -0.3, 0), order=0.1, spin=0.25)
    # bearings on every shaft, both walls
    for k, (x, y) in enumerate(S):
        rin = 19 if k == 0 else (42 if k == 3 else 14 + 4 * k)
        for side, z in (("b", z_back + 8), ("f", z_front - 70 if k < 3 else 160)):
            b = bearing(rin, rin * 1.75 + 10, 18 + 2 * k, z, M, f"brg{k}{side}")
            b.location = (x, y, 0)
            part(b, (60 if side == "f" else -60, 30 * (k - 1.5), (380 if side == "f" else 80) + 70 * k), (0.5, 0.35, 0), order=0.35 + 0.1 * k, spin=0.6)
    # seals on input and output
    for name, (x, y), r, z in (("seal_in", S[0], 19, -168), ("seal_out", S[3], 42, 222)):
        s = tube(r, r + 12, z, z + 9, M["rubber"], name)
        s.location = (x, y, 0)
        part(s, (0, 25, 860 if z > 0 else -520), (0.6, 0.0, 0), order=0.75, spin=0.4)
    # bolts round the split flange
    # bolts: they end in the 8 holes on PCD 180 round the hollow output (measured on the STEP, front face z=235). Their
    # floating positions are kept from the first layout (FLOAT), so the exploded frames did not change.
    FLOAT = [(-150, 100), (150, 100), (-158, -40), (158, -40), (-150, -330), (150, -330), (0, 118), (0, -372)]
    HOLES = [(90 * math.cos(math.radians(a)), -240 + 90 * math.sin(math.radians(a))) for a in (135, 45, 180, 0, 225, 315, 90, 270)]
    for i, ((fx, fy), (x, y)) in enumerate(zip(FLOAT, HOLES)):
        b = bolt(40, 10, M, f"bolt{i}")
        b.location = (x, y, 235)
        r = 1.0 + 0.15 * (i % 3)
        old = Vector((fx, fy, S_SPLIT + 60)) + Vector((fx * 0.6 * r, fy * 0.25 + 40, 980 + 50 * (i % 4)))
        part(b, old - Vector(b.location), (1.2 * (i % 2 * 2 - 1), 0.6, 0), order=1.0, spin=2.0)
    return M


# ------------------------------------------------------------------ animation
def ease(x):
    x = min(1, max(0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


T_ASM0, T_ASM1 = 7.5 * FPS, 13.5 * FPS      # assembly window (frames)


def explode_factor(f, order):
    a = T_ASM0 + order * (T_ASM1 - T_ASM0 - 1.6 * FPS)
    return 1 - ease((f - a) / (1.6 * FPS))


def pose(f):
    for p in PARTS:
        e = explode_factor(f, p["order"])
        drift = Vector((math.sin(f / 40 + p["order"] * 9) * 6, math.cos(f / 47 + p["order"] * 7) * 6, 0)) * e
        p["o"].location = p["loc"] + p["off"] * e + drift
        spin = p["spin"] * (f / FPS) * e
        p["o"].rotation_euler = (p["base"].x + p["rot"].x * e, p["base"].y + p["rot"].y * e, p["base"].z + p["rot"].z * e + spin)
    # lying on its back while exploded (parts stack upward, like a watch movement), standing up as it assembles,
    # then a slow turn for the hero view
    up = ease((f - 8.5 * FPS) / (6.5 * FPS))
    k = ease((f - 14.0 * FPS) / (6.0 * FPS))
    ROOTO.rotation_euler = (math.radians(18 + 72 * up), 0, math.radians(-25 + 25 * up - 35 * k))
    bpy.context.view_layer.update()


def cam_path(f):
    """Camera keys: (frame, world offset from the target in metres, target as a point on the unit in STEP mm).
    The target follows the unit as it stands up; both are interpolated with smootherstep."""
    K_ = [(0, (-0.30, -0.42, 0.06), (0, -120, 420)),
          (int(4 * FPS), (-0.62, -0.88, 0.14), (0, -120, 340)),
          (int(8.5 * FPS), (-0.90, -1.38, 0.24), (0, -120, 260)),
          (int(14 * FPS), (-0.82, -1.28, 0.30), (0, -140, 30)),
          (END, (-0.55, -0.92, 0.22), (0, -140, 30))]
    for (f0, o0, t0), (f1, o1, t1) in zip(K_, K_[1:]):
        if f <= f1:
            k = ease((f - f0) / (f1 - f0))
            t = ROOTO.matrix_world @ Vector(t0).lerp(Vector(t1), k)
            return t + Vector(o0).lerp(Vector(o1), k), t
    t = ROOTO.matrix_world @ Vector(K_[-1][2])
    return t + Vector(K_[-1][1]), t


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.film_transparent = True
    build()
    # bright studio: soft key from top-left, big fill, rim from behind; grey world for reflections
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*srgb((200, 202, 206)), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.55
    K.area((-1.6, -1.2, 2.0), (0, 0, 0), 520, 2.2)
    K.area((1.8, -1.6, 0.6), (0, 0, 0), 200, 3.0)
    K.area((0.6, 1.8, 1.4), (0, 0, 0), 450, 1.5)
    K.area((0.0, -2.5, -1.2), (0, 0, 0), 120, 3.0)
    cam, tgt = K.camera((0, -1, 0), (0, 0, 0), lens=50, fstop=4.0)
    K.render_setup()
    sc.view_settings.exposure = -0.35
    out = os.path.join(ROOT, "render", "yp")
    os.makedirs(out, exist_ok=True)
    if "--still" in A:
        frames = [int(x) for x in arg("--still", "0").split(",")]
    else:
        a, b = [int(x) for x in arg("--frames", f"0-{END - 1}").split("-")]
        frames = list(range(a, b + 1, int(arg("--step", "1"))))
    for f in frames:
        path = os.path.join(out, f"{f:04d}.png")
        if os.path.exists(path) and "--still" not in A:
            continue
        pose(f)
        loc, t = cam_path(f)
        cam.location, tgt.location = loc, t
        cam.data.dof.focus_distance = (loc - t).length
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True)


if __name__ == "__main__":
    main()
