#!/usr/bin/env python3
"""Render a cut-away agitator tank in Blender (Cycles) for the brochure.

Usage:
    python3 tools/render_tank.py [--preview] [--samples N]

Needs the `bpy` module (pip install bpy). Output:
    assets/tank-scene.png        transparent RGBA render (no drive)
    assets/tank-points.json      2D pixel positions of label anchors and of the
                                 mounting flange, used by tools/compose_tank.py
Units are metres. The camera looks along +Y; the front wedge of the tank and the
liquid is cut away so the shaft and impellers are visible.
"""
import json
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
PREVIEW = "--preview" in sys.argv
SAMPLES = int(sys.argv[sys.argv.index("--samples") + 1]) if "--samples" in sys.argv else (24 if PREVIEW else 256)

# ---------------- dimensions ----------------
R = 1.05            # tank inner radius
HS = 2.40           # straight shell height (z = 0 .. HS)
DISH = 0.30         # depth of the dished bottom
WALL = 0.035        # shell thickness (slightly exaggerated so the cut reads)
LEVEL = 1.98        # liquid level
GROUND = -0.85
CUT_C, CUT_HALF = -90.0, 52.0    # cut-away wedge: centre azimuth (towards camera) and half angle
CUT_BOTTOM = 0.22   # the cut stops here; the dished bottom stays closed
SHAFT_R = 0.0575    # Ø115 output shaft
FLANGE_R = 0.32     # mounting flange = gearbox output flange (Ø640)
BEAM_Z = HS + 0.02  # underside of the bridge beams
BEAM_H = 0.22
PLATE_T = 0.03
PED_H = 0.20
FL_T = 0.04
FLANGE_TOP = BEAM_Z + BEAM_H + PLATE_T + PED_H + FL_T
HF_Z, HF_R = 1.40, 0.46      # hydrofoil impeller height / tip radius
RT_Z, RT_R = 0.52, 0.37      # radial disc turbine height / tip radius
SHAFT_BOTTOM = 0.30


# ---------------- helpers ----------------
def clean():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, metallic=0.0, rough=0.5, aniso=0.0, transmission=0.0, ior=1.45, alpha=1.0, coat=0.0, emission=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if aniso:
        p.inputs["Anisotropic"].default_value = aniso
    if transmission:
        p.inputs["Transmission Weight"].default_value = transmission
        p.inputs["IOR"].default_value = ior
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
    if emission:
        p.inputs["Emission Color"].default_value = (*emission[0], 1)
        p.inputs["Emission Strength"].default_value = emission[1]
    return m


def obj_from_mesh(name, bm, material=None, smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if material:
        o.data.materials.append(material)
    if smooth:
        for poly in o.data.polygons:
            poly.use_smooth = True
    return o


def revolve(name, profile, material, steps=192, close=False, solid=0.0):
    """profile: list of (r, z) in the XZ plane; revolved around Z."""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in profile]
    for a, b in zip(vs, vs[1:]):
        bm.edges.new((a, b))
    if close:
        bm.edges.new((vs[-1], vs[0]))
    o = obj_from_mesh(name, bm, material)
    s = o.modifiers.new("screw", "SCREW")
    s.steps = steps
    s.render_steps = steps
    s.use_merge_vertices = True
    s.use_smooth_shade = True
    s.use_normal_calculate = True
    if solid:
        so = o.modifiers.new("solid", "SOLIDIFY")
        so.thickness = solid
        so.offset = 1
        so.use_even_offset = True
    return o


def box(name, size, loc, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
    return o


def cyl(name, r, z0, z1, material, verts=96, loc=(0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0, location=(loc[0], loc[1], (z0 + z1) / 2))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
    return o


def wedge_cutter(material):
    a0 = math.radians(CUT_C - CUT_HALF)
    a1 = math.radians(CUT_C + CUT_HALF)
    L = 6
    pts = [(0, 0)] + [(L * math.cos(a0 + (a1 - a0) * i / 8), L * math.sin(a0 + (a1 - a0) * i / 8)) for i in range(9)]
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, CUT_BOTTOM)) for x, y in pts]
    top = [bm.verts.new((x, y, 6)) for x, y in pts]
    bm.faces.new(bot[::-1])
    bm.faces.new(top)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    o = obj_from_mesh("cutter", bm, material, smooth=False)
    o.hide_render = True
    o.display_type = "WIRE"
    return o


def cut(o, cutter, transfer=True):
    m = o.modifiers.new("cut", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    try:
        m.solver = "EXACT"
    except TypeError:
        pass
    if transfer:
        try:
            m.material_mode = "TRANSFER"
        except (TypeError, AttributeError):
            pass


def in_wedge(az_deg):
    d = (az_deg - CUT_C + 180) % 360 - 180
    return abs(d) < CUT_HALF + 4


# ---------------- scene ----------------
def build():
    clean()
    sc = bpy.context.scene

    steel = mat("brushed steel", (0.80, 0.81, 0.82), metallic=1.0, rough=0.28, aniso=0.6)
    steel_in = mat("steel inside", (0.70, 0.71, 0.72), metallic=1.0, rough=0.35, aniso=0.4)
    polish = mat("polished steel", (0.86, 0.87, 0.88), metallic=1.0, rough=0.12)
    section = mat("section", (0.48, 0.50, 0.53), metallic=0.3, rough=0.55)
    paint = mat("bridge paint", (0.06, 0.065, 0.075), metallic=0.0, rough=0.55)
    paint_lt = mat("pedestal paint", (0.13, 0.135, 0.15), metallic=0.0, rough=0.5)
    arrow = mat("flow arrow", (0.72, 0.015, 0.05), rough=0.32, coat=0.5)
    liquid = bpy.data.materials.new("liquid")
    liquid.use_nodes = True
    nt = liquid.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.80, 0.92, 0.95, 1)
    p.inputs["Roughness"].default_value = 0.04
    p.inputs["Transmission Weight"].default_value = 1.0
    p.inputs["IOR"].default_value = 1.06
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (0.55, 0.80, 0.86, 1)
    vol.inputs["Density"].default_value = 0.14
    nt.links.new(vol.outputs[0], nt.nodes["Material Output"].inputs["Volume"])

    cutter = wedge_cutter(section)

    # shell + dished bottom (one revolved profile)
    prof = [(R, HS)]
    prof += [(R, z / 10 * HS) for z in range(9, -1, -1)]
    for i in range(1, 25):
        t = i / 24 * math.pi / 2
        prof.append((R * math.cos(t), -DISH * math.sin(t)))
    shell = revolve("shell", prof, steel_in, solid=WALL)
    shell.data.materials.append(steel)       # outer faces get index 1 via solidify
    shell.modifiers["solid"].material_offset = 1
    cut(shell, cutter)

    # rim angle ring
    rim = revolve("rim", [(R + WALL, HS - 0.06), (R + WALL + 0.07, HS - 0.06), (R + WALL + 0.07, HS), (R - 0.0, HS + 0.012), (R + WALL, HS - 0.06)], steel, close=True)
    cut(rim, cutter)
    # circumferential weld seam / stiffener band
    band = revolve("band", [(R + WALL, 1.18), (R + WALL + 0.014, 1.18), (R + WALL + 0.014, 1.22), (R + WALL, 1.22)], steel, close=True)
    cut(band, cutter)

    # liquid volume with a shallow vortex
    lp = [(0, LEVEL - 0.05)]
    for i in range(1, 13):
        r = (R - 0.002) * i / 12
        lp.append((r, LEVEL - 0.05 * (1 - (i / 12) ** 0.7)))
    lp += [(R - 0.002, z / 10 * LEVEL) for z in range(9, -1, -1)]
    for i in range(1, 25):
        t = i / 24 * math.pi / 2
        lp.append(((R - 0.002) * math.cos(t), -(DISH - 0.002) * math.sin(t)))
    liq = revolve("liquid", lp, liquid)
    cut(liq, cutter, transfer=False)

    # legs
    for az in (45, 135, 225, 315):
        a = math.radians(az)
        x, y = (R + WALL + 0.10) * math.cos(a), (R + WALL + 0.10) * math.sin(a)
        cyl(f"leg{az}", 0.075, GROUND + 0.03, 0.42, steel, loc=(x, y), bevel=0.004)
        box(f"foot{az}", (0.26, 0.26, 0.03), (x, y, GROUND + 0.015), steel, bevel=0.006)
        rp = R + WALL + 0.012
        box(f"pad{az}", (0.024, 0.26, 0.46), (rp * math.cos(a), rp * math.sin(a), 0.30), steel, bevel=0.004).rotation_euler[2] = a

    # baffles (the two in the cut-away wedge are left out)
    for az in (45, 135, 225, 315):
        if in_wedge(az):
            continue
        a = math.radians(az)
        w, gap = 0.16, 0.03
        rc = R - gap - w / 2
        b = box(f"baffle{az}", (w, 0.016, LEVEL + 0.12 - 0.22), (rc * math.cos(a), rc * math.sin(a), 0.22 + (LEVEL + 0.12 - 0.22) / 2), steel, bevel=0.003)
        b.rotation_euler[2] = a
        for z in (0.40, 1.15, 1.90):
            br = box(f"bkt{az}{z}", (gap + 0.05, 0.03, 0.06), ((R - gap / 2 - 0.02) * math.cos(a), (R - gap / 2 - 0.02) * math.sin(a), z), steel)
            br.rotation_euler[2] = a

    # bridge: two I-beams along X, plate, pedestal, flange
    for y in (-0.24, 0.24):
        for part, (sx, sy, sz, dz) in {"tf": (2.75, 0.16, 0.022, BEAM_H - 0.011), "bf": (2.75, 0.16, 0.022, 0.011), "web": (2.75, 0.016, BEAM_H, BEAM_H / 2)}.items():
            box(f"beam{y}{part}", (sx, sy, sz), (0, y, BEAM_Z + dz), paint, bevel=0.003)
    box("plate", (0.95, 0.75, PLATE_T), (0, 0, BEAM_Z + BEAM_H + PLATE_T / 2), paint_lt, bevel=0.004)
    z0 = BEAM_Z + BEAM_H + PLATE_T
    cyl("pedestal", 0.25, z0, z0 + PED_H, paint_lt, bevel=0.004)
    for i in range(6):
        a = i * math.pi / 3
        box(f"rib{i}", (0.05, 0.016, PED_H * 0.85), (0.29 * math.cos(a), 0.29 * math.sin(a), z0 + PED_H * 0.43), paint_lt).rotation_euler[2] = a
    cyl("flange", FLANGE_R, z0 + PED_H, FLANGE_TOP, paint_lt, verts=128, bevel=0.004)
    for i in range(12):
        a = i * math.pi / 6 + math.pi / 12
        cyl(f"bolt{i}", 0.018, FLANGE_TOP, FLANGE_TOP + 0.022, polish, verts=6, loc=(0.285 * math.cos(a), 0.285 * math.sin(a)))

    # shaft + coupling
    cyl("shaft", SHAFT_R, SHAFT_BOTTOM, FLANGE_TOP - 0.01, polish, verts=64)
    cz = BEAM_Z - 0.20
    cyl("coupl_a", 0.13, cz, cz + 0.04, polish, bevel=0.004)
    cyl("coupl_b", 0.13, cz - 0.045, cz - 0.005, polish, bevel=0.004)
    for i in range(8):
        a = i * math.pi / 4
        cyl(f"cbolt{i}", 0.013, cz - 0.06, cz + 0.055, steel, verts=12, loc=(0.10 * math.cos(a), 0.10 * math.sin(a)))
    cyl("shaft_end", SHAFT_R * 1.15, SHAFT_BOTTOM - 0.03, SHAFT_BOTTOM + 0.02, polish, verts=48)

    # hydrofoil impeller: 3 twisted, cambered, tapered blades
    cyl("hf_hub", 0.10, HF_Z - 0.09, HF_Z + 0.09, polish, bevel=0.006)
    for k in range(3):
        bm = bmesh.new()
        nr, nc = 18, 10
        grid = []
        for i in range(nr + 1):
            u = i / nr
            r = 0.09 + (HF_R - 0.09) * u
            chord = 0.30 - 0.13 * u
            pitch = math.radians(34 - 16 * u)
            row = []
            for j in range(nc + 1):
                s = (j / nc - 0.5) * chord
                camber = 0.04 * chord / 0.30 * (1 - (2 * s / chord) ** 2)
                y = s * math.cos(pitch) - camber * math.sin(pitch)
                z = -s * math.sin(pitch) - camber * math.cos(pitch)
                row.append(bm.verts.new((r, y, z)))
            grid.append(row)
        for i in range(nr):
            for j in range(nc):
                bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
        o = obj_from_mesh(f"hf_blade{k}", bm, polish)
        sol = o.modifiers.new("t", "SOLIDIFY")
        sol.thickness = 0.014
        sol.offset = 0
        sub = o.modifiers.new("s", "SUBSURF")
        sub.levels = 1
        sub.render_levels = 2
        o.location = (0, 0, HF_Z)
        o.rotation_euler[2] = math.radians(20 + k * 120)

    # radial disc turbine
    cyl("rt_hub", 0.09, RT_Z - 0.07, RT_Z + 0.07, polish, bevel=0.005)
    cyl("rt_disc", RT_R * 0.75, RT_Z - 0.008, RT_Z + 0.008, polish, verts=96)
    for k in range(6):
        a = math.radians(10 + k * 60)
        rc = RT_R - 0.075
        b = box(f"rt_blade{k}", (0.16, 0.016, 0.15), (rc * math.cos(a), rc * math.sin(a), RT_Z), polish, bevel=0.002)
        b.rotation_euler[2] = a

    # flow arrows (two loops in the cut plane, slightly in front of the shaft)
    FX, FZ = R / 1.30, LEVEL / 2.30

    def loop(sign):
        pts = [(0.20, 1.36), (0.28, 0.98), (0.40, 0.78), (0.82, 0.60), (1.06, 0.90), (1.10, 1.45), (1.04, 1.98), (0.72, 2.10), (0.42, 1.92)]
        cu = bpy.data.curves.new(f"flow{sign}", "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, (x, z) in zip(sp.bezier_points, pts):
            bp.co = (sign * x * FX, -0.36, z * FZ)
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        cu.bevel_depth = 0.022
        cu.bevel_resolution = 4
        cu.use_fill_caps = True
        o = bpy.data.objects.new(f"flow{sign}", cu)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(arrow)
        # arrow head at the end, pointing along the last segment
        (x1, z1), (x0, z0) = pts[-1], pts[-2]
        d = Vector((sign * (x1 - x0) * FX, 0, (z1 - z0) * FZ)).normalized()
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.06, radius2=0, depth=0.15, location=(sign * x1 * FX + d.x * 0.07, -0.36, z1 * FZ + d.z * 0.07))
        c = bpy.context.object
        c.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        c.data.materials.append(arrow)
        bpy.ops.object.shade_smooth()
    loop(1)
    loop(-1)

    # ground shadow catcher
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, GROUND))
    g = bpy.context.object
    g.is_shadow_catcher = True

    # world + lights
    w = bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(bpy.utils.system_resource("DATAFILES"), "studiolights", "world", "studio.exr"))
    w.node_tree.links.new(env.outputs[0], w.node_tree.nodes["Background"].inputs[0])
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.7

    def area(name, loc, energy, size, rot):
        bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot)
        l = bpy.context.object
        l.name = name
        l.data.energy = energy
        l.data.size = size
        return l
    area("key", (-5.5, -6.0, 7.5), 2600, 4.0, (math.radians(50), 0, math.radians(-40)))
    area("fill", (6.5, -5.0, 3.5), 900, 5.0, (math.radians(70), 0, math.radians(50)))
    area("rim", (1.5, 6.5, 6.0), 1300, 3.0, (math.radians(-50), 0, math.radians(170)))
    area("inside", (0.0, -1.2, 4.6), 260, 1.6, (0, 0, 0))

    # camera: slight elevation, long lens (matches the product renders)
    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 85
    cam = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam)
    target = Vector((0, 0, 1.25))
    elev, dist = math.radians(17), 17.0
    cam.location = target + Vector((0, -math.cos(elev) * dist, math.sin(elev) * dist))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

    r = sc.render
    r.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.transmission_bounces = 12
    sc.cycles.volume_bounces = 2
    r.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    r.resolution_x, r.resolution_y = (600, 820) if PREVIEW else (1500, 2050)
    r.resolution_percentage = 100
    r.filepath = os.path.join(ASSETS, "tank-preview.png" if PREVIEW else "tank-scene.png")
    return sc, cam


def project(sc, cam, p):
    v = world_to_camera_view(sc, cam, Vector(p))
    W, H = sc.render.resolution_x, sc.render.resolution_y
    return [round(v.x * W, 1), round((1 - v.y) * H, 1)]


def main():
    sc, cam = build()
    bpy.ops.render.render(write_still=True)
    pts = {
        "size": [sc.render.resolution_x, sc.render.resolution_y],
        "flange_front_top": project(sc, cam, (0, -FLANGE_R, FLANGE_TOP)),
        "flange_left": project(sc, cam, (-FLANGE_R, 0, FLANGE_TOP)),
        "flange_right": project(sc, cam, (FLANGE_R, 0, FLANGE_TOP)),
        "bridge_end": project(sc, cam, (1.37, -0.24, BEAM_Z + BEAM_H / 2)),
        "shaft": project(sc, cam, (SHAFT_R, -SHAFT_R, 1.95)),
        "coupling": project(sc, cam, (0.13, -0.05, BEAM_Z - 0.2)),
        "wall": project(sc, cam, ((R + WALL) * math.cos(math.radians(-25)), (R + WALL) * math.sin(math.radians(-25)), 1.9)),
        "liquid": project(sc, cam, (0.95, 0.3, LEVEL - 0.02)),
        "baffle": project(sc, cam, ((R - 0.13) * math.cos(math.radians(45)), (R - 0.13) * math.sin(math.radians(45)), 1.2)),
        "hydrofoil": project(sc, cam, (HF_R * 0.85 * math.cos(math.radians(-40)), HF_R * 0.85 * math.sin(math.radians(-40)), HF_Z)),
        "turbine": project(sc, cam, (RT_R * math.cos(math.radians(-50)), RT_R * math.sin(math.radians(-50)), RT_Z)),
        "flow": project(sc, cam, (1.08 * R / 1.30, -0.36, 1.45 * LEVEL / 2.30)),
        "leg": project(sc, cam, ((R + 0.14) * math.cos(math.radians(315)), (R + 0.14) * math.sin(math.radians(315)), -0.3)),
    }
    with open(os.path.join(ASSETS, "tank-points.json" if not PREVIEW else "tank-points-preview.json"), "w") as f:
        json.dump(pts, f, indent=1)
    print(json.dumps(pts))


if __name__ == "__main__":
    main()
