# Finishing pass for the ray-traced hero: true-colour product composite, light wrap, bloom, grade.
# Usage: python post.py <base path without _A/_B> <out.png> [--sun fx,fy]
import sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ap = argparse.ArgumentParser()
ap.add_argument('base'); ap.add_argument('out')
ap.add_argument('--k', type=float, default=0.78)          # how much of the true product colour to restore
ap.add_argument('--sun', default='0.665,0.33')            # sun-core position in the frame (fractions)
ap.add_argument('--glow', type=float, default=0.22)
ap.add_argument('--bloom', type=float, default=0.55)
ap.add_argument('--sat', type=float, default=1.10)
ap.add_argument('--contrast', type=float, default=1.10)
ap.add_argument('--vig', type=float, default=0.30)
ap.add_argument('--grain', type=float, default=0.012)
ap.add_argument('--seed', type=int, default=3)
a = ap.parse_args()

def to_lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def to_srgb(x):
    x = np.clip(x, 0, None)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)
def blur(x, s): return ndi.gaussian_filter(x, (s, s, 0)) if x.ndim == 3 else ndi.gaussian_filter(x, s)

A = np.asarray(Image.open(a.base + '_A.png').convert('RGB')).astype(np.float32) / 255.0
B = np.asarray(Image.open(a.base + '_B.png').convert('RGBA')).astype(np.float32) / 255.0
H, W = A.shape[:2]; S = W / 1920.0                          # scale factor for pixel radii
al = B[..., 3:4]; prod = B[..., :3]

# --- product: restore brand colour, seat it in the light -------------------------------------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); fx = xx / W; fy = yy / H
ys, xs = np.where(al[..., 0] > 0.5)
if len(xs):
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    u = np.clip((xx - x0) / max(1, x1 - x0), 0, 1); v = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
    shade = (0.90 + 0.14 * u - 0.10 * v)[..., None]        # a touch brighter toward the sun side, darker at the base
else:
    shade = 1.0
warm = np.array([1.03, 0.975, 0.90], dtype=np.float32)
prod_l = to_lin(prod) * shade * warm * 0.94
A_l = to_lin(A)
comp = A_l * (1 - al * a.k) + prod_l * (al * a.k)

# light wrap: bright background bleeding over the product's silhouette
bgblur = blur(A_l, 14 * S)
edge = np.clip(al[..., 0] - ndi.minimum_filter(al[..., 0], size=max(3, int(9 * S)) | 1), 0, 1)
edge = ndi.gaussian_filter(edge, 2.2 * S)[..., None]
comp = comp + bgblur * edge * 0.55

# --- sun glow + bloom (linear light) ----------------------------------------------------------
sx, sy = [float(t) for t in a.sun.split(',')]
d2 = ((fx - sx) * W) ** 2 + ((fy - sy) * W) ** 2
core = np.exp(-d2 / (2 * (0.035 * W) ** 2)); halo = np.exp(-d2 / (2 * (0.16 * W) ** 2))
sun = (core * 0.9 + halo * 0.5)[..., None] * np.array([1.0, 0.62, 0.26], dtype=np.float32)
occl = 1 - al * 0.85                                         # the product blocks most of the glow
comp = comp + sun * a.glow * occl

# drifting golden dust / chaff catching the back-light (soft bokeh specks near the sun side)
rs = np.random.default_rng(a.seed + 5); dust = np.zeros((H, W), np.float32)
for _ in range(46):
    cx = rs.normal(sx, 0.20) * W; cy = rs.normal(sy + 0.10, 0.16) * H; rad = rs.uniform(1.6, 6.5) * S; amp = rs.uniform(0.03, 0.13)
    if 0 <= cx < W and 0 <= cy < H:
        x0, x1 = int(max(0, cx - 4 * rad)), int(min(W, cx + 4 * rad + 1)); y0, y1 = int(max(0, cy - 4 * rad)), int(min(H, cy + 4 * rad + 1))
        gy, gx = np.mgrid[y0:y1, x0:x1]
        dust[y0:y1, x0:x1] += amp * np.exp(-((gx - cx) ** 2 + (gy - cy) ** 2) / (2 * rad * rad))
comp = comp + dust[..., None] * np.array([1.0, 0.72, 0.36], dtype=np.float32) * (1 - al * 0.9) * 0.9

lum = comp @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
hi = comp * np.clip((lum - 0.55) / 0.6, 0, 1)[..., None]
bl = blur(hi, 5 * S) * 0.5 + blur(hi, 16 * S) * 0.32 + blur(hi, 48 * S) * 0.18
comp = comp + bl * a.bloom

# --- grade (display space) --------------------------------------------------------------------
img = to_srgb(comp)
img = np.clip(img, 0, 1)
l = (img @ np.array([0.299, 0.587, 0.114], dtype=np.float32))[..., None]
img = l + (img - l) * a.sat                                   # saturation
img = np.clip(img, 0, 1)
img = 0.5 + (img - 0.5) * a.contrast                          # contrast around mid-grey
img = np.clip(img, 0, 1)
img = img - 0.035 * np.sin(2 * np.pi * img) * 0.5             # gentle filmic S
shadow_w = np.clip(1 - l / 0.45, 0, 1); high_w = np.clip((l - 0.55) / 0.45, 0, 1)
img = img + shadow_w * np.array([-0.012, 0.004, 0.022], dtype=np.float32)      # teal-ish shadows
img = img + high_w * np.array([0.020, 0.006, -0.018], dtype=np.float32)        # amber highlights
r2 = ((fx - 0.5) / 0.75) ** 2 + ((fy - 0.52) / 0.72) ** 2
img = img * (1 - a.vig * np.clip(r2 - 0.25, 0, 1.2) ** 1.3)[..., None]          # vignette
rng = np.random.default_rng(a.seed)
g = rng.normal(0, a.grain, (H, W, 1)).astype(np.float32)
g = ndi.gaussian_filter(g, (0.6, 0.6, 0))
img = np.clip(img + g * (0.6 + 0.8 * (1 - l)), 0, 1)

# crisp product: mild unsharp mask limited to the product matte
sharp = img + (img - blur(img, 1.3 * S)) * 0.55
img = np.clip(img * (1 - al) + sharp * al, 0, 1)
Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(a.out)
print('wrote', a.out, (W, H))
