# i.Mak at Anuga FoodTec 2027 – "final countdown" teaser (16:9)

A 21.5-second LinkedIn teaser in the same template as i.Mak's Pack Expo and Propak Cape teasers. It runs:
1. Event logo over blurred machinery.
2. Dates in a red tag and in giant condensed type.
3. Three i.Mak units over food-line footage, with red tags and a giant "I-MAK REDUKTOR".
4. Satellite map zooming to Cologne, with Germany outlined.
5. End card with dates, city, Koelnmesse and the i.Mak logo.

**Output:** `video/imak-anuga-foodtec-2027.mp4` (1920 × 1080, 30 fps, H.264 + AAC, −14 LUFS)

## Build
```bash
python3 tools/prep.py            # footage -> render/fg/<scene>/####.jpg (scenes.json), logo upscale
python3 tools/soundtrack.py      # audio/music.wav
node tools/compose.js            # records compose.html frame by frame -> video/
node tools/compose.js --stills 4.3,9.6   # quick check frames in /tmp/claude-0/anuga
```
Timing and clips are in `scenes.json`; text, tags and animation in `compose.html`. To add the stand number, edit the end card in `compose.html` (the "KOELNMESSE" line) and re-record.
Sources and licences: `assets/footage/SOURCES.md`.
