#!/usr/bin/env python3
"""Photoreal Cycles shots of the i.Mak IRC crane gearbox for the IRC video.

Usage:
    python3 tools/irc_scene.py SHOT [--frames A-B] [--samples N] [--res WxH] [--still F]
SHOT is one of: dark, studio, spline, hoist, hoistwide, closeup
Frames go to render/<shot>/####.png (existing frames are skipped, so runs can resume).

The IRC geometry is the official i.Mak IRC 93 STEP model from i-Guide, split into meshes by
imak-mixing-brochure/tools/step_parts.py (PARTS env var, default /tmp/claude-0/cad/parts).
Paint: i.Mak factory blue, high-gloss enamel over cast-iron texture (matched to factory photos).
"""
import math
import os
import sys

import bpy  # noqa: E402  (bpy must come before bmesh)
import bmesh
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PARTS = os.environ.get("PARTS", "/tmp/claude-0/cad/parts")
HDRI = os.environ.get("HDRI", "/tmp/claude-0/irc/hdri")
A = sys.argv[1:]
SHOT = A[0] if A else "studio"


def arg(name, default):
    return A[A.index(name) + 1] if name in A else default


SAMPLES = int(arg("--samples", 48))
RES = [int(v) for v in arg("--res", "1080x1920").split("x")]
FPS = 24
TAU = math.pi * 2

# ----------------------------------------------------------------- materials
def srgb(c):
    return tuple(((v / 255 + 0.055) / 1.055) ** 2.4 if v / 255 > 0.04045 else v / 255 / 12.92 for v in c)


def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]


def paint_mat(name, rgb, rough=0.2, coat=1.0, cast=0.35, peel=0.25):
    """Industrial enamel: gloss coat over a sand-cast surface (two noise bumps) with tiny colour variation."""
    m, nt, p = node_mat(name)
    N = nt.nodes.new
    L = nt.links.new
    tc = N("ShaderNodeTexCoord")
    n1 = N("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 90; n1.inputs["Detail"].default_value = 8
    n2 = N("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 1400; n2.inputs["Detail"].default_value = 2
    L(tc.outputs["Object"], n1.inputs["Vector"]); L(tc.outputs["Object"], n2.inputs["Vector"])
    b1 = N("ShaderNodeBump"); b1.inputs["Strength"].default_value = cast; b1.inputs["Distance"].default_value = 0.0006
    b2 = N("ShaderNodeBump"); b2.inputs["Strength"].default_value = peel; b2.inputs["Distance"].default_value = 0.00015
    L(n1.outputs["Fac"], b1.inputs["Height"]); L(n2.outputs["Fac"], b2.inputs["Height"]); L(b1.outputs["Normal"], b2.inputs["Normal"])
    L(b1.outputs["Normal"], p.inputs["Normal"])            # base layer follows the casting
    L(b2.outputs["Normal"], p.inputs["Coat Normal"])       # gloss coat shows orange peel
    col = srgb(rgb)
    ramp = N("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * 0.88 for c in col], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * 1.06) for c in col], 1)
    n3 = N("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 6
    L(tc.outputs["Object"], n3.inputs["Vector"]); L(n3.outputs["Fac"], ramp.inputs["Fac"])
    L(ramp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rough
    p.inputs["Coat Weight"].default_value = coat
    p.inputs["Coat Roughness"].default_value = 0.04
    p.inputs["Coat IOR"].default_value = 1.5
    return m


def metal_mat(name, rgb=(200, 203, 207), rough=0.25, aniso=0.0, scratch=0.08):
    m, nt, p = node_mat(name)
    N, L = nt.nodes.new, nt.links.new
    p.inputs["Base Color"].default_value = (*srgb(rgb), 1)
    p.inputs["Metallic"].default_value = 1.0
    tc = N("ShaderNodeTexCoord")
    n = N("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 300; n.inputs["Detail"].default_value = 4
    mp = N("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 60)
    L(tc.outputs["Object"], mp.inputs["Vector"]); L(mp.outputs["Vector"], n.inputs["Vector"])
    r = N("ShaderNodeMapRange"); r.inputs["To Min"].default_value = rough - scratch; r.inputs["To Max"].default_value = rough + scratch
    L(n.outputs["Fac"], r.inputs["Value"]); L(r.outputs["Result"], p.inputs["Roughness"])
    if aniso:
        p.inputs["Anisotropic"].default_value = aniso
    return m


def plain(name, rgb, rough=0.5, metal=0.0, coat=0.0):
    m, nt, p = node_mat(name)
    p.inputs["Base Color"].default_value = (*srgb(rgb), 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    return m


def rope_mat():
    """Steel wire rope: metallic with a strand pattern (wave texture along the rope)."""
    m, nt, p = node_mat("wire rope")
    N, L = nt.nodes.new, nt.links.new
    p.inputs["Base Color"].default_value = (*srgb((120, 118, 112)), 1)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.42
    tc = N("ShaderNodeTexCoord")
    w = N("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "DIAGONAL"
    w.inputs["Scale"].default_value = 60; w.inputs["Distortion"].default_value = 1.5
    L(tc.outputs["UV"], w.inputs["Vector"])
    b = N("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.8
    L(w.outputs["Fac"], b.inputs["Height"]); L(b.outputs["Normal"], p.inputs["Normal"])
    return m


MAT = {}


def mats():
    MAT["blue"] = paint_mat("i.Mak blue", (6, 84, 178))
    MAT["machined"] = metal_mat("machined cast iron", (150, 152, 155), 0.34, scratch=0.05)
    MAT["steel"] = metal_mat("ground shaft steel", (215, 218, 222), 0.12, aniso=0.4, scratch=0.04)
    MAT["oiled"] = metal_mat("oiled spline steel", (120, 118, 112), 0.22)
    MAT["yellow"] = paint_mat("crane yellow", (232, 172, 12), rough=0.3, coat=0.6, cast=0.08, peel=0.2)
    MAT["grey"] = paint_mat("drum grey", (70, 74, 80), rough=0.35, coat=0.4, cast=0.05)
    MAT["black"] = plain("rubber", (18, 18, 20), 0.6)
    MAT["rope"] = rope_mat()
    MAT["concrete"] = plain("concrete", (112, 110, 104), 0.9)
    MAT["red"] = paint_mat("hook red", (190, 24, 18), rough=0.3, coat=0.5, cast=0.1)
    MAT["alu"] = metal_mat("nameplate", (205, 208, 210), 0.3)


# ------------------------------------------------------------------ the IRC
IRC_OUT = Vector((-0.035, 0.0, 0.0))    # filled in by build_irc (world position of the output axis)


MODEL = os.environ.get("MODEL", "IRCM_93-160_L")   # official i.Mak geared motor with brake (IRCM 93-160 L-BR)


def build_irc(name=None, details=True):
    name = name or MODEL
    """Import the three part meshes, stand the unit on its base, classify machined faces."""
    objs = []
    for part in ("paint", "steel", "bore"):
        bpy.ops.wm.stl_import(filepath=os.path.join(PARTS, f"{name}_{part}.stl"), global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = f"irc_{part}"
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # importer keeps mm as scale
        o.select_set(False)
        objs.append(o)
    paint, steel, bore = objs
    # STEP: output/input axes along Z (shafts exit towards -Z), unit tall along Y.
    # machined: flat faces facing -Z near the output end plane, the spline bore, and drilled holes
    me = paint.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    zmin = min(v.co.z for v in bm.verts)
    paint.data.materials.append(MAT["blue"])
    paint.data.materials.append(MAT["machined"])
    paint.data.materials.append(MAT["oiled"])
    ox, oy = -0.035, -0.350
    # the housing is stepped: the output face lies behind the input face. Find it from the spline faces.
    near = [v.co.z for v in bm.verts if math.hypot(v.co.x - ox, v.co.y - oy) < 0.045]
    z_out = min(near) if (near and details) else zmin
    if not details:
        ox, oy = 1e9, 1e9                    # other sizes: plain paint + machined faces only
    for f in bm.faces:
        c = f.calc_center_median()
        r = math.hypot(c.x - ox, c.y - oy)
        n = f.normal
        if r < 0.040 and c.z < z_out + 0.08:
            f.material_index = 2                 # spline end / bore of the output
        elif n.z < -0.98 and c.z < zmin + 0.004 and not name.startswith("IRCM"):
            f.material_index = 1                 # machined input-side face (shaft-input IRC only)
        elif n.z < -0.98 and r < 0.118 and c.z < z_out + 0.035:
            f.material_index = 1                 # machined output flange and spigot
    bm.to_mesh(me)
    bm.free()
    steel.data.materials.append(MAT["steel"])
    bore.data.materials.append(MAT["machined"])
    root = bpy.data.objects.new("IRC", None)
    bpy.context.collection.objects.link(root)
    for o in objs:
        o.parent = root
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
        o.select_set(False)
    # stand up: STEP Y -> world Z, STEP Z -> world -Y (shafts point towards +Y)
    root.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    zlo = min(p.z for p in pts)
    root.location.z = -zlo
    bpy.context.view_layer.update()
    IRC_OUT[:] = root.matrix_world @ Vector((ox, oy, z_out))       # output end centre, world
    root["in"] = list(root.matrix_world @ Vector((0.0, 0.0, zmin)))  # input shaft base (x, y≈0)
    root["geared"] = name.startswith("IRCM")
    if not details:
        return root
    add_details(root, zmin)
    # DIN 5480 W70x3x30x22 output spline (the STEP envelope only shows its end face), 50 HRC ground steel
    sp = spline_shaft(22, 0.0315, 0.0347, 0.065, MAT["oiled"], name="irc output spline")
    sp.location = IRC_OUT + Vector((0, -0.02, 0))
    sp.parent = root
    sp.matrix_parent_inverse = root.matrix_world.inverted()
    IRC_OUT.y += 0.045                      # tip of the spline, world
    return root


def add_details(root, zmin):
    """Small real-world parts the envelope model leaves out: nameplate and breather, placed by ray casts."""
    dg = bpy.context.evaluated_depsgraph_get()
    sc = bpy.context.scene

    def hit(origin, direction):
        ok, loc, nrm, *_ = sc.ray_cast(dg, Vector(origin), Vector(direction).normalized())
        return (loc, nrm) if ok else (None, None)

    # nameplate on the big flat side (world -X), riveted brushed aluminium
    loc, nrm = hit((-1.0, -0.02, 0.36), (1, 0, 0))
    if loc is not None:
        tex = nameplate_texture()
        m, nt, p = node_mat("nameplate print")
        it = nt.nodes.new("ShaderNodeTexImage"); it.image = tex
        nt.links.new(it.outputs["Color"], p.inputs["Base Color"])
        p.inputs["Metallic"].default_value = 0.6
        p.inputs["Roughness"].default_value = 0.32
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc + nrm * 0.0015)
        pl = bpy.context.object
        pl.name = "nameplate"
        pl.scale = (0.095, 0.06, 1)
        pl.rotation_euler = nrm.to_track_quat("Z", "Y").to_euler()
        pl.rotation_euler.rotate_axis("Z", math.radians(90))
        pl.data.materials.append(m)
        sol = pl.modifiers.new("t", "SOLIDIFY"); sol.thickness = 0.0012
        pl.parent = root
        pl.matrix_parent_inverse = root.matrix_world.inverted()
    # breather plug on top
    loc, nrm = hit((0.03, -0.08, 2.0), (0, 0, -1))
    if loc is not None:
        for dz, rad, h, mt, v in ((0.012, 0.010, 0.024, MAT["steel"], 24), (0.003, 0.016, 0.008, MAT["machined"], 6)):
            bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=rad, depth=h, location=loc + Vector((0, 0, dz)))
            c = bpy.context.object
            c.data.materials.append(mt)
            c.parent = root
            c.matrix_parent_inverse = root.matrix_world.inverted()


def nameplate_texture():
    from PIL import Image, ImageDraw, ImageFont
    W, H = 760, 480
    im = Image.new("RGB", (W, H), (196, 199, 201))
    d = ImageDraw.Draw(im)
    fdir = os.path.join(ROOT, "..", "imak-drive-handbook", "fonts")
    def font(n, s):
        try:
            from fontTools.ttLib import TTFont
            p = f"/tmp/{n}.ttf"
            if not os.path.exists(p):
                f = TTFont(os.path.join(fdir, n + ".woff2")); f.flavor = None; f.save(p)
            return ImageFont.truetype(p, s)
        except Exception:
            return ImageFont.load_default()
    d.rectangle((10, 10, W - 10, H - 10), outline=(40, 40, 44), width=5)
    d.rectangle((10, 10, W - 10, 110), fill=(30, 34, 40))
    d.text((34, 22), "i.Mak", font=font("barlow-condensed-latin-700-normal", 74), fill=(230, 40, 30))
    d.text((300, 44), "GEARBOXES & DRIVES", font=font("barlow-condensed-latin-600-normal", 40), fill=(235, 235, 235))
    rows = [("TYPE", "IRC 93"), ("i", "—"), ("SERIAL", "—"), ("OIL", "ISO VG 220"), ("MADE IN", "TÜRKİYE")]
    f2 = font("barlow-condensed-latin-600-normal", 40)
    for k, (a, b) in enumerate(rows):
        y = 130 + k * 66
        d.text((40, y), a, font=f2, fill=(40, 40, 44))
        d.text((300, y), b, font=f2, fill=(20, 20, 24))
        d.line((36, y + 56, W - 36, y + 56), fill=(120, 120, 124), width=2)
    p = "/tmp/claude-0/irc/nameplate.png"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p)
    return bpy.data.images.load(p)


# ---------------------------------------------------------------- the hoist
def cyl(r, length, mat, axis="Y", loc=(0, 0, 0), verts=64, name="cyl"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=length, location=loc)
    o = bpy.context.object
    o.name = name
    if axis == "Y":
        o.rotation_euler = (math.radians(90), 0, 0)
    elif axis == "X":
        o.rotation_euler = (0, math.radians(90), 0)
    o.data.materials.append(mat)
    bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    return o


def boxo(size, loc, mat, name="box", bevel=0.004):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2
    o.data.materials.append(mat)
    return o


def spline_shaft(z, r_root, r_tip, length, mat, name="spline"):
    """External involute-like spline (DIN 5480 look) along +Y, as a toothed profile extruded."""
    bm = bmesh.new()
    pts = []
    for k in range(z):
        a0 = TAU * k / z
        for t, rr in ((-0.30, r_root), (-0.17, r_tip), (0.17, r_tip), (0.30, r_root)):
            a = a0 + t * TAU / z
            pts.append((rr * math.cos(a), rr * math.sin(a)))
    vs0 = [bm.verts.new((x, 0, y)) for x, y in pts]
    vs1 = [bm.verts.new((x, length, y)) for x, y in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))
    bm.faces.new(list(reversed(vs0)))
    bm.faces.new(vs1)
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    b = o.modifiers.new("bev", "BEVEL"); b.width = 0.0012; b.segments = 1; b.limit_method = "ANGLE"
    return o


def build_hoist(irc):
    """Crab layout: IRC at the end, drum on the output (+Y), motor + brake above on the input."""
    out = IRC_OUT.copy()
    inp = Vector(irc["in"])
    H = {}
    DR, DL = 0.17, 0.78                       # drum radius and length (m)
    y0 = out.y + 0.012                        # TBF face sits just past the spline tip when engaged
    drum = bpy.data.objects.new("drum", None)
    bpy.context.collection.objects.link(drum)
    drum.location = (out.x, y0, out.z)
    # shell with rope grooves (bump), end discs, splined stub towards the IRC
    shell = cyl(DR, DL, MAT["machined"], loc=(0, DL / 2, 0), verts=128, name="drum shell")
    shell.parent = drum
    groove(shell.data.materials[0])
    for yy in (0.0, DL):
        d = cyl(DR + 0.035, 0.03, MAT["grey"], loc=(0, yy, 0), name="drum flange")
        d.parent = drum
    tbf = drum_flange()
    tbf.parent = drum
    sp = tbf
    far = cyl(0.045, 0.12, MAT["steel"], loc=(0, DL + 0.06, 0), name="drum journal")
    far.parent = drum
    H["drum"] = drum
    H["spline"] = sp
    # pillow-block bearing at the far end on a yellow pedestal
    ped = boxo((0.20, 0.06, out.z + 0.02), (out.x, y0 + DL + 0.08, (out.z + 0.02) / 2 - 0.06), MAT["yellow"], "pedestal")
    brg = cyl(0.085, 0.07, MAT["blue"], loc=(out.x, y0 + DL + 0.08, out.z), name="bearing housing")
    # frame: two yellow I-beams under everything + cross members
    fz = -0.06
    for x in (-0.36, 0.30):
        beam(x, out.y - 0.45, y0 + DL + 0.35, fz)
    boxo((0.80, 0.08, 0.02), (out.x, out.y - 0.30, fz + 0.01), MAT["yellow"], "cross1")
    boxo((0.80, 0.08, 0.02), (out.x, y0 + DL + 0.08, fz + 0.01), MAT["yellow"], "cross2")
    H["coupling"] = None
    if not irc.get("geared"):
        # shaft-input IRC: separate motor + brake on the input, above the drum
        mz = inp.z
        coup_y = inp.y + 0.10
        H["coupling"] = jaw_coupling(Vector((inp.x, coup_y, mz)))
        H["motor"] = motor(Vector((inp.x, coup_y + 0.09, mz)))
        boxo((0.30, 0.38, 0.03), (inp.x, coup_y + 0.33, mz - 0.155), MAT["yellow"], "motor plate")
        for yy in (coup_y + 0.17, coup_y + 0.50):
            boxo((0.03, 0.03, mz - 0.155 - DR - 0.02), (inp.x + 0.12, yy, (mz - 0.155 + DR + 0.02) / 2 + 0.0), MAT["yellow"], "post")
    H["DR"], H["DL"], H["y0"] = DR, DL, y0
    return H


def drum_flange():
    """i.Mak TBF drum connection flange for IRC 93: Ø198, spigot Ø130, N70x3x30x22 internal spline, 6 bolts."""
    g = bpy.data.objects.new("TBF", None)
    bpy.context.collection.objects.link(g)
    body = cyl(0.099, 0.022, MAT["blue"], loc=(0, -0.030, 0), verts=96, name="TBF flange")
    spig = cyl(0.065, 0.034, MAT["blue"], loc=(0, -0.002, 0), verts=96, name="TBF spigot")
    hole = spline_shaft(22, 0.0322, 0.0354, 0.09, MAT["oiled"], name="cutter")
    hole.location = (0, -0.07, 0)
    for o in (body, spig):
        bpy.context.view_layer.objects.active = o
        m = o.modifiers.new("cut", "BOOLEAN"); m.object = hole; m.operation = "DIFFERENCE"; m.solver = "EXACT"
        bpy.ops.object.modifier_apply(modifier="cut")
        o.parent = g
    inner = cyl(0.0322, 0.05, MAT["oiled"], loc=(0, -0.012, 0), verts=44, name="TBF spline bottom")
    inner.parent = g
    bpy.data.objects.remove(hole)
    for k in range(6):
        a = TAU * k / 6 + 0.26
        b = cyl(0.011, 0.012, MAT["machined"], loc=(math.cos(a) * 0.082, -0.046, math.sin(a) * 0.082), verts=6, name="bolt head")
        b.parent = g
    return g


def groove(mat):
    """Helical rope grooves as a bump (wave along the drum axis)."""
    nt = mat.node_tree
    p = nt.nodes["Principled BSDF"]
    N, L = nt.nodes.new, nt.links.new
    tc = N("ShaderNodeTexCoord")
    w = N("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"
    w.inputs["Scale"].default_value = 52; w.wave_profile = "SIN"
    L(tc.outputs["Object"], w.inputs["Vector"])
    b = N("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.9; b.inputs["Distance"].default_value = 0.004
    L(w.outputs["Fac"], b.inputs["Height"]); L(b.outputs["Normal"], p.inputs["Normal"])


def beam(x, y0, y1, z):
    L = y1 - y0
    for dz, h in ((0.0, 0.012), (-0.14, 0.012)):
        boxo((0.10, L, h), (x, (y0 + y1) / 2, z + dz), MAT["yellow"], "flange")
    boxo((0.010, L, 0.13), (x, (y0 + y1) / 2, z - 0.07), MAT["yellow"], "web")


def jaw_coupling(c):
    g = bpy.data.objects.new("coupling", None)
    bpy.context.collection.objects.link(g)
    g.location = c
    for yy, mt in ((-0.035, MAT["machined"]), (0.035, MAT["machined"])):
        h = cyl(0.055, 0.05, mt, loc=(0, yy, 0), name="hub")
        h.parent = g
    s = cyl(0.058, 0.02, MAT["red"], loc=(0, 0, 0), verts=12, name="spider")
    s.parent = g
    return g


def motor(c):
    """IEC motor with cooling fins, terminal box, fan cover and a disc brake – i.Mak blue."""
    g = bpy.data.objects.new("motor", None)
    bpy.context.collection.objects.link(g)
    g.location = c
    R, L = 0.13, 0.42
    parts = [cyl(R, L, MAT["blue"], loc=(0, L / 2 + 0.04, 0), name="motor body")]
    parts.append(cyl(R + 0.02, 0.04, MAT["blue"], loc=(0, 0.02, 0), name="flange end"))
    for k in range(28):
        a = TAU * k / 28
        f = boxo((0.012, L - 0.05, 0.03), (math.cos(a) * (R + 0.012), L / 2 + 0.05, math.sin(a) * (R + 0.012)), MAT["blue"], "fin", bevel=0.002)
        f.rotation_euler = (0, -a, 0)
        parts.append(f)
    parts.append(boxo((0.13, 0.15, 0.08), (0, L / 2, R + 0.045), MAT["blue"], "terminal box"))
    parts.append(cyl(0.012, 0.04, MAT["black"], axis="X", loc=(0.08, L / 2, R + 0.04), name="gland"))
    # brake + fan cover
    parts.append(cyl(R + 0.005, 0.10, MAT["blue"], loc=(0, L + 0.09, 0), name="brake housing"))
    parts.append(cyl(R - 0.01, 0.12, MAT["grey"], loc=(0, L + 0.20, 0), name="fan cover"))
    parts.append(cyl(0.015, 0.06, MAT["red"], axis="X", loc=(R + 0.02, L + 0.09, 0), name="release lever"))
    for p in parts:
        p.parent = g
    shaft = cyl(0.024, 0.08, MAT["steel"], loc=(0, -0.03, 0), name="motor shaft")
    shaft.parent = g
    return g


def build_hook_block(top, H):
    """Rope falls from the drum to a bottom block with sheave, hook, slings and a concrete load."""
    g = bpy.data.objects.new("hookblock", None)
    bpy.context.collection.objects.link(g)
    g.location = top
    for x in (-0.075, 0.075):
        p = cyl(0.19, 0.03, MAT["yellow"], axis="X", loc=(x, 0, 0), verts=48, name="side plate")
        p.parent = g
        for yy in (-0.12, 0.12):
            bolt = cyl(0.018, 0.2, MAT["machined"], axis="X", loc=(0, yy, -0.1), verts=6, name="tie bolt")
            bolt.parent = g
    sh = cyl(0.14, 0.09, MAT["machined"], axis="X", loc=(0, 0, 0.02), name="sheave")
    sh.parent = g
    # forged hook: shank + bent body (torus segment) + tip
    sk = cyl(0.03, 0.18, MAT["red"], axis="Z", loc=(0, 0, -0.27), name="shank")
    sk.parent = g
    bpy.ops.mesh.primitive_torus_add(major_radius=0.10, minor_radius=0.035, major_segments=48, minor_segments=16, location=(0, 0.10, -0.46))
    t = bpy.context.object
    t.name = "hook"
    t.rotation_euler = (0, math.radians(90), 0)
    t.data.materials.append(MAT["red"])
    bm = bmesh.new(); bm.from_mesh(t.data)
    gone = [v for v in bm.verts if v.co.y > 0.0 and v.co.z < 0.0 and v.co.x > -1]   # open the hook mouth
    bmesh.ops.delete(bm, geom=[v for v in gone if v.co.y > 0.02 and v.co.z < -0.03], context="VERTS")
    bm.to_mesh(t.data); bm.free()
    t.parent = g
    # load: concrete block with lifting slings
    load = boxo((1.3, 1.3, 1.2), (0, 0.10, -1.95), stencil_mat(), "load", bevel=0.025)   # 2.0 m³ concrete ≈ 5 t
    load.parent = g
    for sx in (-0.58, 0.58):
        for sy in (-0.48, 0.68):
            a = Vector((0, 0.10, -0.56))
            b = Vector((sx, sy, -1.35))
            s = rod(a, b, 0.012, MAT["rope"], "sling")
            s.parent = g
    return g


def stencil_mat():
    """Concrete with a sprayed '5 t' stencil, projected on the block's faces (box mapping)."""
    from PIL import Image, ImageDraw, ImageFont
    W = 1024
    im = Image.new("RGB", (W, W), (128, 126, 120))
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/tmp/barlow-condensed-latin-700-normal.ttf", 330)
    except OSError:
        f = ImageFont.load_default()
    d.text((W / 2, W / 2), "5 t", font=f, fill=(24, 24, 26), anchor="mm")
    p = "/tmp/claude-0/irc/stencil.png"
    im.save(p)
    m, nt, pr = node_mat("concrete 5 t")
    N, L = nt.nodes.new, nt.links.new
    tc = N("ShaderNodeTexCoord")
    it = N("ShaderNodeTexImage"); it.image = bpy.data.images.load(p); it.projection = "BOX"; it.projection_blend = 0.1
    mp = N("ShaderNodeMapping"); mp.inputs["Location"].default_value = (0.5, 0.5, 0.5); mp.inputs["Scale"].default_value = (0.77, 0.77, 0.83)
    L(tc.outputs["Object"], mp.inputs["Vector"]); L(mp.outputs["Vector"], it.inputs["Vector"])
    n = N("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 40; n.inputs["Detail"].default_value = 10
    mix = N("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 0.35
    L(it.outputs["Color"], mix.inputs[6]); L(n.outputs["Color"], mix.inputs[7])
    L(mix.outputs[2], pr.inputs["Base Color"])
    b = N("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.4
    L(n.outputs["Fac"], b.inputs["Height"]); L(b.outputs["Normal"], pr.inputs["Normal"])
    pr.inputs["Roughness"].default_value = 0.92
    return m


def rod(a, b, r, mat, name):
    d = b - a
    o = cyl(r, d.length, mat, axis="Z", loc=(a + b) / 2, verts=12, name=name)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return o


# ------------------------------------------------------------ world / render
def world(hdri, strength=1.0, rot=0.0, visible=True, blur=0.0, camera_black=False):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(HDRI, hdri))
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, rot)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    bg = nt.nodes["Background"]
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    if camera_black:
        # the camera sees black; reflections and light still come from the HDRI
        lp = nt.nodes.new("ShaderNodeLightPath")
        blk = nt.nodes.new("ShaderNodeBackground"); blk.inputs["Color"].default_value = (0, 0, 0, 1)
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
        nt.links.new(bg.outputs["Background"], mix.inputs[1])
        nt.links.new(blk.outputs["Background"], mix.inputs[2])
        nt.links.new(mix.outputs["Shader"], nt.nodes["World Output"].inputs["Surface"])
    if not visible:
        sc.render.film_transparent = True


def area(loc, target, energy, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.object
    l.data.energy = energy
    l.data.size = size
    l.data.color = color
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return l


def camera(loc, target, lens=50, fstop=None, focus=None):
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = loc
    cam.data.lens = lens
    cam.data.sensor_width = 36
    tgt = bpy.data.objects.new("target", None)
    sc.collection.objects.link(tgt)
    tgt.location = target
    c = cam.constraints.new("TRACK_TO")
    c.target = tgt
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
        cam.data.dof.focus_object = tgt if focus is None else focus
    return cam, tgt


def render_setup(look="AgX - Base Contrast", exposure=0.0):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 8
    sc.cycles.glossy_bounces = 4
    sc.cycles.transparent_max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.fps = FPS
    sc.view_settings.view_transform = "Standard"     # keeps the i.Mak blue saturated, like the factory photos
    sc.view_settings.look = "None"
    sc.view_settings.exposure = exposure
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if sc.render.film_transparent else "RGB"


def floor(mat=None, catcher=False, size=30):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    f = bpy.context.object
    if catcher:
        f.is_shadow_catcher = True
    elif mat:
        f.data.materials.append(mat)
    return f


def cyclorama(rgb=(118, 118, 115)):
    """Seamless studio sweep: floor curving up into a back wall."""
    bm = bmesh.new()
    prof = []
    for i in range(24):
        a = (i / 23) * math.pi / 2
        prof.append((0, -3 + 0, 0))
    W, R, back = 12, 1.6, 2.4
    pts = [(-6.0, 0.0)]
    for i in range(25):
        a = (i / 24) * math.pi / 2
        pts.append((back - R + math.sin(a) * R, R - math.cos(a) * R))
    pts.append((back, 6.0))
    rows = []
    for x in (-W / 2, W / 2):
        rows.append([bm.verts.new((x, y, z)) for y, z in pts])
    for i in range(len(pts) - 1):
        bm.faces.new((rows[0][i], rows[1][i], rows[1][i + 1], rows[0][i + 1]))
    me = bpy.data.meshes.new("cyc")
    bm.to_mesh(me)
    o = bpy.data.objects.new("cyclorama", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(plain("studio paper", rgb, 0.9))
    for p in o.data.polygons:
        p.use_smooth = True
    return o


# --------------------------------------------------------------------- shots
def shot_dark(irc):
    """Opening: the unit on black, rim light sweeping, slow turn."""
    world("machine_shop_02.exr", 0.35, rot=1.0, camera_black=True)
    sc = bpy.context.scene
    floor(plain("black floor", (6, 6, 7), 0.35))
    area((-1.4, -1.0, 1.9), (0, 0, 0.45), 260, 1.2)
    area((1.6, 1.4, 1.2), (0, 0, 0.45), 520, 0.6, (0.75, 0.85, 1.0))
    area((-1.6, 1.5, 0.9), (0, 0, 0.45), 380, 0.5, (1.0, 0.9, 0.8))
    cam, tgt = camera((1.25, -2.6, 0.62), (0.0, 0.0, 0.42), lens=58, fstop=5.6)
    spin(irc, -40, 15, 0, 96)
    sc.frame_start, sc.frame_end = 0, 95
    render_setup(exposure=-0.3)


def shot_studio(irc):
    """Reference-style light grey sweep, unit turning slowly, room for titles above."""
    cyclorama()
    world("studio_small_09.exr", 0.9, rot=1.2)
    area((-1.5, -1.6, 2.2), (0, 0, 0.4), 420, 2.0)
    area((1.8, -0.6, 1.0), (0, 0, 0.4), 160, 2.0)
    area((0.5, 1.4, 2.0), (0, 0, 0.5), 260, 1.2)
    cam, tgt = camera((0.0, -3.3, 0.78), (0.0, 0.0, 0.48), lens=66)
    spin(irc, -62, 28, 0, 360)        # 90° sweep over 15 s; the edit uses sections
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, 359
    render_setup(exposure=float(arg("--exposure", -1.45)))


def spin(obj, a0, a1, f0, f1):
    """Turn an object about world Z around its own footprint centre."""
    piv = bpy.data.objects.new("pivot", None)
    bpy.context.collection.objects.link(piv)
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in obj.children_recursive if o.type == "MESH" for c in o.bound_box]
    cx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    cy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    piv.location = (cx, cy, 0)
    obj.parent = piv
    obj.location.x -= cx
    obj.location.y -= cy
    for f, a in ((f0, a0), (f1, a1)):
        piv.rotation_euler = (0, 0, math.radians(a))
        piv.keyframe_insert("rotation_euler", frame=f)
    linear(piv)
    return piv


def linear(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return
    try:
        curves = ad.action.fcurves
    except AttributeError:
        curves = [c for layer in ad.action.layers for s in layer.strips for cb in s.channelbags for c in cb.fcurves]
    for fc in curves:
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"


def shot_spline(irc):
    """Macro: the drum's splined shaft slides into the IRC's hollow spline output."""
    H = build_hoist(irc)
    world("industrial_workshop_foundry.exr", 0.9, rot=2.2)
    sc = bpy.context.scene
    floor(plain("shop floor", (60, 62, 64), 0.6))
    drum = H["drum"]
    y_end = drum.location.y
    # start pulled back 0.35 m, slide in, settle
    for f, dy in ((0, 0.30), (16, 0.30), (66, 0.0), (95, 0.0)):
        drum.location.y = y_end + dy
        drum.keyframe_insert("location", frame=f)
    for o in [x for x in bpy.data.objects if x.name.startswith(("pedestal", "bearing housing"))]:
        o.hide_render = True
    out = IRC_OUT
    cam, tgt = camera((out.x - 1.30, out.y + 0.18, out.z + 0.40), (out.x, out.y + 0.04, out.z + 0.06), lens=50, fstop=5.6)
    area((out.x - 0.5, out.y - 0.3, out.z + 0.9), (out.x, out.y, out.z), 45, 0.8)
    area((out.x + 0.5, out.y + 0.6, out.z + 0.3), (out.x, out.y, out.z), 60, 0.5, (0.8, 0.9, 1.0))
    sc.frame_start, sc.frame_end = 0, 95
    render_setup(exposure=0.1)


def shot_hoist(irc, wide=False):
    """The whole hoist at work: motor turns, drum winds the rope, the load rises."""
    H = build_hoist(irc)
    world("industrial_workshop_foundry.exr", 1.0, rot=0.6)
    sc = bpy.context.scene
    drum, DR, DL, y0 = H["drum"], H["DR"], H["DL"], H["y0"]
    out = IRC_OUT
    # rope falls: two ropes leave the drum at its front side and go down to the hook block
    z_top = out.z
    xr = out.x - DR                                   # ropes leave the drum on the -X side
    fall_y = (y0 + 0.25, y0 + DL - 0.25)
    block_y = (fall_y[0] + fall_y[1]) / 2
    start_drop = 2.6
    blk = build_hook_block(Vector((xr + 0.0, block_y, z_top - start_drop)), H)
    blk.rotation_euler = (0, 0, math.radians(90))
    ropes = []
    for fy in fall_y:
        r = cyl(0.009, 1.0, MAT["rope"], axis="Z", verts=12, name="rope fall")
        ropes.append((r, fy))
    nfr = 144
    lift = 0.55                                        # m the load rises during the shot
    turns = lift * 2 / (TAU * DR)                      # 2 falls: rope speed = 2 × hook speed
    for f in (0, nfr - 1):
        k = f / (nfr - 1)
        drum.rotation_euler = (0, -TAU * turns * k, 0)
        drum.keyframe_insert("rotation_euler", frame=f)
        if H["coupling"]:
            H["coupling"].rotation_euler = (0, TAU * turns * k * 18.0, 0)     # coupling turns at motor speed
            H["coupling"].keyframe_insert("rotation_euler", frame=f)
        blk.location.z = z_top - start_drop + lift * k
        blk.keyframe_insert("location", frame=f)
        for r, fy in ropes:
            top = Vector((xr, fy, z_top))
            bot = Vector((xr, block_y + (fy - block_y) * 0.45, blk.location.z + 0.02))
            r.location = (top + bot) / 2
            r.scale = (1, 1, (top - bot).length)
            r.rotation_euler = (bot - top).to_track_quat("-Z", "Y").to_euler()
            r.keyframe_insert("location", frame=f)
            r.keyframe_insert("scale", frame=f)
            r.keyframe_insert("rotation_euler", frame=f)
    for o in (drum, H["coupling"], blk, *[r for r, _ in ropes]):
        if o:
            linear(o)
    if wide:
        cam, tgt = camera((-3.6, -2.9, -2.6), (out.x - 0.1, out.y + 0.45, -1.25), lens=30, fstop=8)
    else:
        cam, tgt = camera((-1.55, -1.45, -0.50), (out.x - 0.02, out.y + 0.14, 0.30), lens=32, fstop=5.6)
        cam.keyframe_insert("location", frame=0)
        cam.location = (-1.75, -1.00, -0.58)
        cam.keyframe_insert("location", frame=nfr - 1)
        linear(cam)
    area((-1.5, -1.0, 2.5), (out.x, out.y + 0.4, 0.3), 380, 1.5)
    area((1.5, 2.5, 1.5), (out.x, out.y + 0.4, 0.3), 220, 1.0, (0.8, 0.88, 1.0))
    sc.frame_start, sc.frame_end = 0, nfr - 1
    render_setup(exposure=0.0)


def shot_closeup(irc):
    """Slow push along the gloss paint and nameplate (realism shot)."""
    world("machine_shop_02.exr", 1.0, rot=0.3)
    floor(plain("shop floor", (70, 72, 74), 0.55))
    area((-1.2, -1.2, 1.6), (0, 0, 0.5), 200, 1.0)
    cam, tgt = camera((-0.95, -0.55, 0.70), (-0.2, -0.05, 0.42), lens=85, fstop=2.2)
    cam.keyframe_insert("location", frame=0)
    cam.location = (-0.85, -0.25, 0.62)
    cam.keyframe_insert("location", frame=95)
    linear(cam)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, 95
    render_setup(exposure=0.0)


def shot_lineup(_irc):
    """All IRC sizes that i-Guide serves complete, side by side on the studio sweep (one wide still)."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    cyclorama()
    world("studio_small_09.exr", 0.9, rot=1.2)
    x = 0.0
    sizes = ["IRC_63", "IRC_73", "IRC_83", "IRC_93", "IRC_123", "IRC_143"]
    marks = []
    for n in sizes:
        r = build_irc(n, details=False)
        r.rotation_euler = (math.radians(90), 0, math.radians(-28))
        bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in r.children if o.type == "MESH" for c in o.bound_box]
        w = max(p.x for p in pts) - min(p.x for p in pts)
        r.location.x += x - min(p.x for p in pts)
        r.location.y -= (min(p.y for p in pts) + max(p.y for p in pts)) / 2
        marks.append((n, x + w / 2))
        x += w + 0.18
    for o in bpy.data.objects:
        if o.name == "cyclorama":
            o.location.x = x / 2
            o.scale.x = 3
    import json
    json.dump({"marks": marks, "width": x}, open(os.path.join(ROOT, "render", "lineup.json"), "w"))
    mid = x / 2
    area((mid - 2.5, -3.5, 3.5), (mid, 0, 0.4), 2400, 4.0)
    area((mid + 4.0, -1.5, 1.6), (mid, 0, 0.4), 700, 4.0)
    area((mid, 2.5, 3.0), (mid, 0, 0.6), 900, 3.0)
    cam, tgt = camera((mid, -6.2, 1.25), (mid, 0, 0.50), lens=50)
    sc = bpy.context.scene
    sc.frame_start = sc.frame_end = 0
    render_setup(exposure=float(arg("--exposure", -1.45)))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats()
    irc = build_irc()
    {"dark": shot_dark, "studio": shot_studio, "spline": shot_spline, "hoist": shot_hoist,
     "hoistwide": lambda i: shot_hoist(i, wide=True), "closeup": shot_closeup, "lineup": shot_lineup}[SHOT](irc)
    sc = bpy.context.scene
    outdir = os.path.join(ROOT, "render", SHOT)
    os.makedirs(outdir, exist_ok=True)
    if "--still" in A:
        f = int(arg("--still", 0))
        sc.frame_set(f)
        sc.render.filepath = os.path.join(ROOT, "render", f"{SHOT}_still_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print("still", sc.render.filepath)
        return
    fr = arg("--frames", f"{sc.frame_start}-{sc.frame_end}")
    a, b = (int(v) for v in fr.split("-"))
    step = int(arg("--step", 1))
    for f in range(a, b + 1, step):
        p = os.path.join(outdir, f"{f:04d}.png")
        if os.path.exists(p):
            continue
        sc.frame_set(f)
        sc.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print("frame", f, flush=True)


if __name__ == "__main__":
    main()
