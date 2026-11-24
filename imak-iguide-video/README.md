# i-Guide teaser (9:16)

A 14.5-second vertical teaser (v2) for i.Mak's i-Guide (iguide.imakreduktor.com), after a CGI "giant phone" product ad. It runs:
1. A deep-red stage with a spotlight, sparks and a reflective floor grid; the phone swings in.
2. Step captions: ① Choose your series, ② Type the code, ③ Download in one tap.
3. Gearboxes drop into the "Gearboxes Categories" grid on the beat; the rest of the range fills in.
4. Quick search returns .STEP / .DWG / .PDF.
5. An MK unit hits the red button and zaps into the phone.
6. End card: i-GUIDE · Your gearbox. In seconds. · QR code · Try it now.

`compose_v1.html` keeps the first version (grey showroom, crane hooks).

**Output:** `video/imak-iguide-9x16.mp4` (1080 × 1920, 30 fps, H.264 + AAC, −14 LUFS)

## Build
```bash
python3 tools/ig_scene.py bg      # Blender: showroom plate + red-button pedestal -> assets/bg.png, assets/bg.json
python3 tools/ig_scene.py hook    # crane hook cutout (assets/hook.png); `dome` renders the button dome
python3 tools/soundtrack.py       # audio/music.wav (synthesised)
node tools/compose.js             # records compose.html frame by frame -> video/
```

## Sources
- Screens and product pictures: i-Guide itself. The home screen is a screenshot of iguide.imakreduktor.com/?lang=en; the gearbox images come from its categories page. The grid and search screens are rebuilt in HTML so they can animate.
- The QR code points to https://iguide.imakreduktor.com/?lang=en.
- The phone is drawn in CSS. The room, hook and button are rendered in Blender (tools/ig_scene.py, using the scenekit helpers from imak-bakery-video).
- Fonts: Montserrat (OFL). Music and sound effects are synthesised in tools/soundtrack.py.
