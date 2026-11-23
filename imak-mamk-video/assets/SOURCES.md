# Picture and sound sources – i.Mak MA / MK video

## 3D renders
- i.Mak MK 703-G07 and MA 703-G00, plus MK 403/803/1004/1204 for the lineup, come from the official STEP models on i-Guide (https://iguide.imakreduktor.com/media/documents/3b_model/MA|MK/…). The MK 603 model on i-Guide is empty, so it was not used.
- The conveyor (pulley, belt, idlers, frame, ore), the lantern and motor, and the torque arm are modelled in `tools/mamk_scene.py`. The MK is shaft-mounted with a hollow shaft and torque arm, as in the MA/MK catalogue 2025.
- HDRI lighting comes from Poly Haven (CC0): abandoned_hopper_terminal_01, industrial_workshop_foundry, machine_shop_02, studio_small_09.
- The mine backplate is `photos/imak_06_open_pit_mine.jpg`, taken from imakreduktor.com. **Please confirm that i.Mak's licence for this photo covers video use.** It looks like a stock photo.

## Photos in the applications montage
| File | Author | Licence | Source |
|---|---|---|---|
| imak_01_mining_conveyor_drive.jpg | i.Mak | i.Mak website | https://www.imakreduktor.com/wp-content/uploads/2025/09/minning-1-scaled.jpg |
| wm_overland_conveyor_red_dirt_portrait.jpg | Calistemon | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Alcoa_overland_conveyor_under_construction,_Western_Australia |
| wm_bucket_wheel_excavator_night.jpg | Jan Anskeit (anskeit.com) | CC BY 4.0 | https://commons.wikimedia.org/wiki/File:Schaufelradbagger_im_Tagebau_Hambach_bei_Nacht.jpg |
| wm_molten_ladle_crane_portrait.jpg | Swapnil199 | CC BY 4.0 | https://commons.wikimedia.org/wiki/File:Molten_ladle.jpg |
| imak_03_conveyor_drive_aerial.jpg | i.Mak | i.Mak website | https://www.imakreduktor.com/wp-content/uploads/2026/01/mining2.jpg |

Only the i.Mak photos show i.Mak equipment. The others show where conveyor and mill drives are used. `photos/ALL_SOURCES.csv` lists every candidate photo that was found.

## Sound
- Voiceover: Microsoft Edge neural TTS, voice en-US-AvaNeural (tools/voiceover.py).
- Music and sound effects are synthesised in tools/soundtrack.py, with no third-party audio.

## Facts
All figures come from the i.Mak MA/MK catalogue 2025 (MA-MK-Katalog-2025-Rev.00.pdf) and imakreduktor.com (mine and steel pages).
