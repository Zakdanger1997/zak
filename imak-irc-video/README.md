# i.Mak IRC – crane hoist video (9:16)

An 83-second vertical product video for the i.Mak IRC hoist drive geared motor. Its format follows a premium product-explainer short: a dark hero opening, a light-grey studio turntable with spec callouts, the mechanism at work, real-world applications and an end card. It has a female voiceover and burned-in captions.

**Output:** `video/imak-irc-9x16.mp4` (1080 × 1920, 30 fps, H.264 + AAC, −14 LUFS)

## How it is made

1. **3D:** Blender/Cycles renders the official i.Mak STEP models from i-Guide: the IRCM 93-160 L-BR geared motor with brake, plus IRC 63–143 for the size lineup. `tools/irc_scene.py` adds what the envelope models leave out:
   - the DIN 5480 W70×3×30×22 output spline
   - the drum connection flange (TBF)
   - the grooved rope drum, crane frame, rope falls, hook block and a 5 t load
   - a nameplate
   - gloss i.Mak-blue enamel over a cast-iron texture
   Lighting comes from real industrial HDRIs (Poly Haven, CC0).
2. **Frames:** `tools/render_queue.sh` renders every 4th, then every 2nd frame. `tools/interp.py` fills in the in-between frames by motion-compensated interpolation (ffmpeg minterpolate).
3. **Voice:** `tools/voiceover.py` uses Edge neural TTS (en-US-AvaNeural) and records word timings for the captions.
4. **Timeline:** `tools/timeline.py` places the voice lines, shots and on-screen titles, and writes `timeline.json`.
5. **Sound:** `tools/soundtrack.py` synthesises an original music bed and sound effects (whooshes, spline clunk, motor hum). The music ducks under the voice, and the mix is loudness-normalised.
6. **Edit:** `tools/compose.js` drives `compose.html` frame by frame (Playwright) and muxes in the audio.

```bash
python3 tools/irc_scene.py hoist --frames 0-143 --step 2      # or tools/render_queue.sh
STEP=2 python3 tools/interp.py dark studio spline hoist hoistwide
python3 tools/irc_scene.py lineup --still 0 --res 3200x1800
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 tools/voiceover.py
python3 tools/timeline.py && python3 tools/soundtrack.py
node tools/compose.js video/imak-irc-9x16.mp4
```

Every figure comes from the i.Mak IRC catalogue 2024 and B00 2025. Picture and sound sources are listed in `assets/SOURCES.md`.
