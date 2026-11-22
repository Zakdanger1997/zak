#!/usr/bin/env python3
"""Fill in missing frames of a rendered shot by motion-compensated interpolation (ffmpeg minterpolate).

Usage: python3 tools/interp.py SHOT [SHOT ...]
Reads render/<SHOT>/####.png (any regular step, e.g. every 2nd frame of the 24 fps shot) and writes a
complete 24 fps sequence to render/<SHOT>_i/####.png. Frames that were really rendered are copied as they
are; only the gaps are interpolated. compose.js prefers <SHOT>_i when it exists.
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def run(shot):
    src = os.path.join(ROOT, "render", shot)
    frames = sorted(int(f[:4]) for f in os.listdir(src) if f.endswith(".png") and f[:4].isdigit())
    if len(frames) < 3:
        print(shot, "not enough frames")
        return
    step = int(os.environ.get("STEP", 0)) or min(b - a for a, b in zip(frames, frames[1:]))
    frames = [f for f in frames if f % step == 0]
    out = os.path.join(ROOT, "render", shot + "_i")
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(frames):
            os.symlink(os.path.join(src, f"{f:04d}.png"), os.path.join(tmp, f"{i:04d}.png"))
        if step > 1:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(24 / step), "-i", os.path.join(tmp, "%04d.png"),
                            "-vf", "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
                            "-start_number", str(frames[0]), os.path.join(out, "%04d.png")], check=True)
    for f in frames:                                   # keep the real renders untouched
        shutil.copyfile(os.path.join(src, f"{f:04d}.png"), os.path.join(out, f"{f:04d}.png"))
    print(shot, f"step {step}: {len(frames)} rendered ->", len(os.listdir(out)), "frames")


for s in sys.argv[1:]:
    run(s)
