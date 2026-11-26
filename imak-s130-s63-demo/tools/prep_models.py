#!/usr/bin/env python3
"""Meshes for the S 130 + S 63 demo from the official i.Mak STEP models (i-Guide: 3b_model/S/S 130.step.rar, S 63.step.rar).

Usage: python3 tools/prep_models.py WORK_DIR
WORK_DIR holds "S 130.step" and "S 63.step". Runs imak-mixing-brochure/tools/step_parts.py on each (paint / steel / bore),
then removes the S 130's solid input shaft (x > 158 mm, within 20 mm of the input axis at y = 130, z = 0): in the combination
the S 63 output shaft enters the S 130 worm instead. Writes models/<name>_<part>.stl (binary, STEP millimetres, Y up).
"""
import os
import struct
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SPLIT = os.path.join(ROOT, "..", "imak-mixing-brochure", "tools", "step_parts.py")
W = sys.argv[1]
DT = np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")])


def load(f):
    b = open(f, "rb").read()
    n = struct.unpack("<I", b[80:84])[0]
    return np.frombuffer(b[84:84 + n * 50], dtype=DT).copy()


def save(f, a):
    with open(f, "wb") as fh:
        fh.write(b"i.Mak S130/S63 demo".ljust(80, b" ") + struct.pack("<I", len(a)) + a.tobytes())


for step, name in (("S 130.step", "s130"), ("S 63.step", "s63")):
    out = os.path.join(W, "parts", name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not os.path.exists(out + "_paint.stl"):
        subprocess.run([sys.executable, SPLIT, os.path.join(W, step), out, "--deflection", "0.3"], check=True)
    for part in ("paint", "steel", "bore"):
        a = load(f"{out}_{part}.stl")
        if name == "s130":
            v = a["v"].reshape(-1, 3, 3)
            r = np.hypot(v[:, :, 1] - 130, v[:, :, 2])
            shaft = ((v[:, :, 0] > 158) & (r < 20)).all(axis=1)
            a = a[~shaft]
        save(os.path.join(ROOT, "models", f"{name}_{part}.stl"), a)
        print(name, part, len(a), "triangles")
