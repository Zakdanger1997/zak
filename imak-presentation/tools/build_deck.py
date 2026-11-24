#!/usr/bin/env python3
"""Apply the requested changes to 'I-MAK Presentation 2025.pptx'.

- simple design: red diagonal master decoration removed (done on the unpacked XML before this script)
- history slides 2 and 3 rebuilt as animated collage infographics (style of the company story video), EGASEN removed
- 233 -> 275 employees
- new slide "Service centres around the globe" (map, partner pins) after "They trust in us"
- fade transitions on every slide, staged entrance animations on every slide (videos keep their playback)
Usage: python3 build_deck.py in.pptx out.pptx
"""
import copy
import json
import re
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

A = "/tmp/claude-0/pptwork/assets/"
CUT = "/home/user/zak/imak-story-video/assets/cut/"
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006"}
P = "{%s}" % NS["p"]
RED = RGBColor(0xCC, 0x06, 0x05)
INK = RGBColor(0x1D, 0x19, 0x15)
GREY = RGBColor(0x5A, 0x55, 0x50)
SERIF = "Cambria"
SANS = "Calibri"
IN = 914400

src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
SW, SH = prs.slide_width, prs.slide_height
slides = list(prs.slides)

# ----------------------------------------------------------------- helpers
ANIM = {}          # slide -> list of steps: [(shape, effect, at_seconds, dur_seconds, extra)]


def anim(slide, shape, effect="fade", at=0.0, dur=0.5, **kw):
    ANIM.setdefault(slide.slide_id, []).append((shape, effect, at, dur, kw))


def tb(slide, text, x, y, w, h, size, font=SANS, bold=False, italic=False, color=INK, align=PP_ALIGN.LEFT,
       spacing=None, anchor=MSO_ANCHOR.TOP, name=None):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = text.split("\n")
    for i, line in enumerate(lines):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = align
        r = par.add_run()
        r.text = line
        f = r.font
        f.size, f.name, f.bold, f.italic = Pt(size), font, bold, italic
        f.color.rgb = color
        if spacing:
            r._r.get_or_add_rPr().set("spc", str(spacing))
    if name:
        s.name = name
    return s


def pic(slide, path, x, y, w=None, h=None, name=None):
    s = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if name:
        s.name = name
    return s


def fit(path, maxw, maxh):
    from PIL import Image
    iw, ih = Image.open(path).size
    k = min(maxw / iw, maxh / ih)
    return iw * k, ih * k


def dot(slide, cx, cy, d, color=RED, line=True):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    if line:
        s.line.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        s.line.width = Pt(1.5)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def XP(expr, el):
    return etree.XPath(expr, namespaces=NS)(el)


def send_to_back(slide, shape):
    tree = slide.shapes._spTree
    tree.remove(shape._element)
    tree.insert(2, shape._element)


def clear_slide(slide, keep=()):
    for s in list(slide.shapes):
        if s.name in keep:
            continue
        s._element.getparent().remove(s._element)


def paper(slide):
    s = pic(slide, A + "paper.jpg", 0, 0, SW / IN, SH / IN, name="Paper background")
    send_to_back(slide, s)
    return s


from PIL import ImageFont
_FB = "/usr/share/fonts/truetype/crosextra/Caladea-Bold.ttf"      # metric twin of Cambria Bold


def text_w(text, size):
    return ImageFont.truetype(_FB, size * 10).getlength(text) / 720


def heading(slide, kicker, black, red_word, x=0.6, y=0.32, size=30, ink=None, at=0.0):
    """One-line collage heading: spaced sans kicker, then '<black> <red_word>' with the red word white on a brush."""
    ink = ink or INK
    k = tb(slide, kicker, x + 0.02, y, 9, 0.3, 12, SANS, bold=True, color=ink, spacing=300)
    lh = size / 72 * 1.25
    ly = y + 0.3
    wb = text_w(black + " ", size) if black else 0
    t1 = tb(slide, black, x, ly, wb + 0.3, lh, size, SERIF, bold=True, color=ink) if black else None
    wr = text_w(red_word, size)
    gap = size / 72 * 0.12
    br = pic(slide, A + "brush1.png", x + wb - gap * 0.3, ly - 0.02, wr + 2.2 * gap, lh * 1.04, name="Brush highlight")
    t2 = tb(slide, red_word, x + wb + gap, ly, wr + 0.3, lh, size, SERIF, bold=True, color=RGBColor(255, 255, 255))
    anim(slide, k, "fade", at, 0.4)
    if t1 is not None:
        anim(slide, t1, "rise", at + 0.1, 0.5)
    anim(slide, br, "wipe", at + 0.45, 0.45)
    anim(slide, t2, "fade", at + 0.7, 0.3)
    return ly + lh


# ----------------------------------------------------------- history slides
HIST = {
    1: ("İ-MAK REDÜKTÖR · OUR STORY", "How it all", "started", [
        ("1973", "Creation of the I-MAK brand.", "logo1973.png"),
        ("1983", "Manufacture of the first industrial gearboxes in Turkey.", "gearbox1983.png"),
        ("1998", "Construction of I-MAK's second factory in Istanbul.", "factory1998.png"),
        ("2000", "Beginning of direct exports.", "export2000.png"),
        ("2012", "Installation of a bar code reading system.", "barcode2012.png")]),
    2: ("İ-MAK REDÜKTÖR · OUR STORY", "Growing", "together", [
        ("2019", "Hudaco – I-MAK mounting center agreement.", "hudaco2019.png"),
        ("2019", "SIPCO – I-MAK mounting center agreement.", "sipco2019.png"),
        ("2022", "Purchase of the I-DÖKSAN foundry.", "foundry2022.png"),
        ("2023", "64,000 m² investment in the new plant.", "plant2023.png"),
        ("2024", "Acceptance to the TURQUALITY programme.", "turquality2024.png")]),
}
corner_logo = {}
for idx, (kick, black, red, items) in HIST.items():
    s = slides[idx]
    # keep only the small corner logo (lowest-right picture)
    pics = [sh for sh in s.shapes if sh.shape_type == 13]
    logo = max(pics, key=lambda q: (q.left + q.top)) if pics else None
    clear_slide(s, keep=(logo.name,) if logo else ())
    paper(s)
    heading(s, kick, black, red)
    LY = 4.05
    line = pic(s, A + "timeline.png", 0.5, LY - 0.6, 12.35, 1.2, name="Timeline line")
    anim(s, line, "wipe", 1.0, 1.6)
    for i, (year, text, img) in enumerate(items):
        cx = 1.55 + i * 2.55
        t0 = 1.5 + i * 0.75
        up = i % 2 == 0
        w, h = fit(CUT + img, 2.0, 1.6)
        py = LY - 0.3 - h if up else LY + 0.3
        ph = pic(s, CUT + img, cx - w / 2, py, w, h, name=f"Milestone {year} photo")
        ph.rotation = (-3, 2.5, -2, 3, -2.5)[i]
        d = dot(s, cx, LY, 0.24)
        ty = LY + 0.32 if up else LY - 1.75
        yr = tb(s, year, cx - 1.2, ty, 2.4, 0.6, 30, SERIF, bold=True, align=PP_ALIGN.CENTER)
        cap = tb(s, text, cx - 1.18, ty + 0.62, 2.36, 0.9, 13, "Cambria", italic=True, color=GREY, align=PP_ALIGN.CENTER)
        anim(s, d, "zoom", t0, 0.35)
        anim(s, ph, "drop", t0 + 0.1, 0.55)
        anim(s, yr, "rise", t0 + 0.3, 0.4)
        anim(s, cap, "fade", t0 + 0.45, 0.4)
    if logo:
        anim(s, logo, "fade", 0.2, 0.4)

# ------------------------------------------------------------ 233 -> 275
for sh in slides[3].shapes:
    if sh.has_text_frame:
        for par in sh.text_frame.paragraphs:
            for r in par.runs:
                if r.text.strip() == "233":
                    r.text = r.text.replace("233", "275")
                    print("employees -> 275")


# --------------------------------------------------------- cover: gears
cover = slides[0]
clear_slide(cover)
G = json.load(open(A + "gears.json"))
ann = pic(cover, A + "gear_annot.png", 0, 0, SW / IN, SH / IN, name="Gear drawing annotations")
gw = {}
for k in ("wheel", "pinion"):
    g = G[k]
    gw[k] = pic(cover, A + f"gear_{k}.png", g["c"][0] - g["size"] / 2, g["c"][1] - g["size"] / 2, g["size"], g["size"],
                name=f"Gear {k}")
lw = 3.6
lg = pic(cover, A + "logo-red.png", 0.75, 1.55, lw, lw * 277 / 934, name="i.Mak logo")
kk = tb(cover, "İ-MAK REDÜKTÖR  ·  ISTANBUL  ·  SINCE 1973", 0.8, 3.0, 6.5, 0.3, 12, SANS, bold=True, color=GREY, spacing=250)
size = 44
lh = size / 72 * 1.25
ty = 3.4
wb = text_w("Gearboxes ", size)
t1 = tb(cover, "Gearboxes", 0.75, ty, wb + 0.3, lh, size, SERIF, bold=True)
wr = text_w("& drives", size)
gap = size / 72 * 0.12
br = pic(cover, A + "brush1.png", 0.75 + wb - gap * 0.3, ty - 0.02, wr + 2.2 * gap, lh * 1.04, name="Brush highlight")
t2 = tb(cover, "& drives", 0.75 + wb + gap, ty, wr + 0.3, lh, size, SERIF, bold=True, color=RGBColor(255, 255, 255))
tag = tb(cover, "Producing powerful solutions since 1973.", 0.8, ty + lh + 0.15, 6, 0.4, 16, "Cambria", italic=True, color=GREY)
web = tb(cover, "www.imakreduktor.com", 0.8, 6.65, 4, 0.3, 12, SANS, bold=True, color=RED, spacing=100)
anim(cover, ann, "fade", 0.0, 1.0)
anim(cover, gw["wheel"], "fade", 0.2, 0.8)
anim(cover, gw["pinion"], "fade", 0.4, 0.8)
for k in ("wheel", "pinion"):
    anim(cover, gw[k], "spin", 0.0, G[k]["period"], dir=G[k]["dir"])
anim(cover, lg, "fade", 0.5, 0.6)
anim(cover, kk, "fade", 0.9, 0.5)
anim(cover, t1, "rise", 1.1, 0.5)
anim(cover, br, "wipe", 1.5, 0.45)
anim(cover, t2, "fade", 1.75, 0.3)
anim(cover, tag, "rise", 2.0, 0.5)
anim(cover, web, "fade", 2.3, 0.5)

# ------------------------------------------------- section dividers
DIV = {9: ("div_products.jpg", "02  ·  PORTFOLIO", "Products &", "solutions", "Gearboxes, geared motors and drive units for every industry."),
       29: ("div_apps.jpg", "03  ·  IN THE FIELD", "Our", "applications", "Where i.Mak drives work every day."),
       39: ("div_thanks.jpg", "İ-MAK REDÜKTÖR", "Thank", "you", "www.imakreduktor.com")}
WHITE = RGBColor(255, 255, 255)
for idx, (img, kick, black, red, sub) in DIV.items():
    s = slides[idx]
    clear_slide(s)
    bg = pic(s, A + img, 0, 0, SW / IN, SH / IN, name="Divider photo")
    ov = pic(s, A + "fade_dark.png", 0, 0, SW / IN, SH / IN, name="Dark overlay")
    lg = pic(s, A + "logo-white.png", 0.75, 0.6, 2.4, 2.4 * 277 / 934, name="i.Mak logo")
    anim(s, bg, "fade", 0.0, 0.8)
    anim(s, ov, "fade", 0.2, 0.6)
    anim(s, lg, "fade", 0.6, 0.5)
    end = heading(s, kick, black, red, x=0.75, y=4.3, size=48, ink=WHITE, at=0.8)
    st = tb(s, sub, 0.78, end + 0.15, 8, 0.4, 18, "Cambria", italic=True, color=RGBColor(0xEE, 0xE8, 0xE0))
    anim(s, st, "rise", 1.9, 0.5)

# ------------------------------------------- slide 4: company in numbers
s = slides[3]
keep_media = [sh for sh in s.shapes if sh.shape_type == 16 or sh.name in ("Resim 1076", "Resim 11", "Resim 1")]
clear_slide(s, keep=tuple(sh.name for sh in keep_media))
heading(s, "İ-MAK REDÜKTÖR  ·  AT A GLANCE", "The company in", "numbers")
STATS = [("275", "employees"), ("65,000", "gearboxes produced per year"), ("16,000 m²", "production plant"),
         ("1,000,000", "product references"), ("3rd", "of 77 exporters in our sector in Türkiye (2017–2021)"),
         ("2nd", "of 22 sector exporters in the Istanbul region (2017–2021)")]
for i, (num, lab) in enumerate(STATS):
    col, row = i % 2, i // 2
    x, y = 0.6 + col * 2.75, 1.7 + row * 1.75
    ln = s.shapes.add_connector(1, Inches(x), Inches(y), Inches(x + 2.35), Inches(y))
    ln.line.color.rgb = RED if i < 4 else INK
    ln.line.width = Pt(2)
    n = tb(s, num, x, y + 0.12, 2.6, 0.7, 34 if len(num) < 8 else 30, SERIF, bold=True, color=RED if i % 3 == 0 else INK)
    l = tb(s, lab, x + 0.02, y + 0.85, 2.4, 0.7, 12.5, "Cambria", italic=True, color=GREY)
    t0 = 1.0 + i * 0.3
    anim(s, ln, "wipe", t0, 0.4)
    anim(s, n, "zoom", t0 + 0.15, 0.4)
    anim(s, l, "fade", t0 + 0.35, 0.4)
for k, sh in enumerate(sh for sh in keep_media if sh.shape_type == 13 and sh.name != "Resim 1"):
    anim(s, sh, "drop", 2.9 + k * 0.25, 0.5)
for sh in keep_media:
    if sh.name == "Resim 1":
        anim(s, sh, "fade", 0.2, 0.4)

# --------------------------- one-line headings on sectors / trust / products
for idx, (kick, black, red) in {4: ("İ-MAK REDÜKTÖR  ·  INDUSTRIES", "Sectors we", "serve"),
                                5: ("İ-MAK REDÜKTÖR  ·  REFERENCES", "They trust", "in us"),
                                10: ("İ-MAK REDÜKTÖR  ·  PORTFOLIO", "Our", "products")}.items():
    s = slides[idx]
    for sh in list(s.shapes):
        if sh.has_text_frame and sh.text_frame.text.strip().upper().strip("\t") in ("SECTORS", "THEY TRUST IN US", "OUR PRODUCTS"):
            sh._element.getparent().remove(sh._element)
    heading(s, kick, black, red, y=0.22, size=28)
    for sh in s.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == "Agriculture":
            sh.left, sh.width = sh.left - Inches(0.3), sh.width + Inches(0.6)
    # staged entrance for the rest (after the heading)
    rest = [sh for sh in s.shapes if sh.name not in ("Brush highlight",) and sh.top > Inches(1.1)]
    rest.sort(key=lambda q: (round(q.top / Inches(0.5)), q.left))
    pics_ = [q for q in rest if q.shape_type == 13]
    texts = [q for q in rest if q.shape_type != 13]
    t = 1.0
    for q in pics_:
        anim(s, q, "zoom" if len(pics_) > 3 else "drop", t, 0.4)
        t += 0.12 if len(pics_) > 8 else 0.25
    for q in texts:
        anim(s, q, "fade", 1.25 + (pics_.index(min(pics_, key=lambda p: abs(p.left + p.width / 2 - q.left - q.width / 2) + abs(p.top - q.top) * 3)) * (0.12 if len(pics_) > 8 else 0.25) if pics_ else 0), 0.35)
    for sh in s.shapes:
        if sh.shape_type == 13 and sh.left > Inches(10.9) and sh.top > Inches(6.5):
            anim(s, sh, "fade", 0.2, 0.4)


# ------------------- slide 10: full-screen video -> online IRK video (YouTube)
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
YT = "https://www.youtube.com/embed/IzF6_iL5BpY?feature=oembed"
s = slides[8]
for sh in s.shapes:
    if sh.shape_type != 16:
        continue
    el, part = sh._element, s.part
    vf = XP(".//a:videoFile", el)[0]
    old = [vf.get("{%s}link" % NS["r"])]
    for ext in XP(".//p:nvPr/p:extLst/p:ext[*[local-name()='media']]", el):
        old.append(ext[0].get("{%s}embed" % NS["r"]))
        ext.getparent().remove(ext)
    vf.set("{%s}link" % NS["r"], part.relate_to(YT, RT.VIDEO, is_external=True))
    blip = XP(".//p:blipFill/a:blip", el)[0]
    old.append(blip.get("{%s}embed" % NS["r"]))
    _, rid = part.get_or_add_image_part(A + "irk_poster.jpg")
    blip.set("{%s}embed" % NS["r"], rid)
    for ext in XP("./a:extLst", blip):
        blip.remove(ext)
    for r in old:
        if r:
            part.drop_rel(r)
    sh.name = "IRK Series - I-MAK Reduktor (YouTube)"
    XP(".//p:cNvPr", el)[0].set("descr", "IRK Series - I-MAK Reduktor, online video: https://youtu.be/IzF6_iL5BpY")
    print("slide 10 video -> YouTube IRK")
# ------------------------------------------- service centres (new slide)
layout = slides[5].slide_layout
ms = prs.slides.add_slide(layout)
for ph in list(ms.placeholders):
    ph._element.getparent().remove(ph._element)
paper(ms)
heading(ms, "İ-MAK REDÜKTÖR · WORLDWIDE", "Service centres", "around the globe", size=36)
D = json.load(open("/home/user/zak/imak-story-video/assets/dealers.json"))
partners = [d for d in D["international"] if d[0] != "EGASEN"]
countries = sorted({d[1].split(", ")[-1] for d in partners})
MX, MY, MW = 2.15, 2.05, 9.9           # map box on the slide (inches); projection -128..152 lon, -48..72 lat
MH = MW * 120 / 280
mp = pic(ms, A + "world.png", MX, MY, MW, MH, name="World map")
anim(ms, mp, "fade", 0.9, 0.8)
proj = lambda lon, lat: (MX + (lon + 128) / 280 * MW, MY + (72 - lat) / 120 * MH)
order = sorted(partners, key=lambda d: (d[2] - 29) ** 2 + (d[3] - 41) ** 2)
for i, (n, where, lon, lat) in enumerate(order):
    x, y = proj(lon, lat)
    big = n.startswith("Sipco") or n.startswith("Bearings International")
    d = dot(ms, x, y, 0.19 if big else 0.12, line=big)
    anim(ms, d, "zoom", 1.9 + i * 0.05, 0.3)
for n, lon, lat in D["turkey_cities"]:
    x, y = proj(lon, lat)
    d = dot(ms, x, y, 0.07, INK, line=False)
    anim(ms, d, "zoom", 1.6, 0.3)
hx, hy = proj(28.98, 41.01)
hq = dot(ms, hx, hy, 0.26, RED)
anim(ms, hq, "zoom", 1.4, 0.4)
lab = []
for txt, lon, lat, dx, dy in (("Istanbul · headquarters & factory", 28.98, 41.01, 0.7, -1.05),
                              ("SIPCO · USA", -95.37, 29.76, -0.55, 0.22),
                              ("Hudaco · South Africa", 28.26, -26.21, 0.22, -0.12)):
    x, y = proj(lon, lat)
    t = tb(ms, txt, x + dx, y + dy, 3.2, 0.35, 13, "Cambria", italic=True, bold=True, color=INK)
    lab.append(t)
from pptx.enum.shapes import MSO_CONNECTOR
ld = ms.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(hx + 0.08), Inches(hy - 0.12), Inches(hx + 0.68), Inches(hy - 0.82))
ld.line.color.rgb = INK
ld.line.width = Pt(1)
anim(ms, ld, "fade", 1.6, 0.4)
for k, t in enumerate(lab):
    anim(ms, t, "fade", 1.6 + k * 0.4 + (2.2 if k else 0), 0.4)
# counters / legend
cnt = tb(ms, f"{len(partners) + D['turkey_count']}", 0.6, 2.6, 1.2, 0.6, 34, SERIF, bold=True)
cl = tb(ms, "partners &\nservice points", 0.62, 3.2, 1.4, 0.6, 12, "Cambria", italic=True, color=GREY)
cnt2 = tb(ms, f"{len(countries) + 1}", 0.6, 4.0, 1.2, 0.6, 34, SERIF, bold=True, color=RED)
cl2 = tb(ms, "countries", 0.62, 4.6, 1.4, 0.4, 12, "Cambria", italic=True, color=GREY)
leg = []
for k, (col, d_, txt) in enumerate(((RED, 0.19, "Assembly & service centres"), (RED, 0.12, "Partners & service points"), (INK, 0.08, "Türkiye network"))):
    yy = 6.25 + k * 0.0
    xx = 7.2 + k * 2.05
    dd = dot(ms, xx, 6.88, d_, col, line=(k == 0))
    tt = tb(ms, txt, xx + 0.18, 6.78, 1.9, 0.3, 11, SANS, color=GREY)
    leg += [dd, tt]
t_end = 1.9 + len(order) * 0.05
for k, sh in enumerate((cnt, cl, cnt2, cl2)):
    anim(ms, sh, "rise", t_end + 0.2 + k * 0.15, 0.4)
for k, sh in enumerate(leg):
    anim(ms, sh, "fade", t_end + 0.6 + k * 0.05, 0.3)
ms.notes_slide.notes_text_frame.text = ("Partner and service locations from imakreduktor.com/business-partners "
                                        "(EGASEN removed). Assembly centres: SIPCO (USA), Hudaco (South Africa).")
# move the new slide right after "They trust in us" (slide 6)
lst = prs.slides._sldIdLst
el = lst[-1]
lst.remove(el)
lst.insert(6, el)
slides = list(prs.slides)

# ------------------------------------------------ generic staged entrances
MEDIA_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/video"


def is_media(sh):
    return bool(XP(".//p:nvPr/a:videoFile|.//p:nvPr/p:extLst//*[local-name()='media']", sh._element))


for s in slides:
    if s.slide_id in ANIM:
        continue
    shapes = [sh for sh in s.shapes if not is_media(sh)]
    if not shapes:
        continue
    title = [sh for sh in shapes if sh.has_text_frame and sh.top < Inches(1.0) and sh.text_frame.text.strip()]
    rest = [sh for sh in shapes if sh not in title]
    rest.sort(key=lambda q: (round(q.top / Inches(0.35)), q.left))
    many = len(rest) > 8
    t = 0.0
    for sh in title:
        anim(s, sh, "rise", t, 0.45)
        t += 0.25
    for sh in rest:
        if sh.shape_type == 13:                       # picture
            eff = "zoom" if (sh.width < Inches(2.6) and many) else "drop"
        elif sh.has_text_frame and len([p for p in sh.text_frame.paragraphs if p.text.strip()]) >= 3:
            eff = "paras"
        else:
            eff = "rise"
        anim(s, sh, eff, t, 0.45)
        t += 0.12 if many else 0.3

# ---------------------------------------------------- timing XML writer
def tgt(spid, para=None):
    if para is None:
        return f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
    return f'<p:tgtEl><p:spTgt spid="{spid}"><p:txEl><p:pRg st="{para}" end="{para}"/></p:txEl></p:spTgt></p:tgtEl>'


def effect_xml(spid, eff, dur, para=None, kw={}):
    d = int(dur * 1000)
    vis = (f'<p:set><p:cBhvr><p:cTn dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
           f'{tgt(spid, para)}<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr>'
           f'<p:to><p:strVal val="visible"/></p:to></p:set>')
    fade = f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn dur="{d}"/>{tgt(spid, para)}</p:cBhvr></p:animEffect>'

    def move(attr, frm, to):
        return (f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn dur="{d}" fill="hold"/>{tgt(spid, para)}'
                f'<p:attrNameLst><p:attrName>{attr}</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
                f'<p:tav tm="0"><p:val><p:strVal val="{frm}"/></p:val></p:tav>'
                f'<p:tav tm="100000"><p:val><p:strVal val="{to}"/></p:val></p:tav></p:tavLst></p:anim>')
    if eff == "fade":
        return 10, 0, vis + fade
    if eff in ("rise", "paras"):
        return 42, 0, vis + fade + move("ppt_y", "#ppt_y+0.04", "#ppt_y")
    if eff == "drop":
        return 42, 0, vis + fade + move("ppt_y", "#ppt_y-0.06", "#ppt_y")
    if eff == "zoom":
        return 53, 16, vis + fade + move("ppt_w", "0", "#ppt_w") + move("ppt_h", "0", "#ppt_h")
    if eff == "spin":
        return 8, 0, (f'<p:animRot by="{21600000 * kw.get("dir", 1)}"><p:cBhvr><p:cTn dur="{d}" fill="hold"/>{tgt(spid)}'
                      f'<p:attrNameLst><p:attrName>r</p:attrName></p:attrNameLst></p:cBhvr></p:animRot>')
    if eff == "wipe":
        return 22, 8, vis + f'<p:animEffect transition="in" filter="wipe(left)"><p:cBhvr><p:cTn dur="{d}"/>{tgt(spid, para)}</p:cBhvr></p:animEffect>'
    raise ValueError(eff)


def build_steps(slide):
    """One <p:par> per effect, each delayed from slide start (all auto, no clicks)."""
    out, bld = [], []
    for sh, eff, at, dur, kw in ANIM.get(slide.slide_id, []):
        spid = sh.shape_id
        targets = [None]
        if eff == "paras":
            n = len(sh.text_frame.paragraphs)
            targets = [i for i in range(n) if sh.text_frame.paragraphs[i].text.strip()]
            bld.append(f'<p:bldP spid="{spid}" grpId="0" build="p"/>')
        elif eff != "spin" and sh.has_text_frame and sh.shape_type != 13:
            bld.append(f'<p:bldP spid="{spid}" grpId="0"/>')
        for k, para in enumerate(targets):
            pid, sub, body = effect_xml(spid, eff, dur, para, kw)
            cls, grp, rep = ("emph", "1", ' repeatCount="indefinite"') if eff == "spin" else ("entr", "0", "")
            delay = int((at + k * 0.18) * 1000)
            out.append(f'<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
                       f'<p:par><p:cTn presetID="{pid}" presetClass="{cls}" presetSubtype="{sub}"{rep} fill="hold" grpId="{grp}" nodeType="withEffect">'
                       f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{body}</p:childTnLst></p:cTn></p:par>'
                       f'</p:childTnLst></p:cTn></p:par>')
    return out, sorted(set(bld))


NSDECL = f'xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"'
for s in slides:
    el = s._element
    steps, bld = build_steps(s)
    timing = el.find(P + "timing")
    if steps:
        if timing is not None and "mediacall" in etree.tostring(timing).decode():
            # keep media playback: add our steps into the auto-start (onBegin) group of the main sequence
            root_par = XP('.//p:cTn[@nodeType="mainSeq"]/p:childTnLst/p:par[p:cTn/p:stCondLst/p:cond[@evt="onBegin"]]/p:cTn/p:childTnLst', timing)
            if root_par:
                for x in steps:
                    root_par[0].append(etree.fromstring(f'<p:wrap {NSDECL}>{x}</p:wrap>')[0])
                if bld:
                    bl = timing.find(P + "bldLst")
                    if bl is None:
                        bl = etree.SubElement(timing, P + "bldLst")
                    for b in bld:
                        bl.append(etree.fromstring(f'<p:wrap {NSDECL}>{b}</p:wrap>')[0])
        else:
            if timing is not None:
                el.remove(timing)
            xml = (f'<p:timing {NSDECL}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
                   f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
                   f'<p:par><p:cTn fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst>'
                   f'<p:childTnLst>{"".join(steps)}</p:childTnLst></p:cTn></p:par>'
                   f'</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                   f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
                   f'</p:childTnLst></p:cTn></p:par></p:tnLst>'
                   + (f'<p:bldLst>{"".join(bld)}</p:bldLst>' if bld else '') + '</p:timing>')
            timing = etree.fromstring(xml)
            el.append(timing)
    # renumber every cTn id (unique, starting at 1)
    if timing is not None:
        for i, c in enumerate(timing.iter(P + "cTn"), 1):
            c.set("id", str(i))
    # transition: one consistent fade (replace whatever was there, incl. mc:AlternateContent wrappers)
    for alt in el.findall("{%s}AlternateContent" % NS["mc"]):
        if XP(".//p:transition", alt):
            el.remove(alt)
    for tr in el.findall(P + "transition"):
        el.remove(tr)
    tr = etree.fromstring(f'<p:transition {NSDECL} spd="med"><p:fade/></p:transition>')
    # order: cSld, clrMapOvr, transition, timing, extLst
    anchor = el.find(P + "timing")
    if anchor is None:
        anchor = el.find(P + "extLst")
    if anchor is not None:
        anchor.addprevious(tr)
    else:
        el.append(tr)

prs.save(dst)
print("saved", dst, "slides", len(slides))
