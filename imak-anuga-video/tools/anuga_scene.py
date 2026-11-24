#!/usr/bin/env python3
"""3D shots of real i.Mak drives (official STEP models, RAL 3020) for the Anuga FoodTec 2027 teaser.

Usage: python3 tools/anuga_scene.py --shot hero|conveyor|lineup [--frames A-B] [--step N] [--samples N] [--res WxH]
Frames -> render/<shot>/####.png at 30 fps.
  hero      IRKM 93 helical-bevel geared motor, slow orbit, dark studio with red and cool rim light
  conveyor  stainless food belt conveyor carrying cartons; IRSDM 83 helical-worm geared motor shaft-mounted
            (hollow shaft) on the head-drum shaft, with a torque arm to the frame - the usual food-conveyor layout
  lineup    the food-industry range side by side (IRAM, IRSDM, IRKM, YPM), camera tracks along
Part meshes come from the STEP files (see imak-bakery-video/tools: step_parts.py output in PARTS).
"""
import math
import os
import sys

import bpy  # noqa
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PARTS = os.environ.get("PARTS", "/tmp/claude-0/cad/parts")
HDRI = os.environ.get("HDRI", "/tmp/claude-0/irc/hdri")
A = sys.argv[1:]
arg = lambda n, d: A[A.index(n) + 1] if n in A else d
SHOT = arg("--shot", "hero")
SAMPLES = int(arg("--samples", 24))
RES = [int(v) for v in arg("--res", "1920x1080").split("x")]
FPS = 30
N = {"hero": 105, "conveyor": 105, "lineup": 105}[SHOT]
TAU = math.pi * 2
RAL3020 = (0.6038, 0.0018, 0.0015)

M = {}


def mat(name, col, rough=0.5, metal=0.0, coat=0.0, aniso=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Anisotropic"].default_value = aniso
    return m


def mats():
    M["red"] = mat("RAL 3020", RAL3020, 0.34, coat=0.6)
    M["steel"] = mat("machined steel", (0.78, 0.79, 0.80), 0.22, 1.0)
    M["inox"] = mat("brushed stainless", (0.80, 0.81, 0.83), 0.28, 1.0, aniso=0.6)
    M["belt"] = mat("white POM belt", (0.86, 0.87, 0.86), 0.42)
    M["kraft"] = mat("carton", (0.50, 0.33, 0.17), 0.82)
    M["tape"] = mat("tape", (0.62, 0.45, 0.27), 0.35, coat=0.4)
    M["floor"] = mat("floor", (0.035, 0.04, 0.05), 0.32, coat=0.3)
    M["dark"] = mat("dark", (0.02, 0.022, 0.025), 0.6)
    M["rubber"] = mat("rubber", (0.03, 0.03, 0.03), 0.7)
    # belt slats: stripe texture, animated along X
    bm = M["belt"]
    nt = bm.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "X"
    wv.inputs["Scale"].default_value = 1.0; wv.inputs["Distortion"].default_value = 0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.06; ramp.color_ramp.elements[0].color = (0.45, 0.46, 0.46, 1)
    ramp.color_ramp.elements[1].position = 0.14; ramp.color_ramp.elements[1].color = (0.86, 0.87, 0.86, 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    M["belt_map"] = mp


def done(o, m, bevel=0.0, smooth=False):
    o.data.materials.append(M[m])
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    if smooth:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    return o


def box(sx, sy, sz, loc, m, bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return done(o, m, bevel)


def cyl(r, h, loc, m, axis="Z", verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.object
    if axis == "X":
        o.rotation_euler = (0, math.radians(90), 0)
    elif axis == "Y":
        o.rotation_euler = (math.radians(90), 0, 0)
    return done(o, m, 0.002, smooth=True)


def rod(a, b, r, m):
    a, b = Vector(a), Vector(b)
    o = cyl(r, (b - a).length, (a + b) / 2, m, verts=20)
    o.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return o


def parts(name, scale=1.0):
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
    return root, objs


def mount(name, out_pt, out_ax, side_ax, w_pt, w_ax, w_side, scale=1.0):
    """Put the unit's output-shaft point/axis (STEP mm) onto a world shaft; side_ax -> w_side fixes the roll."""
    root, _ = parts(name, scale)

    def frame(a, b):
        a = Vector(a).normalized(); b = (Vector(b) - Vector(b).project(a)).normalized()
        return Matrix((a, b, a.cross(b))).transposed()
    R = frame(w_ax, w_side) @ frame(out_ax, side_ax).inverted()
    root.matrix_world = Matrix.Translation(Vector(w_pt) - R @ (Vector(out_pt) * 0.001 * scale)) @ R.to_4x4()
    return root


def stand(name, loc, yaw=0.0, scale=1.0):
    """Unit standing on its feet (STEP Y up) at loc, turned by yaw about Z."""
    root, objs = parts(name, scale)
    root.rotation_euler = (math.radians(90), 0, yaw)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    c = Vector([(min(p[i] for p in pts) + max(p[i] for p in pts)) / 2 for i in range(3)])
    root.location = Vector(loc) - Vector((c.x, c.y, min(p.z for p in pts)))
    return root


# ------------------------------------------------------------- lights/world
def world(hdri, strength, rot=0.0, cam_col=(0.012, 0.016, 0.022)):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(os.path.join(HDRI, hdri))
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, rot)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    bg = nt.nodes["Background"]; nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    lp = nt.nodes.new("ShaderNodeLightPath")
    cb = nt.nodes.new("ShaderNodeBackground"); cb.inputs["Color"].default_value = (*cam_col, 1)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(bg.outputs["Background"], mix.inputs[1]); nt.links.new(cb.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], nt.nodes["World Output"].inputs["Surface"])


def area(loc, target, energy, size, color=(1, 1, 1), shape="RECTANGLE", sy=None):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.data.energy = energy; l.data.size = size; l.data.color = color
    if sy:
        l.data.shape = "RECTANGLE"; l.data.size_y = sy
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return l


def camera(lens=50, fstop=None):
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    sc.camera = cam; cam.data.lens = lens; cam.data.sensor_width = 36
    tgt = bpy.data.objects.new("target", None); sc.collection.objects.link(tgt)
    c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    if fstop:
        cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = fstop; cam.data.dof.focus_object = tgt
    return cam, tgt


def key(obj, f, loc):
    obj.location = loc
    obj.keyframe_insert("location", frame=f)


def linear_all():
    for o in bpy.data.objects:
        ad = o.animation_data
        if ad and ad.action:
            for fc in getattr(ad.action, "fcurves", []):
                for k in fc.keyframe_points:
                    k.interpolation = "LINEAR"


def ease(t):
    return t * t * (3 - 2 * t)


def floor(m="floor"):
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    done(bpy.context.object, m)


def render_setup():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 6; sc.cycles.glossy_bounces = 3
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.fps = FPS
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = -0.4
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
    sc.frame_start, sc.frame_end = 0, N - 1


# ------------------------------------------------------------------ shots
def shot_hero():
    world("studio_small_09.exr", 0.35, rot=1.2)
    floor()
    u = stand("IRKM_93-160_L", (0, 0, 0), yaw=math.radians(25))
    area((-1.6, -1.2, 1.6), (0, 0, 0.35), 150, 1.2, (1.0, 0.86, 0.8))          # warm key
    area((1.4, 1.6, 1.2), (0, 0, 0.4), 260, 0.5, (0.45, 0.7, 1.0), sy=2.0)       # cool rim
    area((0.2, 2.2, 0.6), (0, 0, 0.3), 300, 0.4, (1.0, 0.15, 0.1), sy=1.5)       # red kicker behind
    area((0, 0, 2.6), (0, 0, 0), 50, 2.0)
    cam, tgt = camera(65, fstop=4.0)
    for f in range(N):
        t = ease(f / (N - 1))
        a = math.radians(-58 + 46 * t)
        r = 2.9 - 0.35 * t
        key(cam, f, (r * math.cos(a), r * math.sin(a), 0.7 + 0.15 * t))
        key(tgt, f, (0, 0, 0.33))


def shot_conveyor():
    world("machine_shop_02.exr", 0.55, rot=0.4)
    floor()
    W, Z, X0, X1 = 0.6, 0.86, -3.5, 1.2
    L = X1 - X0
    belt = box(L, W, 0.03, ((X0 + X1) / 2, 0, Z), "belt", 0.002)
    for y in (-W / 2 - 0.025, W / 2 + 0.025):                                    # stainless side channels
        box(L, 0.04, 0.16, ((X0 + X1) / 2, y, Z - 0.04), "inox", 0.004)
        box(L, 0.012, 0.05, ((X0 + X1) / 2, y * 1.08, Z + 0.06), "inox", 0.002)  # guide rails
    cyl(0.07, W + 0.02, (X1, 0, Z - 0.05), "inox", axis="Y")                     # head drum
    cyl(0.07, W + 0.02, (X0, 0, Z - 0.05), "inox", axis="Y")
    rod((X1, -W / 2, Z - 0.05), (X1, -W / 2 - 0.25, Z - 0.05), 0.022, "steel")    # drum shaft into the gearbox
    for x in (X0 + 0.15, -1.2, X1 - 0.15):
        for y in (-W / 2 - 0.02, W / 2 + 0.02):
            rod((x, y, 0), (x, y, Z - 0.12), 0.025, "inox")
            cyl(0.04, 0.03, (x, y, 0.015), "rubber")
        box(0.04, W + 0.04, 0.04, (x, 0, 0.25), "inox", 0.003)
    # IRSDM 83: hollow shaft on the drum shaft (out on -Y), motor hanging down; torque arm to the leg
    sy = -W / 2 - 0.045 - 0.107
    mount("IRSDM_83-112_M", (0, 40, 202), (1, 0, 0), (0, 0, 1), (X1, sy, Z - 0.05), (0, -1, 0), (0, 0, 1))
    rod((X1 + 0.04, sy, Z - 0.30), (X1 - 0.15, -W / 2 - 0.02, Z - 0.42), 0.012, "steel")
    # cartons riding the belt (+X), 0.32 m/s
    v = 0.32 / FPS
    gap = 0.55
    for i in range(int(L / gap) + 2):
        for dy in (-0.13, 0.13):
            x0 = X0 + 0.2 + i * gap + (0.12 if dy > 0 else 0)
            c = box(0.24, 0.2, 0.16, (0, 0, 0), "kraft", 0.006)
            tp = box(0.245, 0.05, 0.004, (0, 0, 0.081), "tape", 0.0)
            tp.parent = c
            def pos(f, x0=x0, dy=dy):
                x = x0 + v * f
                return (x, dy, Z + 0.015 + 0.08) if x < X1 - 0.12 else (x, dy, -2)
            key(c, 0, pos(0)); key(c, N - 1, pos(N - 1))
            if pos(0)[2] > 0 and pos(N - 1)[2] < 0:                              # leaves the belt mid-shot
                fe = int((X1 - 0.12 - x0) / v)
                key(c, fe, pos(fe)); c.location = (0, 0, -2); c.keyframe_insert("location", frame=fe + 1)
    M["belt_map"].inputs["Location"].default_value = (0, 0, 0)
    M["belt_map"].inputs["Location"].keyframe_insert("default_value", frame=0)
    M["belt_map"].inputs["Location"].default_value = (-v * (N - 1) / 0.04, 0, 0)
    M["belt_map"].inputs["Scale"].default_value = (1 / 0.04, 1, 1)
    M["belt_map"].inputs["Location"].keyframe_insert("default_value", frame=N - 1)
    area((1.8, -2.4, 2.4), (X1, -0.3, Z), 300, 1.6, (1.0, 0.93, 0.86))
    area((-1.5, 2.0, 2.2), (0, 0, Z), 200, 2.5, (0.6, 0.78, 1.0))
    area((X1 + 1.5, -0.4, 1.0), (X1, -0.4, 0.7), 160, 0.6, (1.0, 0.3, 0.25))
    cam, tgt = camera(35, fstop=4.0)
    for f in range(N):
        t = ease(f / (N - 1))
        key(cam, f, (X1 + 1.25 - 0.55 * t, -2.0 + 0.2 * t, 1.45 - 0.1 * t))
        key(tgt, f, (X1 - 0.55 - 0.1 * t, -0.15, Z - 0.1))


def shot_lineup():
    world("studio_small_09.exr", 0.4, rot=2.0)
    floor()
    units = [("IRAM_93-160_L", 0.75), ("IRSDM_83-112_M", 1.0), ("IRKM_93-160_L", 0.85), ("YPM_93-160_L", 0.85)]
    for i, (n, s) in enumerate(units):
        stand(n, (i * 0.72, 0, 0), yaw=math.radians(30), scale=s)
    area((0.5, -2.5, 2.2), (1.35, 0, 0.3), 380, 2.5, (1.0, 0.9, 0.85))
    area((2.8, 2.0, 1.2), (1.35, 0, 0.3), 500, 0.6, (0.45, 0.7, 1.0), sy=3.0)
    area((-0.8, 1.8, 0.7), (1.35, 0, 0.3), 400, 0.5, (1.0, 0.15, 0.1), sy=3.0)
    cam, tgt = camera(45, fstop=5.6)
    for f in range(N):
        t = ease(f / (N - 1))
        key(cam, f, (0.15 + 1.6 * t, -2.35, 0.78))
        key(tgt, f, (0.55 + 1.0 * t, 0, 0.26))


def main():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    mats()
    render_setup()
    {"hero": shot_hero, "conveyor": shot_conveyor, "lineup": shot_lineup}[SHOT]()
    linear_all()
    sc = bpy.context.scene
    out = os.path.join(ROOT, "render", SHOT)
    os.makedirs(out, exist_ok=True)
    fr = arg("--frames", f"0-{N - 1}").split("-")
    step = int(arg("--step", 1))
    still = arg("--still", None)
    frames = [int(still)] if still is not None else range(int(fr[0]), int(fr[1]) + 1, step)
    for f in frames:
        p = os.path.join(out, f"{f:04d}.png")
        if os.path.exists(p) and still is None:
            continue
        sc.frame_set(f)
        sc.render.filepath = p if still is None else f"/tmp/claude-0/anuga/still_{SHOT}_{f}.png"
        bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True)


main()
