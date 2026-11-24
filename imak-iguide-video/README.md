# i-Guide teaser (9:16)

A 17-second vertical teaser for i.Mak's i-Guide (iguide.imakreduktor.com), after a CGI "giant phone" product ad. It runs:
1. A dark showroom with a giant phone showing i-Guide.
2. Crane hooks lower i.Mak gearboxes into the "Gearboxes Categories" grid one by one; the rest of the range fills in.
3. Quick Selection: a gearbox code is typed and the .STEP / .DWG files appear.
4. A hook presses the red button.
5. End card: i-GUIDE · Find your gearbox in seconds · QR code · Try it now.

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
