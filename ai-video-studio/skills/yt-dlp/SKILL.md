---
name: yt-dlp
description: Download video, audio, subtitles, thumbnails or metadata from YouTube and the 1,000+ other sites yt-dlp supports (TikTok, Instagram, X/Twitter, Vimeo, Facebook, SoundCloud and more) with the yt-dlp command-line tool. Use when the user pastes a video link and wants it saved, wants an MP3/M4A of it, wants its transcript or subtitles, wants a clip of part of it, wants a whole playlist or channel, or wants a reference video pulled in to study or remake with make-ai-video.
---

# yt-dlp: download media from a link

`yt-dlp` is a free, open-source command-line downloader. You run it with Bash and hand
the user the resulting file. Do the job in as few runs as possible and report exactly
what was saved and where.

## 0. Rights check (one line, not a lecture)

Download only what the user owns, what is openly licensed, or what they need for
personal viewing, study, reference or commentary. If the request is plainly to re-upload
someone else's work as their own, or to get around a paywall or DRM, decline that part and
offer the legitimate alternative (link it, study it, remake it on their own topic). yt-dlp
cannot and must not be used to break DRM (Netflix, Disney+, Spotify and the like).

## 1. Make sure the tools are there

```bash
yt-dlp --version || python3 -m pip install -U yt-dlp
ffmpeg -version | head -1
```

- If `yt-dlp` was just installed with pip and is not on PATH, call it as `python3 -m yt_dlp`.
- ffmpeg is needed to merge best video with best audio, convert audio, cut clips and embed
  subtitles/thumbnails. Without it, use `-f b` (a single pre-merged file) and say so.
- Sites change often; when a download fails with an extractor error, run
  `python3 -m pip install -U yt-dlp` (or `yt-dlp -U`) once and retry before anything else.

## 2. Look before downloading (when it matters)

For a single, ordinary "save this video" request, skip straight to step 3. Inspect first
when the user asks for a quality, a language, a playlist, or something big:

```bash
yt-dlp --no-playlist -J "URL" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['title'],'|',d.get('duration_string'),'|',d.get('uploader'))"
yt-dlp -F "URL"              # list every format (resolution, codec, size)
yt-dlp --list-subs "URL"     # list subtitle and auto-caption languages
yt-dlp --flat-playlist --print "%(playlist_index)s %(title)s" "PLAYLIST_URL"
```

## 3. Recipes

Always quote the URL. Use an output template so names are clean and predictable:
`-o "%(title).80B [%(id)s].%(ext)s"` (title trimmed to 80 bytes, id keeps names unique).
Add `-P <folder>` to choose where files go; default to a `downloads/` folder in the
working directory, never the repo's plugin folders.

| Goal | Command |
|------|---------|
| Best quality video, one MP4 | `yt-dlp --no-playlist -f "bv*+ba/b" --merge-output-format mp4 -o "%(title).80B [%(id)s].%(ext)s" "URL"` |
| Cap the resolution (e.g. 1080p) | `yt-dlp --no-playlist -S "res:1080,ext:mp4:m4a" -o "%(title).80B [%(id)s].%(ext)s" "URL"` |
| Smallest reasonable file | `yt-dlp --no-playlist -S "+size,+br,res:480" "URL"` |
| Audio only, MP3 | `yt-dlp --no-playlist -x --audio-format mp3 --audio-quality 0 -o "%(title).80B.%(ext)s" "URL"` |
| Audio only, original quality (no re-encode) | `yt-dlp --no-playlist -f ba -x "URL"` |
| Just one part (clip) | `yt-dlp --no-playlist --download-sections "*01:15-02:30" --force-keyframes-at-cuts "URL"` |
| Subtitles only (human, else auto) | `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*,ar.*" --convert-subs srt "URL"` |
| Video with subtitles embedded | add `--write-subs --sub-langs "en.*" --embed-subs` |
| Thumbnail only | `yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg "URL"` |
| Metadata only (JSON) | `yt-dlp --skip-download --write-info-json "URL"` |
| Whole playlist, numbered | `yt-dlp --yes-playlist -o "%(playlist_title)s/%(playlist_index)03d %(title).80B.%(ext)s" "URL"` |
| Part of a playlist | add `-I 1:10` (items 1–10) or `-I 5,7,9` |
| Channel, newest N videos | `yt-dlp -I :20 "https://www.youtube.com/@handle/videos"` |
| Keep a playlist in sync (skip done ones) | add `--download-archive archive.txt` |
| YouTube Shorts / TikTok / Reels | same as best-quality video; Shorts URLs work as-is |

Useful extras: `--embed-metadata --embed-thumbnail` (tags and cover art in MP3/MP4),
`--restrict-filenames` (ASCII-only names), `--limit-rate 2M`, `--sleep-interval 2`
for long playlists, `-N 4` (parallel fragments for faster downloads).

## 4. Transcript for reading or summarising

When the user wants what the video *says* (to summarise, translate, quote or remake it),
fetch subtitles, not the video:

```bash
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" --sub-format vtt -o "sub" "URL"
python3 - <<'PY'
import re,glob
f=sorted(glob.glob("sub*.vtt"))[0]
seen=[];out=[]
for line in open(f,encoding="utf-8"):
    line=re.sub(r"<[^>]+>","",line).strip()
    if not line or "-->" in line or line.startswith(("WEBVTT","Kind:","Language:")) or line.isdigit(): continue
    if line not in seen[-3:]: out.append(line)
    seen.append(line)
open("transcript.txt","w",encoding="utf-8").write("\n".join(out))
print(len(out),"lines -> transcript.txt")
PY
```

Auto-captions repeat lines; the script above removes the repeats. If the video has no
captions at all, say so; offer to download the audio so it can be transcribed with a
speech-to-text tool (e.g. `pip install openai-whisper`, then `whisper audio.mp3`).

## 5. Feeding make-ai-video

To remake a reference video on the user's own topic: download it at low resolution
(`-S "res:480"`) plus its transcript (step 4), study the pacing, scene count, hook and
caption style, then write a new `project.json` with the `make-ai-video` skill. Use the
reference for structure only; write new words and new pictures.

## 6. When it fails

| Error | Fix |
|-------|-----|
| `Unsupported URL` / extractor error | Update yt-dlp (step 1) and retry once. Check the URL opens in a browser. |
| `Sign in to confirm you're not a bot` / age-restricted / private / members-only | Needs the user's own login. Ask them to run it on their own computer with `--cookies-from-browser chrome` (or firefox, edge, safari). Never ask them to paste cookies or passwords into chat. |
| `HTTP Error 403` / throttled | Update yt-dlp; add `--sleep-interval 3`; try `-f b`. |
| `ffmpeg not found` / no merge | Install ffmpeg, or use `-f b` for a single pre-merged file. |
| Blocked by the network here (proxy refused the host) | This environment cannot reach that site. Tell the user, and give them the exact command to run on their own machine. |
| `Requested format is not available` | Run `yt-dlp -F "URL"` and pick from the list, or loosen `-S` instead of `-f`. |

## 7. Report back

Say in two or three lines: the file name(s), the folder, size, duration and quality
(e.g. "1080p MP4, 42 MB, 3:12"). For a playlist, give the count saved and any that
failed with the reason. If the session runs in the cloud, remind the user the file is in
the cloud container and offer to send it to them; do not commit downloaded media to git.
