# Renders the regional market maps used in the deck.
# Usage: python make_map.py <countries-110m.json (world-atlas TopoJSON)> <out.png> <region: latam|me>
import sys, json, math
from PIL import Image, ImageDraw, ImageFont

topo_path, out_path, region = sys.argv[1], sys.argv[2], sys.argv[3]
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

FB = '/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf'
COL = {'core': (149, 36, 20), 'secondary': (222, 170, 160), 'brazil': (232, 190, 110), 'other': (226, 222, 214)}
WHITE = (255, 255, 255, 255); INK = (35, 30, 28, 255); BROWN = (122, 78, 10, 255)

REGIONS = {
    'latam': dict(
        lon=(-119.0, -32.0), lat=(34.0, -56.5), klat=15.0, w=1300,
        core={'Argentina', 'Chile', 'Peru', 'Colombia', 'Mexico'},
        secondary={'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay', 'Guatemala', 'Honduras',
                   'El Salvador', 'Nicaragua', 'Costa Rica', 'Panama', 'Cuba', 'Dominican Rep.'},
        brazil={'Brazil'},
        labels=[('MEKSİKA', -102.5, 23.6, 24, WHITE, 'mm'), ('KOLOMBİYA', -73.2, 3.6, 20, WHITE, 'mm'),
                ('PERU', -75.4, -9.6, 21, WHITE, 'mm'), ('ARJANTİN', -64.6, -34.5, 22, WHITE, 'mm'),
                ('ŞİLİ', -76.8, -31.0, 22, INK, 'rm'), ('BREZİLYA', -52.5, -9.0, 26, BROWN, 'mm'),
                ('Portekizce — sonraki', -52.5, -12.9, 16, BROWN, 'mm')]),
    'me': dict(
        lon=(23.0, 60.5), lat=(40.5, 11.5), klat=26.0, w=1300,
        core={'Saudi Arabia', 'United Arab Emirates', 'Qatar', 'Kuwait', 'Oman'},
        secondary={'Egypt', 'Jordan', 'Iraq', 'Lebanon', 'Yemen', 'Bahrain'},
        brazil=set(),
        labels=[('SUUDİ ARABİSTAN', 45.2, 23.8, 20, WHITE, 'mm'), ('MISIR', 29.5, 26.5, 20, WHITE, 'mm'),
                ('UMMAN', 56.6, 20.9, 16, WHITE, 'mm'), ('IRAK', 43.7, 33.1, 16, INK, 'mm'),
                ('B.A.E.', 54.4, 24.1, 14, WHITE, 'mm'), ('KATAR', 51.2, 25.3, 11, INK, 'lm')]),
}
R = REGIONS[region]
LON0, LON1 = R['lon']; LAT0, LAT1 = R['lat']
K = math.cos(math.radians(R['klat'])); SS = 2; W = R['w'] * SS
scale = W / ((LON1 - LON0) * K); H = int((LAT0 - LAT1) * scale)
def proj(lon, lat): return ((lon - LON0) * K * scale, (LAT0 - lat) * scale)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)

def kind_of(name):
    if name in R['core']: return 'core'
    if name in R['brazil']: return 'brazil'
    if name in R['secondary']: return 'secondary'
    return 'other'

layers = {'other': [], 'secondary': [], 'brazil': [], 'core': []}
for g in topo['objects']['countries']['geometries']:
    name = (g.get('properties') or {}).get('name', '')
    kind = kind_of(name)
    polys = [g['arcs']] if g['type'] == 'Polygon' else g.get('arcs', [])
    for poly in polys:
        pts = ring(poly[0])
        lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
        if max(lons) < LON0 - 5 or min(lons) > LON1 + 5 or max(lats) < LAT1 - 5 or min(lats) > LAT0 + 5:
            continue
        if max(lons) - min(lons) > 120:
            continue
        layers[kind].append([proj(*p) for p in pts])
for kind in ('other', 'secondary', 'brazil', 'core'):
    for pts in layers[kind]:
        if len(pts) > 2:
            d.polygon(pts, fill=COL[kind] + (255,))
for kind in ('other', 'secondary', 'brazil', 'core'):
    for pts in layers[kind]:
        if len(pts) > 2:
            d.line(pts + [pts[0]], fill=(255, 255, 255, 255), width=2 * SS, joint='curve')

for text, lon, lat, size, fill, anchor in R['labels']:
    f = ImageFont.truetype(FB, size * SS); x, y = proj(lon, lat)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor)

img = img.resize((W // SS, H // SS), Image.LANCZOS)
img.save(out_path); print('map', region, img.size, '->', out_path)
