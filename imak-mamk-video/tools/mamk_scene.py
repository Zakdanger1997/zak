#!/usr/bin/env python3
"""Photoreal Cycles shots of the i.Mak MA / MK industrial gearboxes on a mining belt conveyor.

Usage:
    python3 tools/mamk_scene.py SHOT [--frames A-B] [--step N] [--samples N] [--res WxH] [--still F]
SHOT: dark | studio | duo | drive | conveyor | steel
Frames go to render/<shot>/####.png (existing frames are skipped).

Geometry: official i.Mak STEP models from i-Guide (MK 703-G07, MA 703-G00), split into paint/steel/bore
meshes by imak-mixing-brochure/tools/step_parts.py. The MK is shaft-mounted on the conveyor head-pulley
shaft (hollow output) with a torque arm; the motor sits on a lantern on the MK input, parallel to the belt.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("HDRI", "/tmp/claude-0/mamk/hdri")
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import scenekit as K  # noqa: E402  (materials, camera, lights, render settings from the IRC video)

ROOT = os.path.join(HERE, "..")
A = sys.argv[1:]
SHOT = A[0] if A else "drive"
TAU = math.pi * 2
FPS = 24
MAT = K.MAT


def arg(name, default):
    return A[A.index(name) + 1] if name in A else default


# ------------------------------------------------------------------ units
def build_unit(name, hollow=None):
    """Import an i.Mak unit (paint/steel/bore), STEP Y -> world Z, STEP Z -> world -Y. Machined faces
    around the hollow output (centre in STEP x, y and radius) get bare cast-iron / oiled steel."""
    objs = []
    for part in ("paint", "steel", "bore"):
        f = os.path.join(K.PARTS, f"{name}_{part}.stl")
        if not os.path.exists(f) or os.path.getsize(f) < 200:
            continue
        bpy.ops.wm.stl_import(filepath=f, global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = f"{name}_{part}"
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.select_set(False)
        objs.append(o)
    paint = objs[0]
    paint.data.materials.append(MAT["blue"])
    paint.data.materials.append(MAT["machined"])
    paint.data.materials.append(MAT["oiled"])
    if hollow:
        cx, cy, rr = hollow
        bm = bmesh.new()
        bm.from_mesh(paint.data)
        zmin = min(v.co.z for v in bm.verts)
        zmax = max(v.co.z for v in bm.verts)
        for f in bm.faces:
            c = f.calc_center_median()
            r = math.hypot(c.x - cx, c.y - cy)
            if r < rr * 0.9:
                f.material_index = 2                      # bore of the hollow shaft
            elif r < rr * 1.9 and abs(f.normal.z) > 0.98 and (c.z < zmin + 0.03 or c.z > zmax - 0.03):
                f.material_index = 1                      # machined hub faces
        bm.to_mesh(paint.data)
        bm.free()
    for o in objs[1:]:
        o.data.materials.append(MAT["steel"] if o.name.endswith("steel") else MAT["machined"])
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for o in objs:
        o.parent = root
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
        o.select_set(False)
    root.rotation_euler = (math.radians(90), 0, 0)
    return root, objs


def stand_on_floor(root):
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in root.children if o.type == "MESH" for c in o.bound_box]
    root.location.z -= min(p.z for p in pts)
    root.location.x -= (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    root.location.y -= (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    bpy.context.view_layer.update()


# --------------------------------------------------------------- materials
def extra_mats():
    MAT["rubber"] = K.plain("belt rubber", (22, 22, 24), 0.75)
    MAT["frame"] = K.paint_mat("structure grey", (64, 70, 76), rough=0.45, coat=0.3, cast=0.05, peel=0.15)
    MAT["galv"] = K.metal_mat("galvanised", (170, 172, 168), 0.45, scratch=0.1)
    MAT["roller"] = K.metal_mat("idler roller", (120, 122, 124), 0.35)
    MAT["lagging"] = K.plain("pulley lagging", (30, 30, 32), 0.85)
    MAT["handrail"] = K.paint_mat("handrail yellow", (232, 172, 12), rough=0.35, coat=0.4, cast=0.05)
    MAT["ore"] = ore_mat()
    MAT["gravel"] = ground_mat()


def ore_mat():
    m, nt, p = K.node_mat("iron ore")
    N, L = nt.nodes.new, nt.links.new
    tc = N("ShaderNodeTexCoord")
    n = N("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 30; n.inputs["Detail"].default_value = 12
    L(tc.outputs["Object"], n.inputs["Vector"])
    ramp = N("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.026, 0.022, 1)
    ramp.color_ramp.elements[1].color = (0.16, 0.09, 0.06, 1)
    L(n.outputs["Fac"], ramp.inputs["Fac"]); L(ramp.outputs["Color"], p.inputs["Base Color"])
    b = N("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.8
    L(n.outputs["Fac"], b.inputs["Height"]); L(b.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.85
    p.inputs["Metallic"].default_value = 0.15
    return m


def ground_mat():
    m, nt, p = K.node_mat("gravel ground")
    N, L = nt.nodes.new, nt.links.new
    tc = N("ShaderNodeTexCoord")
    vor = N("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 60
    n = N("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 1.5; n.inputs["Detail"].default_value = 6
    L(tc.outputs["Object"], vor.inputs["Vector"]); L(tc.outputs["Object"], n.inputs["Vector"])
    ramp = N("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.045, 0.030, 0.024, 1)
    ramp.color_ramp.elements[1].color = (0.13, 0.085, 0.060, 1)
    L(n.outputs["Fac"], ramp.inputs["Fac"]); L(ramp.outputs["Color"], p.inputs["Base Color"])
    b = N("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.6
    L(vor.outputs["Distance"], b.inputs["Height"]); L(b.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.95
    return m


# --------------------------------------------------------------- conveyor
R, FW, BW, L_CONV, INCL = 0.40, 1.40, 1.20, 16.0, math.radians(9)
TROUGH = math.radians(35)


def mesh_from(verts, faces, name, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def belt_profile(x):
    """Cross-section of the carry belt at x (local, head pulley at x=0): list of (y, z) points."""
    k = min(1.0, max(0.0, (-x - 0.5) / 1.8))          # 0 flat at the pulley, 1 fully troughed
    a = TROUGH * k
    c = 0.23                                           # half width of the flat centre
    w = BW / 2 - c
    zc = R + 0.008 - 0.06 * k
    pts = []
    for s in (-1, 1):
        pass
    left = [(-c - w * math.cos(a) * t, zc + w * math.sin(a) * t) for t in (1.0, 0.66, 0.33)]
    mid = [(-c, zc), (0.0, zc), (c, zc)]
    right = [(c + w * math.cos(a) * t, zc + w * math.sin(a) * t) for t in (0.33, 0.66, 1.0)]
    return left + mid + right


def build_belt(parent):
    xs = [-L_CONV + i * 0.25 for i in range(int(L_CONV / 0.25) + 1)]
    verts, faces = [], []
    nprof = len(belt_profile(0))
    for x in xs:
        for y, z in belt_profile(x):
            verts.append((x, y, z))
    for i in range(len(xs) - 1):
        for j in range(nprof - 1):
            a = i * nprof + j
            faces.append((a, a + 1, a + 1 + nprof, a + nprof))
    carry = mesh_from(verts, faces, "belt carry", MAT["rubber"])
    sol = carry.modifiers.new("t", "SOLIDIFY"); sol.thickness = 0.016
    carry.parent = parent
    # wrap around the head pulley and the flat return strand
    verts, faces = [], []
    n = 24
    for i in range(n + 1):
        a = math.pi / 2 - math.pi * i / n
        for y in (-BW / 2, BW / 2):
            verts.append(((R + 0.008) * math.cos(a), y, (R + 0.008) * math.sin(a)))
    for i in range(n):
        a = 2 * i
        faces.append((a, a + 1, a + 3, a + 2))
    base = len(verts)
    for x in (0.0, -L_CONV):
        for y in (-BW / 2, BW / 2):
            verts.append((x, y, -R - 0.008))
    faces.append((base, base + 1, base + 3, base + 2))
    wrap = mesh_from(verts, faces, "belt wrap", MAT["rubber"])
    sol = wrap.modifiers.new("t", "SOLIDIFY"); sol.thickness = 0.016
    wrap.parent = parent


def roller(p0, p1, r, parent, mat=None):
    o = K.rod(Vector(p0), Vector(p1), r, mat or MAT["roller"], "roller")
    o.parent = parent
    return o


def build_idlers(parent):
    rollers = []
    x = -2.4
    while x > -L_CONV + 0.5:
        prof = belt_profile(x)
        z0 = prof[4][1] - 0.008 - 0.07
        c = 0.25
        w = BW / 2 - 0.23 + 0.06
        rollers.append(roller((x, -c, z0), (x, c, z0), 0.065, parent))
        for s in (-1, 1):
            a0 = (s * (c + 0.02), z0)
            a1 = (s * (c + 0.02 + w * math.cos(TROUGH)), z0 + w * math.sin(TROUGH))
            rollers.append(roller((x, a0[0], a0[1]), (x, a1[0], a1[1]), 0.065, parent))
        fr = K.boxo((0.06, BW + 0.35, 0.05), (x, 0, z0 - 0.11), MAT["frame"], "idler frame", bevel=0.003)
        fr.parent = parent
        for s in (-1, 1):
            br = K.boxo((0.05, 0.05, 0.42), (x, s * (BW / 2 + 0.15), z0 - 0.11), MAT["frame"], "bracket", bevel=0.003)
            br.parent = parent
        x -= 1.25
    x = -1.6
    while x > -L_CONV + 0.5:
        rollers.append(roller((x, -BW / 2 - 0.05, -R - 0.09), (x, BW / 2 + 0.05, -R - 0.09), 0.06, parent))
        x -= 3.0
    # stringers
    for s in (-1, 1):
        st = K.boxo((L_CONV + 0.6, 0.12, 0.22), (-L_CONV / 2 + 0.3, s * (BW / 2 + 0.18), R - 0.42), MAT["frame"], "stringer", bevel=0.004)
        st.parent = parent
    return rollers


def build_pulley(parent):
    g = bpy.data.objects.new("head pulley", None)
    bpy.context.collection.objects.link(g)
    g.parent = parent
    shell = K.cyl(R, FW, MAT["lagging"], loc=(0, 0, 0), verts=96, name="pulley shell")
    shell.parent = g
    lag(shell.data.materials[0])
    for y in (-FW / 2, FW / 2):
        d = K.cyl(R - 0.01, 0.03, MAT["frame"], loc=(0, y, 0), verts=96, name="pulley end disc")
        d.parent = g
    shaft = K.cyl(0.0575, FW + 1.35, MAT["steel"], loc=(0, 0.28, 0), verts=32, name="pulley shaft")
    shaft.parent = g
    return g


def lag(mat):
    """Diamond-grooved rubber lagging (bump)."""
    nt = mat.node_tree
    p = nt.nodes["Principled BSDF"]
    N, Lk = nt.nodes.new, nt.links.new
    tc = N("ShaderNodeTexCoord")
    w1 = N("ShaderNodeTexWave"); w1.bands_direction = "DIAGONAL"; w1.inputs["Scale"].default_value = 18
    Lk(tc.outputs["Object"], w1.inputs["Vector"])
    b = N("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.5
    Lk(w1.outputs["Fac"], b.inputs["Height"]); Lk(b.outputs["Normal"], p.inputs["Normal"])


def pillow_block(y, parent):
    g = K.boxo((0.34, 0.16, 0.10), (0, y, -0.20), MAT["frame"], "pillow base", bevel=0.01)
    h = K.cyl(0.12, 0.15, MAT["frame"], loc=(0, y, 0), verts=48, name="bearing housing")
    for o in (g, h):
        o.parent = parent
    return h


def lantern_and_motor(c, parent):
    """Bell housing (lantern) + IEC motor on the MK input, axis along -X from point c."""
    g = bpy.data.objects.new("motor set", None)
    bpy.context.collection.objects.link(g)
    g.parent = parent
    g.location = c
    g.rotation_euler = (0, 0, math.radians(90))       # scenekit.motor builds along +Y; turn it to -X
    lant = K.cyl(0.17, 0.30, MAT["blue"], loc=(0, 0.15, 0), verts=64, name="lantern")
    lant.parent = g
    for k in range(2):
        win = K.boxo((0.13, 0.16, 0.06), (0, 0.15, 0), MAT["black"], "lantern window", bevel=0.01)
        win.rotation_euler = (0, math.radians(90 * k), 0)
        win.location = (0.16 * (1 if k == 0 else 0), 0.15, 0.16 * (1 if k == 1 else 0))
        win.parent = g
    m = K.motor(Vector((0, 0.30, 0)))
    m.parent = g
    m.scale = (1.45, 1.45, 1.45)
    return g


def ore_lump(size, seed):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=size)
    o = bpy.context.object
    rnd = random.Random(seed)
    for v in o.data.vertices:
        v.co *= 0.75 + 0.5 * rnd.random()
    o.scale = (1.0, 0.8 + 0.4 * rnd.random(), 0.6 + 0.3 * rnd.random())
    o.data.materials.append(MAT["ore"])
    return o


def build_conveyor(env="mine"):
    """Whole head end: inclined conveyor, pulley, MK drive, motor, torque arm, ore, stockpile, ground."""
    H = {}
    HEAD_Z = 5.0 if env == "mine" else 1.55              # head pulley centre above the ground
    FOOT = -40.0 if env == "mine" else 0.0             # mine: trestles run down out of frame over the pit edge
    inc = bpy.data.objects.new("incline", None)
    bpy.context.collection.objects.link(inc)
    inc.location = (0, 0, HEAD_Z)
    inc.rotation_euler = (0, -INCL, 0)
    build_belt(inc)
    H["rollers"] = build_idlers(inc)
    pul = build_pulley(inc)
    H["pulley"] = pul
    yb = FW / 2 + 0.16
    for y in (-yb, yb):
        pillow_block(y, inc)
    # MK shaft-mounted on the pulley shaft beyond the drive-side bearing
    mk, _ = build_unit("MK_703-G07", hollow=(0.0, 0.0, 0.058))
    mk.parent = inc
    y_mk = yb + 0.40
    # STEP (0, 0, 0) (hollow axis centre) -> local (0, y_mk, 0); STEP Z -> -Y so the unit is symmetric about y_mk
    mk.location = (0, y_mk, 0)
    mk.rotation_euler = (math.radians(90), math.radians(8), 0)    # small roll about the shaft; torque arm holds it
    H["mk"] = mk
    # lantern + motor on the input (STEP x = -0.84 is the input flange end)
    bpy.context.view_layer.update()
    inp = mk.matrix_world @ Vector((-0.84, -0.002, 0.0))
    H["motor"] = lantern_and_motor(inc.matrix_world.inverted() @ inp, inc)
    H["motor"].rotation_euler = (0, math.radians(8), math.radians(90))
    # torque arm: from the MK housing down to a bracket on the head frame
    a = mk.matrix_world @ Vector((-0.55, -0.26, 0.0))
    b = a + Vector((0, 0, -0.75))
    ta = K.rod(a, b, 0.03, MAT["galv"], "torque arm")
    for p in (a, b):
        eye = K.cyl(0.055, 0.06, MAT["galv"], loc=p, verts=32, name="rod end")
    br = K.boxo((0.4, 0.3, 0.06), b + Vector((0, 0, -0.05)), MAT["frame"], "torque arm bracket")
    # head frame: columns and beams to the ground
    for x in (-0.25, 0.25):
        for y in (-yb, yb):
            col = K.boxo((0.18, 0.18, HEAD_Z - 0.45 - FOOT), (x, y, (HEAD_Z - 0.45 + FOOT) / 2), MAT["frame"], "column", bevel=0.005)
    for y in (-yb, yb):
        K.boxo((0.7, 0.24, 0.2), (0, y, HEAD_Z - 0.35), MAT["frame"], "head beam", bevel=0.005)
    K.boxo((0.5, 0.5, 0.06), b + Vector((0, 0, -0.08)), MAT["frame"], "arm plinth")
    K.boxo((0.18, 0.18, b.z - 0.1 - FOOT), (b.x, b.y, (b.z - 0.1 + FOOT) / 2), MAT["frame"], "arm column", bevel=0.005)
    # legs under the inclined stringers
    for k in range(1, 6 if env == "mine" else 2):
        xl = -k * 3.0
        p = inc.matrix_world @ Vector((xl, 0, R - 0.55))
        for s in (-1, 1):
            K.boxo((0.14, 0.14, p.z - FOOT), (p.x, s * (BW / 2 + 0.18), (p.z + FOOT) / 2), MAT["frame"], "leg", bevel=0.004)
    # ground and stockpile
    if env != "mine":
        gnd = K.floor(catcher=True, size=60)           # plant floor from the HDRI; keep the shadows
    tex = bpy.data.textures.new("pile", "CLOUDS"); tex.noise_scale = 0.6
    piles = []
    for (px, py, _), r_, h_ in piles:
        bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=r_, depth=h_, location=(px, py, h_ / 2 - 0.05))
        pile = bpy.context.object
        pile.data.materials.append(MAT["ore"] if r_ < 5 else MAT["gravel"])
        sub = pile.modifiers.new("sub", "SUBSURF"); sub.levels = 2; sub.render_levels = 3
        d = pile.modifiers.new("disp", "DISPLACE"); d.texture = tex; d.strength = 0.06 * r_
    # ore lumps riding the belt and falling off the head into the pile
    H["lumps"] = []
    rnd = random.Random(3)
    for i in range(170):
        size = 0.035 + 0.075 * rnd.random() ** 2
        o = ore_lump(size, i)
        o.parent = inc
        H["lumps"].append((o, rnd.random() * L_CONV, rnd.uniform(-0.28, 0.28), size, rnd.random() * TAU))
    H["inc"] = inc
    H["HEAD_Z"] = HEAD_Z
    # discharge chute under the head pulley: ore disappears into it (plant) or onto the pile (mine)
    ch = K.boxo((0.9, BW + 0.3, 0.9), (0.55, 0, -0.95), MAT["frame"], "chute", bevel=0.01)
    ch.parent = inc
    hole = K.boxo((0.75, BW + 0.1, 0.5), (0.55, 0, -0.62), MAT["black"], "chute mouth", bevel=0.0)
    hole.parent = inc
    H["sink"] = -0.55
    return H


def animate_conveyor(H, nfr, speed=1.6):
    """Belt speed in m/s (visual), pulley turns at v / R, lumps ride and are thrown off the pulley."""
    pul = H["pulley"]
    for f in (0, nfr - 1):
        pul.rotation_euler = (0, speed / R * f / FPS, 0)
        pul.keyframe_insert("rotation_euler", frame=f)
    K.linear(pul)
    for r_ in H["rollers"]:
        pass                                            # rollers are smooth cylinders; spin is invisible
    g = 9.81
    for o, s0, y, size, rot in H["lumps"]:
        for f in range(0, nfr, 2):
            t = f / FPS
            s = s0 + speed * t                          # distance travelled from the tail end
            x = -L_CONV + s
            if x <= 0:
                prof = belt_profile(x)
                k = min(1.0, max(0.0, (-x - 0.5) / 1.8))
                z = prof[4][1] + 0.008 + size * 0.6 + abs(y) * math.tan(TROUGH * k) * 0.8
                loc = Vector((x, y, z))
            else:
                # thrown off the top of the pulley: ballistic in world space (local frame is inclined)
                tt = x / speed
                vx, vz = speed * math.cos(INCL), speed * math.sin(INCL)
                lx = vx * tt
                lz = vz * tt - 0.5 * g * tt * tt
                # convert world offsets back to the inclined local frame
                c, si = math.cos(INCL), math.sin(INCL)
                wx, wz = lx, lz
                loc = Vector((wx * c - wz * si, y, (R + 0.02 + size) + wx * si + wz * c))
            hidden = loc.z < H["sink"]                  # fell into the chute / onto the pile
            o.scale = (0.001,) * 3 if hidden else (1, 1, 1)
            o.keyframe_insert("scale", frame=f)
            o.location = loc
            o.rotation_euler = (rot + (max(0, x) * 3), rot, 0)
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_euler", frame=f)


def world_backplate(hdri, photo, rot=0.0, shift=0.5, lift=0.0, zoom=1.0):
    """HDRI lights the scene; camera rays see a real photo (screen-space, cover-fit to 9:16)."""
    K.world(hdri, 1.0, rot=rot)
    nt = bpy.context.scene.world.node_tree
    img = bpy.data.images.load(photo)
    iw, ih = img.size
    fw, fh = K.RES
    sx = (fw / fh) / (iw / ih) / zoom                   # fraction of the photo width the frame shows
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (sx, 1 / zoom, 1)
    mp.inputs["Location"].default_value = ((1 - sx) * shift, lift + (1 - 1 / zoom) / 2, 0)
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; tex.extension = "EXTEND"
    nt.links.new(tc.outputs["Window"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    bgp = nt.nodes.new("ShaderNodeBackground"); bgp.inputs["Strength"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], bgp.inputs["Color"])
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(nt.nodes["Background"].outputs["Background"], mix.inputs[1])
    nt.links.new(bgp.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], nt.nodes["World Output"].inputs["Surface"])


# ------------------------------------------------------------------ shots
def shot_drive(env="mine"):
    H = build_conveyor(env)
    nfr = 144
    animate_conveyor(H, nfr)
    if env == "mine":
        world_backplate("abandoned_hopper_terminal_01.exr", os.path.join(ROOT, "assets", "photos", "pit_blur_drive.jpg" if SHOT == "drive" else "pit_blur_wide.jpg"),
                        rot=1.9, shift=0.62 if SHOT == "drive" else 0.35, zoom=1.0)
    else:
        K.world("industrial_workshop_foundry.exr", 1.0, rot=0.6)
    hz = H["HEAD_Z"]
    sc = bpy.context.scene
    if SHOT in ("drive", "steel"):
        cam, tgt = K.camera((-3.1, 3.5, hz + 1.25), (-0.55, 1.05, hz - 0.15), lens=30, fstop=5.6)
        cam.keyframe_insert("location", frame=0)
        cam.location = (-2.6, 3.95, hz + 1.0)
        cam.keyframe_insert("location", frame=nfr - 1)
        K.linear(cam)
    else:   # wide conveyor: long belt rising to the head drive, stockpile below
        cam, tgt = K.camera((-9.5, 4.2, hz + 2.2), (-3.2, 0.4, hz - 0.5), lens=26, fstop=8)
        cam.keyframe_insert("location", frame=0)
        cam.location = (-8.2, 4.9, hz + 1.9)
        cam.keyframe_insert("location", frame=nfr - 1)
        K.linear(cam)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.data.energy = 2.2 if env == "mine" else 0.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(-140))
    sc.frame_start, sc.frame_end = 0, nfr - 1
    K.render_setup(exposure=float(arg("--exposure", 0.0)))


def shot_studio_unit(kind):
    """dark: MK on black; studio: MK on the grey sweep; duo: MA and MK side by side."""
    if kind == "dark":
        K.world("machine_shop_02.exr", 0.35, rot=1.0, camera_black=True)
        K.floor(K.plain("black floor", (6, 6, 7), 0.35))
        K.area((-2.0, -1.6, 2.6), (0, 0, 0.3), 520, 1.6)
        K.area((2.4, 1.8, 1.4), (0, 0, 0.3), 900, 0.8, (0.75, 0.85, 1.0))
        K.area((-2.4, 2.0, 1.2), (0, 0, 0.3), 600, 0.7, (1.0, 0.9, 0.8))
    else:
        K.cyclorama()
        K.world("studio_small_09.exr", 0.9, rot=1.2)
        K.area((-2.2, -2.4, 3.0), (0, 0, 0.3), 900, 2.6)
        K.area((2.6, -0.8, 1.4), (0, 0, 0.3), 340, 2.6)
        K.area((0.6, 2.0, 2.8), (0, 0, 0.4), 520, 1.6)
    sc = bpy.context.scene
    if kind == "duo":
        ma, _ = build_unit("MA703-G00")
        mk, _ = build_unit("MK_703-G07", hollow=(0.0, 0.0, 0.058))
        for u, (x, y), rz in ((ma, (-0.20, 1.05), -24), (mk, (0.18, -0.50), 48)):
            stand_on_floor(u)
            u.rotation_euler.z = math.radians(rz)
            stand_on_floor(u)
            u.location.x += x
            u.location.y += y
        cam, tgt = K.camera((0.30, -5.2, 1.30), (0.0, 0.25, 0.40), lens=60)
        sc.frame_start = sc.frame_end = 0
    else:
        mk, _ = build_unit("MK_703-G07", hollow=(0.0, 0.0, 0.058))
        stand_on_floor(mk)
        piv = K.spin(mk, -70, 20, 0, 192 if kind == "studio" else 96)
        if kind == "dark":
            cam, tgt = K.camera((2.4, -4.2, 1.1), (0.0, 0.0, 0.32), lens=60, fstop=5.6)
            sc.frame_start, sc.frame_end = 0, 95
        else:
            cam, tgt = K.camera((0.0, -5.2, 1.25), (0.0, 0.0, 0.30), lens=58)
            sc.frame_start, sc.frame_end = 0, 191
    K.render_setup(exposure=float(arg("--exposure", -0.3 if kind == "dark" else -1.45)))


def shot_lineup():
    """MK sizes from i-Guide side by side on the grey sweep (one wide still)."""
    K.cyclorama()
    K.world("studio_small_09.exr", 0.9, rot=1.2)
    x = 0.0
    import json
    marks = []
    for n in arg("--sizes", "MK_403,MK_703-G07,MK_803,MK_1004,MK_1204").split(","):
        u, _ = build_unit(n)
        stand_on_floor(u)
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in u.children if o.type == "MESH" for c in o.bound_box]
        ex = max(p.x for p in pts) - min(p.x for p in pts)
        ey = max(p.y for p in pts) - min(p.y for p in pts)
        ez = max(p.z for p in pts) - min(p.z for p in pts)
        if ez > max(ex, ey) * 1.3:                       # model stored standing on its end: lay it down
            u.rotation_euler.x = 0
        elif ey > ex:
            u.rotation_euler.z = math.radians(90)
        stand_on_floor(u)
        u.rotation_euler.z += math.radians(-30)
        stand_on_floor(u)
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in u.children if o.type == "MESH" for c in o.bound_box]
        w = max(p.x for p in pts) - min(p.x for p in pts)
        u.location.x += x + w / 2
        marks.append((n, x + w / 2, max(p.z for p in pts)))
        x += w + 0.25
    for o in bpy.data.objects:
        if o.name == "cyclorama":
            o.location.x = x / 2
            o.scale.x = 4
    json.dump({"marks": marks, "width": x}, open(os.path.join(ROOT, "render", "lineup.json"), "w"))
    mid = x / 2
    K.area((mid - 3.0, -4.5, 4.5), (mid, 0, 0.5), 4200, 6.0)
    K.area((mid + 5.0, -2.0, 2.0), (mid, 0, 0.5), 1300, 6.0)
    K.area((mid, 3.0, 4.0), (mid, 0, 0.8), 1600, 4.0)
    cam, tgt = K.camera((mid, -11.0, 2.1), (mid, 0, 0.65), lens=50)
    sc = bpy.context.scene
    sc.frame_start = sc.frame_end = 0
    K.render_setup(exposure=float(arg("--exposure", -1.45)))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    K.mats()
    extra_mats()
    if SHOT in ("drive", "conveyor"):
        shot_drive("mine")
    elif SHOT == "steel":
        shot_drive("steel")
    elif SHOT == "lineup":
        shot_lineup()
    else:
        shot_studio_unit(SHOT)
    sc = bpy.context.scene
    outdir = os.path.join(ROOT, "render", SHOT)
    os.makedirs(outdir, exist_ok=True)
    if "--still" in A:
        f = int(arg("--still", 0))
        sc.frame_set(f)
        sc.render.filepath = os.path.join(ROOT, "render", f"{SHOT}_still_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print("still", sc.render.filepath)
        return
    a, b = (int(v) for v in arg("--frames", f"{sc.frame_start}-{sc.frame_end}").split("-"))
    for f in range(a, b + 1, int(arg("--step", 1))):
        p = os.path.join(outdir, f"{f:04d}.png")
        if os.path.exists(p):
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True)


if __name__ == "__main__":
    main()
