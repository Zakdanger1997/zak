# i.Mak — Milling-industry marketing images

Two product-in-scene marketing visuals for the *Millers' Guide* article, compositing
i.Mak's real product renders + logo onto milling-industry backgrounds.

## Deliverables (1500×900)
- `IMAK_IRNX_global-milling.jpg` — IRNX shaft-mounted gearbox on grain silos at golden hour.
  Headline "Engineering the future of global milling".
- `IMAK_IRK_milling-line.jpg` — IRK helical-bevel geared motor on an industrial conveyor line.
  Headline "Built to drive the milling line".

Both carry the i.Mak logo, a red stat bar (50+ years · 140+ countries · 1,000,000+
configurations) and the website — copy and figures taken from the uploaded
`IMAK_Reduktor_Millers_Guide_Makale.docx`.

## Backgrounds — licensing
Fetched from the web via the Openverse API, filtered to **commercial-use** licenses.
Both chosen photos are **CC0 1.0 (public domain)** from rawpixel — free for commercial
use, no attribution required. A small "Background: rawpixel · CC0" credit is included
in-frame as a courtesy; it can be removed.
- Silos: rawpixel "Grain silos small railroad station" (CC0).
- Conveyor: rawpixel "Free conveyor belt photo" (CC0).

Product renders (IRK, IRNX) and the i.Mak logo are the company's own assets.

## Assets
- `assets/products/` — background-removed product cutouts (RGBA PNG) + logo.
- `assets/backgrounds/` — the source photos used.
- `assets/fonts/` — Oswald (headlines) + Inter (body), SIL OFL.

## Regenerate / edit
Edit text or swap backgrounds in `compose.py`, then:
```bash
python3 -I cutout.py    # rebuild product cutouts (only if source art changes)
python3 -I compose.py   # rebuild the two JPGs
```
Paths in the scripts point at the scratchpad used when first built; update the
`bg/raw/*` and `work/*` paths to `assets/backgrounds/*` and `assets/products/*`
to re-run inside this folder.

## Notes
- Higgsfield was not used (account has 0 credits); these are hand-composited from
  real photos per the "fetch the background from the web" instruction.
- Easy variants on request: a pure wheat-field-at-sunset version, a flour-sacks
  (flour pocket) scene, a mixers scene, or square 1080×1080 / vertical 4:5 crops.
