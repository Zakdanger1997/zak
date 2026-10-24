# الجيربوكس بيشتغل إزاي؟ — explainer short

A 93-second vertical (9:16) explainer in the style of the Egyptian "طب إزاي؟" shorts: flat line drawings on cream grid paper, one red accent, an Egyptian-Arabic narrator, burned-in captions. Topic: how a geared motor trades speed for torque.

Everything is generated locally, no video-generation service involved:

| Step | File | Tool |
|------|------|------|
| Narration (9 lines, word timings) | `narrate.py` → `audio/line0N.mp3` + `.vtt`, `narration.json` | `edge-tts`, voice `ar-EG-ShakirNeural` |
| Timeline (scene = narration + 0,4 s lead + 0,6 s tail) | `build_timeline.py` → `timeline.json` | Python |
| Drawing (nine scenes, Canvas 2D, `window.__seek(t)` renders any instant) | `animation.html` | hand-written vector code |
| Frames (1080×1920 @ 30 fps, exported from the canvas) | `render.js` → `frames/` | Playwright + Chromium |
| Encode (narration mix + H.264) | `encode.sh` → `gearbox_explainer.mp4` | ffmpeg |
| Web player (same drawing driven by the audio clock) | `player.html` + `voice.mp3` | browser |

## Rebuild

```bash
pip install edge-tts            # narration
python3 narrate.py              # needs network; through a proxy set HTTPS_PROXY
python3 build_timeline.py
node render.js test             # 18 check frames into test/
node render.js full             # all frames into frames/
./encode.sh                     # gearbox_explainer.mp4
```

`render.js` reads pixels with `canvas.toDataURL` rather than page screenshots, because headless Chromium without a GPU does not composite the canvas into screenshots.

## Script

The nine narration lines live in `narrate.py` (and `narration.json`). Facts come from the i.Mak catalogues: a 1,5 kW motor at 1400 rpm gives about 10 N·m, and through a ratio-30 helical gearbox about 300 N·m at 46 rpm (IR series table); gears in 16MnCr5 case-hardened to 58 HRC; oil change every 6000 h (YP catalogue).

## Structure (mirrors the reference short)

1. Hook with the surprising numbers (1400 rpm in, 50 rpm and a tonne out) and "I'll explain in ninety seconds".
2. Everyday analogy: bicycle gears on a hill.
3. Mechanism: 20 teeth driving 60 teeth, three turns for one.
4. The trade: speed ÷ 3 means torque × 3, energy is conserved.
5. Real numbers from the catalogue.
6. Helical teeth: quieter, stronger.
7. Material and oil bath.
8. The common misconception: a bigger motor is not the answer.
9. One-sentence recap and sign-off.

Fonts: Cairo (Google Fonts, OFL), cached in `fonts/`.
