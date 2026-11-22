# i.Mak brochure – Gearboxes for mixing and agitating processes

A 12-page A4 product brochure for i.Mak Redüktör, modelled on the structure of NORD's "MAXXDRIVE for mixing and agitating processes" flyer (F1060) but built entirely from i.Mak's own products, data and photos.

**Output:** `imak-mixing-agitating-brochure-EN.pdf`

## Pages

| # | Page | Content |
|---|------|---------|
| 1 | Cover | Vertical MA agitator drive with oil cooler and pump, 4DSM unit |
| 2 | Driven by passion since 1973 | Product families, company facts, key figures, factory and fair photos |
| 3 | Gearboxes for mixing and agitating processes | Characteristics, applications, torque-by-series chart, series selection table |
| 4 | 4DSM | Vertical agitator / aerator unit: features, technical data, exploded and 3D views, site photo |
| 5 | Heavy-duty drives | MA/MK monobloc agitator drive with callouts, MA/MK size table, A and IPR series |
| 6 | From the impeller to the gearbox | 3D-rendered cut-away agitator tank with the i.Mak drive, six-step sizing, load classes, service factors |
| 7 | Water and wastewater | Application photos and drive mapping for each treatment stage |
| 8 | Output shafts, bearings and sealing | Option codes, exploded view, 3D half-section of the output stage with a / x dimensions and deflection |
| 9 | Lubrication, cooling and monitoring | Option tiles with i.Mak codes, C2–C5 corrosion protection |
| 10 | Inside an i.Mak gearbox | IRK and YP cut-aways, materials, production |
| 11 | Geared motors | IR, IRK, YP, IRSD, motors and motor options |
| 12 | Product family | Product network graphic, portfolio, headquarters and worldwide contacts |

## Build

```bash
# 1. images: download the originals listed in SOURCES.md into RAW/ (wp/, catimg/, social/), then
python3 tools/prepare_assets.py RAW          # needs Pillow, numpy, scipy
python3 tools/make_ticks.py                   # background line pattern as flat PNGs
# 2. PDF (Playwright + Chromium)
# optional: page-6 tank figure (pip install bpy; about 15 min on 4 CPU cores)
python3 tools/render_tank.py                  # Blender/Cycles cut-away tank -> assets/tank-scene.png
python3 tools/compose_tank.py                 # seat the i.Mak drive on the flange -> assets/tank-diagram.png
python3 tools/tank_labels.py                  # write labels and leader lines into brochure.html
# optional: page-8 output-stage section (about 12 min)
python3 tools/render_bearing.py               # -> assets/bearing-scene.png (+ --points-only to refresh label positions)
python3 tools/bearing_labels.py               # crop + dimensions, F_R, deflection, labels into brochure.html
node tools/build_pdf.js                       # -> imak-mixing-agitating-brochure-EN.pdf
node tools/build_pdf.js --png /tmp/pages      # also writes one PNG per page for review
```

Edit the text in `brochure.html` and the styles in `brochure.css`, then rebuild. Positions are absolute in millimetres on a 210 × 297 mm page.

## Content rules followed

- Only i.Mak products and photos: i.Mak renders, i.Mak catalogue images, and installation photos published by i.Mak or its official distributors (`SOURCES.md`). Competitor brochures were studied for structure only; none of their images or text is reused.
- Every figure comes from i.Mak's published catalogues (B00 2025 overview, 4DS, 4DSM, A, ADK/ADS) or website. No inverter (VFD) range is shown because i.Mak's catalogues do not list one.
- Things to confirm internally before printing: the "new facility in Egypt" line (from i.Mak's 2026 news post), the certificate list on page 2, and the typical-speed column on page 3, which gives engineering guide values.
