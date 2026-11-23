"""Photoreal product post (4:5): one i.Mak unit standing on a real floor inside a real 16K HDRI
photograph (Poly Haven, CC0). The HDRI lights the unit, gives its reflections and is the background;
the floor under the camera is re-projected from the HDRI capture point onto a ground plane so it holds
perspective for a low camera, and a shadow catcher puts the unit's real contact shadow on that floor.

  UNIT=irc  : IRC 93 hoist drive with motor + splined drum-hub flange beside it, machine shop with cranes
  UNIT=irnx : IRNX 07 shaft-mounted unit, mine-dump flats at sunset
python3 tools/scene_photo_product.py [--preview] [--samples N] [--scale F]
Env overrides: YAW (deg, HDRI rotation), CAMX/CAMY/CAMZ, LENS, FSTOP, HCAP (HDRI capture height, m)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import bmesh
from mathutils import Vector
import hero_lib as H

HDRI_DIR = "/home/user/zak/downloads/bg/hdri"
UNIT = os.environ.get("UNIT", "irc")
CFG = {
    "irc": dict(hdri="machine_shop_02_16k.exr", yaw=105.0, hcap=1.65, strength=1.0,
                cam=(2.05, -1.75, 0.66), tgt=(0.24, -0.14, 0.30), lens=50, fstop=3.2, exposure=0.0),
    "irnx": dict(hdri="minedump_flats_16k.exr", yaw=300.0, hcap=1.7, strength=1.0,
                 cam=(1.95, -1.65, 0.70), tgt=(0.05, -0.05, 0.44), lens=50, fstop=3.2, exposure=0.0),
}[UNIT]
env = os.environ.get
YAW = float(env("YAW", CFG["yaw"]))
HCAP = float(env("HCAP", CFG["hcap"]))
CAM = Vector((float(env("CAMX", CFG["cam"][0])), float(env("CAMY", CFG["cam"][1])), float(env("CAMZ", CFG["cam"][2]))))
TGT = Vector(CFG["tgt"])
LENS = float(env("LENS", CFG["lens"]))
FSTOP = float(env("FSTOP", CFG["fstop"]))

H.fresh()
mats = H.M()
# realistic finishes: RAL 3020 on cast iron (orange-peel, satin), machined steel, black rubber seals
mats["paint"] = H.mat("imak red", (0.56, 0.018, 0.014), 0.0, 0.38, coat=0.12, spec=0.45, bump=(1400, 0.035))
mats["steel"] = H.mat("machined steel", (0.78, 0.78, 0.77), 1.0, 0.24, aniso=0.55)
mats["bore"] = H.mat("bore steel", (0.55, 0.55, 0.54), 1.0, 0.32)
spline_m = H.mat("spline steel", (0.80, 0.80, 0.79), 1.0, 0.20, aniso=0.4)
hub_m = H.mat("hub steel", (0.62, 0.62, 0.61), 1.0, 0.22, aniso=0.0)


# ---------------------------------------------------------------- world: HDRI with ground projection for camera rays
def world_projected(path, yaw_deg, hcap, cam, strength=1.0, r0=5.0, r1=12.0):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("hdri")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links

    def vm(op, a=None, b=None, val=None):
        n = N.new("ShaderNodeVectorMath")
        n.operation = op
        if a is not None:
            L.new(a, n.inputs[0])
        if b is not None:
            if isinstance(b, (tuple, list, Vector)):
                n.inputs[1].default_value = tuple(b)
            else:
                L.new(b, n.inputs[1])
        if val is not None:
            n.inputs[3].default_value = val
        return n

    def m(op, a=None, b=None, av=None, bv=None, clamp=False):
        n = N.new("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        if a is not None:
            L.new(a, n.inputs[0])
        elif av is not None:
            n.inputs[0].default_value = av
        if b is not None:
            L.new(b, n.inputs[1])
        elif bv is not None:
            n.inputs[1].default_value = bv
        return n

    tc = N.new("ShaderNodeTexCoord")
    D = vm("NORMALIZE", tc.outputs["Generated"])
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(D.outputs[0], sep.inputs[0])
    dz = sep.outputs["Z"]
    # t = -cam.z / dz  (only meaningful for dz < 0)
    dzc = m("MINIMUM", dz, None, bv=-1e-4)
    t = m("DIVIDE", None, dzc.outputs[0], av=-cam.z)
    tD = vm("SCALE", D.outputs[0], val=0.0)
    L.new(t.outputs[0], tD.inputs["Scale"])
    v = vm("ADD", tD.outputs[0], (cam.x, cam.y, cam.z - hcap))          # P - Hcap
    dir2 = vm("NORMALIZE", v.outputs[0])
    # ground distance from the capture point -> blend weight (1 near, 0 far / above horizon)
    P = vm("ADD", tD.outputs[0], (cam.x, cam.y, 0.0))
    seP = N.new("ShaderNodeSeparateXYZ")
    L.new(P.outputs[0], seP.inputs[0])
    dist = m("SQRT", m("ADD", m("MULTIPLY", seP.outputs["X"], seP.outputs["X"]).outputs[0],
                        m("MULTIPLY", seP.outputs["Y"], seP.outputs["Y"]).outputs[0]).outputs[0])
    mr = N.new("ShaderNodeMapRange")
    L.new(dist.outputs[0], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = r0
    mr.inputs["From Max"].default_value = r1
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    mr.clamp = True
    below = m("LESS_THAN", dz, None, bv=-0.002)
    lp = N.new("ShaderNodeLightPath")
    wgt = m("MULTIPLY", m("MULTIPLY", mr.outputs[0], below.outputs[0]).outputs[0], lp.outputs["Is Camera Ray"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "VECTOR"
    L.new(wgt.outputs[0], mix.inputs["Factor"])
    L.new(D.outputs[0], mix.inputs[4])
    L.new(dir2.outputs[0], mix.inputs[5])
    rot = N.new("ShaderNodeVectorRotate")
    rot.rotation_type = "Z_AXIS"
    rot.inputs["Angle"].default_value = math.radians(yaw_deg)
    L.new(mix.outputs[1], rot.inputs["Vector"])
    tex = N.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(path)
    tex.interpolation = "Cubic"
    L.new(rot.outputs[0], tex.inputs["Vector"])
    bg = N["Background"]
    L.new(tex.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = strength
    return w


world_projected(os.path.join(HDRI_DIR, CFG["hdri"]), YAW, HCAP, CAM, CFG["strength"])

# shadow catcher floor (its own colour only matters for bounce light onto the unit)
floor_m = H.mat("floor bounce", (0.25, 0.23, 0.21) if UNIT == "irnx" else (0.22, 0.22, 0.21), 0.0, 0.8)
fl = H.plane("catcher", (40, 40), floor_m)
fl.is_shadow_catcher = True


# ---------------------------------------------------------------- helpers for the spline parts
def prism(name, outer, inner, length, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    bm = bmesh.new()
    vo0 = [bm.verts.new((0, x, y)) for x, y in outer]
    vo1 = [bm.verts.new((length, x, y)) for x, y in outer]
    vi0 = [bm.verts.new((0, x, y)) for x, y in inner] if inner else None
    vi1 = [bm.verts.new((length, x, y)) for x, y in inner] if inner else None
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vo0[i], vo0[j], vo1[j], vo1[i]))
        if inner:
            bm.faces.new((vi0[j], vi0[i], vi1[i], vi1[j]))
            bm.faces.new((vo0[j], vo0[i], vi0[i], vi0[j]))
            bm.faces.new((vo1[i], vo1[j], vi1[j], vi1[i]))
    if not inner:
        bm.faces.new(list(reversed(vo0)))
        bm.faces.new(vo1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return H.obj_from_bmesh(bm, name, m, loc=loc, rot=rot)


def star(n, r1, r2):
    out = []
    for i in range(n):
        a0 = 2 * math.pi * i / n
        w = math.pi / n * 0.45
        out += [(r2 * math.cos(a0 - w * 1.05), r2 * math.sin(a0 - w * 1.05)), (r1 * math.cos(a0 - w), r1 * math.sin(a0 - w)),
                (r1 * math.cos(a0 + w), r1 * math.sin(a0 + w)), (r2 * math.cos(a0 + w * 1.05), r2 * math.sin(a0 + w * 1.05))]
    return out


def circle(n, r):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def motor_from_iram(mats, spin, scale=1.0):
    """Motor part of the IRAM 93-160 L STEP (cut at its front face), returns (unit, front-face x offset)."""
    m = H.load_unit("IRAM_93-160_L", mats, spin=spin, scale=0.001 * scale)
    for o in m["objs"]:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, -157.0), plane_no=(0, 0, 1), clear_outer=True)
        bm.to_mesh(o.data)
        bm.free()
    return m, 0.315 * scale


# ---------------------------------------------------------------- the product
focus_pt = TGT
if UNIT == "irc":
    u = H.load_unit("IRC_93", mats, spin=-90)                 # shaft face looks to +X
    in_c = Vector((0.16, -0.03, 0.50))
    out_c = Vector((0.01, 0.01, 0.16))
    FX = 0.21
    BX0, BX1 = 0.135, 0.355
    H.cyl("bell", 0.105, BX1 - BX0, mats["paint"], loc=((BX0 + BX1) / 2, in_c.y, in_c.z), axis="X", seg=128, chamfer=0.008)
    H.cyl("bell_fl0", 0.135, 0.022, mats["paint"], loc=(BX0 + 0.011, in_c.y, in_c.z), axis="X", seg=128, chamfer=0.003)
    H.cyl("bell_fl1", 0.16, 0.022, mats["paint"], loc=(BX1 - 0.011, in_c.y, in_c.z), axis="X", seg=128, chamfer=0.003)
    H.bolts("bellb", [(BX1 + 0.004, in_c.y + 0.145 * math.cos(math.radians(a)), in_c.z + 0.145 * math.sin(math.radians(a))) for a in range(0, 360, 45)], mats["bolt"], r=0.009, h=0.012, axis="X")
    m, MF = motor_from_iram(mats, -90)
    m["parent"].location = (BX1 - MF, in_c.y, in_c.z - 0.21)
    # splined output shaft
    SX0, SL, NT = FX - 0.02, 0.17, 24
    prism("spline_shaft", star(NT, 0.040, 0.034), None, SL, spline_m, loc=(SX0, out_c.y, out_c.z))
    H.cyl("spline_end", 0.031, 0.008, spline_m, loc=(SX0 + SL + 0.004, out_c.y, out_c.z), axis="X", seg=64, chamfer=0.003)
    H.cyl("shaft_root", 0.047, 0.03, spline_m, loc=(FX + 0.015, out_c.y, out_c.z), axis="X", seg=64, chamfer=0.002)
    # splined drum-hub flange standing on its edge in front of the unit, face turned to the camera
    hub_loc = Vector((float(env("HUBX", 0.34)), float(env("HUBY", -0.50)), 0.125))
    hub_rot = (0, 0, math.radians(float(env("HUBR", -55))))
    hb = prism("hub_flange", circle(4 * NT, 0.125), star(NT, 0.0415, 0.0355), 0.03, hub_m, loc=hub_loc, rot=hub_rot)
    hb2 = prism("hub_boss", circle(4 * NT, 0.072), star(NT, 0.0415, 0.0355), 0.07, hub_m, loc=hub_loc, rot=hub_rot)
    hb2.location = hub_loc - Vector((math.cos(hub_rot[2]), math.sin(hub_rot[2]), 0)) * 0.07 + Vector((math.cos(hub_rot[2]), math.sin(hub_rot[2]), 0)) * 0.0
    # bolt holes on the flange: dark discs
    hole_m = H.mat("hole", (0.01, 0.01, 0.01), 0.0, 0.6)
    ca, sa = math.cos(hub_rot[2]), math.sin(hub_rot[2])
    for k in range(8):
        a = 2 * math.pi * k / 8
        ly, lz = 0.098 * math.cos(a), 0.098 * math.sin(a)
        p = hub_loc + Vector((0.0305 * ca - ly * sa, 0.0305 * sa + ly * ca, lz))
        H.cyl(f"hole{k}", 0.0085, 0.002, hole_m, loc=tuple(p), rot=(0, math.pi / 2, hub_rot[2]), seg=24)
    focus_pt = Vector((0.30, -0.10, 0.25))
else:
    u = H.load_unit("IRNX_07", mats, spin=0)
    pul_m = H.mat("pulley grey cast", (0.07, 0.07, 0.075), 0.35, 0.45, bump=(500, 0.03))
    belt_m = H.mat("v-belt rubber", (0.025, 0.025, 0.026), 0.0, 0.55, spec=0.3, bump=(900, 0.02))
    galv = H.mat("motor base", (0.08, 0.085, 0.09), 0.0, 0.45, coat=0.1)         # black painted motor mount
    IN = Vector((0.178, -0.062, 0.394))          # input shaft exit on the +X face
    TOP = 0.592
    PX = IN.x + 0.075                            # pulley plane
    RB, RS = 0.118, 0.058
    # motor mount: base plate on the top lugs, two side cheeks, adjustable slide plate
    H.box("mm_plate", (0.40, 0.34, 0.016), galv, loc=(-0.02, -0.03, TOP + 0.008), bevel=0.002)
    for s_ in (-1, 1):
        H.box(f"mm_cheek{s_}", (0.40, 0.012, 0.07), galv, loc=(-0.02, -0.03 + s_ * 0.164, TOP + 0.045), bevel=0.001)
    H.box("mm_slide", (0.36, 0.30, 0.014), galv, loc=(-0.02, -0.03, TOP + 0.087), bevel=0.002)
    for sx in (-1, 1):
        for sy in (-1, 1):
            H.cyl(f"mm_stud{sx}{sy}", 0.008, 0.11, mats["bolt"], loc=(-0.02 + sx * 0.16, -0.03 + sy * 0.13, TOP + 0.05), seg=16)
            H.cyl(f"mm_nut{sx}{sy}", 0.013, 0.01, mats["bolt"], loc=(-0.02 + sx * 0.16, -0.03 + sy * 0.13, TOP + 0.099), seg=6)
    MS = 0.78                                     # motor scale: 160 L geometry scaled to a ~132 frame
    MZ = TOP + 0.094 + 0.165 * MS                 # motor axis height (motor belly sits on the slide plate)
    m, MF = motor_from_iram(mats, 90, MS)         # shaft end to +X
    FRONT = PX - 0.075
    # the cut motor's front (raw cut plane) sits at local x = -0.107 * MS after the 90 deg spin
    m["parent"].location = (FRONT - 0.012 + 0.107 * MS, IN.y, MZ - 0.21 * MS)
    # drive-end shield closing the cut front of the motor
    H.cyl("m_shield", 0.165 * MS, 0.03, mats["paint"], loc=(FRONT - 0.012, IN.y, MZ), axis="X", seg=128, chamfer=0.008)
    H.cyl("m_shield_boss", 0.055, 0.025, mats["paint"], loc=(FRONT + 0.012, IN.y, MZ), axis="X", seg=64, chamfer=0.004)
    H.cyl("m_shaft", 0.019, 0.09, mats["steel"], loc=(FRONT + 0.05, IN.y, MZ), axis="X", seg=48)
    H.cyl("in_shaft", 0.024, 0.09, mats["steel"], loc=(IN.x + 0.03, IN.y, IN.z), axis="X", seg=48)
    # pulleys (3-groove) and V-belts
    def pulley(name, r, c, w=0.07):
        H.cyl(name, r, w, pul_m, loc=tuple(c), axis="X", seg=160, chamfer=0.004)
        for g in range(3):
            H.torus(f"{name}_g{g}", r - 0.004, 0.0055, H.mat("groove", (0.02, 0.02, 0.02), 0.5, 0.5), loc=(c.x - 0.024 + g * 0.024, c.y, c.z), rot=(0, math.pi / 2, 0), seg=160, rseg=10)
        H.cyl(name + "_hub", r * 0.38, w + 0.03, pul_m, loc=tuple(c), axis="X", seg=64, chamfer=0.003)
        H.cyl(name + "_bore", 0.014, w + 0.032, H.mat("dark", (0.02, 0.02, 0.02), 0.0, 0.5), loc=tuple(c), axis="X", seg=32)
    MC = Vector((PX, IN.y, MZ))
    BC = Vector((PX, IN.y, IN.z))
    pulley("pulley_big", RB, BC)
    pulley("pulley_small", RS, MC)

    def belt(name, c1, r1, c2, r2, x0, width, thick, mt, seg=64):
        (y1, z1), (y2, z2) = c1, c2
        d = math.hypot(y2 - y1, z2 - z1)
        a = math.atan2(z2 - z1, y2 - y1)
        b = math.acos((r1 - r2) / d)
        pts = []
        for t in range(seg + 1):
            ang = a + b + (2 * math.pi - 2 * b) * t / seg
            pts.append((y1 + r1 * math.cos(ang), z1 + r1 * math.sin(ang)))
        for t in range(seg + 1):
            ang = a - b + (2 * b) * t / seg
            pts.append((y2 + r2 * math.cos(ang), z2 + r2 * math.sin(ang)))
        bm = bmesh.new()
        v0 = [bm.verts.new((x0, y, z)) for y, z in pts]
        v1 = [bm.verts.new((x0 + width, y, z)) for y, z in pts]
        n = len(pts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        o = H.obj_from_bmesh(bm, name, mt)
        md = o.modifiers.new("solid", "SOLIDIFY")
        md.thickness = thick
        md.offset = 1.0
        H.smooth(o, 40)
        return o
    for k in range(3):
        belt(f"vbelt{k}", (BC.y, BC.z), RB - 0.002, (MC.y, MC.z), RS - 0.002, PX - 0.031 + k * 0.024, 0.016, 0.011, belt_m)
    focus_pt = Vector((0.18, -0.06, 0.45))

# ---------------------------------------------------------------- the HDRI's own sun as a lamp (same direction, crisp shadow)
if UNIT == "irnx":
    u_sun, elev = 0.60, math.radians(4.0)                 # sun position in the equirect (u) and its elevation
    phi = (u_sun - 0.5) * 2 * math.pi                     # atan2(y, -x) in HDRI space
    ex, ey = -math.cos(phi), math.sin(phi)
    r = -math.radians(YAW)                                # undo the world rotation
    wx, wy = ex * math.cos(r) - ey * math.sin(r), ex * math.sin(r) + ey * math.cos(r)
    sd = Vector((wx * math.cos(elev), wy * math.cos(elev), math.sin(elev)))
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = float(env("SUN_E", 2.2))
    sun.angle = math.radians(1.0)
    sun.color = (1.0, 0.72, 0.45)
    so = bpy.data.objects.new("sun", sun)
    bpy.context.collection.objects.link(so)
    so.rotation_euler = (-sd).to_track_quat("-Z", "Y").to_euler()
    print("sun dir", tuple(round(v, 2) for v in sd))

# ---------------------------------------------------------------- camera
cam = H.camera(tuple(CAM), tuple(TGT), lens=LENS, fstop=FSTOP, focus=tuple(focus_pt), shift=(float(env("SHIFTX", 0.0)), float(env("SHIFTY", 0.085))))
bpy.context.scene.cycles.film_exposure = 1.0
# no extra lights: the HDRI is the only light source (that is what makes it match the background)
from bpy_extras.object_utils import world_to_camera_view
import json
sc = bpy.context.scene
bpy.context.view_layer.update()
cp = Vector((0.21 + 0.10, 0.01, 0.16)) if UNIT == "irc" else Vector((0.178, 0.0, 0.232))
ndc = world_to_camera_view(sc, sc.camera, cp)
json.dump({"spline": [ndc.x, 1 - (ndc.y + sc.camera.data.shift_y)]}, open(os.path.join(H.PREVIEW_DIR if H.PREVIEW else H.OUT, f"photo_{UNIT}.json"), "w"))
H.render(f"photo_{UNIT}", w=2160, h=2700, exposure=CFG["exposure"] + float(env("EXPO", 0.0)))
