---
name: yt-dlp
description: Download video, audio, subtitles, transcripts, thumbnails or metadata from YouTube, TikTok, Instagram, X, Vimeo, SoundCloud and 1,800+ other sites with yt-dlp. Use when the user pastes a video or playlist URL and wants it saved, converted to MP3/MP4, clipped to a time range, its subtitles or transcript pulled, a channel or playlist archived, or just its title, duration, formats or other info listed.
---

# yt-dlp: download media from the web

[yt-dlp](https://github.com/yt-dlp/yt-dlp) is a command-line downloader for YouTube and
over 1,800 other sites. You drive it from the shell: pick the right flags for what the
user wants, run it, check the result, and tell them where the files are.

Recipes for less common jobs are in `references/recipes.md` next to this file.

## 0. Ground rules

- Download only what the user has a right to save: their own uploads, public-domain or
  Creative Commons material, or personal offline viewing where the site's terms allow it.
  If a request is plainly about pirating paid content, say so and do not proceed.
- yt-dlp does **not** break DRM (Netflix, Disney+, Spotify, most paid streaming). Say so
  instead of trying.
- Never ask the user to paste passwords or cookies into the chat. For logged-in content
  use `--cookies-from-browser` on their own machine, or a cookies file they supply.

## 1. Make sure the tools are there

```bash
yt-dlp --version || python3 -m yt_dlp --version
ffmpeg -version | head -1
```

- Missing yt-dlp: `python3 -m pip install -U "yt-dlp[default]"` (or `pipx install yt-dlp`,
  `brew install yt-dlp`, `winget install yt-dlp`). If `yt-dlp` is not on PATH afterwards,
  call it as `python3 -m yt_dlp`.
- Old yt-dlp is the number one cause of failures, because sites change constantly. If a
  download fails, update first: `yt-dlp -U` (standalone binary) or
  `python3 -m pip install -U "yt-dlp[default]"` (pip), then retry.
- ffmpeg is needed for merging best video + best audio, for `-x` audio extraction, for
  clipping and for embedding. Without it yt-dlp falls back to a single pre-merged file,
  often low quality. Install it (`apt-get install -y ffmpeg`, `brew install ffmpeg`,
  `winget install ffmpeg`) before any of those jobs.
- YouTube needs a JavaScript runtime to solve its player challenges. yt-dlp uses
  `deno` by default; if deno is not installed but node or bun is, add
  `--js-runtimes node` (or `bun`). The challenge-solver scripts come with the
  `[default]` extra (package `yt-dlp-ejs`); a bare `pip install yt-dlp` lacks them, so
  either install `"yt-dlp[default]"` or add `--remote-components ejs:github`.
  Symptoms: warnings about "n challenge", "jsc" or "remote component", only
  images/storyboards listed, or 403 errors.

## 2. Look before you download

For anything bigger than a single video, inspect first so you do not pull 300 GB by mistake:

```bash
# Title, duration, uploader, without downloading
yt-dlp --print "%(title)s | %(duration_string)s | %(uploader)s" "URL"

# Every available format (resolution, codec, size)
yt-dlp -F "URL"

# How many items a playlist or channel holds, fast
yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "URL"
```

Always wrap URLs in double quotes: `&` and `?` in them break the shell otherwise.

## 3. Pick the recipe

Default output folder: a `downloads/` folder in the current project, unless the user
names another. Use `-P` for the folder and `-o` for the file name:

```bash
-P downloads -o "%(title).150B [%(id)s].%(ext)s"
```

(`.150B` caps the title at 150 bytes so long titles do not exceed filename limits; add
`--restrict-filenames` if the files must be plain ASCII.)

| The user wants | Command |
|---|---|
| The video, best quality | `yt-dlp -P downloads "URL"` |
| An MP4 that plays everywhere (phones, PowerPoint, WhatsApp) | `yt-dlp -t mp4 -P downloads "URL"` |
| Max 1080p (smaller file) | `yt-dlp -t mp4 -f "bv*[height<=1080]+ba/b[height<=1080]" -P downloads "URL"` |
| Audio only as MP3 | `yt-dlp -t mp3 -P downloads "URL"` |
| Audio, best quality, no re-encode | `yt-dlp -f ba -x -P downloads "URL"` |
| A clip (e.g. 1:30 to 2:45) | `yt-dlp -t mp4 --download-sections "*1:30-2:45" --force-keyframes-at-cuts -P downloads "URL"` |
| Subtitles only (no video) | `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" --convert-subs srt -P downloads "URL"` |
| Video with subtitles inside it | `yt-dlp -t mp4 --embed-subs --sub-langs "en.*,ar" -P downloads "URL"` |
| Thumbnail only | `yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg -P downloads "URL"` |
| Full metadata as JSON | `yt-dlp -j --no-playlist "URL" > info.json` |
| A whole playlist, numbered | `yt-dlp -t mp4 -P downloads -o "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s" "PLAYLIST_URL"` |
| Items 1-10 of a playlist | add `-I 1:10` |
| A single video from a `watch?v=...&list=...` URL | add `--no-playlist` |

Add `--embed-metadata --embed-thumbnail --embed-chapters` when the user will keep the
files in a media library. Add `--sponsorblock-remove sponsor` to cut sponsor segments
from YouTube videos.

Language codes for `--sub-langs`: `en.*` matches `en`, `en-US`, `en-orig` and so on;
`ar` is Arabic, `tr` Turkish, `all` everything (can be dozens of files; avoid it unless
asked). Run `yt-dlp --list-subs "URL"` to see what exists.

## 4. Transcript for Claude to read

When the user wants a summary, quotes, notes or a translation of a video, you do not
need the video itself. Pull the subtitles and turn them into plain text:

```bash
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" \
  --convert-subs srt -P downloads -o "transcript" "URL"
```

Then read the `.srt`, drop the cue numbers and timestamps and de-duplicate the
repeated lines that auto-captions produce, and work from that text. Keep the
timestamps if the user wants quotes with times or chapter notes.

If no subtitles exist, say so; the fallback is to download audio (`-f ba -x`) and run
a speech-to-text tool, which only works if one is installed.

## 5. Big jobs: channels, playlists, archives

Use an archive file so re-running continues where it stopped and skips what is done:

```bash
yt-dlp -t mp4 -P "downloads/%(uploader)s" \
  -o "%(upload_date>%Y-%m-%d)s - %(title).120B [%(id)s].%(ext)s" \
  --download-archive downloads/archive.txt \
  --embed-metadata --embed-thumbnail \
  -t sleep "CHANNEL_OR_PLAYLIST_URL"
```

- `-t sleep` waits between downloads so the site does not rate-limit or block you; keep
  it on for anything over ~20 videos.
- Filter instead of downloading everything:
  `--match-filters "duration>60 & !is_live"`, `--dateafter 20260101`,
  `--max-downloads 50`.
- Run long jobs in the background and report progress from the log.

## 6. When it fails

| Error says | Do this |
|---|---|
| `HTTP Error 403`, `Unable to extract`, `nsig`/`n challenge` | Update yt-dlp, make sure a JS runtime is available (step 1), retry |
| YouTube 403 even after the log says the challenges were solved, on a cloud server | YouTube blocks most datacenter IPs. Run yt-dlp on the user's own computer, or use their cookies; other sites usually still work from the cloud |
| `Sign in to confirm you're not a bot` / `confirm your age` / private / members-only | The user must supply their own login: `--cookies-from-browser chrome` (or `firefox`, `edge`, `safari`, `brave`) run on their machine, or `--cookies cookies.txt`. Cloud containers have no browser profile, and datacenter IPs are often blocked by YouTube; say so plainly |
| `Requested format is not available` | Run `-F`, then pick an existing format or loosen the filter (`/b` fallback) |
| `ffmpeg not found`, files left as separate `.f137.mp4` + `.f251.webm` | Install ffmpeg and re-run; already-downloaded parts are reused |
| `HTTP Error 429` | Slow down: `-t sleep`, `--limit-rate 2M`, try later |
| Cloudflare / "impersonation" warning | `pip install "yt-dlp[default,curl-cffi]"` then add `--impersonate chrome` |
| Site not supported | Check `yt-dlp --list-extractors | grep -i NAME`; the generic extractor often still works on pages with an embedded video |
| DRM | Not possible with yt-dlp; tell the user |

Read the actual error text before changing flags; do not try random options.

## 7. Finish

After a download, list what was saved with sizes (`ls -lh downloads/`), and for media
files confirm they are valid: `ffprobe -v error -show_entries format=duration,size -of
default=nw=1 FILE`. Tell the user the path, the duration and the size. If the session runs
in a cloud container, say the files are in the container, not on their computer, and
offer to move them where they need them.

Related: the `ai-video-studio` plugin in this marketplace can use a downloaded
reference video or its transcript as the starting point for a new video on the user's
own topic.
