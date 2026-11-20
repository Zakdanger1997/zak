# yt-dlp plugin

A Claude Code skill for [yt-dlp](https://github.com/yt-dlp/yt-dlp), the command-line
downloader for YouTube and 1,800+ other sites. Paste a link and ask in plain words;
Claude picks the flags, runs the download, checks the file and tells you where it is.

## What you can ask for

- "Download this video as MP4" / "just the audio as MP3"
- "Cut 1:30 to 2:45 out of this video"
- "Get the English subtitles" / "summarise this video" (Claude reads the transcript, no video download)
- "Download the first 10 videos of this playlist, numbered"
- "Archive this channel, and only fetch new uploads next time"
- "What formats and resolutions does this video have?"

## Install

```
/plugin marketplace add Zakdanger1997/zak
/plugin install yt-dlp
```

The skill needs these on the machine where Claude runs:

| Tool | Install |
|---|---|
| yt-dlp | `python3 -m pip install -U "yt-dlp[default]"` (or `pipx`, `brew`, `winget`) |
| ffmpeg | `apt-get install ffmpeg` / `brew install ffmpeg` / `winget install ffmpeg` |
| A JavaScript runtime (for YouTube) | [deno](https://deno.com) (default), or node / bun with `--js-runtimes node` |

Claude checks for these and installs what is missing when it can.

## Notes

- **Keep yt-dlp up to date.** Sites change often; most failures are fixed by updating.
- **YouTube blocks most cloud and datacenter IPs.** In a cloud session other sites usually
  work, but YouTube often returns 403. Run Claude Code on your own computer for YouTube.
- **Logged-in content** (age-restricted, members-only, private) needs your own browser
  cookies via `--cookies-from-browser`, on your own computer. Never paste cookies or
  passwords into the chat.
- **No DRM.** Netflix, Disney+, Spotify and similar paid streams cannot be downloaded.
- Download only what you have the right to save.

## Files

```
yt-dlp/
├── .claude-plugin/plugin.json
├── README.md
└── skills/yt-dlp/
    ├── SKILL.md               # main workflow: check tools, inspect, recipe table, fixes
    └── references/recipes.md  # format selectors, templates, clips, audio, subs, live, config
```

yt-dlp itself is released under the Unlicense and is not bundled here; this plugin only
contains instructions.
