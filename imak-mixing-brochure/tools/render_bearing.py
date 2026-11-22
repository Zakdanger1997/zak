#!/usr/bin/env python3
"""Render a half-section of a vertical agitator gear unit (page 8) in Blender (Cycles).

Usage: python3 tools/render_bearing.py [--preview] [--samples N] [--points-only]
Output: assets/bearing-scene.png (transparent) and assets/bearing-points.json
(2D pixel positions used by tools/bearing_labels.py for dimensions and labels).

Illustrative two-stage parallel-shaft unit in the style of i.Mak's cut-away posters:
the housing is sectioned, gears and shafts are shown whole, bearings are cut so the
rolling elements show.
  input shaft (from the motor adapter / PAM flange) with pinion Z1
  intermediate shaft with gear Z2 and pinion Z3
  output shaft with gear Z4, two tapered roller bearings at spacing a in an
  extended bearing barrel, shaft seal, mounting flange, agitator shaft and hub.
All shaft axes are vertical and lie in the cut plane y = 0.
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

# ---- output stage ----
SR = 0.0575                       # output shaft radius (Ø115)
ZU, ZL = 0.36, 0.02               # upper / lower output bearing centre -> spacing a = 0.34
ZF = -0.56                        # impeller hub: radial force acts here
SHAFT_BOT = ZF - 0.07

# ---- gear train (module, teeth) ----
M1, Z1, Z2 = 0.008, 13, 43        # stage 1: input pinion / intermediate gear
M2, Z3, Z4 = 0.012, 11, 43        # stage 2: intermediate pinion / output gear
BETA = math.radians(15)           # helix angle
R1, R2 = M1 * Z1 / 2, M1 * Z2 / 2
R3, R4 = M2 * Z3 / 2, M2 * Z4 / 2
X_OUT = 0.0
X_INT = X_OUT - (R3 + R4)         # intermediate shaft
X_IN = X_INT - (R1 + R2)          # input shaft

# ---- housing heights ----
CH_Z0, CH_Z1 = 0.40, 0.735         # gear chamber (outer)
WALL = 0.035
S2_Z0, S2_Z1 = 0.462, 0.565         # stage-2 gear face width
S1_Z0, S1_Z1 = 0.598, 0.672       # stage-1 gear face width
B_BOT, B_TOP = 0.425, 0.71       # bearing centres in the bottom and top walls
LANTERN_Z1 = 0.90


def half_cutter(material):
    o = T.box("cutter", (3, 1.5, 4), (0, -0.75, 0), material)
    o.hide_render = True
    o.display_type = "WIRE"
    return o


def tooth_profile(m, z, steps=4):
    """2D outline of a spur gear with straight-flank (20°) teeth and round tips."""
    r = m * z / 2
    ra, rf = r + m, r - 1.25 * m
    pitch = 2 * math.pi / z
    half_p = (math.pi * m / 2) / r / 2          # half tooth thickness at pitch circle (angle)
    tan20 = math.tan(math.radians(20))
    half_a = half_p - (ra - r) * tan20 / r        # at tip
    half_f = half_p + (r - rf) * tan20 / r        # at root
    pts = []
    for k in range(z):
        c = k * pitch
        # root gap (from previous tooth) -> flank up -> tip arc -> flank down
        for i in range(steps + 1):
            a = c - pitch / 2 + (pitch / 2 - half_f) * i / steps
            pts.append((rf * math.cos(a), rf * math.sin(a)))
        for i in range(1, steps + 1):
            t = i / steps
            rr = rf + (ra - rf) * t
            a = c - (half_f + (half_a - half_f) * t)
            pts.append((rr * math.cos(a), rr * math.sin(a)))
        for i in range(1, steps):
            a = c - half_a + 2 * half_a * i / steps
            pts.append((ra * math.cos(a), ra * math.sin(a)))
        for i in range(steps + 1):
            t = 1 - i / steps
            rr = rf + (ra - rf) * t
            a = c + (half_f + (half_a - half_f) * t)
            pts.append((rr * math.cos(a), rr * math.sin(a)))
        for i in range(1, steps):
            a = c + half_f + (pitch / 2 - half_f) * i / steps
            pts.append((rf * math.cos(a), rf * math.sin(a)))
    return pts, r


def helical_gear(name, m, z, x, z0, z1, hand, phase, material, layers=10):
    """Helical gear: the tooth outline is twisted along the face width (hand = +1 / -1)."""
    prof, r = tooth_profile(m, z)
    bm = bmesh.new()
    rings = []
    for li in range(layers + 1):
        zz = z0 + (z1 - z0) * li / layers
        tw = phase + hand * math.tan(BETA) * (zz - z0) / r
        ca, sa = math.cos(tw), math.sin(tw)
        rings.append([bm.verts.new((x + px * ca - py * sa, py * ca + px * sa, zz)) for px, py in prof])
    n = len(prof)
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    o = T.obj_from_mesh(name, bm, material, smooth=False)
    b = o.modifiers.new("chamfer", "BEVEL")
    b.width = m * 0.12
    b.segments = 1
    b.limit_method = "ANGLE"
    return o


def gear_face_detail(x, z0, z1, r_hub, r_web, material):
    """Recessed web rings on both faces so large gears read as machined parts."""
    for zz in (z0, z1):
        s = -1 if zz == z0 else 1
        T.cyl(f"web{x:.2f}{zz:.2f}", r_web, zz - 0.004 * (s < 0) , zz + 0.004 * (s > 0), material, loc=(x, 0))
        T.cyl(f"hubface{x:.2f}{zz:.2f}", r_hub, zz - 0.010 * (s < 0), zz + 0.010 * (s > 0), material, loc=(x, 0))


def tapered_bearing(name, zc, r_in, r_out, width, steel, roller, cutter, x=0.0, flip=False):
    t = math.radians(14) * (-1 if flip else 1)
    h = width / 2
    ri_o = r_in + (r_out - r_in) * 0.32
    ro_i = r_in + (r_out - r_in) * 0.70
    dz = math.tan(t) * h
    inner = T.revolve(name + "_in", [(r_in, zc - h), (ri_o - dz * 0.6, zc - h), (ri_o + dz * 0.6, zc + h), (r_in, zc + h)], steel, close=True)
    outer = T.revolve(name + "_out", [(ro_i - dz * 0.6, zc - h), (r_out, zc - h), (r_out, zc + h), (ro_i + dz * 0.6, zc + h)], steel, close=True)
    for o in (inner, outer):
        o.location.x = x
        T.cut(o, cutter)
    rm = (ri_o + ro_i) / 2
    rr = (ro_i - ri_o) / 2 * 0.92
    n = 18
    for i in range(n):
        phi = 2 * math.pi * i / n
        if math.sin(phi) < -0.05:
            continue
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=rr * 1.08, radius2=rr * 0.86, depth=width * 0.78,
                                        location=(x + rm * math.cos(phi), rm * math.sin(phi), zc))
        c = bpy.context.object
        d = Vector((math.sin(t) * math.cos(phi), math.sin(t) * math.sin(phi), math.cos(t)))
        c.rotation_euler = d.to_track_quat("Z", "X").to_euler()
        c.data.materials.append(roller)
        bpy.ops.object.shade_smooth()


def ball_bearing(name, x, zc, r_in, r_out, width, steel, ball, cutter):
    h = width / 2
    rm = (r_in + r_out) / 2
    rb = (r_out - r_in) * 0.27
    inner = T.revolve(name + "_in", [(r_in, zc - h), (rm - rb * 0.55, zc - h), (rm - rb * 0.55, zc + h), (r_in, zc + h)], steel, close=True)
    outer = T.revolve(name + "_out", [(rm + rb * 0.55, zc - h), (r_out, zc - h), (r_out, zc + h), (rm + rb * 0.55, zc + h)], steel, close=True)
    for o in (inner, outer):
        o.location.x = x
        T.cut(o, cutter)
    n = max(8, int(2 * math.pi * rm / (rb * 2.4)))
    for i in range(n):
        phi = 2 * math.pi * i / n
        if math.sin(phi) < -0.05:
            continue
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=rb, location=(x + rm * math.cos(phi), rm * math.sin(phi), zc))
        s = bpy.context.object
        s.data.materials.append(ball)
        bpy.ops.object.shade_smooth()


def bore(name, x, z0, z1, r):
    o = T.cyl(name, r, z0, z1, None if False else bpy.data.materials[0], loc=(x, 0))
    o.hide_render = True
    o.display_type = "WIRE"
    return o


def build():
    T.clean()
    sc = bpy.context.scene
    red = T.mat("i.Mak red", (0.62, 0.025, 0.045), rough=0.38, coat=0.35)
    section = T.mat("machined section", (0.11, 0.115, 0.125), metallic=0.0, rough=0.75)
    steel = T.mat("bearing steel", (0.62, 0.63, 0.65), metallic=1.0, rough=0.28)
    roller = T.mat("rollers", (0.88, 0.89, 0.90), metallic=1.0, rough=0.10)
    polish = T.mat("shaft", (0.86, 0.87, 0.88), metallic=1.0, rough=0.14)
    gearm = T.mat("ground gear steel", (0.50, 0.51, 0.53), metallic=1.0, rough=0.30)
    pinion = T.mat("pinion steel", (0.58, 0.59, 0.61), metallic=1.0, rough=0.24)
    rubber = T.mat("seal", (0.03, 0.03, 0.035), rough=0.6)
    brass = T.mat("brass", (0.80, 0.55, 0.22), metallic=1.0, rough=0.3)
    cutter = half_cutter(section)

    # ---------- housing: gear chamber with bearing bosses, then cut ----------
    x0, x1 = X_IN - 0.11, X_OUT + R4 + 0.07
    cx, wx = (x0 + x1) / 2, x1 - x0
    shell = T.box("chamber", (wx, 0.62, CH_Z1 - CH_Z0), (cx, 0, (CH_Z0 + CH_Z1) / 2), red, bevel=0.02)
    void = T.box("chamber_void", (wx - 2 * WALL, 0.62 - 2 * WALL, CH_Z1 - CH_Z0 - 2 * WALL), (cx, 0, (CH_Z0 + CH_Z1) / 2), red)
    void.hide_render = True
    void.display_type = "WIRE"
    holes = [void]
    # bearing bores through bottom and top walls (input, intermediate), output bore in the bottom
    for nm, x, r in (("in", X_IN, 0.062), ("int", X_INT, 0.082)):
        holes.append(T.cyl(f"bore_{nm}", r, CH_Z0 - 0.02, CH_Z1 + 0.02, red, loc=(x, 0)))
    holes.append(T.cyl("bore_out", 0.125, CH_Z0 - 0.05, CH_Z0 + 0.06, red, loc=(X_OUT, 0)))
    for h in holes[1:]:
        h.hide_render = True
        h.display_type = "WIRE"
    for h in holes:
        m = shell.modifiers.new("hole", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.object = h
    T.cut(shell, cutter)
    # bearing bosses (rings around the bores, inside the chamber) - cut too
    for nm, x, ri, ro in (("in", X_IN, 0.062, 0.088), ("int", X_INT, 0.082, 0.108)):
        for zz0, zz1 in ((CH_Z0 + WALL, CH_Z0 + WALL + 0.03), (CH_Z1 - WALL - 0.03, CH_Z1 - WALL)):
            boss = T.revolve(f"boss_{nm}{zz0:.2f}", [(ri, zz0), (ro, zz0), (ro, zz1), (ri, zz1)], red, close=True)
            boss.location.x = x
            T.cut(boss, cutter)
    # internal stiffening rib between the bosses on the back wall
    rib = T.box("rib_back", (0.03, 0.03, 0.5), ((X_IN + X_INT) / 2, 0.255, (CH_Z0 + CH_Z1) / 2), red)
    rib.rotation_euler[1] = math.radians(38)

    # motor adapter (PAM flange lantern) on top of the input shaft
    lan = T.revolve("lantern", [(0.075, CH_Z1), (0.12, CH_Z1), (0.12, CH_Z1 + 0.02), (0.095, CH_Z1 + 0.03),
                                (0.095, LANTERN_Z1 - 0.03), (0.15, LANTERN_Z1 - 0.03), (0.15, LANTERN_Z1),
                                (0.085, LANTERN_Z1), (0.085, CH_Z1 + 0.02), (0.075, CH_Z1 + 0.02)], red, close=True)
    lan.location.x = X_IN
    T.cut(lan, cutter)
    # jaw coupling inside the lantern
    T.cyl("coupl_lo", 0.05, CH_Z1 + 0.06, CH_Z1 + 0.10, steel, loc=(X_IN, 0), bevel=0.003)
    T.cyl("coupl_mid", 0.046, CH_Z1 + 0.10, CH_Z1 + 0.115, rubber, loc=(X_IN, 0))
    T.cyl("coupl_hi", 0.05, CH_Z1 + 0.115, CH_Z1 + 0.155, steel, loc=(X_IN, 0), bevel=0.003)
    T.cyl("motor_shaft", 0.024, CH_Z1 + 0.15, LANTERN_Z1 + 0.02, polish, loc=(X_IN, 0))
    # breather plug on the cover
    T.cyl("breather", 0.012, CH_Z1, CH_Z1 + 0.035, brass, verts=6, loc=(X_INT, 0.18))

    # ---------- extended output bearing barrel with stepped bore + flange ----------
    barrel = T.revolve("barrel", [(0.125, CH_Z0 + 0.02), (0.125, 0.325), (0.095, 0.325), (0.095, 0.06), (0.14, 0.06),
                                  (0.14, -0.02), (0.10, -0.02), (0.10, -0.065), (0.072, -0.065), (0.072, -0.105),
                                  (0.33, -0.105), (0.33, -0.065), (0.205, -0.065), (0.205, CH_Z0 + 0.02)], red, close=True)
    T.cut(barrel, cutter)
    for k in range(6):
        a = math.radians(30 + k * 60)
        if math.sin(a) < 0:
            continue
        rb = T.box(f"rib{k}", (0.12, 0.022, 0.16), (0.26 * math.cos(a), 0.26 * math.sin(a), 0.0), red, bevel=0.004)
        rb.rotation_euler[2] = a
    for k in range(12):
        a = math.radians(15 + k * 30)
        if math.sin(a) < -0.1:
            continue
        T.cyl(f"fbolt{k}", 0.016, -0.065, -0.045, steel, verts=6, loc=(0.29 * math.cos(a), 0.29 * math.sin(a)))

    # ---------- shafts ----------
    T.cyl("shaft_in", 0.030, B_BOT - 0.03, CH_Z1 + 0.10, polish, loc=(X_IN, 0))
    T.cyl("shaft_int", 0.040, B_BOT - 0.03, B_TOP + 0.03, polish, loc=(X_INT, 0))
    T.cyl("shaft_out", SR, SHAFT_BOT, S2_Z1 + 0.03, polish, verts=96)

    # ---------- gears (whole, meshing; opposite hands per pair) ----------
    # pinions are drawn with half a tooth offset so the teeth interleave on the centre line
    helical_gear("Z1", M1, Z1, X_IN, S1_Z0, S1_Z1, +1, 0.0, pinion)
    helical_gear("Z2", M1, Z2, X_INT, S1_Z0, S1_Z1, -1, math.pi + math.pi / Z2, gearm)
    gear_face_detail(X_INT, S1_Z0, S1_Z1, 0.07, R2 - 2.2 * M1, gearm)
    helical_gear("Z3", M2, Z3, X_INT, S2_Z0, S2_Z1, +1, 0.0, pinion)
    helical_gear("Z4", M2, Z4, X_OUT, S2_Z0, S2_Z1, -1, math.pi + math.pi / Z4, gearm)
    gear_face_detail(X_OUT, S2_Z0, S2_Z1, 0.11, R4 - 2.2 * M2, gearm)
    # spacer sleeve on the intermediate shaft
    T.cyl("spacer", 0.052, S2_Z1, S1_Z0, steel, loc=(X_INT, 0))

    # ---------- bearings ----------
    ball_bearing("brg_in_lo", X_IN, B_BOT, 0.030, 0.062, 0.03, steel, roller, cutter)
    ball_bearing("brg_in_hi", X_IN, B_TOP, 0.030, 0.062, 0.03, steel, roller, cutter)
    ball_bearing("brg_int_lo", X_INT, B_BOT, 0.040, 0.082, 0.034, steel, roller, cutter)
    ball_bearing("brg_int_hi", X_INT, B_TOP, 0.040, 0.082, 0.034, steel, roller, cutter)
    tapered_bearing("brg_up", ZU, SR, 0.125, 0.07, steel, roller, cutter, flip=False)
    tapered_bearing("brg_lo", ZL, SR, 0.14, 0.08, steel, roller, cutter, flip=True)
    seal = T.revolve("seal", [(SR, -0.062), (0.10, -0.062), (0.10, -0.024), (0.088, -0.024), (0.08, -0.047), (SR, -0.032)], rubber, close=True)
    T.cut(seal, cutter)

    # ---------- impeller hub ----------
    T.cyl("hub", 0.095, ZF - 0.07, ZF + 0.07, polish, bevel=0.006)
    for k in range(3):
        a = math.radians(-60 + k * 120)
        b = T.box(f"blade{k}", (0.20, 0.10, 0.012), (0.18 * math.cos(a), 0.18 * math.sin(a), ZF), polish, bevel=0.003)
        b.rotation_euler = (math.radians(28), 0, a)

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
        l.rotation_euler = (Vector((-0.2, 0, 0.3)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    area((-3.8, -4.5, 3.8), 560, 2.6)
    area((4.0, -3.2, 1.2), 240, 3.0)
    area((0.0, 3.5, 3.2), 520, 2.0)

    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 85
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    target = Vector((-0.20, 0, 0.12))
    az, elev, dist = math.radians(-106), math.radians(19), 4.9
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
    r.resolution_x, r.resolution_y = (720, 820) if PREVIEW else (1800, 2050)
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
        "force_at": P((SR, -SR, ZF)), "force_to": P((0.34, -SR, ZF)),
        "deflection": defl,
        "z1": P((X_IN + R1 * 0.7, -R1 * 0.7, (S1_Z0 + S1_Z1) / 2)),
        "z2": P((X_INT + R2 * 0.55, -R2 * 0.8, S1_Z1)),
        "z3": P((X_INT + R3 * 0.8, -R3 * 0.6, (S2_Z0 + S2_Z1) / 2)),
        "z4": P((X_OUT + R4 * 0.45, -R4 * 0.85, S2_Z1)),
        "lantern": P((X_IN + 0.15, 0.0, LANTERN_Z1 - 0.015)),
        "brg_int": P((X_INT + 0.07, 0.0, B_TOP)),
        "chamber": P((X_OUT + 0.2, 0.15, CH_Z1)),
        "brg_up": P((0.11, 0.0, ZU + 0.01)), "brg_lo": P((0.125, 0.0, ZL)),
        "seal": P((0.09, 0.0, -0.045)), "flange": P((0.31, -0.12, -0.085)),
        "shaft": P((SR, -SR, -0.45)), "hub": P((0.095, -0.05, ZF + 0.05)),
    }
    json.dump(pts, open(os.path.join(ASSETS, "bearing-points-preview.json" if PREVIEW else "bearing-points.json"), "w"), indent=1)
    print("ok")


if __name__ == "__main__":
    main()
