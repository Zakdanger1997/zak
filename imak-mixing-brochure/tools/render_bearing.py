#!/usr/bin/env python3
"""Render a half-section of an agitator output stage (page 8) in Blender (Cycles).

Usage: python3 tools/render_bearing.py [--preview] [--samples N] [--points-only]
Output: assets/bearing-scene.png (transparent) and assets/bearing-points.json
(2D pixel positions used by tools/bearing_labels.py for dimensions and labels).

The model is illustrative: i.Mak-red housing with an output gear chamber, an
extended bearing barrel with two tapered roller bearings at spacing A, shaft
seal, mounting flange with ribs, and the agitator shaft down to an impeller hub.
"""
import json
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_tank as T  # shared helpers: mat, revolve, box, cyl, cut, obj_from_mesh, project

ASSETS = T.ASSETS
PREVIEW = "--preview" in sys.argv
SAMPLES = int(sys.argv[sys.argv.index("--samples") + 1]) if "--samples" in sys.argv else (24 if PREVIEW else 200)

SR = 0.0575                       # shaft radius (Ø115)
ZU, ZL = 0.36, 0.02               # upper / lower bearing centre -> spacing A = 0.34
ZF = -0.90                        # impeller hub: radial force acts here
SHAFT_BOT = ZF - 0.07


def half_cutter(material):
    o = T.box("cutter", (3, 1.5, 4), (0, -0.75, 0), material)
    o.hide_render = True
    o.display_type = "WIRE"
    return o


def tapered_bearing(name, zc, r_in, r_out, width, steel, roller, cutter, flip=False):
    """Tapered roller bearing as revolved rings + rollers (only the rear half of the rollers)."""
    t = math.radians(14) * (-1 if flip else 1)
    h = width / 2
    ri_o = r_in + (r_out - r_in) * 0.32          # inner ring outer race
    ro_i = r_in + (r_out - r_in) * 0.70          # outer ring inner race
    dz = math.tan(t) * h
    inner = T.revolve(name + "_in", [(r_in, zc - h), (ri_o - dz * 0.6, zc - h), (ri_o + dz * 0.6, zc + h), (r_in, zc + h)], steel, close=True)
    outer = T.revolve(name + "_out", [(ro_i - dz * 0.6, zc - h), (r_out, zc - h), (r_out, zc + h), (ro_i + dz * 0.6, zc + h)], steel, close=True)
    T.cut(inner, cutter)
    T.cut(outer, cutter)
    rm = (ri_o + ro_i) / 2
    rr = (ro_i - ri_o) / 2 * 0.92
    n = 18
    for i in range(n):
        phi = 2 * math.pi * i / n
        if math.sin(phi) < -0.05:                # front half is cut away
            continue
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=rr * 1.08, radius2=rr * 0.86, depth=width * 0.78,
                                        location=(rm * math.cos(phi), rm * math.sin(phi), zc))
        c = bpy.context.object
        d = Vector((math.sin(t) * math.cos(phi), math.sin(t) * math.sin(phi), math.cos(t)))
        c.rotation_euler = d.to_track_quat("Z", "X").to_euler()
        c.data.materials.append(roller)
        bpy.ops.object.shade_smooth()


def gear(name, z0, z1, r_root, r_tip, teeth, material, cutter):
    bm = bmesh.new()
    pts = []
    for k in range(teeth):
        a0 = 2 * math.pi * k / teeth
        da = 2 * math.pi / teeth
        for f, r in ((0.0, r_root), (0.18, r_root), (0.32, r_tip), (0.58, r_tip), (0.72, r_root)):
            pts.append((r * math.cos(a0 + f * da), r * math.sin(a0 + f * da)))
    bot = [bm.verts.new((x, y, z0)) for x, y in pts]
    top = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(bot[::-1])
    bm.faces.new(top)
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    o = T.obj_from_mesh(name, bm, material, smooth=False)
    T.cut(o, cutter)
    return o


def build():
    T.clean()
    sc = bpy.context.scene
    red = T.mat("i.Mak red", (0.62, 0.025, 0.045), rough=0.38, coat=0.35)
    section = T.mat("machined section", (0.11, 0.115, 0.125), metallic=0.0, rough=0.75)
    steel = T.mat("bearing steel", (0.62, 0.63, 0.65), metallic=1.0, rough=0.28)
    roller = T.mat("rollers", (0.88, 0.89, 0.90), metallic=1.0, rough=0.10)
    polish = T.mat("shaft", (0.86, 0.87, 0.88), metallic=1.0, rough=0.14)
    gearm = T.mat("gear", (0.45, 0.46, 0.48), metallic=1.0, rough=0.35)
    rubber = T.mat("seal", (0.03, 0.03, 0.035), rough=0.6)
    cutter = half_cutter(section)

    # gear chamber (hollow box) on top of the bearing barrel
    shell = T.box("chamber", (0.70, 0.56, 0.28), (0, 0, 0.53), red, bevel=0.02)
    inner = T.box("chamber_void", (0.62, 0.48, 0.22), (0, 0, 0.535), red)
    inner.hide_render = True
    m = shell.modifiers.new("void", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = inner
    bore = T.cyl("chamber_bore", 0.125, 0.30, 0.45, red)
    bore.hide_render = True
    m2 = shell.modifiers.new("bore", "BOOLEAN")
    m2.operation = "DIFFERENCE"
    m2.object = bore
    T.cut(shell, cutter)

    # bearing barrel with stepped bore (revolved closed profile)
    prof = [(0.105, 0.39), (0.105, 0.33), (0.082, 0.33), (0.082, 0.055), (0.12, 0.055), (0.12, -0.015),
            (0.09, -0.015), (0.09, -0.065), (0.30, -0.065), (0.30, -0.105), (0.072, -0.105), (0.072, -0.07),
            (0.17, -0.07), (0.17, 0.40), (0.105, 0.40)]
    # (the profile is drawn as one outline: bore steps, flange, outer wall)
    barrel = T.revolve("barrel", [(0.125, 0.40), (0.125, 0.325), (0.095, 0.325), (0.095, 0.06), (0.14, 0.06),
                                  (0.14, -0.02), (0.10, -0.02), (0.10, -0.065), (0.072, -0.065), (0.072, -0.105),
                                  (0.33, -0.105), (0.33, -0.065), (0.205, -0.065), (0.205, 0.40)], red, close=True)
    T.cut(barrel, cutter)
    for k in range(6):
        a = math.radians(30 + k * 60)
        if math.sin(a) < 0:
            continue
        rib = T.box(f"rib{k}", (0.12, 0.022, 0.16), (0.26 * math.cos(a), 0.26 * math.sin(a), 0.0), red, bevel=0.004)
        rib.rotation_euler[2] = a
        # tapered rib: shear the top inwards with a simple scale on z-position of verts
        for v in rib.data.vertices:
            if v.co.z > 0 and v.co.x > 0:
                v.co.x -= 0.05
    # flange bolts
    for k in range(12):
        a = math.radians(15 + k * 30)
        if math.sin(a) < -0.1:
            continue
        T.cyl(f"fbolt{k}", 0.016, -0.065, -0.045, steel, verts=6, loc=(0.29 * math.cos(a), 0.29 * math.sin(a)))

    # output gear, keyed on the shaft
    gear("gear", 0.45, 0.56, 0.24, 0.257, 64, gearm, cutter)
    hub = T.cyl("gear_hub", 0.11, 0.43, 0.58, gearm)
    T.cut(hub, cutter)

    # bearings (upper smaller, lower larger; opposed tapered rollers)
    tapered_bearing("brg_up", ZU, SR, 0.125, 0.07, steel, roller, cutter, flip=False)
    tapered_bearing("brg_lo", ZL, SR, 0.14, 0.08, steel, roller, cutter, flip=True)
    # shaft seal
    seal = T.revolve("seal", [(SR, -0.062), (0.10, -0.062), (0.10, -0.024), (0.088, -0.024), (0.08, -0.047), (SR, -0.032)], rubber, close=True)
    T.cut(seal, cutter)

    # shaft + impeller hub
    T.cyl("shaft", SR, SHAFT_BOT, 0.60, polish, verts=96)
    T.cyl("hub", 0.095, ZF - 0.07, ZF + 0.07, polish, bevel=0.006)
    for k in range(3):
        a = math.radians(-60 + k * 120)
        b = T.box(f"blade{k}", (0.20, 0.10, 0.012), (0.18 * math.cos(a), 0.18 * math.sin(a), ZF), polish, bevel=0.003)
        b.rotation_euler = (math.radians(28), 0, a)

    # ground shadow
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, SHAFT_BOT - 0.25))
    bpy.context.object.is_shadow_catcher = True

    w = bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(bpy.utils.system_resource("DATAFILES"), "studiolights", "world", "studio.exr"))
    w.node_tree.links.new(env.outputs[0], w.node_tree.nodes["Background"].inputs[0])
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.55

    def area(loc, energy, size):
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.data.energy = energy
        l.data.size = size
        l.rotation_euler = (Vector((0, 0, 0.1)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    area((-3.5, -4.5, 3.5), 520, 2.5)
    area((4.0, -3.0, 1.0), 220, 3.0)
    area((0.5, 3.5, 3.0), 500, 2.0)

    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 85
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    target = Vector((0, 0, -0.16))
    az, elev, dist = math.radians(-114), math.radians(12), 4.9
    cam.location = target + dist * Vector((math.cos(elev) * math.cos(az), math.cos(elev) * math.sin(az), math.sin(elev)))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

    r = sc.render
    r.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    r.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    r.resolution_x, r.resolution_y = (520, 760) if PREVIEW else (1300, 1900)
    r.filepath = os.path.join(ASSETS, "bearing-preview.png" if PREVIEW else "bearing-scene.png")
    return sc, cam


def main():
    sc, cam = build()
    if "--points-only" not in sys.argv:          # re-export label positions without rendering
        bpy.ops.render.render(write_still=True)
    bpy.context.view_layer.update()              # camera matrix must be current for the projection
    P = lambda p: T.project(sc, cam, p)
    defl = []                     # exaggerated deflection line from the lower bearing to the hub
    for i in range(13):
        z = ZL - (ZL - ZF) * i / 12
        u = (ZL - z) / (ZL - ZF)
        defl.append(P((0.11 * u ** 2, -SR, z)))
    pts = {
        "size": [sc.render.resolution_x, sc.render.resolution_y],
        "a_top": P((-0.40, 0, ZU)), "a_bot": P((-0.40, 0, ZL)),
        "brg_up_l": P((-0.125, 0, ZU)), "brg_lo_l": P((-0.14, 0, ZL)),
        "x_top": P((0.42, 0, ZL)), "x_bot": P((0.42, 0, ZF)),
        "brg_lo_r": P((0.14, 0, ZL)), "force_r": P((0.42, 0, ZF)),
        "force_at": P((SR, -SR, ZF)), "force_to": P((0.34, -SR, ZF)),
        "deflection": defl,
        "gear": P((0.22, 0.0, 0.50)), "chamber": P((0.24, 0.12, 0.67)),
        "brg_up": P((0.11, 0.0, ZU + 0.01)), "brg_lo": P((0.125, 0.0, ZL)),
        "seal": P((0.09, 0.0, -0.045)), "flange": P((0.31, -0.12, -0.085)),
        "rib": P((0.27, 0.15, 0.03)), "shaft": P((SR, -SR, -0.45)), "hub": P((0.095, -0.05, ZF + 0.05)),
    }
    json.dump(pts, open(os.path.join(ASSETS, "bearing-points-preview.json" if PREVIEW else "bearing-points.json"), "w"), indent=1)
    print("ok")


if __name__ == "__main__":
    main()
