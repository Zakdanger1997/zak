#!/usr/bin/env python3
"""Pack the paint / steel / bore meshes of an i.Mak STEP model into one small GLB for the web.

Usage: python3 tools/parts_to_glb.py PARTS_DIR NAME out.glb [--tris 60000]
PARTS_DIR holds NAME_paint/_steel/_bore.stl from imak-mixing-brochure/tools/step_parts.py.
Needs Blender as a Python module (pip install bpy). Output is in metres, Y up, centred on
the floor, with three materials named paint / steel / bore so the page can restyle them.
"""
import math
import os
import sys

import bpy
from mathutils import Vector


def main(parts, name, out, tris=60000):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = []
    for part in ("paint", "steel", "bore"):
        f = os.path.join(parts, f"{name}_{part}.stl")
        if not os.path.exists(f) or os.path.getsize(f) < 200:
            continue
        bpy.ops.wm.stl_import(filepath=f, global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = part
        mt = bpy.data.materials.new(part)
        o.data.materials.append(mt)
        objs.append(o)
    total = sum(len(o.data.polygons) for o in objs)
    ratio = min(1.0, tris / max(total, 1))
    for o in objs:
        bpy.context.view_layer.objects.active = o
        if ratio < 1.0 and len(o.data.polygons) > 4000:
            d = o.modifiers.new("dec", "DECIMATE")
            d.ratio = ratio
            bpy.ops.object.modifier_apply(modifier="dec")
        o.select_set(True)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(32))
        bpy.ops.object.modifier_apply(modifier=o.modifiers[-1].name) if o.modifiers else None
        o.select_set(False)
    # STEP models are Z-up in Blender after import with the shaft along Y; stand them on the floor
    for o in objs:
        o.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    shift = Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))
    for o in objs:
        o.location += shift
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_apply=True,
                              export_yup=True, export_normals=True, export_materials="EXPORT")
    print(name, "tris", total, "->", sum(len(o.data.polygons) for o in objs), "size", [round(v, 3) for v in (mx - mn)])


if __name__ == "__main__":
    t = int(sys.argv[sys.argv.index("--tris") + 1]) if "--tris" in sys.argv else 60000
    main(sys.argv[1], sys.argv[2], sys.argv[3], t)
