# i.Mak "golden hour" hero scene — fully procedural, rendered with Cycles (bpy module).
# Usage: python scene.py --product irnx --res 640x360 --samples 24 --out out/test   (needs: pip install bpy numpy)
import bpy, bmesh, math, os, argparse, time
import numpy as np
from mathutils import Vector, Matrix, noise

ROOT = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--product', default='irnx')
ap.add_argument('--res', default='640x360')
ap.add_argument('--samples', type=int, default=24)
ap.add_argument('--out', default=os.path.join(ROOT, 'out', 'test'))
ap.add_argument('--hdri', default='the_sky_is_on_fire_4k.hdr')
ap.add_argument('--sun_az', type=float, default=5.5)      # degrees right of camera forward
ap.add_argument('--exposure', type=float, default=-2.4)
ap.add_argument('--fstop', type=float, default=2.8)
ap.add_argument('--lens', type=float, default=60.0)
ap.add_argument('--cam_z', type=float, default=1.60)
ap.add_argument('--aim_z', type=float, default=1.47)
ap.add_argument('--emit', type=float, default=0.85)
ap.add_argument('--fill', type=float, default=2600.0)
ap.add_argument('--border', default='')
ap.add_argument('--fit', default='AUTO')
ap.add_argument('--sun_drop', type=float, default=4.0)
ap.add_argument('--passB', type=int, default=1)
ap.add_argument('--density', type=float, default=1.0)
ap.add_argument('--look', default='AgX - Medium High Contrast')
ap.add_argument('--world', type=float, default=1.0)
ap.add_argument('--fog', type=float, default=0.45)
ap.add_argument('--seed', type=int, default=11)
ap.add_argument('--rim', type=int, default=1)
ap.add_argument('--sun', type=float, default=20.0)
ap.add_argument('--sun_el', type=float, default=7.0)
args = ap.parse_args()
T0 = time.time()
rng = np.random.default_rng(args.seed)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'

# ------------------------------------------------------------------ layout constants
Z_TOP = 1.20                      # top of the polished slab
LAY = {'irnx': dict(sx=0.575, ph=0.60, px=0.03, sheafL=((0.10, 0.27), (-0.86, -0.50)), sheafR=((-0.02, 0.31), (0.93, -0.30)), pile=(0.37, -0.27)),
       'irk':  dict(sx=0.720, ph=0.46, px=0.00, sheafL=((-0.36, 0.35), (-0.50, -0.86)), sheafR=((0.33, 0.34), (0.80, -0.60)), pile=(0.53, -0.31))}[args.product]
SX = LAY['sx']
SLAB = (-SX, SX, -0.56, 0.44, 1.105, Z_TOP)
PROD_Y = 0.06
CAM = Vector((0.0, -3.6, args.cam_z))
AIM = Vector((0.0, PROD_Y, args.aim_z))
WS = 1.12                         # global wheat scale (stylised, hero-sized ears)
FOG_LAMBDA = 260.0

# ------------------------------------------------------------------ helpers
def link(ob):
    scene.collection.objects.link(ob); return ob

def mesh_obj(name, V, F, mats=(), midx=None, smooth=True, recalc=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], [tuple(f) for f in F])
    me.update()
    if recalc:
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    if smooth:
        me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    for m in mats:
        me.materials.append(m)
    if midx is not None:
        me.polygons.foreach_set('material_index', midx)
    me.update()
    return link(bpy.data.objects.new(name, me))

def tube(path, radii, sides, cap_end=True):
    verts = []; faces = []; n = len(path); prev_x = None
    for i, p in enumerate(path):
        if i == 0: t = (path[1] - path[0])
        elif i == n - 1: t = (path[-1] - path[-2])
        else: t = (path[i + 1] - path[i - 1])
        t = t.normalized()
        if prev_x is None:
            ref = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
            x = (ref - t * ref.dot(t)).normalized()
        else:
            x = (prev_x - t * prev_x.dot(t)).normalized()
        y = t.cross(x); prev_x = x
        for k in range(sides):
            a = 2 * math.pi * k / sides
            verts.append(p + (x * math.cos(a) + y * math.sin(a)) * radii[i])
    for i in range(n - 1):
        for k in range(sides):
            a = i * sides + k; b = i * sides + (k + 1) % sides
            c = (i + 1) * sides + (k + 1) % sides; d = (i + 1) * sides + k
            faces.append((a, b, c, d))
    if cap_end:
        verts.append(path[-1].copy()); ci = len(verts) - 1
        for k in range(sides):
            faces.append(((n - 1) * sides + k, (n - 1) * sides + (k + 1) % sides, ci))
    return verts, faces

def ellipsoid(c, la, wa, ta, L, Wd, T, segs=6, rings=4):
    verts = [c + la * (L / 2)]; faces = []
    for r in range(1, rings):
        phi = math.pi * r / rings
        for s in range(segs):
            th = 2 * math.pi * s / segs
            verts.append(c + la * (L / 2 * math.cos(phi)) + wa * (Wd / 2 * math.sin(phi) * math.cos(th))
                         + ta * (T / 2 * math.sin(phi) * math.sin(th)))
    verts.append(c - la * (L / 2))
    for s in range(segs):
        faces.append((0, 1 + s, 1 + (s + 1) % segs))
    for r in range(rings - 2):
        for s in range(segs):
            a = 1 + r * segs + s; b = 1 + r * segs + (s + 1) % segs
            cc = 1 + (r + 1) * segs + (s + 1) % segs; d = 1 + (r + 1) * segs + s
            faces.append((a, d, cc, b))
    last = len(verts) - 1; base = 1 + (rings - 2) * segs
    for s in range(segs):
        faces.append((last, base + (s + 1) % segs, base + s))
    return verts, faces

def box(x0, x1, y0, y1, z0, z1):
    V = [Vector((x0, y0, z0)), Vector((x1, y0, z0)), Vector((x1, y1, z0)), Vector((x0, y1, z0)),
         Vector((x0, y0, z1)), Vector((x1, y0, z1)), Vector((x1, y1, z1)), Vector((x0, y1, z1))]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return V, F

class Geo:
    def __init__(self): self.V = []; self.F = []; self.M = []
    def add(self, vs, fs, mi=0):
        off = len(self.V); self.V.extend(vs)
        self.F.extend([tuple(i + off for i in f) for f in fs]); self.M.extend([mi] * len(fs))

# ------------------------------------------------------------------ node helpers
def nodes_of(mat):
    try: mat.use_nodes = True
    except Exception: pass
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    return nt

def N(nt, typ, **kw):
    n = nt.nodes.new(typ)
    for k, v in kw.items(): setattr(n, k, v)
    return n

def ramp(nt, stops):
    n = nt.nodes.new('ShaderNodeValToRGB'); cr = n.color_ramp
    while len(cr.elements) < len(stops): cr.elements.new(0.5)
    for e, (pos, col) in zip(cr.elements, stops):
        e.position = pos; e.color = (col[0], col[1], col[2], 1.0)
    return n

def fog_wrap(nt, shader_socket, haze, amount=1.0):
    """Mix a surface shader toward a warm haze emission with camera distance (aerial perspective)."""
    cam = N(nt, 'ShaderNodeCameraData')
    m1 = N(nt, 'ShaderNodeMath', operation='MULTIPLY'); m1.inputs[1].default_value = -1.0 / FOG_LAMBDA
    nt.links.new(cam.outputs['View Z Depth'], m1.inputs[0])
    ex = N(nt, 'ShaderNodeMath', operation='EXPONENT'); nt.links.new(m1.outputs[0], ex.inputs[0])
    sub = N(nt, 'ShaderNodeMath', operation='SUBTRACT'); sub.inputs[0].default_value = 1.0
    nt.links.new(ex.outputs[0], sub.inputs[1])
    mul = N(nt, 'ShaderNodeMath', operation='MULTIPLY', use_clamp=True); mul.inputs[1].default_value = amount * args.fog
    nt.links.new(sub.outputs[0], mul.inputs[0])
    em = N(nt, 'ShaderNodeEmission'); em.inputs['Color'].default_value = (haze[0], haze[1], haze[2], 1)
    em.inputs['Strength'].default_value = 1.0
    mix = N(nt, 'ShaderNodeMixShader'); nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(shader_socket, mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    return mix.outputs[0]

def out_surface(nt, sock):
    o = N(nt, 'ShaderNodeOutputMaterial'); nt.links.new(sock, o.inputs['Surface']); return o

# ------------------------------------------------------------------ world (real captured sunset sky)
hdr_path = os.path.join(ROOT, 'hdri', args.hdri)
img = bpy.data.images.load(hdr_path)
w, h = img.size
px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)[:, :, :3]
lum = px @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
bs = 8
lb = lum[:h // bs * bs, :w // bs * bs].reshape(h // bs, bs, w // bs, bs).mean(axis=(1, 3))
iy, ix = np.unravel_index(np.argmax(lb), lb.shape)
u_s = (ix + 0.5) * bs / w; v_s = (iy + 0.5) * bs / h
sun_el = (v_s - 0.5) * 180.0
psi = (u_s - 0.5) * 2 * math.pi
# haze colour = sky just above the horizon around the sun (sun disc excluded)
band = px[int(h * 0.505):int(h * 0.53), :, :]
cols = (np.arange(w) + 0.5) / w
dsun = np.minimum(np.abs(cols - u_s), 1 - np.abs(cols - u_s)) * 360.0
sel = band[:, (dsun > 6) & (dsun < 40), :].reshape(-1, 3)
HAZE = np.median(sel, axis=0) * args.world
HAZE = HAZE * 0.72 + HAZE.mean() * 0.28          # slightly desaturated aerial haze
print(f'[hdri] sun u={u_s:.4f} el={sun_el:.2f}deg  haze={HAZE.round(3)}  max={lum.max():.1f}')
del px, lum

world = bpy.data.worlds.new('W'); scene.world = world
try: world.use_nodes = True
except Exception: pass
wt = world.node_tree
for n in list(wt.nodes): wt.nodes.remove(n)
tc = N(wt, 'ShaderNodeTexCoord'); mp = N(wt, 'ShaderNodeMapping')
alpha = math.radians(args.sun_az)
mp.inputs['Rotation'].default_value = (math.radians(args.sun_drop), 0, -math.pi / 2 - psi + alpha)
env = N(wt, 'ShaderNodeTexEnvironment'); env.image = img
bg = N(wt, 'ShaderNodeBackground'); bg.inputs['Strength'].default_value = args.world
wo = N(wt, 'ShaderNodeOutputWorld')
wt.links.new(tc.outputs['Generated'], mp.inputs['Vector']); wt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
wt.links.new(env.outputs['Color'], bg.inputs['Color']); wt.links.new(bg.outputs[0], wo.inputs['Surface'])

# ------------------------------------------------------------------ materials
def wheat_mat(name, c_lo, c_mid, c_hi, transl, rough=0.55):
    m = bpy.data.materials.new(name); nt = nodes_of(m)
    oi = N(nt, 'ShaderNodeObjectInfo')
    rp = ramp(nt, [(0.0, c_lo), (0.5, c_mid), (1.0, c_hi)]); nt.links.new(oi.outputs['Random'], rp.inputs[0])
    pb = N(nt, 'ShaderNodeBsdfPrincipled'); pb.inputs['Roughness'].default_value = rough
    pb.inputs['Specular IOR Level'].default_value = 0.35
    nt.links.new(rp.outputs['Color'], pb.inputs['Base Color'])
    tr = N(nt, 'ShaderNodeBsdfTranslucent'); nt.links.new(rp.outputs['Color'], tr.inputs['Color'])
    mx = N(nt, 'ShaderNodeMixShader'); mx.inputs[0].default_value = transl
    nt.links.new(pb.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    out_surface(nt, mx.outputs[0]); return m

M_STEM = wheat_mat('stem', (0.50, 0.38, 0.13), (0.62, 0.47, 0.17), (0.70, 0.55, 0.22), 0.22)
M_EAR = wheat_mat('ear', (0.62, 0.40, 0.11), (0.74, 0.50, 0.15), (0.82, 0.58, 0.20), 0.34)
M_AWN = wheat_mat('awn', (0.74, 0.54, 0.20), (0.84, 0.64, 0.27), (0.90, 0.72, 0.34), 0.50, rough=0.4)
M_LEAF = wheat_mat('leaf', (0.52, 0.40, 0.14), (0.63, 0.49, 0.18), (0.70, 0.56, 0.23), 0.45)
M_GRAIN = wheat_mat('grain', (0.66, 0.43, 0.15), (0.77, 0.52, 0.20), (0.84, 0.61, 0.27), 0.10, rough=0.45)
WMATS = [M_STEM, M_EAR, M_AWN, M_LEAF]

def simple_mat(name, color, rough=0.6, metallic=0.0, fog=0.0, sheen=0.0, bump=None, spec=0.5):
    m = bpy.data.materials.new(name); nt = nodes_of(m)
    pb = N(nt, 'ShaderNodeBsdfPrincipled')
    pb.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1)
    pb.inputs['Roughness'].default_value = rough; pb.inputs['Metallic'].default_value = metallic
    pb.inputs['Specular IOR Level'].default_value = spec
    if sheen:
        pb.inputs['Sheen Weight'].default_value = sheen; pb.inputs['Sheen Roughness'].default_value = 0.5
        pb.inputs['Sheen Tint'].default_value = (1.0, 0.78, 0.45, 1)
    if bump:
        tcn = N(nt, 'ShaderNodeTexCoord')
        if bump[0] == 'noise':
            tx = N(nt, 'ShaderNodeTexNoise'); tx.inputs['Scale'].default_value = bump[1]; tx.inputs['Detail'].default_value = 6
        else:
            tx = N(nt, 'ShaderNodeTexWave', wave_type='BANDS', bands_direction='Z'); tx.inputs['Scale'].default_value = bump[1]
        nt.links.new(tcn.outputs['Object'], tx.inputs['Vector'])
        bp = N(nt, 'ShaderNodeBump'); bp.inputs['Strength'].default_value = bump[2]
        nt.links.new(tx.outputs[0], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], pb.inputs['Normal'])
    sock = pb.outputs[0]
    if fog: sock = fog_wrap(nt, sock, HAZE, fog)
    out_surface(nt, sock); return m

M_SOIL = simple_mat('soil', (0.035, 0.024, 0.014), 0.95, fog=1.0)
M_ROCK = simple_mat('rock', (0.030, 0.027, 0.025), 0.86, bump=('noise', 14.0, 0.9))
M_STEEL = simple_mat('steel', (0.58, 0.60, 0.63), 0.48, metallic=1.0, fog=1.0, bump=('wave', 3.3, 0.25))
M_STEEL2 = simple_mat('steel2', (0.20, 0.21, 0.23), 0.62, metallic=1.0, fog=1.0)
M_TREE = simple_mat('tree', (0.012, 0.018, 0.010), 0.95, fog=1.0)

def canopy_mat():
    m = bpy.data.materials.new('canopy'); nt = nodes_of(m)
    tcn = N(nt, 'ShaderNodeTexCoord'); nz = N(nt, 'ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 0.35; nz.inputs['Detail'].default_value = 8
    nt.links.new(tcn.outputs['Object'], nz.inputs['Vector'])
    rp = ramp(nt, [(0.3, (0.66, 0.44, 0.14)), (0.7, (0.86, 0.62, 0.24))]); nt.links.new(nz.outputs[0], rp.inputs[0])
    pb = N(nt, 'ShaderNodeBsdfPrincipled'); pb.inputs['Roughness'].default_value = 0.9
    pb.inputs['Sheen Weight'].default_value = 0.45; pb.inputs['Sheen Roughness'].default_value = 0.55
    pb.inputs['Sheen Tint'].default_value = (1.0, 0.74, 0.38, 1)
    nt.links.new(rp.outputs['Color'], pb.inputs['Base Color'])
    tr = N(nt, 'ShaderNodeBsdfTranslucent'); nt.links.new(rp.outputs['Color'], tr.inputs['Color'])
    mx = N(nt, 'ShaderNodeMixShader'); mx.inputs[0].default_value = 0.3
    nt.links.new(pb.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    out_surface(nt, fog_wrap(nt, mx.outputs[0], HAZE, 1.0)); return m
M_CANOPY = canopy_mat()

def marble_mat():
    m = bpy.data.materials.new('marble'); nt = nodes_of(m)
    tcn = N(nt, 'ShaderNodeTexCoord')
    wv = N(nt, 'ShaderNodeTexWave', wave_type='BANDS', bands_direction='DIAGONAL')
    wv.inputs['Scale'].default_value = 0.55; wv.inputs['Distortion'].default_value = 14.0
    wv.inputs['Detail'].default_value = 4.0; wv.inputs['Detail Scale'].default_value = 1.4
    nt.links.new(tcn.outputs['Object'], wv.inputs['Vector'])
    rp = ramp(nt, [(0.0, (0.010, 0.009, 0.009)), (0.455, (0.016, 0.014, 0.013)), (0.5, (0.36, 0.29, 0.20)),
                   (0.545, (0.016, 0.014, 0.013)), (1.0, (0.010, 0.009, 0.009))])
    nt.links.new(wv.outputs[0], rp.inputs[0])
    pb = N(nt, 'ShaderNodeBsdfPrincipled'); pb.inputs['Roughness'].default_value = 0.13
    pb.inputs['Coat Weight'].default_value = 0.5; pb.inputs['Coat Roughness'].default_value = 0.04
    nt.links.new(rp.outputs['Color'], pb.inputs['Base Color'])
    out_surface(nt, pb.outputs[0]); return m
M_MARBLE = marble_mat()

# ------------------------------------------------------------------ wheat models
def build_wheat(seed, h=0.86, lean=0.05, droop=0.55, ear_len=0.085, pairs=11, awn=0.075, leaves=2, lod=0):
    r = np.random.default_rng(seed); g = Geo()
    az = r.uniform(0, 2 * math.pi); ld = Vector((math.cos(az), math.sin(az), 0))
    segs = 8 if lod == 0 else 3
    path = [Vector((ld.x * lean * t * t, ld.y * lean * t * t, h * t)) for t in [i / segs for i in range(segs + 1)]]
    rad = [0.0024 * (1 - 0.3 * i / segs) for i in range(segs + 1)]
    g.add(*tube(path, rad, 5 if lod == 0 else 3, cap_end=False), 0)
    t0 = (path[-1] - path[-2]).normalized()
    axis = t0.cross(ld)
    if axis.length < 1e-5: axis = Vector((0, 1, 0))
    axis.normalize()
    n = pairs * 2; steps = n + 1; pts = []; tans = []; p = path[-1].copy()
    for i in range(steps + 1):
        s = i / steps
        td = (Matrix.Rotation(droop * s, 3, axis) @ t0).normalized()
        pts.append(p.copy()); tans.append(td); p = p + td * (ear_len / steps)
    if lod == 0:
        g.add(*tube(pts, [0.0016] * len(pts), 4, cap_end=True), 0)
        for i in range(n):
            j = i + 1; td = tans[j]; c0 = pts[j]
            side = 1 if i % 2 == 0 else -1
            wv = axis * side; front = td.cross(axis).normalized()
            sc = 0.72 + 0.30 * math.sin(math.pi * (i + 0.5) / n)
            tilt = math.radians(r.uniform(22, 32))
            la = (td * math.cos(tilt) + wv * math.sin(tilt)).normalized()
            wa = (wv * math.cos(tilt) - td * math.sin(tilt)).normalized()
            L = 0.0128 * sc; Wd = 0.0060 * sc; T = 0.0054 * sc
            c = c0 + wv * 0.0034 * sc + la * (L * 0.30)
            g.add(*ellipsoid(c, la, wa, front, L, Wd, T, 6, 4), 1)
            a0 = c + la * (L * 0.46); ang = math.radians(r.uniform(8, 22)); fr = r.uniform(-0.35, 0.35)
            d0 = (td * math.cos(ang) + wv * math.sin(ang) + front * fr * math.sin(ang)).normalized()
            Lw = awn * r.uniform(0.75, 1.2) * (0.8 + 0.4 * sc)
            apth = [a0, a0 + d0 * (Lw * 0.34), a0 + (d0 + wv * 0.06) * (Lw * 0.68), a0 + (d0 + wv * 0.14) * Lw]
            g.add(*tube(apth, [0.00075, 0.0006, 0.00045, 0.00022], 3, cap_end=True), 2)
            if i % 2 == 0 and 1 < i < n - 2:
                for sgn in (1, -1):
                    c2 = c0 + front * sgn * 0.0030 * sc + td * (L * 0.25)
                    la2 = (td * 0.94 + front * sgn * 0.34).normalized()
                    fa2 = la2.cross(axis).normalized()
                    g.add(*ellipsoid(c2, la2, axis, fa2, L * 0.92, Wd * 0.95, T, 6, 4), 1)
        td = tans[-1]; front = td.cross(axis).normalized()
        g.add(*ellipsoid(pts[-1], td, axis, front, 0.011, 0.005, 0.0045, 6, 4), 1)
        for k in range(3):
            d0 = (td + axis * r.uniform(-0.25, 0.25) + front * r.uniform(-0.25, 0.25)).normalized()
            a0 = pts[-1] + td * 0.004; Lw = awn * r.uniform(0.8, 1.1)
            g.add(*tube([a0, a0 + d0 * Lw * 0.5, a0 + d0 * Lw], [0.0007, 0.0005, 0.00022], 3, cap_end=True), 2)
        for k in range(leaves):
            zl = h * (0.30 + 0.22 * k + r.uniform(-0.04, 0.04)); t = zl / h
            base = Vector((ld.x * lean * t * t, ld.y * lean * t * t, zl))
            a = r.uniform(0, 2 * math.pi); dh = Vector((math.cos(a), math.sin(a), 0)); sd = Vector((-dh.y, dh.x, 0))
            Ll = r.uniform(0.22, 0.34); ns = 7; vs = []; fs = []
            for i in range(ns + 1):
                s = i / ns
                pc = base + dh * (Ll * 0.85 * s) + Vector((0, 0, 1)) * (Ll * (0.62 * s - 0.9 * s * s))
                wdt = 0.0055 * (1 - s) ** 0.7 * (0.5 + min(1.0, s * 6) * 0.5)
                vs += [pc - sd * wdt, pc + sd * wdt]
            for i in range(ns): fs.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
            g.add(vs, fs, 3)
    else:
        mid = pts[len(pts) // 2]; td = tans[len(tans) // 2]; fa = td.cross(axis).normalized()
        g.add(*ellipsoid(mid, td, axis, fa, ear_len * 1.05, 0.016, 0.013, 5, 3), 1)
        for k in range(7):
            s = 0.25 + 0.7 * k / 6; b = pts[int(s * (len(pts) - 1))]; tdk = tans[int(s * (len(tans) - 1))]
            sgn = 1 if k % 2 == 0 else -1
            d0 = (tdk * 0.93 + axis * sgn * 0.30 + fa * r.uniform(-0.2, 0.2)).normalized()
            tip = b + d0 * awn * r.uniform(0.8, 1.15)
            g.add([b + fa * 0.0011, b - fa * 0.0011, tip], [(0, 1, 2)], 2)
    return g

def wheat_object(name, **kw):
    g = build_wheat(**kw)
    return mesh_obj(name, g.V, g.F, WMATS, g.M, smooth=True, recalc=True)

NEAR = [wheat_object('w_near0', seed=1, h=0.80, lean=0.06, droop=0.75),
        wheat_object('w_near1', seed=2, h=0.86, lean=0.04, droop=0.45),
        wheat_object('w_near2', seed=3, h=0.90, lean=0.08, droop=0.95, pairs=12)]
FAR = [wheat_object('w_far0', seed=4, h=0.82, lean=0.06, droop=0.7, lod=1),
       wheat_object('w_far1', seed=5, h=0.90, lean=0.05, droop=0.5, lod=1)]
CUT = [wheat_object('w_cut0', seed=6, h=0.36, lean=0.004, droop=0.10, leaves=0),
       wheat_object('w_cut1', seed=7, h=0.33, lean=0.006, droop=0.16, leaves=0, pairs=12)]
gk = Geo(); gk.add(*ellipsoid(Vector((0, 0, 0)), Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)),
                              0.0100, 0.0048, 0.0040, 8, 5), 0)
KERNEL = mesh_obj('kernel', gk.V, gk.F, [M_GRAIN], [0] * len(gk.F), smooth=True, recalc=True)

# ------------------------------------------------------------------ face-instancing scatter
def instancer(name, frames, child):
    if not frames: return None
    V = []; F = []
    for i, (c, ex, ey, s) in enumerate(frames):
        hx = ex * (s / 2); hy = ey * (s / 2)
        V += [c - hx - hy, c + hx - hy, c + hx + hy, c - hx + hy]; F.append((4 * i, 4 * i + 1, 4 * i + 2, 4 * i + 3))
    ob = mesh_obj(name, V, F, smooth=False)
    ob.instance_type = 'FACES'; ob.use_instance_faces_scale = True; ob.instance_faces_scale = 1.0
    ob.show_instancer_for_render = False; ob.show_instancer_for_viewport = False
    child.parent = ob
    return ob

def frame_from_axis(c, ez, s, roll=None):
    ez = ez.normalized(); roll = rng.uniform(0, 2 * math.pi) if roll is None else roll
    ref = Vector((0, 0, 1)) if abs(ez.z) < 0.9 else Vector((1, 0, 0))
    e1 = (ref - ez * ref.dot(ez)).normalized(); e2 = ez.cross(e1)
    ex = e1 * math.cos(roll) + e2 * math.sin(roll); ey = ez.cross(ex)
    return (c, ex, ey, s)

def upright(x, y, s, tilt=0.10, wind=(0.05, 0.0), z=0.0):
    ez = Vector((wind[0] + rng.normal(0, tilt * 0.5), wind[1] + rng.normal(0, tilt * 0.5), 1.0))
    return frame_from_axis(Vector((x, y, z)), ez, s)

def in_podium(x, y):
    return (-(SX + 0.045) < x < (SX + 0.045)) and (-0.62 < y < 0.52)

def band(d0, d1, dens, half_deg=20.0):
    tanh_ = math.tan(math.radians(half_deg)); out = []
    n = int(tanh_ * (d1 * d1 - d0 * d0) * dens * args.density)
    for _ in range(n):
        d = math.sqrt(rng.uniform(d0 * d0, d1 * d1)); x = rng.uniform(-1, 1) * tanh_ * d; y = CAM.y + d
        if not in_podium(x, y): out.append((x, y))
    return out

near_frames = [[] for _ in NEAR]; far_frames = [[] for _ in FAR]
def stalk_scale(x, y):
    sc = rng.uniform(0.90, 1.10) * WS
    if abs(x) < SX + 0.23 and -2.9 < y < -0.5:            # in front of the slab: keep low so its face stays visible
        sc = min(sc, rng.uniform(1.02, 1.24))
    elif SX + 0.17 < abs(x) < SX + 1.0 and -0.9 < y < 1.0:     # flanks: slightly taller, nests the podium into the field
        sc *= rng.uniform(1.04, 1.20)
    return sc
for (x, y) in band(0.95, 6.0, 150) + band(6.0, 10.0, 85):
    near_frames[rng.integers(0, len(NEAR))].append(upright(x, y, stalk_scale(x, y)))
for (x, y) in band(10.0, 20.0, 34) + band(20.0, 37.0, 12) + band(37.0, 90.0, 3.6):
    far_frames[rng.integers(0, len(FAR))].append(upright(x, y, rng.uniform(0.90, 1.12) * WS))
# hero foreground stalks (big soft bokeh framing the bottom corners)
# (x as a fraction of the half frame width at that distance, distance from camera, ear-top height)
hero = [(-0.93, 1.00, 1.50), (-0.86, 1.22, 1.45), (-0.97, 1.40, 1.57), (-0.90, 1.66, 1.50), (-1.00, 1.98, 1.47),
        (-0.80, 1.52, 1.40), (0.92, 0.98, 1.49), (0.87, 1.24, 1.44), (0.98, 1.44, 1.58), (0.90, 1.70, 1.49),
        (1.01, 2.02, 1.46), (0.81, 1.56, 1.39)]
HW = math.tan(math.atan(18.0 / args.lens))
hero_frames = []
for (fx, d, top) in hero:
    lean_out = 0.05 if fx > 0 else -0.05
    hero_frames.append(upright(fx * 1.04 * HW * d, CAM.y + d, (top - 0.09) / 0.93, tilt=0.03, wind=(lean_out, 0.0)))
HERO = wheat_object('w_hero', seed=21, h=0.86, lean=0.03, droop=0.6, leaves=0, pairs=12)
instancer('inst_hero', hero_frames, HERO)
for i, fr in enumerate(near_frames): instancer(f'inst_near{i}', fr, NEAR[i])
for i, fr in enumerate(far_frames): instancer(f'inst_far{i}', fr, FAR[i])
n_wheat = sum(len(f) for f in near_frames) + sum(len(f) for f in far_frames)

# wheat sheaves lying on the slab
cut_frames = [[] for _ in CUT]
def sheaf(n, base_xy, dir_xy, spread_deg, scale):
    for _ in range(n):
        a = math.atan2(dir_xy[1], dir_xy[0]) + math.radians(rng.normal(0, spread_deg * 0.5))
        dz = rng.uniform(0.004, 0.035)
        D = Vector((math.cos(a), math.sin(a), dz))
        b = Vector((base_xy[0] + rng.normal(0, 0.035), base_xy[1] + rng.normal(0, 0.035),
                    Z_TOP + 0.009 + rng.uniform(0, 0.022)))
        cut_frames[rng.integers(0, len(CUT))].append(frame_from_axis(b, D, scale * rng.uniform(0.92, 1.08)))
sheaf(26, LAY['sheafL'][0], LAY['sheafL'][1], 30, 1.45)
sheaf(9, LAY['sheafR'][0], LAY['sheafR'][1], 20, 1.40)
for i, fr in enumerate(cut_frames): instancer(f'inst_cut{i}', fr, CUT[i])

# grain pile + scattered kernels on the slab
PC = Vector((LAY['pile'][0], LAY['pile'][1], Z_TOP)); PR = 0.15; PH = 0.058
def pile_h(r): return PH * max(0.0, 1 - (r / PR) ** 2) ** 0.9
gm = Geo(); rings_ = 9; segs_ = 28; vs = [PC + Vector((0, 0, PH * 0.96))]
for i in range(1, rings_ + 1):
    r = PR * i / rings_
    for s in range(segs_):
        th = 2 * math.pi * s / segs_
        vs.append(PC + Vector((r * math.cos(th), r * math.sin(th), max(0.0005, pile_h(r) * 0.94))))
fs = [(0, 1 + s, 1 + (s + 1) % segs_) for s in range(segs_)]
for i in range(rings_ - 1):
    for s in range(segs_):
        a = 1 + i * segs_ + s; b = 1 + i * segs_ + (s + 1) % segs_
        fs.append((a, a + segs_, b + segs_, b))
gm.add(vs, fs, 0)
mesh_obj('pile', gm.V, gm.F, [M_GRAIN], [0] * len(gm.F), smooth=True)
kf = []
for _ in range(int(3000 * args.density)):
    r = PR * math.sqrt(rng.uniform(0, 1)); th = rng.uniform(0, 2 * math.pi)
    hgt = pile_h(r); dr = 1e-3
    slope = (pile_h(min(PR, r + dr)) - hgt) / dr
    nrm = Vector((-slope * math.cos(th), -slope * math.sin(th), 1.0)).normalized()
    nrm = (nrm + Vector((rng.normal(0, 0.35), rng.normal(0, 0.35), rng.normal(0, 0.15)))).normalized()
    c = PC + Vector((r * math.cos(th), r * math.sin(th), hgt + 0.0025))
    kf.append(frame_from_axis(c, nrm, 1.35 * rng.uniform(0.85, 1.12)))
for _ in range(190):
    r = PR * (1.0 + abs(rng.normal(0, 0.55))); th = rng.uniform(0, 2 * math.pi)
    x = PC.x + r * math.cos(th); y = PC.y + r * math.sin(th)
    if SLAB[0] + 0.02 < x < SLAB[1] - 0.02 and SLAB[2] + 0.02 < y < SLAB[3] - 0.02:
        nrm = Vector((rng.normal(0, 0.08), rng.normal(0, 0.08), 1.0))
        kf.append(frame_from_axis(Vector((x, y, Z_TOP + 0.0028)), nrm, 1.35 * rng.uniform(0.85, 1.12)))
instancer('inst_kernel', kf, KERNEL)

# ------------------------------------------------------------------ podium (polished slab on rough rock)
def bevel_box(name, b, bevel, mat, segs=3):
    V, F = box(*b); me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in V], [], F); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=segs, profile=0.5, affect='EDGES')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    try: me.set_sharp_from_angle(angle=math.radians(35))
    except Exception: pass
    me.materials.append(mat); me.update()
    return link(bpy.data.objects.new(name, me))
bevel_box('slab', SLAB, 0.012, M_MARBLE)

V, F = box(-(SX - 0.075), SX - 0.075, -0.47, 0.36, -0.05, 1.112)
me = bpy.data.meshes.new('rock'); me.from_pydata([tuple(v) for v in V], [], F); me.update()
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=7, use_grid_fill=True)
for v in bm.verts:
    if v.co.z < 1.09:
        d = noise.fractal(v.co * 3.1, 1.0, 2.0, 4) * 0.035 + noise.noise(v.co * 11.0) * 0.012
        v.co.x += d * (1 if v.co.x > 0 else -1) + noise.noise(v.co * 5.0 + Vector((9, 0, 0))) * 0.02
        v.co.y += d * (1 if v.co.y > 0 else -1) + noise.noise(v.co * 5.0 + Vector((0, 7, 0))) * 0.02
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
me.polygons.foreach_set('use_smooth', [True] * len(me.polygons)); me.materials.append(M_ROCK)
link(bpy.data.objects.new('rock', me))

# ------------------------------------------------------------------ product billboard
tex_name = f'{args.product}_rim.png' if args.rim else f'{args.product}.png'
pimg = bpy.data.images.load(os.path.join(ROOT, 'tex', tex_name))
try: pimg.alpha_mode = 'STRAIGHT'
except Exception: pass
aspect = pimg.size[0] / pimg.size[1]
PH_ = LAY['ph']; PW_ = PH_ * aspect
PX_ = LAY['px']
z0 = Z_TOP - 0.003
bbV = [Vector((PX_ - PW_ / 2, PROD_Y, z0)), Vector((PX_ + PW_ / 2, PROD_Y, z0)),
       Vector((PX_ + PW_ / 2, PROD_Y, z0 + PH_)), Vector((PX_ - PW_ / 2, PROD_Y, z0 + PH_))]

def product_mat(name, clean=False):
    m = bpy.data.materials.new(name); nt = nodes_of(m)
    ti = N(nt, 'ShaderNodeTexImage'); ti.image = pimg; ti.extension = 'CLIP'; ti.interpolation = 'Cubic'
    if clean:
        em = N(nt, 'ShaderNodeEmission'); nt.links.new(ti.outputs['Color'], em.inputs['Color'])
        tr = N(nt, 'ShaderNodeBsdfTransparent'); mx = N(nt, 'ShaderNodeMixShader')
        nt.links.new(ti.outputs['Alpha'], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2]); out_surface(nt, mx.outputs[0])
    else:
        pb = N(nt, 'ShaderNodeBsdfPrincipled'); pb.inputs['Roughness'].default_value = 0.6
        pb.inputs['Specular IOR Level'].default_value = 0.0
        nt.links.new(ti.outputs['Color'], pb.inputs['Base Color']); nt.links.new(ti.outputs['Color'], pb.inputs['Emission Color'])
        pb.inputs['Emission Strength'].default_value = args.emit * (2.0 ** (-args.exposure))
        nt.links.new(ti.outputs['Alpha'], pb.inputs['Alpha']); out_surface(nt, pb.outputs[0])
    return m
M_PROD = product_mat('product'); M_PROD_CLEAN = product_mat('product_clean', clean=True)
BB = mesh_obj('billboard', bbV, [(0, 1, 2, 3)], [M_PROD], [0], smooth=False)
uvl = BB.data.uv_layers.new(name='UVMap')
for li, uv in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uvl.data[li].uv = uv

# ------------------------------------------------------------------ far field: canopy, treeline, silos
CY0 = CAM.y + 70.0
mesh_obj('soil', *[[Vector((-2500, -60, 0)), Vector((2500, -60, 0)), Vector((2500, 2500, 0)), Vector((-2500, 2500, 0))],
                   [(0, 1, 2, 3)]], mats=[M_SOIL], midx=[0], smooth=False)
mesh_obj('canopy', *[[Vector((-2500, CY0, 1.0)), Vector((2500, CY0, 1.0)), Vector((2500, 2500, 1.0)), Vector((-2500, 2500, 1.0))],
                     [(0, 1, 2, 3)]], mats=[M_CANOPY], midx=[0], smooth=False)
def treeline(y, hmin, hmax, seed):
    V = []; F = []; nseg = 220
    for i in range(nseg + 1):
        x = -700 + 1400 * i / nseg
        hh = hmin + (hmax - hmin) * (0.5 + 0.5 * noise.noise(Vector((x * 0.012 + seed, seed, 0)))) \
             + 2.2 * noise.noise(Vector((x * 0.07 + seed, 3.0, 0)))
        V += [Vector((x, y, 0.5)), Vector((x, y, max(1.5, hh)))]
    for i in range(nseg): F.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    mesh_obj(f'trees{seed}', V, F, [M_TREE], [0] * len(F), smooth=False)
treeline(560, 6, 13, 1); treeline(900, 5, 11, 2)

def cylinder(g, cx, cy, r0, r1, z0_, z1_, segs, mi=0, cap=True):
    vs = []
    for s in range(segs):
        th = 2 * math.pi * s / segs
        vs.append(Vector((cx + r0 * math.cos(th), cy + r0 * math.sin(th), z0_)))
    for s in range(segs):
        th = 2 * math.pi * s / segs
        vs.append(Vector((cx + r1 * math.cos(th), cy + r1 * math.sin(th), z1_)))
    fs = [(s, (s + 1) % segs, segs + (s + 1) % segs, segs + s) for s in range(segs)]
    if cap:
        vs.append(Vector((cx, cy, z1_))); ci = len(vs) - 1
        fs += [(segs + s, segs + (s + 1) % segs, ci) for s in range(segs)]
    g.add(vs, fs, mi)

def silo_row(xc, ys, R=5.0, Hw=11.0, Hr=2.7, leg=False):
    g = Geo(); g2 = Geo()
    for y in ys:
        cylinder(g, xc, y, R, R, 0, Hw, 72, cap=False)
        cylinder(g2, xc, y, R + 0.12, 0.55, Hw, Hw + Hr, 40, cap=False)        # ribbed cone roof (flat shaded)
        cylinder(g2, xc, y, 0.55, 0.55, Hw + Hr, Hw + Hr + 0.5, 12)
        for k in range(36):                                                      # vertical stiffeners
            th = 2 * math.pi * k / 36; px_ = xc + (R + 0.05) * math.cos(th); py_ = y + (R + 0.05) * math.sin(th)
            g2.add(*box(px_ - 0.05, px_ + 0.05, py_ - 0.05, py_ + 0.05, 0, Hw))
        g2.add(*box(xc - 0.07, xc + 0.07, y - 0.07, y + 0.07, Hw + Hr, Hw + Hr + 1.3))
    zg = Hw + Hr + 1.3
    g2.add(*box(xc - 0.6, xc + 0.6, ys[0] - 2, ys[-1] + 2, zg, zg + 1.15))       # conveyor gallery over the roofs
    if leg:
        sx = 1 if xc < 0 else -1; lx = xc + sx * (R + 1.6); ly = ys[0] + 6.5
        g2.add(*box(lx - 0.7, lx + 0.7, ly - 0.7, ly + 0.7, 0, zg + 5.5))        # bucket-elevator leg
        g2.add(*box(lx - 1.3, lx + 1.3, ly - 1.3, ly + 1.3, zg + 5.5, zg + 7.9)) # head house
        a = Vector((lx, ly, zg + 5.6)); b = Vector((xc, ys[1], Hw + Hr + 0.4))
        g2.add(*tube([a, b], [0.28, 0.28], 10, cap_end=False))                   # spout
    mesh_obj(f'silo_wall{xc}', g.V, g.F, [M_STEEL], [0] * len(g.F), smooth=True)
    mesh_obj(f'silo_parts{xc}', g2.V, g2.F, [M_STEEL2], [0] * len(g2.F), smooth=False)
YS = [67 + 13 * i for i in range(6)]
silo_row(-24.0, YS, leg=True); silo_row(24.0, YS, leg=False)

# ------------------------------------------------------------------ lights, camera
fl = bpy.data.lights.new('fill', 'AREA'); fl.energy = args.fill; fl.size = 2.4; fl.color = (1.0, 0.86, 0.70)
flo = link(bpy.data.objects.new('fill', fl)); flo.location = (-2.6, -3.3, 2.7)
flo.rotation_euler = (Vector((0, -0.2, 1.25)) - Vector(flo.location)).to_track_quat('-Z', 'Y').to_euler()
flo.visible_camera = False

if args.sun > 0:
    sl = bpy.data.lights.new('sun', 'SUN'); sl.energy = args.sun; sl.color = (1.0, 0.56, 0.24); sl.angle = math.radians(3.0)
    slo = link(bpy.data.objects.new('sun', sl))
    a_ = math.radians(args.sun_az); e_ = math.radians(args.sun_el)
    Dsun = Vector((math.sin(a_) * math.cos(e_), math.cos(a_) * math.cos(e_), math.sin(e_)))
    slo.rotation_euler = Dsun.to_track_quat('Z', 'Y').to_euler()

cam = bpy.data.cameras.new('cam'); cam.lens = args.lens; cam.sensor_width = 36.0
cam.clip_start = 0.05; cam.clip_end = 6000; cam.sensor_fit = args.fit
cam.dof.use_dof = True; cam.dof.focus_distance = (Vector((CAM.x, PROD_Y, CAM.z)) - CAM).length
cam.dof.aperture_fstop = args.fstop
camo = link(bpy.data.objects.new('cam', cam)); camo.location = CAM
camo.rotation_euler = (AIM - CAM).to_track_quat('-Z', 'Y').to_euler(); scene.camera = camo

# ------------------------------------------------------------------ render settings
rx, ry = [int(v) for v in args.res.split('x')]
r = scene.render; r.resolution_x = rx; r.resolution_y = ry; r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGB'; r.image_settings.color_depth = '8'
c = scene.cycles; c.samples = args.samples; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
c.use_denoising = True
try: c.denoiser = 'OPENIMAGEDENOISE'
except Exception as e: print('denoiser', e)
c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 4; c.transmission_bounces = 6
c.transparent_max_bounces = 12; c.sample_clamp_indirect = 10.0
c.caustics_reflective = False; c.caustics_refractive = False
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = args.look
except Exception as e: print('look', e)
scene.view_settings.exposure = args.exposure
if args.border:
    bx0, by0, bx1, by1 = [float(v) for v in args.border.split(',')]
    r.use_border = True; r.use_crop_to_border = True
    r.border_min_x = bx0; r.border_max_x = bx1; r.border_min_y = 1 - by1; r.border_max_y = 1 - by0
os.makedirs(os.path.dirname(args.out), exist_ok=True)
print(f'[build] wheat instances={n_wheat} kernels={len(kf)} build={time.time() - T0:.1f}s')

t1 = time.time(); r.filepath = args.out + '_A.png'
bpy.ops.render.render(write_still=True)
print(f'[render A] {time.time() - t1:.1f}s -> {r.filepath}')

# ------------------------------------------------------------------ pass B: clean product colour + coverage
if args.passB:
    t2 = time.time()
    for ob in scene.objects:
        if ob.type == 'MESH' and ob is not BB: ob.is_holdout = True
    BB.data.materials[0] = M_PROD_CLEAN
    bg.inputs['Strength'].default_value = 0.0; fl.energy = 0.0
    if args.sun > 0: sl.energy = 0.0
    r.film_transparent = True; r.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'Standard'; scene.view_settings.look = 'None'; scene.view_settings.exposure = 0.0
    c.samples = max(48, args.samples // 2); c.max_bounces = 1
    r.filepath = args.out + '_B.png'
    bpy.ops.render.render(write_still=True)
    print(f'[render B] {time.time() - t2:.1f}s -> {r.filepath}')
print(f'[done] total {time.time() - T0:.1f}s')
