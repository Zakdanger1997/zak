#!/usr/bin/env python3
"""Write PUBLISH.md: for each finished video, the TikTok caption, the YouTube Shorts title + description, and the
photo credits for exactly the players shown (CC BY / BY-SA photos must be credited).
Usage: python3 tools/publish_kit.py slug [slug ...]"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = {p["name"]: p for p in json.load(open(os.path.join(ROOT, "data", "players.json")))}
TAGS = "#football #soccer #stats #footballstats #shorts"
out = ["# Publishing kit: stat-twin shorts", "",
       "Each video is 1080×1920 and 66 s, which works for TikTok, YouTube Shorts and Reels. Post one a day; the order below "
       "starts with the biggest names. Paste the credits into the YouTube description (TikTok: put them in a pinned comment if the caption runs out).",
       ""]
for n, slug in enumerate(sys.argv[1:], 1):
    s = json.load(open(os.path.join(ROOT, "data", f"story_{slug}.json")))
    h, t = s["hero"], s["twins"]
    hero_tag = "#" + "".join(ch for ch in h["name"].split()[-1] if ch.isalnum())
    twin1 = t[0]
    sim = round(twin1["sim"] * 100)
    hook = (f"Nobody has a career like {h['name']}. The closest is only {sim}%." if sim < 60
            else f"{h['name']}'s statistical twin is {twin1['name']} ({sim}% match).")
    out += [f"## {n}. {h['name']}  ·  `video/{slug}-stat-twin.mp4`", "",
            f"**Top five:** " + ", ".join(f"{x['rank']}. {x['name']} {round(x['sim'] * 100)}%" for x in reversed(t)), "",
            "**TikTok caption**", "",
            f"> {h['name']}'s statistical twin 🧬 Who's closest? Who should I do next? 👇 {hero_tag} {TAGS}", "",
            "**YouTube Shorts title**", "", f"> {h['name']}'s Statistical Twin 🧬 #shorts", "",
            "**YouTube description**", "",
            f"> {hook} We compared {s['pool']} legends on five numbers: club goals per game, international goals per cap, "
            f"career goals, career games and seasons. Data: Wikipedia career statistics (official club + international matches), "
            f"as of November 2026. Similarity = standardized distance on the five numbers.", ">",
            "> Photos (Wikimedia Commons):"]
    for name in [h["name"]] + [x["name"] for x in t]:
        p = P[name]
        out.append(f"> {name}: {p.get('photo_author') or 'unknown'}, {p.get('photo_license')}, {p.get('photo_page')}")
    out += [">", f"> {hero_tag} {TAGS}", ""]
open(os.path.join(ROOT, "PUBLISH.md"), "w").write("\n".join(out) + "\n")
print("PUBLISH.md:", len(sys.argv) - 1, "videos")
