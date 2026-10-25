---
name: make-ai-video
description: Make a finished narrated AI video (explainer, short, picture story, faceless channel episode) for free with the bundled freevid pipeline. Use when the user asks to create, generate or produce a video, a YouTube short, a Reel, an explainer, a faceless video, or to remake a reference video on their own topic, in any language, without a paid video platform.
---

# Make an AI video (free, local pipeline)

You are the creative department; the pipeline is the production line. You write the
script and the shot list as a `project.json`, then run `tools/freevid.py`, which
voices every line (edge-tts, free), draws one picture per scene (Pollinations image
API, free, no key), animates each picture with camera motion, burns captions timed
from the speech, and renders `final.mp4` with ffmpeg.

The plugin root is the folder that contains this `skills/` directory; the tool is
`<plugin root>/tools/freevid.py`. Call it with `python3`.

## 1. Intake (one round, only what is missing)

Ask in a single message for whatever the request did not already state:

- **Topic**, or a **reference video link** to mirror.
- **Language and dialect** (narration and captions follow it; e.g. Egyptian Arabic, Turkish, English).
- **Length**: 30 s / 60 s / 90 s / 2 min (10 s per scene is the unit).
- **Aspect**: 9:16 for Shorts, Reels, TikTok; 16:9 for YouTube.
- **Style**: one of the cards in `tools/styles.json` (`stickman`, `paper-cutout`, `editorial`, `watercolor`, `clay`, `3d-cartoon`, `whiteboard`, `isometric`, `pixel`, `storybook`, `photoreal`) or a free-text look.
- **Voice**: offer two or three `edge-tts` voices for the language (list below). Default to a male narrator voice unless asked.

Do not ask about anything else. Reasonable defaults: 90 s, 9:16, `stickman`, captions on.

## 2. If a reference video was given

Mirror its *structure*, never its words or pictures. Get the transcript with
`yt-dlp --skip-download --write-auto-subs --sub-langs "<lang>.*" <url>` (falls back to
the title and description when subtitles are unavailable), then write down its beat
sheet: hook, promise, everyday analogy, mechanism steps, numbers, a common
misconception corrected, recap, kicker. Rebuild the same beats for the new topic.

## 3. Write the script (the part that decides whether the video is good)

Rules per scene (one scene = one narration line ≈ 10 s):

- **20 to 23 words**, at most two sentences, comma-light, numbers written as words.
- **Scene 1 opens with the most surprising concrete fact in eight words or fewer**, no greeting, no "in this video".
- One idea per scene; each scene adds one new concrete thing (a number, a name, a mechanism, a comparison).
- Build scenes escalate (the shuffle test: if two scenes could swap places, rewrite them).
- Scene N−1 is the turn: correct a common misconception.
- Last scene: one-sentence recap whose kicker echoes the hook.
- Keep a **through-line object** that appears in every scene (a dial that climbs, a stack that grows) and resolves at the end.
- Facts must be traceable: research first, keep the source URLs in `sources`.

Per scene also write:

- `title`: a 2 to 5 word on-screen headline in the narration language (optional but recommended for explainers).
- `image`: an English picture prompt, **short and concrete (10 to 25 words)**: one subject doing one action in one setting, with the key prop. Keep characters consistent across scenes ("stick figure engineer in a white hard hat"). **Never ask for text in the picture.** The style card is appended automatically, so do not repeat style words. The free anonymous image tier runs a basic model that follows short prompts well and long ones badly; a free Pollinations token (`POLLINATIONS_TOKEN`) or a free Hugging Face token (`HF_TOKEN` with `"image_provider": "huggingface"`) switches to Flux-class quality.
- `motion`: `in`, `out`, `left`, `right`, `up`, `down` or `auto`.

## 4. Build

```bash
pip install -r <plugin root>/tools/requirements.txt       # once
python3 <plugin root>/tools/freevid.py narrate project.json
python3 <plugin root>/tools/freevid.py images  project.json
python3 <plugin root>/tools/freevid.py preview project.json   # writes preview.jpg
```

Look at `preview.jpg`. A picture that shows text, a wrong subject, or a broken
character gets `"reseed": <small integer>` on its scene (or a sharper prompt), delete
that `images/sceneNN.jpg`, and rerun `images`. Then:

```bash
python3 <plugin root>/tools/freevid.py assemble project.json
```

Check `final.mp4` with `ffprobe` (duration = sum of scene durations, video + audio
streams) and extract two frames at different times to confirm captions and pictures.
Deliver the file. Say plainly which image tier was used: anonymous (basic model, small
corner logo) or token (Flux-class, no logo). Registering for either token is free.

Behind a corporate proxy set `HTTPS_PROXY`; `freevid` passes it to edge-tts and
`requests` honours `REQUESTS_CA_BUNDLE`.

## 5. project.json reference

```json
{
  "title": "How a gearbox works",
  "lang": "ar", "voice": "ar-EG-ShakirNeural", "rate": "+4%",
  "aspect": "9:16", "fps": 30,
  "style": "stickman",            // key from styles.json, or free text
  "seed": 7,                      // image seed base
  "lead": 0.4, "tail": 0.6,       // silence before/after each line
  "caption": { "enabled": true, "font": "Cairo", "size": 58, "max_words": 4, "margin_v": 240 },
  "music": "bed.mp3", "music_gain": -20,   // optional, your own licensed file
  "sources": ["https://..."],
  "scenes": [
    { "title": "...", "text": "narration line", "image": "picture prompt", "motion": "in" }
  ]
}
```

Outputs next to `project.json`: `audio/`, `images/`, `clips/`, `timeline.json`,
`captions.ass`, `preview.jpg`, `final.mp4`. Every stage is idempotent; delete a file to
regenerate it.

## Voices (edge-tts, free) — a useful subset

| Language | Voices |
|----------|--------|
| Arabic (Egypt) | `ar-EG-ShakirNeural` (m), `ar-EG-SalmaNeural` (f) |
| Arabic (Saudi) | `ar-SA-HamedNeural` (m), `ar-SA-ZariyahNeural` (f) |
| English (US) | `en-US-GuyNeural`, `en-US-ChristopherNeural`, `en-US-JennyNeural`, `en-US-AriaNeural` |
| English (UK) | `en-GB-RyanNeural`, `en-GB-SoniaNeural` |
| Turkish | `tr-TR-AhmetNeural`, `tr-TR-EmelNeural` |
| German | `de-DE-ConradNeural`, `de-DE-KatjaNeural` |
| French | `fr-FR-HenriNeural`, `fr-FR-DeniseNeural` |
| Spanish | `es-ES-AlvaroNeural`, `es-MX-DaliaNeural` |

Full list: `python3 -m edge_tts --list-voices`.

## Limits to state plainly

- Pictures are stills with camera motion, not generated video clips; characters do not lip-sync.
- The image service is a free public endpoint: no uptime promise, occasional slow responses, a small logo without a token.
- Voices are synthetic; they read dialect text well but with a neutral acting range.
- Facts come from your research, not from the tool. Cite sources in the project file.
