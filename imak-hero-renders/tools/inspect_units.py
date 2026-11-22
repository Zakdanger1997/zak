import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import hero_lib as H
from mathutils import Vector
names = [a for a in sys.argv[1:] if not a.startswith("--") and not a.replace(".","").isdigit()] or ["IRAM_93-160_L","IRKM_93-160_L","YPM_93-160_L","IRFM_93-160_L","IRSDM_83-112_M","MK_703-G07","MA_703-G00","IRNX_07"]
H.fresh(); mats = H.M()
H.world_dark(0.6)
x = 0
for n in names:
    u = H.load_unit(n, mats, loc=(x, 0, 0))
    print(n, "size", [round(v,3) for v in u["size"]], "min", [round(v,2) for v in u["min"]], "max", [round(v,2) for v in u["max"]])
    for s in u["shafts"][:4]:
        c, a = s["c"], s["axis"]
        print("   shaft r=%.3f c=(%.2f %.2f %.2f) axis=(%.2f %.2f %.2f) area=%.0f" % (s["r"], c.x-x, c.y, c.z, a.x, a.y, a.z, s["area"]))
    x += 1.6
H.plane("floor", (40, 40), mats["floor"])
H.light_area("key", (x/2-4, -6, 6), (x/2, 0, 0.4), 6000, 6)
H.light_area("fill", (x/2+4, -3, 3), (x/2, 0, 0.4), 2500, 6)
H.camera((x/2 - 1.5, -9.5, 3.0), (x/2 - 0.8, 0, 0.35), lens=35)
H.SAMPLES = 24
H.render("inspect", w=3840, h=1000)
