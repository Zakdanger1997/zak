#!/usr/bin/env python3
"""Build the LinkedIn carousel (PDF, 1080 x 1350 pages) and the video cover image from the recorded video.

Usage: python3 tools/carousel.py [video/drive-handbook-4x5.mp4]
Pages alternate question / answer, taken from frames of the video, with a title page in front.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
VIDEO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "video", "drive-handbook-4x5.mp4")
OUT = os.path.join(ROOT, "linkedin")
# (time in s, small label at the top of the page)
FRAMES = [(1.6, "1 / Question"), (6.9, "1 / Answer"), (11.9, "2 / Planetary"), (17.9, "3 / Question"),
          (23.6, "3 / Answer"), (28.4, "4 / Question"), (33.4, "4 / Answer"), (40.4, "5 / The real unit")]


_TTF = {}


def font(name, size):
    """Brand font from fonts/*.woff2 (converted once with fontTools), DejaVu as a fallback."""
    if name not in _TTF:
        src = os.path.join(ROOT, "fonts", name + ".woff2")
        dst = os.path.join(tempfile.gettempdir(), name + ".ttf")
        try:
            from fontTools.ttLib import TTFont
            f = TTFont(src)
            f.flavor = None
            f.save(dst)
            _TTF[name] = dst
        except Exception:
            _TTF[name] = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(_TTF[name], size)


def frame(t, tmp):
    f = os.path.join(tmp, f"f{t:.1f}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", VIDEO, "-frames:v", "1", f], check=True)
    return Image.open(f).convert("RGB")


def label(im, text):
    d = ImageDraw.Draw(im)
    f = font("barlow-condensed-latin-600-normal", 32)
    w = d.textlength(text, font=f)
    d.rounded_rectangle((im.width - w - 70, 20, im.width - 30, 66), 10, fill=(204, 6, 5))
    d.text((im.width - w - 50, 25), text, font=f, fill="white")
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        title = frame(8.95, tmp)               # the page turn, book seen whole
        d = ImageDraw.Draw(title, "RGBA")
        d.rectangle((0, 0, 1080, 520), fill=(16, 20, 25, 235))
        big = font("barlow-condensed-latin-700-normal", 88)
        small = font("barlow-latin-500-normal", 38)
        y = 90
        for line in ["5 questions every drive", "engineer should answer", "without a calculator"]:
            d.text((70, y), line, font=big, fill="white")
            y += 96
        d.text((72, y + 30), "Guess first. The answer is on the next page.", font=small, fill=(255, 90, 80))
        pages = [title] + [label(frame(t, tmp), lab) for t, lab in FRAMES]
        end = frame(44.5, tmp)
        pages.append(end)
        pages[0].save(os.path.join(OUT, "carousel.pdf"), save_all=True, append_images=pages[1:], resolution=144)
        frame(1.6, tmp).save(os.path.join(OUT, "cover.jpg"), quality=92)
    print("wrote", os.path.join(OUT, "carousel.pdf"), len(pages), "pages and cover.jpg")


if __name__ == "__main__":
    main()
