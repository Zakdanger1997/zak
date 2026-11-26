#!/usr/bin/env python3
"""PUBLISH_V2.md: TikTok caption, YouTube Shorts title/description and photo credits for every football countdown/versus short.
Usage: python3 tools/v2_publish.py slug [slug ...]"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TAGS = "#football #soccer #footballfacts #shorts"
out = ["# Publishing kit: football countdown & versus shorts", "",
       "Each video is 1080×1920, H.264 + AAC, for TikTok, YouTube Shorts and Reels. Put the credits line in the YouTube description, "
       "or in a pinned comment on TikTok. The flags come from flag-icons (MIT licence).", ""]
for n, slug in enumerate(sys.argv[1:], 1):
    s = json.load(open(os.path.join(ROOT, "data", "v2", f"{slug}.json")))
    head = s["title"].rstrip(".").capitalize()
    out += [f"## {n}. {head}  ·  `video/v2/{slug}.mp4`", ""]
    if s["mode"] == "countdown":
        one = s["items"][-1]
        out += ["**Top 5:** " + " · ".join(f"{i['rank']}. {i['name']} ({i.get('value_label', i['value'])})" for i in s["items"]), "",
                "**TikTok caption**", "", f"> {s['question']} Number 1 will surprise you 👀 Who's missing? 👇 {TAGS}", "",
                "**YouTube Shorts title**", "", f"> {head} – top 5 ⚽ #shorts", "",
                "**YouTube description**", "", f"> {s['question']} {one['name']} tops the list with {one.get('value_label', one['value'])} {s.get('metric', '')}. {s.get('ending', '')}"]
    else:
        out += ["**Head to head:** " + " · ".join(f"{r['label']}: {r['left']}–{r['right']}" for r in s["rows"]), "",
                "**TikTok caption**", "", f"> {s['question']} The numbers settle it ⚔️ Who wins it for you? 👇 {TAGS}", "",
                "**YouTube Shorts title**", "", f"> {head} – who really leads? ⚽ #shorts", "",
                "**YouTube description**", "", f"> {s['verdict']} {s.get('fact', '')}"]
    src = s.get("source", {})
    out += [">", f"> Data: {src.get('title', 'Wikipedia')} ({src.get('url', '')}), as of {src.get('as_of', 'Nov 2026')}."]
    if s.get("credits"):
        out.append("> Photos (Wikimedia Commons): " + "; ".join(f"{c.get('author', '?')}, {c.get('license', '?')} ({c.get('page', '')})" for c in s["credits"]) + ".")
    out += [">", f"> {TAGS}", ""]
open(os.path.join(ROOT, "PUBLISH_V2.md"), "w").write("\n".join(out) + "\n")
print("PUBLISH_V2.md:", len(sys.argv) - 1)
