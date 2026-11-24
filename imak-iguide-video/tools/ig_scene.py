#!/usr/bin/env python3
"""Blender plates for the i-Guide teaser (9:16): dark showroom with a giant phone, a crane hook cutout, a red button.

Usage: python3 tools/ig_scene.py bg|hook|dome [--samples N]
  bg   -> assets/bg.png + assets/bg.json (screen rectangle in pixels, for compose.html)
  hook -> assets/hook.png (transparent, hook block hanging from its rope, front view)
  dome -> assets/dome.png (transparent red push button dome)
"""
import json
import math
import os
import sys

sys.argv = [sys.argv[0]] + sys.argv[1:]
sys.path.insert(0, "/home/user/zak/imak-bakery-video/tools")
import scenekit as K  # noqa: E402
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PART = sys.argv[1] if len(sys.argv) > 1 else "bg"
SAMPLES = int(K.arg("--samples", 64))


def clear():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def emit(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o.inputs[0])
    return m


def setup(res, transparent=False):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = transparent
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"


def bg():
    clear(); K.mats(); setup((1080, 1920))
    wallm = K.plain("wall", (14, 15, 17), 0.6)
    slatm = K.plain("slat", (22, 23, 26), 0.5)
    floorm = K.plain("floor", (36, 38, 42), 0.12, coat=0.6)
    frame = K.metal_mat("phone frame", (60, 62, 66), 0.25)
    blk = K.plain("glass black", (6, 6, 8), 0.05, coat=1.0)
    warm = emit("led", (1.0, 0.72, 0.42), 6.0)
    K.boxo((30, 0.2, 12), (0, 3.2, 6), wallm, "wall", bevel=0.0)
    for i in range(-30, 31):                                    # vertical slats
        K.boxo((0.06, 0.08, 12), (i * 0.18, 3.06, 6), slatm, "slat", bevel=0.005)
    for x in (-2.55, 2.55):                                     # warm LED strips
        K.boxo((0.05, 0.05, 12), (x, 3.0, 6), warm, "led", bevel=0.0)
    K.boxo((12, 0.06, 0.04), (0, 3.0, 6.2), warm, "led top", bevel=0.0)
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); bpy.context.object.data.materials.append(floorm)
    # the giant phone itself is drawn in compose.html (crisp corners, exact screen)
    # red button pedestal, right of the phone (dome rendered separately)
    K.boxo((0.62, 0.62, 0.95), (1.75, 0.0, 0.475), K.plain("marble", (225, 222, 216), 0.25, coat=0.4), "pedestal", bevel=0.01)
    K.cyl(0.2, 0.06, K.MAT["machined"], axis="Z", loc=(1.75, 0.0, 0.98), name="button ring")
    K.area((0, -6, 6), (0, 0.5, 2), 700, 6)
    K.area((-4, -2, 3), (0, 0.5, 2), 400, 2, (1.0, 0.8, 0.6))
    K.area((4, -2, 3), (0, 0.5, 2), 400, 2, (1.0, 0.8, 0.6))
    cam, tgt = K.camera((0, -9.2, 2.2), (0, 0.6, 2.2), lens=42)
    cam.constraints.clear(); cam.rotation_euler = (math.radians(90), 0, 0)
    cam.data.shift_y = 0.012
    bpy.context.view_layer.update()
    sc = bpy.context.scene
    def px(x, y, z):
        v = world_to_camera_view(sc, cam, Vector((x, y, z)))
        return v.x * 1080, (1 - v.y) * 1920
    bx, by = px(1.75, 0.0, 1.01)
    fx, fy = px(0, 0.6, 0.0)                                   # floor point under the phone position
    json.dump({"button": [bx, by], "floor_y": fy}, open(os.path.join(ROOT, "assets", "bg.json"), "w"))
    sc.render.filepath = os.path.join(ROOT, "assets", "bg.png")
    bpy.ops.render.render(write_still=True)


def hook():
    clear(); K.mats(); setup((600, 900), transparent=True)
    g = K.build_hook_block(Vector((0, 0, 0)), 0)
    for c in list(g.children):
        if c.name.startswith("load") or c.name.startswith("sling"):
            bpy.data.objects.remove(c, do_unlink=True)
    K.cyl(0.012, 1.2, K.MAT["rope"], axis="Z", loc=(-0.04, 0, 0.6), name="rope l")
    K.cyl(0.012, 1.2, K.MAT["rope"], axis="Z", loc=(0.04, 0, 0.6), name="rope r")
    K.area((-2, -3, 2), (0, 0, 0), 300, 2); K.area((2, -2, 1), (0, 0, 0), 150, 1, (0.8, 0.9, 1.0))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 1.6; cam.location = (0, -5, -0.05); cam.rotation_euler = (math.radians(90), 0, math.radians(0))
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = os.path.join(ROOT, "assets", "hook.png")
    bpy.ops.render.render(write_still=True)


def dome():
    clear(); K.mats(); setup((500, 300), transparent=True)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0, 0, 0), segments=48, ring_count=24)
    d = bpy.context.object; d.scale = (1, 1, 0.55); bpy.ops.object.shade_smooth()
    d.data.materials.append(K.paint_mat("button red", (215, 18, 20), rough=0.15, coat=1.0, cast=0.0, peel=0.0))
    K.area((-1, -2, 2), (0, 0, 0), 120, 1); K.area((1.5, -1, 1), (0, 0, 0), 60, 1)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.scene.collection.objects.link(cam)
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 0.4; cam.location = (0, -3, 0.06); cam.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = os.path.join(ROOT, "assets", "dome.png")
    bpy.ops.render.render(write_still=True)


{"bg": bg, "hook": hook, "dome": dome}[PART]()
