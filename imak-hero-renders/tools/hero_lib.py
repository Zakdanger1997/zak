"""Shared helpers for the i.Mak website hero renders (Blender 5.x, Cycles).

Units: metres. The STEP envelope models are imported from parts/<name>_{paint,steel,bore}.stl
(made by step_parts.py, millimetres) and stood on their feet with ROT.
"""
import json
import math
import os
import sys

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PARTS = os.path.join(ROOT, "parts")
OUT = os.path.join(ROOT, "out")
PREVIEW_DIR = os.path.join(ROOT, "preview")

PREVIEW = "--preview" in sys.argv
def _arg(flag, default, cast=float):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default
SAMPLES = _arg("--samples", 32 if PREVIEW else 512, int)
SCALE = _arg("--scale", 0.25 if PREVIEW else 1.0)      # fraction of 3840x2160

# RAL 3020 traffic red, sRGB #CC0605 -> linear
RAL3020 = (0.6038, 0.0018, 0.0015)
# RAL 7016 anthracite grey #383E42 -> linear
RAL7016 = (0.0395, 0.0484, 0.0546)
# RAL 5010 gentian blue #0E294B
RAL5010 = (0.0030, 0.0222, 0.0742)


# ----------------------------------------------------------------------------- materials
_MATS = {}


def mat(name, col=(0.8, 0.8, 0.8), metal=0.0, rough=0.5, coat=0.0, spec=0.5, aniso=0.0, emit=None, bump=None):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = spec
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.1
    if aniso:
        p.inputs["Anisotropic"].default_value = aniso
    if emit:
        p.inputs["Emission Color"].default_value = (*emit[0], 1)
        p.inputs["Emission Strength"].default_value = emit[1]
    if bump:
        # bump: (noise scale, strength) procedural micro texture
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = bump[0]
        tex.inputs["Detail"].default_value = 6
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump[1]
        nt.links.new(tex.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    _MATS[name] = m
    return m


def M():
    """The material set, created once per scene."""
    return {
        "paint": mat("RAL3020 paint", RAL3020, 0.0, 0.42, coat=0.35, spec=0.45, bump=(900, 0.04)),
        "steel": mat("shaft steel", (0.80, 0.81, 0.83), 1.0, 0.18, aniso=0.4),
        "bore": mat("machined", (0.40, 0.41, 0.43), 0.9, 0.40),
        "frame": mat("RAL7016 frame", RAL7016, 0.0, 0.5, coat=0.15, spec=0.4, bump=(600, 0.05)),
        "blue": mat("RAL5010 frame", RAL5010, 0.0, 0.45, coat=0.2, spec=0.4),
        "galv": mat("galvanised", (0.55, 0.56, 0.57), 1.0, 0.45, bump=(80, 0.25)),
        "stainless": mat("stainless", (0.72, 0.73, 0.74), 1.0, 0.28, aniso=0.6),
        "rubber": mat("belt rubber", (0.035, 0.035, 0.037), 0.0, 0.45, spec=0.35, bump=(300, 0.06)),
        "floor": mat("studio floor", (0.010, 0.010, 0.011), 0.0, 0.18, spec=0.5, bump=(40, 0.015)),
        "concrete": mat("concrete", (0.11, 0.11, 0.105), 0.0, 0.85, spec=0.2, bump=(25, 0.3)),
        "wall": mat("hall wall", (0.03, 0.032, 0.035), 0.0, 0.9, spec=0.1),
        "dark": mat("dark metal", (0.05, 0.05, 0.052), 0.6, 0.5),
        "yellow": mat("RAL1003 guard", (0.95, 0.52, 0.0), 0.0, 0.5, coat=0.2),
        "lamp": mat("lamp", (1, 1, 1), 0.0, 0.5, emit=((1.0, 0.97, 0.9), 12.0)),
        "bolt": mat("bolt zinc", (0.5, 0.5, 0.5), 1.0, 0.5),
        "rock": mat("aggregate", (0.09, 0.08, 0.07), 0.0, 0.92, spec=0.2, bump=(90, 0.6)),
    }


# ----------------------------------------------------------------------------- units
# name -> (rotation XYZ degrees that stands the model on its feet / flange)
ROT = {"default": (90, 0, 0)}


def load_unit(name, mats, rot=None, spin=0.0, loc=(0, 0, 0), scale=0.001):
    """Import a STEP unit (paint/steel/bore STLs). Returns a dict with the parts, a parent empty,
    the world bbox (min, max) and the shafts (centre, axis, r, length) in metres, world space."""
    rot = rot or ROT.get(name, ROT["default"])
    parent = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(parent)
    objs = []
    for part in ("paint", "steel", "bore"):
        f = os.path.join(PARTS, f"{name}_{part}.stl")
        if not os.path.exists(f) or os.path.getsize(f) < 200:
            continue
        before = set(bpy.data.objects)
        bpy.ops.wm.stl_import(filepath=f, global_scale=scale)
        o = (set(bpy.data.objects) - before).pop()
        o.name = f"{name}_{part}"
        o.data.materials.append(mats[part])
        smooth(o, 30)
        o.parent = parent
        objs.append(o)
    r = Euler([math.radians(a) for a in rot], "XYZ").to_matrix()
    r.rotate(Euler((0, 0, math.radians(spin))))
    for o in objs:
        o.matrix_parent_inverse = Matrix.Identity(4)
        o.rotation_euler = r.to_euler()
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    # stand on z=0 and centre xy on the parent, then move the parent
    shift = Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))
    for o in objs:
        o.location = shift
    parent.location = loc
    bpy.context.view_layer.update()
    shafts = []
    meta = os.path.join(PARTS, f"{name}.json")
    if os.path.exists(meta):
        for s in json.load(open(meta))["shafts"]:
            c = r @ (Vector(s["c"]) * scale) + shift + Vector(loc)
            a = (r @ Vector(s["axis"])).normalized()
            shafts.append({"c": c, "axis": a, "r": s["r"] * scale, "area": s["area"]})
    return {"name": name, "parent": parent, "objs": objs, "min": mn + shift + Vector(loc),
            "max": mx + shift + Vector(loc), "shafts": shafts, "size": mx - mn}


# ----------------------------------------------------------------------------- primitives
def smooth(o, angle=30):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
    o.select_set(False)


def obj_from_bmesh(bm, name, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m)
    o.location = loc
    o.rotation_euler = rot
    return o


def box(name, size, m, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.verts[:] + bm.edges[:], offset=bevel, segments=3, affect="EDGES")
    o = obj_from_bmesh(bm, name, m, loc, rot)
    if bevel:
        smooth(o, 40)
    return o


def cyl(name, r, h, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=64, axis="Z", cap=True, chamfer=0.0):
    """Cylinder of radius r, length h, centred at loc, along the given axis."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=cap, segments=seg, radius1=r, radius2=r, depth=h)
    if chamfer:
        ends = [e for e in bm.edges if abs(abs(e.verts[0].co.z) - h / 2) < 1e-6 and abs(abs(e.verts[1].co.z) - h / 2) < 1e-6]
        bmesh.ops.bevel(bm, geom=ends, offset=chamfer, segments=2, affect="EDGES")
    o = obj_from_bmesh(bm, name, m, loc, rot)
    if axis == "X":
        o.rotation_euler = Euler((0, math.pi / 2, 0)) if rot == (0, 0, 0) else rot
    elif axis == "Y":
        o.rotation_euler = Euler((math.pi / 2, 0, 0)) if rot == (0, 0, 0) else rot
    smooth(o, 35)
    return o


def torus(name, R, r, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=96, rseg=24):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=rseg, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return o


def plane(name, size, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1)
    o.data.materials.append(m)
    return o


def bolts(prefix, positions, m, r=0.012, h=0.014, axis="Z"):
    for i, p in enumerate(positions):
        o = cyl(f"{prefix}_bolt{i}", r, h, m, loc=p, seg=6, axis=axis)
        o.data.materials.clear()
        o.data.materials.append(m)


# ----------------------------------------------------------------------------- environment
def rocks(name, m, x0, x1, y0, y1, z, n=500, rmin=0.02, rmax=0.06, heap=0.12, seed=1):
    """A heap of broken rock lying on a surface at height z between x0..x1, y0..y1."""
    import random
    rnd = random.Random(seed)
    bm = bmesh.new()
    for i in range(n):
        x = rnd.uniform(x0, x1)
        yc = (y0 + y1) / 2
        hw = (y1 - y0) / 2
        y = yc + hw * (rnd.random() * 2 - 1) * rnd.random() ** 0.5
        hz = heap * (1 - ((y - yc) / hw) ** 2) * rnd.uniform(0.3, 1.0)
        r = rnd.uniform(rmin, rmax)
        g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        vs = g["verts"]
        for v in vs:
            v.co = v.co * Vector((rnd.uniform(0.6, 1.3), rnd.uniform(0.6, 1.3), rnd.uniform(0.5, 1.0)))
        rot = Euler((rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28))).to_matrix()
        for v in vs:
            v.co = rot @ v.co + Vector((x, y, z + r * 0.5 + hz))
    o = obj_from_bmesh(bm, name, m)
    return o


def world_dark(strength=0.35, haze=0.0, tint=(0.75, 0.82, 0.95)):
    """Dark studio world: the built-in Blender studio HDR for reflections, dimmed and cooled,
    plus an optional thin volume haze (light beams on the floor)."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(bpy.utils.system_resource("DATAFILES"), "studiolights", "world", "studio.exr"))
    mul = nt.nodes.new("ShaderNodeMixRGB")
    mul.blend_type = "MULTIPLY"
    mul.inputs["Fac"].default_value = 1.0
    mul.inputs["Color2"].default_value = (*tint, 1)
    nt.links.new(env.outputs[0], mul.inputs["Color1"])
    # light path: camera sees pure black, reflections see the HDR
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    black = nt.nodes.new("ShaderNodeBackground")
    black.inputs[0].default_value = (0, 0, 0, 1)
    nt.links.new(mul.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = strength
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1])
    nt.links.new(black.outputs[0], mix.inputs[2])
    out = nt.nodes["World Output"]
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    if haze:
        vol = nt.nodes.new("ShaderNodeVolumeScatter")
        vol.inputs["Density"].default_value = haze
        vol.inputs["Anisotropy"].default_value = 0.3
        nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return w


def hall(mats, floor=40.0, ceiling_h=7.0, lamps=True, floor_mat="floor"):
    """A dark hall: glossy floor, back wall, long ceiling light strips that reflect in the floor."""
    f = plane("floor", (floor, floor), mats[floor_mat])
    plane("wall_back", (floor, ceiling_h * 2), mats["wall"], loc=(0, floor / 2, ceiling_h), rot=(math.pi / 2, 0, 0))
    plane("wall_left", (floor, ceiling_h * 2), mats["wall"], loc=(-floor / 2, 0, ceiling_h), rot=(math.pi / 2, 0, math.pi / 2))
    if lamps:
        for i, y in enumerate((-4, 2, 8, 14)):
            for x in (-6, 0, 6):
                box(f"lamp{i}_{x}", (4.0, 0.18, 0.08), mats["lamp"], loc=(x, y, ceiling_h - 0.5))
    return f


def light_area(name, loc, target, energy, size, color=(1, 1, 1), spread=180, shape="RECTANGLE", size_y=None):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.name = name
    l.data.energy = energy
    l.data.shape = shape
    l.data.size = size
    if size_y:
        l.data.size_y = size_y
    l.data.color = color
    l.data.spread = math.radians(spread)
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return l


def three_point(target, radius, key=(-1.0, -1.2, 1.3), fill=(1.4, -0.8, 0.5), rim=(0.4, 1.3, 0.9),
                ke=900, fe=220, re=700, kcol=(1.0, 0.96, 0.9), rcol=(0.8, 0.88, 1.0)):
    t = Vector(target)
    light_area("key", t + Vector(key).normalized() * radius * 4, t, ke * radius ** 2, radius * 2.2, kcol)
    light_area("fill", t + Vector(fill).normalized() * radius * 4, t, fe * radius ** 2, radius * 3.0, (1, 1, 1))
    light_area("rim", t + Vector(rim).normalized() * radius * 4, t, re * radius ** 2, radius * 1.4, rcol)


def camera(loc, target, lens=50, fstop=None, focus=None, shift=(0, 0), sensor=36):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    cam.data.lens = lens
    cam.data.sensor_width = sensor
    cam.data.shift_x, cam.data.shift_y = shift
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_distance = (Vector(focus or target) - Vector(loc)).length
    bpy.context.scene.camera = cam
    return cam


def render_settings(name, w=3840, h=2160, transparent=False, view="Khronos PBR Neutral", look="None", exposure=0.0):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.012 if not PREVIEW else 0.05
    sc.cycles.use_denoising = True
    sc.cycles.denoising_use_gpu = False
    sc.cycles.max_bounces = 8
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.5
    sc.render.film_transparent = transparent
    sc.view_settings.view_transform = view
    sc.view_settings.look = look
    sc.view_settings.exposure = exposure
    sc.render.resolution_x = int(w * SCALE)
    sc.render.resolution_y = int(h * SCALE)
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16" if not PREVIEW else "8"
    sc.render.image_settings.compression = 50
    sc.render.use_persistent_data = True
    os.makedirs(PREVIEW_DIR if PREVIEW else OUT, exist_ok=True)
    sc.render.filepath = os.path.join(PREVIEW_DIR if PREVIEW else OUT, name + ".png")
    return sc


def render(name, **kw):
    sc = render_settings(name, **kw)
    import time
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"rendered {sc.render.filepath} in {time.time() - t:.0f} s")


def fresh():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
