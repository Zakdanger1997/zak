#!/usr/bin/env python3
"""Original music bed + sound design for the IRC video, synthesised (no third-party audio), then the mix.

Usage: python3 tools/soundtrack.py     (needs timeline.json and audio/line_*.mp3)
Writes audio/bed.wav (music + effects, ducked under the voice), audio/voice.wav and audio/mix.wav.
"""
import json
import os
import subprocess

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SR = 48000
TL = json.load(open(os.path.join(ROOT, "timeline.json")))
T = TL["total"]
N = int(T * SR)
rng = np.random.default_rng(7)
BPM = 96
BEAT = 60 / BPM


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def tt(d):
    return np.arange(int(d * SR)) / SR


def saw(f, d, harm=18, detune=0.0):
    t = tt(d)
    y = np.zeros_like(t)
    for k in range(1, harm + 1):
        if f * k > 9000:
            break
        y += np.sin(2 * np.pi * f * (1 + detune) * k * t) / k
    return y * 0.6


def env(d, a=0.01, r=0.3, hold=None):
    t = tt(d)
    e = np.minimum(1, t / max(a, 1e-4))
    h = d - r if hold is None else hold
    e *= np.where(t > h, np.clip(1 - (t - h) / r, 0, 1), 1)
    return e


def place(buf, x, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    if x.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        x = np.stack([x * l, x * r], 1)
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * gain


def reverb(x, secs=2.4, wet=0.25):
    ir_n = int(secs * SR)
    t = np.arange(ir_n) / SR
    irs = []
    for s in (11, 12):
        r = np.random.default_rng(s).standard_normal(ir_n) * np.exp(-t * 6.9 / secs)
        irs.append(lp(r, 6000))
    y = np.stack([fftconvolve(x[:, c], irs[c])[:len(x)] for c in range(2)], 1)
    y /= np.max(np.abs(y)) + 1e-9
    return x * (1 - wet) + y * wet * np.max(np.abs(x))


def note(n):                # MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)


# --------------------------------------------------------------- music cues
seg = {s.get("shot") or s.get("still") or ("photos" if s.get("photos") else "end"): s for s in TL["segments"]}
starts = [s["start"] for s in TL["segments"]]
S_STUDIO = TL["segments"][1]["start"]
S_RATIOS = TL["segments"][3]["start"]
S_SPLINE = TL["segments"][4]["start"]
S_HOIST = TL["segments"][5]["start"]
S_WIDE = TL["segments"][6]["start"]
S_PHOTOS = TL["segments"][7]["start"]
S_OPT = TL["segments"][8]["start"]
S_END = TL["segments"][9]["start"]

music = np.zeros((N, 2))
# chords (D minor): Dm, Bb, F, C – two bars each
CH = [[50, 53, 57, 62], [46, 50, 53, 58], [53, 57, 60, 65], [48, 52, 55, 60]]
bar = 4 * BEAT


def chord_at(t):
    return CH[int(((t - S_STUDIO) // (2 * bar)) % 4)] if t >= S_STUDIO else CH[0]


# 1) drone through the whole piece (D1 + A1), swelling into the reveal
d = saw(note(26), T, 10) + 0.6 * saw(note(33), T, 8, 0.002)
d = lp(d, 220)
swell = np.clip(np.arange(N) / SR / S_STUDIO, 0, 1) ** 2
drone_env = 0.5 + 0.5 * swell
place(music, d * drone_env * 0.30, 0)

# 2) heartbeat in the dark opening
for b in np.arange(0.5, S_STUDIO - 0.3, BEAT * 2):
    k = np.sin(2 * np.pi * np.cumsum(np.linspace(70, 38, int(0.4 * SR))) / SR) * env(0.4, 0.002, 0.35)
    place(music, k, b, 0.55)
    place(music, k, b + 0.22, 0.32)

# 3) pads from the reveal on
t0 = S_STUDIO
while t0 < S_END + 1:
    ch = chord_at(t0 + 0.01)
    dur = 2 * bar
    pad = sum(saw(note(n + 12), dur + 1.0, 12, dt) for n in ch for dt in (-0.003, 0.003))
    pad = lp(pad, 1400 if t0 < S_WIDE else 2600) * env(dur + 1.0, 0.8, 1.2)
    lvl = 0.05 if S_OPT <= t0 < S_END else 0.075
    place(music, pad * lvl, t0, pan=0.0)
    t0 += dur

# 4) 8th-note pulse (plucked saw arpeggio)
t0 = S_STUDIO
i = 0
while t0 < S_END:
    if not (S_OPT + 0.5 < t0 < S_END - 1.2):
        ch = chord_at(t0)
        n = ch[[0, 2, 1, 3, 2, 1, 3, 2][i % 8]] + 12
        p = lp(saw(note(n), 0.3, 14), 2200 if t0 > S_WIDE else 1500) * env(0.3, 0.003, 0.26)
        place(music, p, t0, 0.10, pan=0.25 * np.sin(i * 0.8))
    t0 += BEAT / 2
    i += 1

# 5) drums: kick 4/4 from the lineup, hats from the spline, bigger in the lift
def kick():
    f = np.linspace(110, 42, int(0.45 * SR))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.45, 0.001, 0.42)


def hat(d=0.05):
    return hp(rng.standard_normal(int(d * SR)), 7000) * env(d, 0.001, d * 0.9)


def snare():
    n = bp(rng.standard_normal(int(0.25 * SR)), 900, 6000) * env(0.25, 0.001, 0.22)
    tone = np.sin(2 * np.pi * 190 * tt(0.25)) * env(0.25, 0.001, 0.12)
    return n * 0.6 + tone * 0.4


t0 = S_STUDIO + 4 * bar
k = 0
while t0 < S_END - 0.4:
    quiet = S_OPT + 0.4 < t0 < S_END - 0.4
    if not quiet:
        place(music, kick(), t0, 0.42 if t0 > S_WIDE else 0.32)
        if t0 > S_SPLINE:
            place(music, hat(), t0 + BEAT / 2, 0.07, pan=0.3)
        if t0 > S_WIDE and k % 2 == 1:
            place(music, snare(), t0, 0.20)
    t0 += BEAT
    k += 1

music = reverb(music, 2.6, 0.22)

# --------------------------------------------------------------- sound design
fx = np.zeros((N, 2))


def impact(at, g=1.0):
    boom = np.sin(2 * np.pi * np.cumsum(np.linspace(62, 30, int(2.8 * SR))) / SR) * np.exp(-tt(2.8) * 1.6)
    crack = lp(rng.standard_normal(int(0.5 * SR)), 2500) * np.exp(-tt(0.5) * 9)
    place(fx, boom * 0.9, at, g)
    place(fx, crack * 0.35, at, g)


def riser(end, d=2.2, g=0.5):
    n = rng.standard_normal(int(d * SR))
    out = np.zeros_like(n)
    steps = 40
    for j in range(steps):
        a, b = j * len(n) // steps, (j + 1) * len(n) // steps
        f = 400 * (10 ** (j / steps * 1.2))
        out[a:b] = bp(n, f, min(f * 2.5, 20000))[a:b]
    out *= np.linspace(0, 1, len(out)) ** 2
    place(fx, out, end - d, g)


def whoosh(at, g=0.35, pan=0.0):
    d = 0.7
    n = rng.standard_normal(int(d * SR))
    out = np.zeros_like(n)
    for j in range(20):
        a, b = j * len(n) // 20, (j + 1) * len(n) // 20
        f = 300 + 2500 * np.sin(np.pi * j / 20)
        out[a:b] = bp(n, f, f * 1.8)[a:b]
    out *= np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2
    place(fx, out, at - d / 2, g, pan)


def clunk(at, g=0.9):
    d = 0.9
    t = tt(d)
    parts = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dk) * a for f, dk, a in
                ((182, 7, 1.0), (467, 11, 0.6), (913, 16, 0.4), (1630, 24, 0.25), (2710, 30, 0.15)))
    thump = np.sin(2 * np.pi * 68 * t) * np.exp(-t * 14)
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 80)
    place(fx, parts * 0.5 + thump * 0.8 + click * 0.3, at, g)


def machine(start, end, g=0.18, whine=420):
    d = end - start
    t = tt(d)
    hum = sum(np.sin(2 * np.pi * 50 * k * t) / k for k in (1, 2, 3, 4, 6))
    wh = np.sin(2 * np.pi * whine * t + 0.6 * np.sin(2 * np.pi * 7 * t)) * 0.35
    fan = lp(rng.standard_normal(len(t)), 900) * 0.5
    e = np.minimum(1, np.minimum(t / 0.8, (d - t) / 0.8))
    place(fx, lp(hum * 0.5 + wh + fan, 2500) * e, start, g)


impact(S_STUDIO, 0.9)
for s in starts[2:9]:
    whoosh(s, 0.28, pan=rng.uniform(-0.4, 0.4))
riser(S_SPLINE, 2.0, 0.35)
# drum flange seats on the spline: render frame 66 of the spline shot
sp = TL["segments"][4]
src0, src1 = sp["src"]
seat = sp["start"] + (66 / 24 - src0) / (src1 - src0) * (sp["end"] - sp["start"])
clunk(seat, 0.8)
machine(S_HOIST, S_PHOTOS - 0.2, 0.10, 380)
machine(S_WIDE, S_PHOTOS - 0.2, 0.06, 455)
riser(S_END, 2.4, 0.4)
impact(S_END + 0.05, 1.0)
# shimmer on the logo
sh = sum(np.sin(2 * np.pi * note(n) * tt(3.0)) for n in (74, 81, 86, 90)) * np.exp(-tt(3.0) * 1.2) * 0.08
place(fx, sh, S_END + 0.3, 1.0)
fx = reverb(fx, 1.8, 0.18)

# --------------------------------------------------------------- voice track + ducking
voice = np.zeros((N, 2))
active = np.zeros(N)
for v in TL["voice"]:
    p = os.path.join(ROOT, "audio", v["file"])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    x = hp(x, 80)
    place(voice, x, v["start"], 1.0)
    a, b = int(v["start"] * SR), int((v["start"] + v["dur"]) * SR)
    active[a:b] = 1
# smooth duck envelope: -7 dB under the voice, 120 ms attack / 400 ms release
k = int(0.25 * SR)
duck = fftconvolve(active, np.hanning(k) / np.hanning(k).sum(), "same")
duck = 1 - 0.55 * np.clip(duck, 0, 1)

bed = music * duck[:, None] * 0.9 + fx * 0.85
fade = np.minimum(1, np.minimum(np.arange(N) / (0.05 * SR), (N - np.arange(N)) / (1.6 * SR)))
bed *= fade[:, None]


def save(name, x):
    x = x / max(1.0, np.max(np.abs(x)) / 0.98)
    p = os.path.join(ROOT, "audio", name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", p],
                   input=x.astype(np.float32).tobytes(), check=True)
    return p


bed = bed / np.max(np.abs(bed)) * 0.5
voice = voice / np.max(np.abs(voice)) * 0.9
save("bed.wav", bed)
save("voice.wav", voice)
mix = save("mix_raw.wav", bed + voice)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mix, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=disabled",
                "-ar", "48000", "-c:a", "pcm_s16le", os.path.join(ROOT, "audio", "mix.wav")], check=True)
print("wrote audio/mix.wav", round(T, 2), "s; flange seats at", round(seat, 2), "s")
