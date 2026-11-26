# i.Mak S 130 + S 63 combination: customer demo video

A 49.5-second 16:9 explainer (Turkish captions and narration) made for a customer (Ramazan Bey). It shows that the worm–worm
combination S 130 + S 63 is possible, but that the small unit (S 63) must always have an **output shaft** and an **output flange**:

1. Both units, apart.
2. A standard S 63 has a hollow output and no output flange, so it cannot be connected to the S 130 (red ✕).
3. Step 1: an output shaft is fitted through the S 63's hollow output.
4. Step 2: an output flange is bolted to the S 63.
5. Assembly: the shaft enters the S 130 input, and the flange is bolted to the S 130 input flange.
6. "Bu kombinasyon yapılabilir": the small gearbox always needs an output shaft and an output flange.

**Output:** `video/s130-s63-kombinasyon.mp4` (1920 × 1080, 30 fps, H.264 + AAC, −15 LUFS)

## How it is made

- `models/*.stl`: meshes of the official i.Mak STEP models from i-Guide (`3b_model/S/S 130.step.rar`, `S 63.step.rar`), made by
  `tools/prep_models.py WORK_DIR`. It uses `imak-mixing-brochure/tools/step_parts.py` and removes the S 130's solid input
  shaft, because in the combination the S 63 shaft enters the S 130 worm instead.
- `demo.html`: a three.js scene (vendored in `vendor/`), deterministic `setup()` / `renderAt(t)`. The output shaft, the
  flanges and the bolts are drawn in the scene; they are illustrative, not to catalogue dimensions.
- `tools/voiceover.py`: Turkish narration (edge-tts `tr-TR-AhmetNeural`) mixed over a soft music bed → `audio/mix.wav`.
  `SCN` in `demo.html` stretches each scene so each narration line fits.
- `tools/record.js`: renders the page frame by frame in headless Chromium and writes the MP4.

```
python3 tools/prep_models.py /path/with/step/files
python3 tools/voiceover.py
node tools/record.js video/s130-s63-kombinasyon.mp4 --audio audio/mix.wav   # --stills 5,20,40 for QA frames
```
