# i.Mak MA / MK – mining and steel conveyor video (9:16)

An 86-second vertical product video for the i.Mak MA (helical, parallel shaft) and MK (bevel-helical, right-angle) heavy-duty industrial gearboxes, focused on belt conveyors in mines and steel plants. It follows the same format and pipeline as `../imak-irc-video`.

**Output:** `video/imak-mamk-9x16.mp4` (1080 × 1920, 30 fps, H.264 + AAC, −14 LUFS)

## Shots
- **dark / studio:** MK 703 hero on black, then the grey studio turntable
- **duo:** MA 703 and MK 703 side by side
- **lineup:** MK 403 · 703 · 803 · 1004 · 1204
- **drive:** an MK shaft-mounted on a conveyor head pulley (hollow shaft, torque arm, lantern and motor), with ore on the belt. The backdrop is a real open-pit mine photo, seen only by the camera.
- **conveyor:** the inclined, loaded belt rising to the head drive over the mine
- **steel:** the same drive inside a real steel-plant interior (HDRI, shadow-catcher floor)
- **photos:** i.Mak's own conveyor-drive photos plus licensed mine and steel photos, credited on screen

## Build
```bash
python3 tools/mamk_scene.py lineup --still 0 --res 3200x1800      # stills: lineup, duo
tools/render_queue.sh                                              # every 4th, then every 2nd frame of each shot
STEP=4 python3 tools/interp.py drive conveyor steel dark studio    # fill in frames (motion interpolation)
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 tools/voiceover.py  # female voice (edge-tts), word timings
python3 tools/timeline.py && python3 tools/soundtrack.py           # layout, original music + effects, mix
node tools/compose.js video/imak-mamk-9x16.mp4                     # titles, captions, logo, end card
```
`tools/scenekit.py` holds the materials, lights and camera helpers shared with the IRC video.

Every figure comes from the i.Mak MA/MK catalogue 2025 and imakreduktor.com. Sources and licences are listed in `assets/SOURCES.md`, which also notes the open-pit photo whose licence should be confirmed.
