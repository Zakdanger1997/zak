# Build the corner logo card: i.Mak logo on a white rounded card with a soft shadow.
import sys
from PIL import Image, ImageDraw, ImageFilter
W = 330  # card width in px for a 1080-wide video
logo = Image.open(sys.argv[1]).convert('RGBA')
lw = W - 44
logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
H = logo.height + 36
pad = 16
card = Image.new('RGBA', (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
sh = Image.new('L', card.size, 0)
ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 4, pad + W, pad + H + 4), 22, fill=110)
card.putalpha(sh.filter(ImageFilter.GaussianBlur(8)))
card = Image.composite(Image.new('RGBA', card.size, (0, 0, 0, 255)), Image.new('RGBA', card.size, (0, 0, 0, 0)), card.split()[3])
ImageDraw.Draw(card).rounded_rectangle((pad, pad, pad + W, pad + H), 22, fill=(255, 255, 255, 240))
card.alpha_composite(logo, (pad + 22, pad + 18))
card.save(sys.argv[2])
print(card.size)
