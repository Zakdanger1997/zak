# i.Mak – Solutions for baking process (16:9)

An 82-second application video modelled on a competitor's "solutions for food baking processes" format. It runs: logo, title card, real bakery footage, then a clay-style 3D bakery line. The camera flies from an overview into each station, where a station tag and i.Mak product cards appear. It ends with more real footage and the logo. As in the reference, there is music and no voiceover.

**Output:** `video/imak-bakery-16x9.mp4` (1920 × 1080, 30 fps, H.264 + AAC, −14 LUFS)

## Stations and drives (official i.Mak STEP models, RAL 3020)
| Station | Drive and mounting | Card |
|---|---|---|
| Feeding system | IRAM 93 inline helical geared motor at the top of the silo screw conveyor (in line with the screw), plus a second one standing vertically on the spiral-mixer head driving the hook | IR Series – helical geared motor units |
| Extruder | MA 703 parallel-shaft unit in line with the barrel (MAE layout); IEC motor and coupling behind it on the base frame | MAE / MKE Series – monobloc extruder gear units; i.Mak three-phase asynchronous motors |
| Ovens, dryers and conveyors | IRSDM 83 helical-worm geared motor shaft-mounted on the outlet drive roller, with a torque arm | IRSD Series – helical worm geared motor units |
| Spiral freezer | IRKM 93 helical-bevel geared motor beside the drum: vertical output, sprocket and chain to the drum | IRK Series – helical bevel geared motor units; i.Mak motors |

Product names are taken from the product menu on imakreduktor.com.

## Build
```bash
tools/render_queue.sh                       # Blender/Cycles, every 4th then every 2nd frame -> render/line
STEP=4 python3 tools/interp.py line         # motion-interpolate to 24 fps -> render/line_i
LINEDIR=line_i python3 tools/timeline.py    # timing, stations, cards, footage
python3 tools/soundtrack.py                 # original music -> audio/music.wav
node tools/compose.js video/imak-bakery-16x9.mp4
```

## Footage
All footage comes from Wikimedia Commons and is credited on screen. The full list is in `assets/footage/ALL_SOURCES.csv`.
- v03: Beachfront B-Roll, CC BY 3.0
- v04: Robert Cole, CC0
- p01 and p02: U.S. Air Force, public domain
- p05 and p07: Chmee2, CC BY 3.0
