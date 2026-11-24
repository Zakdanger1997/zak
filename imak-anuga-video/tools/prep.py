#!/usr/bin/env python3
"""Cut the footage for each scene into 30 fps JPG frames (1920x1080) and prepare the logo.

Usage: python3 tools/prep.py   -> render/fg/<scene>/0000.jpg ..., assets/anugafoodtec_logo_2x.png
Scene list (clip, in-point s, length s) must match SCENES in compose.html.
"""
import json
import os
import subprocess

from PIL import Image, ImageFilter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SC = json.load(open(os.path.join(ROOT, "scenes.json")))
for s in SC["scenes"]:
    if not s.get("clip"):
        continue
    out = os.path.join(ROOT, "render", "fg", s["id"])
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, "0000.jpg")):
        continue
    dur = s["t1"] - s["t0"] + 0.6
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["in"]), "-i", os.path.join(ROOT, "assets", "footage", s["clip"]),
                    "-t", str(dur), "-vf", "fps=30,scale=1920:1080:flags=lanczos,eq=contrast=1.06:saturation=1.08",
                    "-q:v", "3", "-start_number", "0", os.path.join(out, "%04d.jpg")], check=True)
    print(s["id"], len(os.listdir(out)))
lg = Image.open(os.path.join(ROOT, "assets", "anugafoodtec_logo.png")).convert("RGBA")
lg = lg.resize((lg.width * 2, lg.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
lg.save(os.path.join(ROOT, "assets", "anugafoodtec_logo_2x.png"))
