# Ar-Ge Departmanı Genel Eğitim Sunumu: technical restyle

The source deck has 146 slides (from SharePoint). The rebuilt deck has 154 and is written to `out/`; it is not committed because of its size.

## What changed
- **Master:** a blueprint grid background, a red rule under the header strip and a technical footer ("DOK. AR-GE-EĞT-01" plus slide number). All content slides pick these up.
- **Title, 10 section dividers and closing slide:** a dark industrial style with big red section numbers, black-and-white photography and corner marks (`assets/div_*.png`).
- **8 new technical slides** in Turkish:

  | Slide | Content |
  |---|---|
  | 10 | Range comparison table (data extracted from product slides 10–21) |
  | 11 | Maximum torque chart (native chart) and headline figures |
  | 26 | IRK gearbox anatomy as a HUD view: callouts, power-flow path, materials from slide 22 |
  | 96 | Core formulas (torque, ratio, efficiency, output torque, service factor, peripheral speed) |
  | 97 | Worked selection example (belt conveyor, 7.5 kW, 1450 → 45 rpm) |
  | 100 | Gear geometry (m = 4, z = 20/48, a = 136 mm example) |
  | 101 | Typical efficiency by gear type |
  | 109 | Bearing life L10 (ISO 281), with example and a native L10h–P chart |

- **Video:** the slide-46 video is re-encoded from 297 MB to 6.5 MB, bringing the whole file from 377 MB to 95 MB.

## Build
```bash
python3 tools/prep_assets.py                          # plates, cutaway, gear drawing
python3 tools/build_deck.py light.pptx out_light.pptx # light.pptx = source with videos stubbed
# then copy the compressed video into ppt/media/media1.mp4 and re-zip (see the session notes)
```
