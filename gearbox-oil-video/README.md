# Gearbox oil: leaks, levels and life (3D explainer reel)

An 83-second vertical (9:16, 1080×1920, 30 fps) English explainer modelled on the
"What if…" 3D engineering reels: a real product on a workshop bench, one highlight
colour, word-by-word captions and tag labels. Topic: why gearboxes leak oil, how to fix
it, why the oil level depends on the mounting position, and what too little or too much
oil does to efficiency and service life.

The unit is the real **i.Mak IRAM 93-160 L** (IR 93 helical geared motor, foot mounted),
from i.Mak's public i-Guide STEP model, painted RAL 3020 traffic red. The STEP model is an
envelope model (outside only), so the gears, bearings, seal, breather and oil shown in the
see-through shots are drawn procedurally inside the real housing.

| Step | File | Tool |
|------|------|------|
| Narration, word timings | `narrate.py` → `audio/lineNN.mp3`, `narration.json` | edge-tts, `en-US-ChristopherNeural` |
| 3D model | `models/iram_lo.glb` from `IRAM 93-160 L.step` via `step_to_glb.py` | OpenCascade (`cadquery-ocp`) |
| Scenes (9 shots, `window.__seek(t)` renders any instant) | `scene.html` | three.js + Canvas 2D overlay |
| Frames → video | `render.js full <worker> <workers>` → `parts/partN.mp4` | Playwright Chromium (SwiftShader WebGL) + ffmpeg |
| Voice track on the scene timeline | `build_audio.py` → `voice.wav` | ffmpeg |
| Final mux | `encode.sh` → `gearbox_oil_explainer.mp4` | ffmpeg |

## Rebuild

```bash
npm install three@0.170 @fontsource/anton @fontsource/inter
pip install edge-tts cadquery-ocp
# model: IRAM_93-160_L.step.rar lives on the brochure branch (imak-mixing-brochure/3d/)
mkdir -p models && cd models && unar IRAM_93-160_L.step.rar && \
  python3 ../step_to_glb.py "IRAM 93-160 L.step" iram_lo.glb --deflection 1.0 && cd ..
python3 narrate.py
node render.js test                       # two check frames per scene into test/
for w in 0 1 2; do node render.js full $w 3 & done; wait   # ~3-4 s per frame per worker on CPU
python3 build_audio.py && ./encode.sh
```

## Script and sources

1. Hook: a few drops a day, does it matter?
2. Shaft seal: the lip hardens or the shaft wears a groove.
3. Heat expands the air; a blocked breather pushes oil past the seals.
4. Fix: new seal on a clean shaft, breather moved to the highest port.
5. Six mounting positions; the oil level follows gravity (positions shown are illustrative).
6. NORD SK 072.1 needs 0.16 L in M1 and 0.29 L in M2: fill to the level plug.
   ([NORD oil quantity table](https://media.nord.com/res/Document/97342.pdf);
   [SEW: check the oil level plug, refill after a position change](https://download.sew-eurodrive.com/download/html/31964060/en-EN/53068520331.html))
7. Too little oil: dry gears and bearings, wear.
8. Too much oil: churning losses and heat; rule of thumb 80 °C ≈ 10,000 h, 90 °C ≈ 5,000 h of oil life
   ([SEW churning losses](https://download.sew-eurodrive.com/download/html/33348626/en-EN/55361833867.html);
   [Machinery Lubrication, Arrhenius rule](https://machinerylubrication.com/Read/32752/how-heat-affects-lubricants-understanding-the-arrhenius-rate-rule);
   the halving rule is a simplification, see [Precision Lubrication](https://precisionlubrication.com/articles/heat-halve-lubricant-lifespan/)).
9. Recap and kicker.

The 0.16 L / 0.29 L figures are NORD's, used to show the effect of the mounting position;
for an i.Mak unit, use the oil quantities in the i.Mak catalogue for that series and size.

Fonts: Anton and Inter (OFL, via Fontsource).
