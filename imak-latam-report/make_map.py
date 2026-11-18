# Renders the Latin America market map used in the deck.
# Usage: python make_map.py <countries-110m.json (world-atlas TopoJSON)> <out.png>
import sys, json, math
from PIL import Image, ImageDraw

topo_path, out_path = sys.argv[1], sys.argv[2]
topo = json.load(open(topo_path))
sx, sy = topo['transform']['scale']; tx, ty = topo['transform']['translate']

def decode(arc):
    x = y = 0; out = []
    for dx, dy in arc:
        x += dx; y += dy
        out.append((x * sx + tx, y * sy + ty))
    return out
ARCS = [decode(a) for a in topo['arcs']]

def ring(ids):
    pts = []
    for i in ids:
        a = ARCS[i] if i >= 0 else ARCS[-1 - i][::-1]
        pts.extend(a[1:] if pts else a)
    return pts

CORE = {'Argentina', 'Chile', 'Peru', 'Colombia', 'Mexico'}
SPANISH = {'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay', 'Guatemala', 'Honduras', 'El Salvador',
           'Nicaragua', 'Costa Rica', 'Panama', 'Cuba', 'Dominican Rep.', 'Puerto Rico'}
COL = {'core': (149, 36, 20), 'spanish': (222, 170, 160), 'brazil': (232, 190, 110), 'other': (226, 222, 214)}

LON0, LON1, LAT0, LAT1 = -119.0, -32.0, 34.0, -56.5
K = math.cos(math.radians(15.0)); SS = 2; W = 1300 * SS
scale = W / ((LON1 - LON0) * K); H = int((LAT0 - LAT1) * scale)
def proj(lon, lat): return ((lon - LON0) * K * scale, (LAT0 - lat) * scale)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
layers = {'other': [], 'spanish': [], 'brazil': [], 'core': []}
for g in topo['objects']['countries']['geometries']:
    name = (g.get('properties') or {}).get('name', '')
    kind = 'core' if name in CORE else 'spanish' if name in SPANISH else 'brazil' if name == 'Brazil' else 'other'
    polys = [g['arcs']] if g['type'] == 'Polygon' else g.get('arcs', [])
    for poly in polys:
        pts = ring(poly[0])
        lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
        if max(lons) < LON0 - 5 or min(lons) > LON1 + 5 or max(lats) < LAT1 - 5 or min(lats) > LAT0 + 5:
            continue
        if max(lons) - min(lons) > 120:        # polygons that wrap the date line (e.g. Fiji) would smear across
            continue
        layers[kind].append([proj(*p) for p in pts])
for kind in ('other', 'spanish', 'brazil', 'core'):
    for pts in layers[kind]:
        if len(pts) > 2:
            d.polygon(pts, fill=COL[kind] + (255,))
for kind in ('other', 'spanish', 'brazil', 'core'):          # white borders on top
    for pts in layers[kind]:
        if len(pts) > 2:
            d.line(pts + [pts[0]], fill=(255, 255, 255, 255), width=2 * SS, joint='curve')

# country labels are added in PowerPoint (build_deck.py) so they stay crisp and editable
img = img.resize((W // SS, H // SS), Image.LANCZOS)
img.save(out_path); print('map', img.size, '->', out_path)
