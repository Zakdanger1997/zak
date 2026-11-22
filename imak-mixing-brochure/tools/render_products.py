#!/usr/bin/env python3
"""Studio renders of the i.Mak STEP models (one consistent look for the whole brochure).

Usage:
    python3 tools/render_products.py PARTS_DIR [names...] [--preview] [--samples N]
PARTS_DIR holds <name>_paint/_steel/_bore.stl from tools/step_parts.py.
Writes assets/3d-<key>.png (transparent, soft floor shadow, cropped).

Every unit uses the same camera direction, lens, lights and materials; ROT gives
the rotation (degrees, XYZ) that stands each model on its feet / flange.
"""
import math
import os
import sys

import bpy
from mathutils import Euler, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
ARGS = [a for i, a in enumerate(sys.argv[1:], 1)
        if not a.startswith("--") and sys.argv[i - 1] not in ("--samples", "--exposure", "--spec")]
PREVIEW = "--preview" in sys.argv
SAMPLES = int(sys.argv[sys.argv.index("--samples") + 1]) if "--samples" in sys.argv else (12 if PREVIEW else 160)

# model name -> (output key, rotation XYZ in degrees applied after import, extra Z spin for the view)
MODELS = {
    "MA703-G00":  ("ma", (90, 0, 0), 180),
    "MK_703-G07": ("mk", (90, 0, 0), 0),
    "IRK_93":     ("irk", (90, 0, 0), 0),
    "IRA_93":     ("ir", (90, 0, 0), 0),
    "YP_93":      ("yp", (90, 0, 0), 0),
    "IRSD_83":    ("irsd", (90, 0, 0), 0),
    "IRC_93":     ("irc", (90, 0, 0), 0),
    "IRO_61":     ("iro", (90, 0, 0), 0),
    "IRNX_7":     ("irnx", (90, 0, 0), 0),
    "S_90":       ("s", (90, 0, 0), 0),
    # geared motors with their i.Mak motors
    "IRKM_93-160_L":  ("irkm", (90, 0, 0), 0),
    "IRAM_93-160_L":  ("iram", (90, 0, 0), 0),
    "IRFM_93-160_L":  ("irfm", (90, 0, 0), 0),
    "YPM_93-160_L":   ("ypm", (90, 0, 0), 0),
    "IRSDM_83-112_M": ("irsdm", (90, 0, 0), 0),
}
VIEW_AZ, VIEW_EL = -38.0, 22.0       # camera direction, same for every unit
RAL3020 = (0.6038, 0.0018, 0.0015)   # RAL 3020 Traffic Red, sRGB #CC0605 in linear values
SPEC = float(sys.argv[sys.argv.index("--spec") + 1]) if "--spec" in sys.argv else 0.05
EXPOSURE = float(sys.argv[sys.argv.index("--exposure") + 1]) if "--exposure" in sys.argv else -0.55


def materials():
    def m(name, col, metal, rough, coat=0.0, aniso=0.0):
        mt = bpy.data.materials.new(name)
        mt.use_nodes = True
        p = mt.node_tree.nodes["Principled BSDF"]
        p.inputs["Base Color"].default_value = (*col, 1)
        p.inputs["Metallic"].default_value = metal
        p.inputs["Roughness"].default_value = rough
        if coat:
            p.inputs["Coat Weight"].default_value = coat
            p.inputs["Coat Roughness"].default_value = 0.08
        if aniso:
            p.inputs["Anisotropic"].default_value = aniso
        if metal == 0.0:
            p.inputs["Specular IOR Level"].default_value = SPEC
        return mt
    return {
        "paint": m("RAL 3020 traffic red", RAL3020, 0.0, 0.5),
        "steel": m("shaft steel", (0.86, 0.87, 0.88), 1.0, 0.16, aniso=0.3),
        "bore": m("machined", (0.42, 0.43, 0.45), 0.8, 0.38),
    }


def setup_world(sc):
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(bpy.utils.system_resource("DATAFILES"), "studiolights", "world", "studio.exr"))
    w.node_tree.links.new(env.outputs[0], w.node_tree.nodes["Background"].inputs[0])
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.30


def render_one(name, parts_dir):
    key, rot, spin = MODELS[name]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    mats = materials()
    objs = []
    for part in ("paint", "steel", "bore"):
        f = os.path.join(parts_dir, f"{name}_{part}.stl")
        if not os.path.exists(f) or os.path.getsize(f) < 200:
            continue
        bpy.ops.wm.stl_import(filepath=f, global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.data.materials.append(mats[part])
        bpy.ops.object.shade_auto_smooth(angle=math.radians(32))
        objs.append(o)
    # rotate the whole model about the origin, then put it on the floor, centred
    for o in objs:
        o.rotation_euler = Euler([math.radians(a) for a in rot], "XYZ")
        o.rotation_euler.rotate(Euler((0, 0, math.radians(spin))))
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    shift = Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))
    for o in objs:
        o.location += shift
    size = (mx - mn)
    radius = size.length / 2
    target = Vector((0, 0, size.z / 2))

    bpy.ops.mesh.primitive_plane_add(size=radius * 12, location=(0, 0, 0))
    bpy.context.object.is_shadow_catcher = True
    setup_world(sc)

    def area(direction, energy, size_):
        loc = target + Vector(direction).normalized() * radius * 6
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.data.energy = energy * radius ** 2 * 4
        l.data.size = size_ * radius
        l.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
    area((-1.0, -1.1, 1.4), 120, 2.4)     # key, front-left-top
    area((1.3, -0.6, 0.4), 40, 3.0)      # fill, right
    area((0.3, 1.2, 1.0), 80, 1.6)       # rim, behind

    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.data.lens = 85
    az, el = math.radians(VIEW_AZ - 90), math.radians(VIEW_EL)
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    cam.location = target + d * radius * 7.4
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"      # keeps the RAL colour exact on lit faces
    sc.view_settings.look = "None"
    sc.view_settings.exposure = EXPOSURE
    sc.render.resolution_x = sc.render.resolution_y = 420 if PREVIEW else 1200
    out = os.path.join(ASSETS, f"3d-{key}{'-preview' if PREVIEW else ''}.png")
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    crop(out)
    print("rendered", name, "->", out)


def crop(path):
    """Trim to the product (+ a little of its floor shadow)."""
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert("RGBA")
    a = np.array(im).astype(np.float32)
    shadow = a[..., :3].max(axis=2) < 10
    al = a[..., 3]
    al[shadow] = np.clip((al[shadow] - 30) * 1.2, 0, 255)
    solid = (al > 8) & ~shadow
    ys, xs = np.where(solid)
    pad = int(im.width * 0.03)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, im.width)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, im.height)
    a = a[y0:y1, x0:x1]
    h, w = a.shape[:2]
    sh = a[..., :3].max(axis=2) < 10
    fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (w * 0.08), 0, 1)
    fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (h * 0.08), 0, 1)
    a[..., 3] = np.where(sh, a[..., 3] * np.minimum(fx[None, :], fy[:, None]), a[..., 3])
    Image.fromarray(a.astype(np.uint8), "RGBA").save(path, optimize=True)


def main():
    parts_dir = ARGS[0]
    names = ARGS[1:] or list(MODELS)
    for n in names:
        render_one(n, parts_dir)


if __name__ == "__main__":
    main()
