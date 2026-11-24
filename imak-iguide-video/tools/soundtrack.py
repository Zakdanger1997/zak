#!/usr/bin/env python3
"""Sound for the i-Guide teaser: light beat, crane whir + clunk for every gearbox landing, pops for the fast fill,
typing clicks, whooshes on screen changes, a boom on the button press, shimmer on the end card. All synthesised.
Usage: python3 tools/soundtrack.py -> audio/music.wav (-14 LUFS). Event times must match compose.html.
"""
import os
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR, T = 48000, 14.5
N = int(SR * T)
rng = np.random.default_rng(9)
tt = lambda d: np.arange(int(d * SR)) / SR
lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
hp = lambda x, f: sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
note = lambda n: 440 * 2 ** ((n - 69) / 12)
mix = np.zeros((N, 2))


def place(x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    if x.ndim == 1:
        x = np.stack([x * np.cos((pan + 1) * np.pi / 4), x * np.sin((pan + 1) * np.pi / 4)], 1)
    n = min(len(x), N - i)
    mix[i:i + n] += x[:n] * g


BPM = 112; B = 60 / BPM
kick = np.sin(2 * np.pi * np.cumsum(np.linspace(110, 45, int(.3 * SR))) / SR) * np.exp(-tt(.3) * 10)
hat = lambda: hp(rng.standard_normal(int(.04 * SR)), 8000) * np.exp(-tt(.04) * 80)
CH = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]]
def keys(f, d):
    t = tt(d); return sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + k)) / k ** 1.3 for k in range(1, 6))
t, beat = 0.4, 0
while t < 14.0:
    ch = CH[(beat // 4) % 4]
    if 1.7 < t < 9.1 or t > 10.3:
        if beat % 2 == 0: place(kick, t, .32)
        place(hat(), t + B / 2, .05, .3)
    if beat % 2 == 0:
        for k, n in enumerate(ch):
            place(keys(note(n + 12), 1.2), t + k * B / 4, .045, -.3 + .2 * k)
    place(lp(np.sin(2 * np.pi * note(ch[0] - 24) * tt(B)) * np.exp(-tt(B) * 2), 400), t, .12)
    t += B; beat += 1
# crane whir + clunk per delivery
DROP0, DT, LEN = 2.0, .535, .42 / .78
for i in range(6):
    t0 = DROP0 + i * DT
    d = LEN * .78
    f = np.linspace(180, 120, int(d * SR))
    whir = np.sin(2 * np.pi * np.cumsum(f) / SR) * .5 + bp(rng.standard_normal(len(f)), 300, 1200) * .3
    place(hp(rng.standard_normal(len(f)), 2500) * np.linspace(0, 1, len(f)) ** 2, t0, .05, -.2 + .08 * i)
    cl = lp(rng.standard_normal(int(.25 * SR)), 900) * np.exp(-tt(.25) * 25) + np.sin(2 * np.pi * 90 * tt(.25)) * np.exp(-tt(.25) * 18)
    place(cl, t0 + d, .4)
    place(np.sin(2 * np.pi * 1760 * tt(.15)) * np.exp(-tt(.15) * 30), t0 + d + .05, .05)
for i in range(7):                                                     # fast fill pops
    place(np.sin(2 * np.pi * np.cumsum(np.linspace(600, 1400, int(.08 * SR))) / SR) * np.exp(-tt(.08) * 30), 5.75 + i * .08, .12)
for i in range(12):                                                    # typing
    place(hp(rng.standard_normal(int(.03 * SR)), 2000) * np.exp(-tt(.03) * 120), 6.85 + i * .067 + rng.uniform(0, .015), .2)
for i in range(3):                                                     # file chips
    place(keys(note(76 + i * 4), .6), 8.2 + i * .18, .12)
def whoosh(at, g=.18):
    d = .5; n = rng.standard_normal(int(d * SR)); out = np.zeros_like(n)
    for j in range(16):
        a, b = j * len(n) // 16, (j + 1) * len(n) // 16; f = 500 + 4000 * j / 16
        out[a:b] = bp(n, f, f * 1.7)[a:b]
    place(out * np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2, at - .25, g)
for w in (1.75, 6.6, 9.3):
    whoosh(w)
place(np.sin(2 * np.pi * np.cumsum(np.linspace(70, 32, int(1.8 * SR))) / SR) * np.exp(-tt(1.8) * 2.5), 9.55, .6)
place(hp(rng.standard_normal(int(.3 * SR)), 1500) * np.exp(-tt(.3) * 12), 9.55, .15)
place(np.sin(2 * np.pi * np.cumsum(np.linspace(300, 2400, int(.4 * SR))) / SR) * np.exp(-tt(.4) * 4), 9.62, .08)
for k, n in enumerate((72, 76, 79, 84, 88)):
    place(keys(note(n), 2.0), 10.35 + k * .07, .09, -.4 + .2 * k)
n = int(1.4 * SR); tr = np.arange(n) / SR
irs = [lp(np.random.default_rng(s).standard_normal(n) * np.exp(-tr * 5), 6000) for s in (1, 2)]
wet = np.stack([fftconvolve(mix[:, c], irs[c])[:N] for c in range(2)], 1)
wet *= np.max(np.abs(mix)) / (np.max(np.abs(wet)) + 1e-9)
y = mix * .85 + wet * .15
fade = np.minimum(1, np.minimum(np.arange(N) / (.3 * SR), (N - np.arange(N)) / (1.0 * SR)))
y = y * fade[:, None]; y = y / np.max(np.abs(y)) * .8
raw = os.path.join(ROOT, "audio", "raw.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", raw], input=y.astype(np.float32).tobytes(), check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "pcm_s16le",
                os.path.join(ROOT, "audio", "music.wav")], check=True)
os.remove(raw); print("audio/music.wav")
