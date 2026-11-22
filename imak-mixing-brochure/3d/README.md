# i.Mak 3D models (STEP AP203)

Official i.Mak models, downloaded from i.Mak's public i-Guide configurator
(https://iguide.imakreduktor.com → Quick Search → "3D Model Step"). Each archive holds
one STEP AP203 file exported from SolidWorks. They are customer envelope models: the
outer housing and shafts as solids, no internal gears and no colours.

| File | Unit |
|---|---|
| MA_703-G00.step.rar | MA 703 monobloc helical (parallel shaft) |
| MK_703-G07.step.rar | MK 703 monobloc helical-bevel |
| IRK_93.step.rar | IRK 93 helical-bevel |
| IRA_93.step.rar | IR 93 helical, foot mounted |
| YP_93.step.rar | YP 93 parallel shaft |
| IRSD_83.step.rar | IRSD 83 helical-worm |
| IRS_127.step.rar | IRS 127 worm |
| S_90.step.rar | S 90 aluminium worm |
| IRNX_7.step.rar | IRNX 7 shaft mounted |

Download address pattern (other sizes): `https://iguide.imakreduktor.com/media/documents/3b_model/<SERIES>/<CODE>.step.rar`,
e.g. `IRK/IRK 123.step.rar`, `MA/MA 703-G00.step.rar`. The 4DSM and IPR series are not in i-Guide.

Extract with `unar` (or 7-Zip / WinRAR). Convert for Blender with `python3 ../tools/step_to_glb.py model.step model.glb`.
