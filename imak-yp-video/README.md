# i.Mak YP series: "exploded movement" film

A 23.5-second vertical film (1080 × 1920) for the i.Mak YP parallel-shaft gear units, after a luxury-watch tourbillon
reveal (Pinterest reference). The YP floats apart in a bright studio, its housing split open, with three helical stages,
shafts, bearings, seals and bolts drifting in a column. Everything flies together, the unit stands up and turns, and the
film ends on a white card: i.Mak, YP SERIES, SINCE 1972.

**Output:** `video/imak-yp-9x16.mp4` (1080 × 1920, 24 fps, H.264 + AAC, −16 LUFS)

## How it is made

- `assets/yp93_*.stl`: the official i.Mak YP 93 STEP model from i-Guide (`3b_model/YP/YP 93.step.rar`), split into
  paint / bore / steel meshes by `imak-mixing-brochure/tools/step_parts.py`. The input shaft (Ø38, at x=0 y=0) and the
  hollow output (Ø60, at x=0 y=−240) were measured on it.
- `tools/yp_scene.py`: the Blender (bpy, Cycles CPU) scene. The STEP is an envelope model with no internals, so the gear
  train is modelled after i.Mak's YP cutaway poster (Z1–Z6, three stages, input at the top, hollow shaft at the
  bottom). Gear sizes are illustrative. Materials, lights and the camera come from `imak-bakery-video/tools/scenekit.py`.
- `tools/render_queue.sh`: renders every 2nd frame (720 × 1280, 16 samples, denoised), then the rest if time allows.
- `tools/compose.py`: studio gradient behind the transparent frames, motion interpolation to 24 fps, upscale, cross-fade
  into `assets/endcard.png` (from `endcard.html`, Cormorant Garamond), and the soundtrack.
- `tools/soundtrack.py`: synthesised score (pad, watch tick, assembly swell, part clicks, housing hit, end bell).

```
STEPS=2 tools/render_queue.sh
python3 tools/soundtrack.py
python3 tools/compose.py
```
