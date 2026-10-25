# ai-video-studio

A free, local alternative to hosted AI-video platforms for **narrated picture-story videos**: explainers, Shorts and Reels, faceless-channel episodes, in any language.

Claude does the creative work (research, script, shot list, picture prompts) through the `make-ai-video` skill. The bundled `freevid` tool does the production with free services and open tools:

| Stage | Tool | Cost |
|-------|------|------|
| Narration with word timings | [edge-tts](https://github.com/rany2/edge-tts) (Microsoft neural voices, 300+ voices, Egyptian/Gulf Arabic included) | free |
| One AI picture per scene | [Pollinations](https://pollinations.ai) image API (basic model anonymously; Flux with a free token in `POLLINATIONS_TOKEN`) or the Hugging Face inference API (`HF_TOKEN`, free account) | free |
| Camera motion, captions, mix, encode | ffmpeg (zoompan, libass with Arabic shaping, loudnorm) | free |

Output: an MP4 (1080×1920 or 1920×1080, 30 fps, H.264 + AAC) with burned captions timed from the speech. A three-scene test renders in about a minute on a laptop.

## Install

```
/plugin install ai-video-studio --marketplace Zakdanger1997/zak
pip install -r <plugin root>/tools/requirements.txt
```

Also needed on the machine: `python3`, `ffmpeg` built with libass (the standard builds are), and Node is **not** required.

## Use

Ask Claude: *"make me a 90-second Egyptian-Arabic short explaining how a gearbox works, stickman style"* or *"remake this YouTube short for my product"*. The skill asks only for what is missing (topic or reference link, language, length, aspect, style, voice), writes `project.json`, runs the pipeline, shows you a contact sheet of the pictures, and delivers `final.mp4`.

Or run it yourself:

```bash
python3 tools/freevid.py all examples/gearbox-ar.json
```

Stages can be run separately (`narrate`, `images`, `preview`, `assemble`) and are idempotent: delete a generated file to redo only that part.

## Project file

```json
{
  "title": "How a gearbox works",
  "lang": "ar", "voice": "ar-EG-ShakirNeural",
  "aspect": "9:16", "style": "stickman", "seed": 7,
  "caption": { "enabled": true, "font": "Cairo", "size": 58, "max_words": 4 },
  "scenes": [
    { "title": "الجيربوكس بيشتغل إزاي؟",
      "text": "الموتور ده بيلف ألف وأربعمية لفة في الدقيقة…",
      "image": "a small red geared motor beside a conveyor belt carrying a steel coil, a stick-figure engineer shrugging",
      "motion": "in" }
  ]
}
```

`style` is a card from `tools/styles.json` (stickman, paper-cutout, editorial, watercolor, clay, 3d-cartoon, whiteboard, isometric, pixel, storybook, photoreal) or your own prompt prefix. `music` points to your own licensed audio file (optional).

## What it is not

- It does not generate video clips with moving characters; each scene is a still picture with camera motion (the "picture story" format). That is what keeps it free and fast.
- The image endpoint is a public free service with no uptime guarantee. When it fails after retries, the scene gets a plain placeholder so the cut still renders; rerun `images` later.
- Voices are synthetic. They read dialect text well but with a limited acting range.

## Files

```
ai-video-studio/
├── .claude-plugin/plugin.json
├── skills/make-ai-video/SKILL.md   # the workflow Claude follows
├── tools/freevid.py                # the pipeline (narrate, images, preview, assemble, all)
├── tools/styles.json               # style cards (prompt prefixes)
├── tools/requirements.txt
├── fonts/Cairo-Bold.ttf            # caption font with Arabic coverage (OFL)
└── examples/gearbox-ar.json        # three-scene Egyptian-Arabic example
```

Proxy environments: set `HTTPS_PROXY` (passed to edge-tts) and `REQUESTS_CA_BUNDLE` (used by the image requests).
