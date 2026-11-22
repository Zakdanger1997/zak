# The Drive Handbook – i.Mak

An interactive 3D handbook that runs in the browser. It is an open book on a drafting mat, and each lesson's mechanism pops up from the page. On every lesson you turn the dial, make a prediction, then lift the flap to check the answer. It was made for i.Mak's LinkedIn, and the same scripted walkthrough produces the video.

| # | Lesson | What moves | The dial |
|---|--------|-----------|----------|
| 0 | Cover | Three-gear train | – |
| 1 | Speed for torque | 4 kW motor, pinion, wheel, hoist drum and load | Wheel teeth (ratio 1 : 1 → 4 : 1) |
| 2 | A big ratio in a small ring | Sun, three planets, held ring, carrier | Sun teeth (ratio 3 : 1 → 7 : 1) |
| 3 | Slower is not always cooler | Rotating field, three-phase coils, rotor, shaft fan, cooling air | VFD frequency 60 → 10 Hz |
| 4 | The cube law | Impeller, volute, water | Pump speed 100 → 50 % |
| 5 | From drawing to the real unit | i.Mak IRKM 93 / 160 L geared motor (official 3D model) | Hours per day → service factor |

Every number is plain physics or comes from the i.Mak catalogue: the service-factor table and the class-M load class for mixers. The gears are true involute gears. The phases are set so the teeth really mesh, including the internal ring gear.

## Open it

**Easiest:** double-click `dist/imak-drive-handbook.html`. It is one self-contained file (about 3.6 MB) holding the code, the i.Mak model, the fonts and the logo. It works offline on Windows, Mac and phones, and it can be emailed or put on any web host as-is. On a phone in portrait it shows one page at a time; the red button switches between the question and the 3D model.

`index.html` is the source version. It only runs from a web server, not by double-click, because browsers block ES modules on `file://`. To work on it, serve the folder with any static server:

```bash
python3 -m http.server 8000      # then open http://localhost:8000
```

- `?demo=1` plays the scripted walkthrough live.
- `?lesson=3` opens a lesson directly.
- Controls: drag the red dial, click an answer, click the flap, and use ← / → to turn pages (↑ / ↓ also move the dial).

Rebuild the single file after any change: `npm i esbuild` once, then `node tools/build_standalone.js`.

## Make the video and stills

```bash
npm i playwright                    # once, or use a global install
node tools/record.js video/drive-handbook-4x5.mp4          # 1080 x 1350, 30 fps, about 45 s
node tools/record.js --stills 1,12,38                      # PNG stills at those seconds (for review)
node tools/shot.js out.png 4 mech                          # one lesson, one camera view
python3 tools/carousel.py                                  # LinkedIn carousel PDF + cover from the video
```

The video script (timing, headlines, captions, cursor taps) is in `src/demo.js`. Frames are rendered deterministically, one at a time, so the recording never drops frames.

## Files

- `src/main.js`: scene, book, page turn, pop-up, interaction, camera
- `src/pages.js`: the printed pages, drawn on canvases
- `src/lessons.js`: the five lessons (text, quiz, dial, mechanism)
- `src/parts.js`: involute gears, ring gear, ink outlines, badges
- `src/demo.js`: the scripted walkthrough
- `models/*.glb`: i.Mak IRKM, IRAM and MA 703, converted from the official STEP models on iguide.imakreduktor.com with `tools/parts_to_glb.py` (the part meshes come from `imak-mixing-brochure/tools/step_parts.py`)
- `vendor/`: three.js r187 (MIT, see `vendor/THREE-LICENSE`)
- `fonts/`: Barlow and Barlow Condensed (SIL OFL)
- `linkedin/`: post text, posting plan, carousel PDF and cover image
