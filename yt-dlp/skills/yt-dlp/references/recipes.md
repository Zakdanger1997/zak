# yt-dlp recipes

Extra recipes for the `yt-dlp` skill. Every flag here was checked against yt-dlp
2026.10.26 (`yt-dlp --help`). When in doubt, run `yt-dlp --help | grep -A5 -- --flag`.

## Format selection (`-f`)

| Selector | Meaning |
|---|---|
| `bv*+ba/b` | Best video + best audio, merged; fall back to best single file (the default) |
| `bv*[height<=720]+ba/b[height<=720]` | Cap at 720p |
| `bv*[vcodec^=avc1]+ba[acodec^=mp4a]/b[ext=mp4]` | H.264 + AAC, for old players and editors |
| `ba` | Best audio only |
| `ba[ext=m4a]` | Best M4A audio (no re-encode needed for most players) |
| `wv*+wa/w` | Smallest file |
| `137+140` | Exact format IDs from `-F` |

Sort instead of filter: `-S "res:1080,fps,vcodec:h264"` prefers those properties but never
fails just because they are missing.

## Output templates (`-o`)

Useful fields: `%(title)s`, `%(id)s`, `%(uploader)s`, `%(channel)s`, `%(upload_date>%Y-%m-%d)s`,
`%(playlist_title)s`, `%(playlist_index)03d`, `%(duration_string)s`, `%(ext)s`.

- Fallback when a field is missing: `%(artist,uploader)s`
- Default text when missing: `%(series|Unknown)s`
- Truncate: `%(title).100B` (bytes) or `%(title).60s` (characters)
- Separate folders per type: `-P downloads -P "temp:tmp" -P "subtitle:subs" -P "thumbnail:thumbs"`

## Printing info without downloading

```bash
# One line per video in a playlist, with URL
yt-dlp --flat-playlist --print "%(title)s	%(url)s" "PLAYLIST_URL" > list.tsv

# Specific fields as JSON
yt-dlp -j --no-playlist "URL" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['title'], d['view_count'], d['upload_date'])"

# Print the final file path after download (for scripting)
yt-dlp --print after_move:filepath -P downloads "URL"
```

## Clips and chapters

```bash
# Several ranges in one go
yt-dlp --download-sections "*0:00-0:30" --download-sections "*5:00-5:20" "URL"

# From a time to the end
yt-dlp --download-sections "*10:15-inf" "URL"

# Only chapters whose title matches a regex
yt-dlp --download-sections "intro|summary" "URL"

# One file per chapter
yt-dlp --split-chapters -o "chapter:%(title)s/%(section_number)02d - %(section_title)s.%(ext)s" "URL"
```

`--force-keyframes-at-cuts` gives exact cut points (re-encodes around the cuts; slower).
Without it cuts snap to the nearest keyframe.

## Audio

```bash
# MP3 at best VBR quality, with cover and tags
yt-dlp -t mp3 --audio-quality 0 --embed-thumbnail --embed-metadata "URL"

# Other formats: aac, m4a, opus, flac, wav, vorbis, alac
yt-dlp -f ba -x --audio-format m4a "URL"

# Music playlist into Artist/Album folders
yt-dlp -t mp3 --embed-metadata --embed-thumbnail \
  -o "%(artist,uploader)s/%(album,playlist_title)s/%(track_number,playlist_index)02d - %(track,title)s.%(ext)s" "URL"
```

## Subtitles

```bash
yt-dlp --list-subs "URL"                                   # what exists
yt-dlp --skip-download --write-subs --sub-langs "ar,en" "URL"   # uploader subtitles only
yt-dlp --skip-download --write-auto-subs --sub-langs "en" "URL" # auto captions
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en.*" --convert-subs srt "URL"
```

YouTube auto-translated captions are listed as `xx-yy` (e.g. `ar-en` is English
translated to Arabic); request them by that code.

Turn an `.srt` into plain text for reading:

```bash
python3 - "file.en.srt" <<'PY'
import re, sys
lines, last = [], None
for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip()
    if not line or line.isdigit() or "-->" in line:
        continue
    line = re.sub(r"<[^>]+>", "", line)
    if line != last:
        lines.append(line)
    last = line
print("\n".join(lines))
PY
```

## Live streams

```bash
yt-dlp --live-from-start "LIVE_URL"          # from the beginning (YouTube, Twitch)
yt-dlp --wait-for-video 60 "UPCOMING_URL"     # wait for a scheduled stream, retry every 60 s
```

## Logged-in content

On the user's own machine (never in chat):

```bash
yt-dlp --cookies-from-browser firefox "URL"
yt-dlp --cookies-from-browser chrome:"Profile 1" "URL"
yt-dlp --cookies cookies.txt "URL"            # Netscape-format file the user exported
```

Chrome on Windows locks its cookie database while running; close Chrome or use Firefox.

## Speed and politeness

- `-N 4` downloads 4 fragments at once (HLS/DASH) - faster for long videos.
- `-r 2M` caps bandwidth at 2 MB/s.
- `-t sleep` (or `--sleep-interval 5 --max-sleep-interval 15`) between items on big jobs.
- `--download-archive archive.txt` + `--break-on-existing` makes a daily
  "fetch only new uploads" job stop as soon as it reaches something already saved.

## Config file

Defaults the user always wants can go in `~/.config/yt-dlp/config` (Linux/macOS) or
`%APPDATA%\yt-dlp\config.txt` (Windows), one option per line:

```
-P ~/Videos/yt-dlp
-o %(title).150B [%(id)s].%(ext)s
--embed-metadata
--embed-thumbnail
```

`--ignore-config` skips it for one run.
