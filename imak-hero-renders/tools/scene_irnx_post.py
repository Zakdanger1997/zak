"""Social post (4:5): i.Mak IRNX 07 shaft-mounted gear unit on a quarry conveyor head pulley,
torque arm to the head frame, V-belt drive from a motor above. Outdoors, crushed stone, dust.
Renders 2160x2700; layout via tools/post_layout.py --copy irnx.
python3 tools/scene_irnx_post.py [--preview] [--samples N] [--scale F]
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import bmesh
from mathutils import Vector, Matrix
import hero_lib as H

PHOTO = bool(os.environ.get("PHOTO"))      # product + conveyor head only, transparent background
H.fresh()
mats = H.M()
mats["paint"] = H.mat("imak red", (0.52, 0.012, 0.012), 0.0, 0.52, coat=0.08, spec=0.38, bump=(900, 0.05))
galv = H.mat("galvanised frame", (0.42, 0.43, 0.44), 0.8, 0.5, bump=(60, 0.08))
steel = mats["steel"]
rubber = H.mat("belt", (0.045, 0.045, 0.047), 0.0, 0.5, spec=0.3, bump=(200, 0.08))
vbelt = H.mat("v-belt", (0.03, 0.03, 0.03), 0.0, 0.6, spec=0.3)
gravel = H.mat("gravel", (0.17, 0.16, 0.14), 0.0, 0.9, spec=0.2, bump=(8, 0.9))
rock_m = H.mat("stone", (0.22, 0.21, 0.19), 0.0, 0.85, spec=0.25, bump=(30, 0.5))
pulley_m = H.mat("pulley cast", (0.12, 0.12, 0.12), 0.6, 0.45, bump=(300, 0.04))

if PHOTO:
    H.world_dark(0.45, haze=0.0, tint=(0.9, 0.93, 1.0))
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = float(os.environ.get("SUN_E", 4.5))
    sun.angle = math.radians(1.5)
    sun.color = (1.0, 0.9, 0.78)
    so = bpy.data.objects.new("sun", sun)
    bpy.context.collection.objects.link(so)
    so.rotation_euler = (math.radians(float(os.environ.get("SUN_ALT", 60))), 0, math.radians(float(os.environ.get("SUN_AZ", -40))))
    rnd = random.Random(3)
    sc = bpy.context.scene
else:
    # ---------------------------------------------------------------- world: daylight sky + sun + haze
    sc = bpy.context.scene
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"
    sky.sun_elevation = math.radians(20)
    sky.sun_rotation = math.radians(215)
    sky.sun_intensity = 0.0          # sun comes from a lamp (sharper control)
    for attr, val in (("altitude", 300), ("air_density", 1.2), ("dust_density", 2.5), ("aerosol_density", 2.5)):
        if hasattr(sky, attr):
            setattr(sky, attr, val)
    bg = nt.nodes["Background"]
    nt.links.new(sky.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 0.3
    # haze as a bounded volume box (a world volume would black out the infinitely distant sky)
    haze_m = bpy.data.materials.new("haze")
    haze_m.use_nodes = True
    hn = haze_m.node_tree
    for n in list(hn.nodes):
        if n.type != "OUTPUT_MATERIAL":
            hn.nodes.remove(n)
    vs = hn.nodes.new("ShaderNodeVolumeScatter")
    vs.inputs["Density"].default_value = 0.0015
    vs.inputs["Anisotropy"].default_value = 0.45
    hn.links.new(vs.outputs[0], hn.nodes["Material Output"].inputs["Volume"])
    hb = H.box("hazebox", (70, 70, 16), haze_m, loc=(0, 8, 8))
    hb.display_type = "WIRE"
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 5.5
    sun.angle = math.radians(1.2)
    sun.color = (1.0, 0.88, 0.72)
    so = bpy.data.objects.new("sun", sun)
    bpy.context.collection.objects.link(so)
    so.rotation_euler = (math.radians(66), 0, math.radians(-40))   # warm sun from front-right, low

    # ---------------------------------------------------------------- ground, stockpile, background
    H.plane("ground", (120, 120), gravel)
    rnd = random.Random(3)
    # stone stockpile under the discharge (in front of the head pulley), a bigger one behind
    H.rocks("pile", rock_m, -3.2, 1.2, -4.6, -1.2, 0.0, n=2600, rmin=0.04, rmax=0.13, heap=1.8, seed=5)
    H.rocks("pile2", rock_m, -9.0, -3.5, 2.0, 7.0, 0.0, n=1800, rmin=0.06, rmax=0.2, heap=2.6, seed=9)
    H.rocks("scatter", rock_m, -4.0, 4.0, -5.0, 3.0, 0.0, n=500, rmin=0.02, rmax=0.07, heap=0.0, seed=11)
    # a distant screening tower + second conveyor, hazy
    H.box("tower", (4.0, 3.0, 9.0), galv, loc=(-9, 16, 4.5))
    H.box("tower2", (2.2, 2.2, 6.0), galv, loc=(-5.5, 19, 3.0))
    H.box("conv2", (0.9, 22, 0.5), galv, loc=(4.5, 14, 4.2), rot=(math.radians(-9), 0, 0))
    for i in range(6):
        H.box(f"conv2leg{i}", (0.15, 0.15, 3.0 + i * 0.55), galv, loc=(4.5, 4 + i * 3.6, (3.0 + i * 0.55) / 2))

# ---------------------------------------------------------------- conveyor head (pulley axis along X)
GZ = 2.35                        # IRNX feet height (it hangs on the shaft; feet plane is just a reference)
PZ = GZ + 0.228                  # pulley shaft axis height (IRNX hollow shaft)
RP = 0.22                        # head pulley radius
BW = 0.8                         # belt width
PX0, PX1 = -1.35, -0.55          # pulley span in x
H.cyl("pulley", RP, PX1 - PX0, pulley_m, loc=((PX0 + PX1) / 2, 0, PZ), axis="X", seg=128, chamfer=0.01)
H.cyl("pshaft", 0.045, 1.75, steel, loc=(-0.60, 0, PZ), axis="X", seg=48)      # -1.475 .. 0.275: through the hollow shaft
# plummer blocks either side of the pulley
for x in (-0.42, -1.48):
    H.box(f"pb_base{x}", (0.16, 0.30, 0.04), galv, loc=(x, 0, PZ - 0.17), bevel=0.003)
    H.cyl(f"pb{x}", 0.11, 0.13, galv, loc=(x, 0, PZ), axis="X", seg=64, chamfer=0.008)
    H.box(f"pb_body{x}", (0.13, 0.24, 0.16), galv, loc=(x, 0, PZ - 0.09))
    H.bolts(f"pbb{x}", [(x, s * 0.11, PZ - 0.14) for s in (-1, 1)], mats["bolt"], r=0.011, h=0.014)
# head frame: two columns + cross beams, stringers going back (+Y)
for x in (-0.42, -1.48):
    H.box(f"col{x}", (0.12, 0.12, PZ - 0.19), galv, loc=(x, 0, (PZ - 0.19) / 2))
    H.box(f"colb{x}", (0.12, 0.12, PZ - 0.19), galv, loc=(x, 1.2, (PZ - 0.19) / 2))
    H.box(f"str{x}", (0.10, 7.0, 0.20), galv, loc=(x, 3.5, PZ - 0.40))                 # stringers
    H.box(f"strt{x}", (0.10, 1.6, 0.10), galv, loc=(x, 0.6, PZ - 0.20))
    for i in range(1, 5):
        H.box(f"leg{x}{i}", (0.10, 0.10, PZ - 0.5), galv, loc=(x, 1.2 + i * 1.5, (PZ - 0.5) / 2))
H.box("xbeam", (1.5, 0.12, 0.12), galv, loc=(-0.95, 1.2, PZ - 0.25))
H.box("xbeam2", (1.5, 0.12, 0.12), galv, loc=(-0.95, 0.0, PZ - 0.25))
H.box("xbeam_top", (1.5, 0.10, 0.10), galv, loc=(-0.95, 1.2, PZ + 0.60))               # torque-arm anchor beam
H.box("xbeam_topb", (0.10, 1.3, 0.10), galv, loc=(-0.42, 0.6, PZ + 0.60))
H.box("xbeam_topc", (0.10, 1.3, 0.10), galv, loc=(-1.48, 0.6, PZ + 0.60))
for x in (-0.42, -1.48):
    H.box(f"post{x}", (0.10, 0.10, 0.80), galv, loc=(x, 1.2, PZ + 0.20))
# carrying idlers on the stringers
for i in range(1, 9):
    y = 0.4 + i * 0.75
    H.cyl(f"idler{i}", 0.05, BW + 0.1, galv, loc=(-0.95, y, PZ + 0.02), axis="X", seg=32)
# belt: loop around the head pulley and a far tail pulley, top run carries stone
def belt_loop(name, c1, r1, c2, r2, x0, width, thick, m, seg=48):
    """Belt around two circles in the YZ plane (centres (y,z)), extruded along X from x0 by width."""
    (y1, z1), (y2, z2) = c1, c2
    d = math.hypot(y2 - y1, z2 - z1)
    a = math.atan2(z2 - z1, y2 - y1)
    b = math.acos((r1 - r2) / d)
    pts = []
    for t in range(seg + 1):                     # arc on circle 1 (far side)
        ang = a + b + (2 * math.pi - 2 * b) * t / seg
        pts.append((y1 + r1 * math.cos(ang), z1 + r1 * math.sin(ang)))
    for t in range(seg + 1):                     # arc on circle 2
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
    o = H.obj_from_bmesh(bm, name, m)
    mod = o.modifiers.new("solid", "SOLIDIFY")
    mod.thickness = thick
    mod.offset = 1.0
    H.smooth(o, 40)
    return o

belt_loop("belt", (0.0, PZ), RP + 0.006, (7.0, PZ + 0.0), RP, PX0 + 0.0, BW, 0.014, rubber)
H.rocks("onbelt", rock_m, PX0 + 0.12, PX1 - 0.12, 0.35, 6.5, PZ + RP + 0.01, n=1500, rmin=0.015, rmax=0.045, heap=0.10, seed=21)
# falling stone from the discharge (a few in the air)
H.rocks("falling", rock_m, PX0 + 0.1, PX1 - 0.1, -0.55, -0.25, PZ - 0.9, n=70, rmin=0.015, rmax=0.04, heap=0.9, seed=31)

# ---------------------------------------------------------------- IRNX 07 on the shaft end (+X side)
u = H.load_unit("IRNX_07", mats, loc=(0.0, 0.0, GZ))
in_c = Vector((0.178, -0.062, GZ + 0.394))      # input shaft exit on the +X face
bore_c = Vector((0.178, 0.0, PZ))               # hollow shaft end cover on the +X face
# end cover + retaining plate on the hollow shaft
H.cyl("hs_cover", 0.062, 0.012, steel, loc=(bore_c.x + 0.006, 0, PZ), axis="X", seg=64, chamfer=0.003)
H.bolts("hsb", [(bore_c.x + 0.016, 0.04 * math.cos(math.radians(a)), PZ + 0.04 * math.sin(math.radians(a))) for a in (90, 210, 330)], mats["bolt"], r=0.007, h=0.01, axis="X")
# torque arm: from the top lugs back to the top beam, with a rubber buffer
LUG = Vector((0.0, 0.10, GZ + 0.58))
ANC = Vector((0.0, 1.2, PZ + 0.60))
d = ANC - LUG
H.cyl("tarm", 0.018, d.length - 0.1, steel, loc=tuple(LUG + d * 0.5), axis="Z", seg=24)
bpy.data.objects["tarm"].rotation_euler = d.to_track_quat("Z", "Y").to_euler()
H.cyl("tarm_eye", 0.035, 0.05, galv, loc=tuple(LUG), axis="X", seg=32)
H.cyl("tarm_eye2", 0.035, 0.05, galv, loc=tuple(ANC), axis="X", seg=32)
H.box("tarm_brk", (0.12, 0.05, 0.16), galv, loc=(0.0, 1.2, PZ + 0.68))
H.cyl("tarm_buf", 0.045, 0.06, rubber, loc=tuple(ANC + Vector((0, -0.05, 0))), axis="Y", seg=32)

# ---------------------------------------------------------------- V-belt drive: motor above, belts down to the input shaft
BPX = in_c.x + 0.075                             # plane of the pulleys (x centre)
RB, RS = 0.135, 0.058                            # big / small pulley radii
MC = Vector((BPX, 0.42, PZ + 0.92))              # small pulley / motor shaft centre
H.cyl("pulley_big", RB, 0.075, pulley_m, loc=(BPX, in_c.y, in_c.z), axis="X", seg=128, chamfer=0.006)
H.cyl("pulley_big_hub", 0.055, 0.11, pulley_m, loc=(BPX, in_c.y, in_c.z), axis="X", seg=64)
H.cyl("pulley_small", RS, 0.075, pulley_m, loc=tuple(MC), axis="X", seg=96, chamfer=0.005)
for k in range(3):                                # three V-belts
    belt_loop(f"vbelt{k}", (in_c.y, in_c.z), RB - 0.004, (MC.y, MC.z), RS - 0.004, BPX - 0.034 + k * 0.024, 0.014, 0.010, vbelt, seg=40)
# motor (IRAM 93-160 L motor part), shaft to +X, on a bracket above the head frame
m = H.load_unit("IRAM_93-160_L", mats, spin=-90)
for o in m["objs"]:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, -157.0), plane_no=(0, 0, 1), clear_outer=True)
    bm.to_mesh(o.data)
    bm.free()
MOTOR_FACE = 0.315
MFX = BPX - 0.06                                  # motor front face x
m["parent"].location = (MFX - MOTOR_FACE, MC.y, MC.z - 0.21)
H.cyl("mshaft", 0.021, 0.12, steel, loc=(MFX + 0.05, MC.y, MC.z), axis="X", seg=32)
# motor mounting: flange bracket plate + slide base on a platform
H.box("mplate", (0.03, 0.42, 0.42), galv, loc=(MFX - 0.015, MC.y, MC.z), bevel=0.003)
H.box("mbase", (0.55, 0.50, 0.03), galv, loc=(MFX - 0.30, MC.y, MC.z - 0.21 - 0.015), bevel=0.003)
H.box("mbase_ch", (0.55, 0.10, 0.08), galv, loc=(MFX - 0.30, MC.y + 0.20, MC.z - 0.21 - 0.07))
H.box("mbase_ch2", (0.55, 0.10, 0.08), galv, loc=(MFX - 0.30, MC.y - 0.20, MC.z - 0.21 - 0.07))
H.box("mplatform", (1.9, 0.9, 0.08), galv, loc=(-0.80, 0.80, MC.z - 0.21 - 0.15))
for x in (-0.42, -1.48):
    H.box(f"mpost{x}", (0.10, 0.10, MC.z - 0.21 - 0.19 - (PZ + 0.60)), galv, loc=(x, 0.8, (MC.z - 0.21 - 0.19 + PZ + 0.60) / 2))
H.box("mbrace", (0.06, 0.06, 0.9), galv, loc=(0.1, 0.42, MC.z - 0.21 - 0.19 - 0.45))
# belt guard back plate (open towards the camera so the belts stay visible)


# ---------------------------------------------------------------- dust in the sun
dust_m = H.mat("dust", (0.85, 0.78, 0.65), 0.0, 0.7)
bm = bmesh.new()
for i in range(70):
    x, y, z = rnd.uniform(-1.5, 2.0), rnd.uniform(-1.6, 1.0), rnd.uniform(PZ - 1.4, PZ + 1.2)
    r = rnd.uniform(0.001, 0.003)
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((x, y, z)))
H.obj_from_bmesh(bm, "dust", dust_m)

# ---------------------------------------------------------------- lights & camera
target = Vector((-0.1, 0.0, PZ + 0.25))
H.light_area("key", (2.6, -2.2, PZ + 1.6), target, 500, 1.6, (1.0, 0.95, 0.9))
H.light_area("fill", (1.5, -3.0, PZ + 0.2), target, 160, 4.0, (0.8, 0.86, 1.0))
H.light_area("cover_acc", (1.0, -0.6, PZ - 0.1), bore_c, 50, 0.3, (1.0, 0.96, 0.9))
H.camera((2.3, -2.2, PZ + 0.42), (-0.1, 0.1, PZ + 0.25), lens=45, fstop=4.5, focus=tuple(bore_c), shift=(0.0, 0.10))
from bpy_extras.object_utils import world_to_camera_view
import json
bpy.context.view_layer.update()
ndc = world_to_camera_view(sc, sc.camera, bore_c)
json.dump({"spline": [ndc.x, 1 - (ndc.y + sc.camera.data.shift_y)]}, open(os.path.join(H.PREVIEW_DIR if H.PREVIEW else H.OUT, "irnx_post_raw" + ("_photo" if PHOTO else "") + ".json"), "w"))
H.render("irnx_post_raw" + ("_photo" if PHOTO else ""), w=2160, h=2700, exposure=-0.8, transparent=PHOTO)
