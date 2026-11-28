#!/usr/bin/env python3
"""Final edit of the YP film: render/yp/*.png (RGBA) on a soft studio gradient (white glow top-left, cool grey falloff,
like the watch reference), motion-interpolated to 24 fps where only every 2nd frame exists, upscaled to 1080x1920,
then a cross-fade into the white end card (assets/endcard.png, from endcard.html) and the soundtrack.
Usage: python3 tools/compose.py  -> video/imak-yp-9x16.mp4"""
import glob
import os
import shutil
import subprocess

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *x: os.path.join(ROOT, *x)
FPS, MAIN, END = 24, 20.0, 3.5
frames = sorted(glob.glob(P("render", "yp", "*.png")))
nums = [int(os.path.basename(f)[:4]) for f in frames]
w, h = Image.open(frames[0]).size

# background gradient
yy, xx = np.mgrid[0:h, 0:w]
d = np.hypot((xx - 0.22 * w) / w, (yy - 0.18 * h) / h * 0.62)
v = np.clip(1 - d * 0.85, 0, 1) ** 1.6
bg = np.zeros((h, w, 3))
for c, (lo, hi) in enumerate(((150, 252), (153, 252), (160, 253))):
    bg[..., c] = lo + (hi - lo) * v
bgi = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")

tmp = P("render", "comp")
shutil.rmtree(tmp, ignore_errors=True)
os.makedirs(tmp)
step = 2 if all(n % 2 == 0 for n in nums) else 1
for i, f in enumerate(frames if step == 1 else [f for f, n in zip(frames, nums) if n % 2 == 0]):
    im = Image.open(f).convert("RGBA")
    out = bgi.copy()
    out.alpha_composite(im)
    out.convert("RGB").save(os.path.join(tmp, f"{i:04d}.png"))

main = P("render", "main.mp4")
import sys  # noqa: E402
SKIP = "--edit-only" in sys.argv and os.path.exists(main)
vf = f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1," if step == 2 else ""
vf += "scale=1080:1920:flags=lanczos,unsharp=5:5:0.4"
if not SKIP:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS // step), "-i", os.path.join(tmp, "%04d.png"),
                "-vf", vf, "-t", str(MAIN), "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", main], check=True)
os.makedirs(P("video"), exist_ok=True)
out = P("video", "imak-yp-9x16.mp4")
fc = (f"[0:v]tpad=stop_mode=clone:stop_duration=1,fps={FPS},format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[a];"
      f"[1:v]fps={FPS},format=yuv420p,setsar=1,settb=AVTB,setpts=PTS-STARTPTS[b];"
      f"[a][b]xfade=transition=fade:duration=0.8:offset={MAIN - 0.4}[v]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", main, "-loop", "1", "-framerate", str(FPS), "-t", str(END + 1),
                "-i", P("assets", "endcard.png"), "-i", P("audio", "soundtrack.wav"),
                "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-t", str(MAIN + END), "-c:v", "libx264", "-crf", "17",
                "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print("->", out)
