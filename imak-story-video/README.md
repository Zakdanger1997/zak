# i.Mak company story – collage video (16:9)

An 80-second company video built from i.Mak's company presentation (`assets/imak-company-deck.pdf`). It is styled after a mixed-media collage reference: cream paper, cut-out photos with paper edges, a heavy display serif, red brush-stroke highlights, hand-drawn red doodles and kinetic typography. It has a female voiceover and an original soundtrack.

**Output:** `video/imak-story-16x9.mp4` (1920 × 1080, 30 fps, H.264 + AAC, −14 LUFS)

Scenes: the hook "What does it take to keep the world turning?", then the timeline 1973 → 1983 → 1998/2000 → 2012 → 2019/2021 partners → 2022 foundry → 2023 new plant → 2024 TURQUALITY. After that come today's figures (233 people, 65,000 gearboxes a year, 1,000,000 references), the export ranking, the seven sectors, "They trust in us", and the logo end card.

## Build
```bash
pdfimages -png -p assets/imak-company-deck.pdf assets/pdf/img      # deck photos (RGB + soft masks)
python3 tools/prep_assets.py                                       # collage cut-outs + paper texture
SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 tools/voiceover.py  # female voice (edge-tts) with word timings
python3 tools/timeline.py && python3 tools/soundtrack.py           # scene timing, original music + paper swishes, mix
node tools/compose.js video/imak-story-16x9.mp4                    # story.html recorded frame by frame
```
All animation lives in `story.html` (`build()` defines every scene; `renderAt(t)` is deterministic).

## Sources and notes
- Every fact and photo comes from the i.Mak deck, except the red units in "Today": those are the brochure's renders of the official i.Mak STEP models (`../imak-mixing-brochure/assets/3d-*.png`).
- Fonts: Fraunces and Barlow (SIL OFL).
- Music and sound are synthesised in `tools/soundtrack.py`. The voice is Microsoft Edge neural TTS (en-US-AvaNeural).
- "They trust in us" shows the customer names from the deck as typography, without their logos. Before publishing, confirm i.Mak may name these companies.
- The "Partners worldwide" map uses Natural Earth land outlines (public domain, `assets/world.svg`). Istanbul is linked to SIPCO (USA), EGASEN (Pontevedra, Spain) and Hudaco (South Africa). The small dots mark the countries where imakreduktor.com lists i.Mak offices and partners.
