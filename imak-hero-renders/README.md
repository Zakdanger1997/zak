# i.Mak website hero renders

Photoreal hero / header images of i.Mak gear units built from the official i.Mak STEP
models (i-Guide "3D Model Step" downloads) and rendered with Blender Cycles (the `bpy`
pip module, CPU). Paint is RAL 3020 traffic red.

| Scene | Script | Shows |
|---|---|---|
| hero_conveyor_iram93 | `tools/scene_conveyor.py` | IRAM 93-160 L helical geared motor on a pedestal, coupled to a belt-conveyor head pulley |
| hero_agitator_irkm93 | `tools/scene_agitator.py` | IRKM 93-160 L helical-bevel geared motor, wall-mounted on a bracket, driving a vertical agitator on a process tank |
| hero_lineup_family | `tools/scene_lineup.py` | product family on a dark reflective floor: IRAM, IRKM, YPM, IRFM, IRSDM, MK 703, MA 703, IRNX 07 |
| hero_closeup_irkm93 | `tools/scene_closeup.py` | close-up of the IRKM 93 with shallow depth of field (dark background, text space on the left) |
| hero_pump_irfm93 | `tools/scene_pump.py` | IRFM 93-160 L flange-mounted on a progressive-cavity pump skid |

## Rebuild

```sh
pip install bpy cadquery-ocp pillow          # Blender 5.x as a Python module
# STEP archives: iguide.imakreduktor.com -> Quick Search -> "3D Model Step" (see ../imak-mixing-brochure/3d/README.md on branch claude/dazzling-fermi-xfi6de)
unar -o 3d 3d/*.rar
for f in 3d/*.step; do n=$(basename "$f" .step | tr ' ' '_'); python3 tools/step_parts.py "$f" "parts/$n" --deflection 0.25; done
python3 tools/scene_conveyor.py --preview --scale 0.33 --samples 48   # quick look -> preview/
./render_all.sh                                                      # 3840x2160 finals -> out/
```

`tools/hero_lib.py` holds the shared materials, the dark hall, lights, camera and render
settings (Cycles, adaptive 512 samples, OpenImageDenoise, Khronos PBR Neutral view transform
so the RAL colour stays honest). Each final takes roughly an hour on four CPU cores.

## Social post: IRC 93 hoist drive (4:5)

`tools/scene_irc_post.py` renders the IRC 93 (STEP) with the motor borrowed from the IRAM 93-160 L
model (cut at the motor front, joined by a bell adapter) on a hoist frame, driving a rope drum through
its splined output shaft; the shaft and the splined drum hub are pulled apart so the spline is visible.
Output `out/irc_post_raw.png` (2160x2700) plus `irc_post_raw.json` with the spline's screen position.
`tools/post_layout.py raw.png out.jpg --lang tr|en` adds the headline, i.Mak badge, spline call-out and
the brand band. Debug: `CAM=input` (front view of the bell joint), `SKIP=motor,bell`, `NORENDER=1`.
