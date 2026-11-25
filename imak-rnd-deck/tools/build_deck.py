#!/usr/bin/env python3
"""Technical restyle of 'Ar-Ge Departmanı Genel Eğitim Sunumu'.

- master: blueprint grid background, red rule under the header strip, technical footer with slide number
- title, 10 section dividers and the closing slide rebuilt in a dark industrial style (assets/div_*.png)
- 8 new technical slides (Turkish): range comparison table, max-torque chart, gearbox anatomy (HUD),
  core formulas, worked selection example, gear geometry, typical efficiencies, bearing life
Data for the table/chart is extracted from the deck's own product slides (10-21); materials on the
anatomy slide come from slide 22. Usage: python3 tools/build_deck.py in.pptx out.pptx
"""
import copy
import math
import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "assets") + "/"
RED, DRED, INK, GREY, LG = RGBColor(0xC0, 0, 0), RGBColor(0x8E, 0x0B, 0x0A), RGBColor(0x1E, 0x22, 0x26), RGBColor(0x5F, 0x66, 0x6D), RGBColor(0xF2, 0xF4, 0xF6)
WHITE = RGBColor(255, 255, 255)
F, FM = "Century Gothic", "Cambria Math"
src, dst = sys.argv[1], sys.argv[2]
prs = Presentation(src)
SW, SH = prs.slide_width, prs.slide_height
slides = list(prs.slides)
ORIG = [s.slide_id for s in slides]


def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()


def tb(slide, text, x, y, w, h, size, color=INK, bold=False, italic=False, font=F, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, lsp=None):
    s = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = s.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if lsp:
            p.line_spacing = lsp
        r = p.add_run(); r.text = line
        f = r.font; f.size, f.bold, f.italic, f.name = Pt(size), bold, italic, font; f.color.rgb = color
        if spacing:
            r._r.get_or_add_rPr().set("spc", str(spacing))
    return s


def rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(lw)
    s.shadow.inherit = False
    return s


def line(slide, x0, y0, x1, y1, color=RED, w=1.0, dash=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(y0), Inches(x1), Inches(y1))
    c.line.color.rgb = color; c.line.width = Pt(w)
    if dash:
        ln = c.line._get_or_add_ln(); pd = etree.SubElement(ln, qn("a:prstDash")); pd.set("val", dash)
    return c


def clear(slide):
    for s in list(slide.shapes):
        s._element.getparent().remove(s._element)
    el = slide._element
    for tag in ("p:timing",):
        t = el.find(qn(tag))
        if t is not None:
            el.remove(t)
    bg = el.cSld.find(qn("p:bg"))
    if bg is not None:
        el.cSld.remove(bg)


def full_pic(slide, path):
    return slide.shapes.add_picture(path, 0, 0, SW, SH)


# ------------------------------------------------------------------ master
master = prs.slide_masters[0]
_, rid = master.part.get_or_add_image_part(A + "blueprint.png")
old = master._element.cSld.find(qn("p:bg"))
if old is not None:
    master._element.cSld.remove(old)
bg = etree.fromstring(f'<p:bg xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                      f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                      f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                      f'<p:bgPr><a:blipFill dpi="0" rotWithShape="1"><a:blip r:embed="{rid}"/><a:srcRect/><a:stretch><a:fillRect/></a:stretch></a:blipFill>'
                      f'<a:effectLst/></p:bgPr></p:bg>')
master._element.cSld.insert(0, bg)
# red rule under the grey header strip + technical footer (title block) on every content slide
scratch = prs.slides.add_slide(master.slide_layouts[0])     # build on a scratch slide, then move into the master
ms = scratch.shapes
rl = ms.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(134559), Emu(150120 + 400110 + 25000), Emu(134559 + 8051504), Emu(150120 + 400110 + 25000))
rl.line.color.rgb = RED; rl.line.width = Pt(1.5)
fl = ms.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.35), Inches(7.2), Inches(12.98), Inches(7.2))
fl.line.color.rgb = RGBColor(0xC9, 0xD2, 0xDA); fl.line.width = Pt(0.75)
ft = ms.add_textbox(Inches(0.35), Inches(7.24), Inches(9), Inches(0.2))
ft.text_frame.margin_left = ft.text_frame.margin_top = 0
r = ft.text_frame.paragraphs[0].add_run(); r.text = "İ-MAK REDÜKTÖR  ·  AR-GE DEPARTMANI  ·  GENEL EĞİTİM SUNUMU  ·  DOK. AR-GE-EĞT-01"
r.font.size, r.font.name = Pt(7.5), F; r.font.color.rgb = GREY; r._r.get_or_add_rPr().set("spc", "100")
pn = ms.add_textbox(Inches(11.4), Inches(7.24), Inches(1.58), Inches(0.2))
pn.text_frame.margin_left = pn.text_frame.margin_top = pn.text_frame.margin_right = 0
p = pn.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
r = p.add_run(); r.text = "SAYFA  "; r.font.size, r.font.name, r.font.bold = Pt(7.5), F, True; r.font.color.rgb = GREY
fld = etree.SubElement(p._p, qn("a:fld")); fld.set("id", "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}"); fld.set("type", "slidenum")
rpr = etree.SubElement(fld, qn("a:rPr")); rpr.set("lang", "tr-TR"); rpr.set("sz", "750"); rpr.set("b", "1")
sf = etree.SubElement(rpr, qn("a:solidFill")); c = etree.SubElement(sf, qn("a:srgbClr")); c.set("val", "C00000")
lt = etree.SubElement(rpr, qn("a:latin")); lt.set("typeface", F)
etree.SubElement(fld, qn("a:t")).text = "‹#›"
for sh in (rl, fl, ft, pn):
    master.shapes._spTree.append(sh._element)
_lst = prs.slides._sldIdLst
_e = _lst[-1]; prs.part.drop_rel(_e.get(qn("r:id"))); _lst.remove(_e)

# ------------------------------------------------------- dark slides
DIV = {7: ("01", "Ürünlerimiz", "12 seri  ·  teknik karşılaştırma  ·  kodlama  ·  redüktör anatomisi"),
       23: ("02", "Ar-Ge Departmanı", "Misyon  ·  değerler  ·  hedefler  ·  organizasyon  ·  görevler"),
       31: ("03", "Kullandığımız Yazılım ve Programlar", "KISSsoft  ·  DraftSight  ·  SOLIDWORKS  ·  CANIAS ERP"),
       36: ("04", "Proje Yönetimi", "Yeni ürün süreci  ·  aşamalı geçit  ·  inovasyon komitesi"),
       40: ("05", "İ-MAK İnovasyon Stratejisi", "Liderlik  ·  savunmacı  ·  verimlilik  ·  pazar bölümlendirme"),
       58: ("06", "Benchmark Çalışmaları", "Rakip ürün gamları, tork ve güç aralıkları"),
       90: ("07", "Redüktör-Motor & Güç Aktarım Elemanları", "Formüller  ·  seçim hesabı  ·  dişli geometrisi  ·  verim  ·  rulman ömrü"),
       122: ("08", "Soğutma Sistemleri", "Eşanjör tipleri  ·  ısıl kapasite tabloları"),
       131: ("09", "Sektörün ve Trendlerin Takibi", "Fuarlar  ·  sektör çalışmaları  ·  web siteleri  ·  dergiler"),
       140: ("10", "I-GUIDE Uygulaması", "Dijital redüktör seçimi ve teknik doküman platformu")}
for idx, (num, title, sub) in DIV.items():
    s = slides[idx]
    clear(s)
    full_pic(s, A + f"div_{num}.png")
    n = tb(s, num, 0.62, 0.55, 5, 2.3, 150, RED, bold=True)
    rp = n.text_frame.paragraphs[0].runs[0]._r.get_or_add_rPr()
    for child in list(rp):
        if child.tag == qn("a:solidFill"):
            rp.remove(child)
    lnx = etree.SubElement(rp, qn("a:ln")); lnx.set("w", "22225"); sfx = etree.SubElement(lnx, qn("a:solidFill")); cx = etree.SubElement(sfx, qn("a:srgbClr")); cx.set("val", "C00000")
    rp.insert(0, lnx); etree.SubElement(rp, qn("a:noFill")); rp.insert(1, rp[-1])
    tb(s, f"BÖLÜM {num}", 0.78, 3.15, 4, 0.35, 13, RED, bold=True, spacing=600)
    rect(s, 0.62, 3.62, 0.07, 1.35, RED)
    tb(s, tr_upper(title), 0.85, 3.55, 6.6, 1.6, 34 if len(title) < 26 else 28, WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE, lsp=0.95)
    tb(s, sub, 0.85, 5.35, 6.4, 0.6, 13, RGBColor(0xB8, 0xBE, 0xC4))

# title slide
s = slides[0]; clear(s); full_pic(s, A + "div_title.png")
s.shapes.add_picture(A + "imak-logo-white.png", Inches(0.75), Inches(0.75), Inches(2.6))
tb(s, "İ-MAK REDÜKTÖR  ·  AR-GE DEPARTMANI", 0.8, 2.35, 7, 0.35, 13, RED, bold=True, spacing=400)
rect(s, 0.62, 2.85, 0.07, 1.9, RED)
tb(s, "GENEL EĞİTİM\nSUNUMU", 0.85, 2.8, 7, 2.0, 54, WHITE, bold=True, lsp=0.9)
tb(s, "Hoş geldiniz", 0.85, 5.0, 6, 0.5, 20, RGBColor(0xB8, 0xBE, 0xC4), italic=True)
tb(s, "Redüktör tasarımı · güç aktarım elemanları · hesap yöntemleri · inovasyon", 0.85, 5.55, 7, 0.4, 12, RGBColor(0x8A, 0x91, 0x98))
# closing slide
s = slides[145]; clear(s); full_pic(s, A + "div_end.png")
s.shapes.add_picture(A + "imak-logo-white.png", Inches(7.9), Inches(1.0), Inches(3.4))
tb(s, "TEŞEKKÜR EDERİZ", 6.4, 3.1, 6.3, 1.0, 44, WHITE, bold=True, align=PP_ALIGN.RIGHT)
rect(s, 12.62, 3.2, 0.07, 0.85, RED)
tb(s, "Hazırlayan: Ozan Çetinkaya\nAr-Ge Departmanı", 6.4, 4.25, 6.1, 0.8, 16, RGBColor(0xB8, 0xBE, 0xC4), align=PP_ALIGN.RIGHT)
tb(s, "www.imakreduktor.com  ·  iguide.imakreduktor.com", 6.4, 5.3, 6.1, 0.4, 12, RED, bold=True, align=PP_ALIGN.RIGHT)

# ------------------------------------------------------- new technical slides
LAYOUT = next(l for l in master.slide_layouts if l.name == "Yalnızca Başlık")
TITLE_EL = next(sh for sh in slides[9].shapes if sh.name == "Metin kutusu 10")._element
NEW = {}


def new_slide(key, header, dark=False):
    s = prs.slides.add_slide(LAYOUT)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    if dark:
        full_pic(s, A + "dark.png")
    t = copy.deepcopy(TITLE_EL)
    s.shapes._spTree.append(t)
    sh = s.shapes[-1]
    p = sh.text_frame.paragraphs[0]
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = header
    if dark:
        p.runs[0].font.color.rgb = WHITE
    NEW[key] = s
    return s


def kicker(s, text, y=0.95, color=RED):
    tb(s, text, 0.35, y, 9, 0.3, 11, color, bold=True, spacing=300)


# T1 range table -------------------------------------------------------------
DATA = [("IR", "Helisel dişli", 12, "2,4 – 852 d/d", "0,12 – 160", 120, 18000),
        ("IRK", "Helisel-konik dişli", 11, "0,17 – 214 d/d", "0,12 – 200", 120, 18000),
        ("YP", "Paralel milli", 10, "2,4 – 391 d/d", "0,12 – 200", 120, 18000),
        ("IRSD", "Helisel-sonsuz vidalı", 5, "3,2 – 370 d/d", "0,09 – 11", 70, 4820),
        ("IRC", "Vinç / kaldırma", 6, "7 – 59 d/d", "0,37 – 45", 120, 19200),
        ("IRNX", "Kovan montajlı", 12, "i = 5 – 30", "0,55 – 450", 190, 42700),
        ("IRS", "Pik gövde sonsuz vidalı", 8, "i = 7,5 – 111", "0,12 – 45", 90, 12500),
        ("S", "Alüminyum gövde sonsuz vidalı", 7, "i = 7,5 – 100", "0,12 – 4", 50, 1500),
        ("IRO", "Kovan montajlı", 5, "i = 5 – 30", "2,2 – 160", 100, 7530),
        ("M (MA/MK)", "Monoblok ağır hizmet", 9, "i = 6 – 511", "0,55 – 560", 180, 70000),
        ("A/AE", "Ağır hizmet tipi", 6, "i = 3,6 – 487", "0,37 – 160", 140, 33000),
        ("AD/ADK", "Roll-form özel tip", 5, "30 – 500 d/d", "2,2 – 90", 80, 8000)]
tr_num = lambda v: f"{v:,}".replace(",", ".")
s = new_slide("T1", "Ar-Ge Departmanı – Ürün Gamı Teknik Karşılaştırma")
kicker(s, "12 SERİ  ·  96 GÖVDE BÜYÜKLÜĞÜ  ·  0,09 – 560 kW  ·  70.000 Nm'YE KADAR")
cols = ["Seri", "Tip", "Gövde", "Çıkış devri / tahvil", "Motor gücü (kW)", "Maks. mil Ø (mm)", "Maks. tork (Nm)"]
widths = [1.35, 3.0, 0.95, 2.1, 1.9, 1.75, 1.6]
tbl = s.shapes.add_table(len(DATA) + 1, len(cols), Inches(0.35), Inches(1.35), Inches(sum(widths)), Inches(5.6)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
def cell(c, text, size=11, bold=False, color=INK, fill=None, align=PP_ALIGN.LEFT):
    c.text = ""; p = c.text_frame.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = str(text); r.font.size, r.font.bold, r.font.name = Pt(size), bold, F; r.font.color.rgb = color
    c.margin_left = c.margin_right = Inches(0.08); c.margin_top = c.margin_bottom = Inches(0.03); c.vertical_anchor = MSO_ANCHOR.MIDDLE
    if fill is not None:
        c.fill.solid(); c.fill.fore_color.rgb = fill
for j, h in enumerate(cols):
    cell(tbl.cell(0, j), h, 11, True, WHITE, RED, PP_ALIGN.CENTER if j > 1 else PP_ALIGN.LEFT)
top = max(d[6] for d in DATA)
for i, row in enumerate(DATA, 1):
    fill = WHITE if i % 2 else LG
    vals = [row[0], row[1], row[2], row[3], row[4], row[5], tr_num(row[6])]
    for j, v in enumerate(vals):
        cell(tbl.cell(i, j), v, 11, j in (0, 6), RED if (j == 6 and row[6] == top) else INK, fill, PP_ALIGN.CENTER if j > 1 else PP_ALIGN.LEFT)
tb(s, "Kaynak: Ar-Ge ürün sayfaları (slayt 10–21).   d/d: çıkış devri (devir/dakika)   ·   i: tahvil oranı", 0.35, 6.98, 10, 0.2, 8, GREY, italic=True)

# T2 torque chart --------------------------------------------------------------
s = new_slide("T2", "Ar-Ge Departmanı – Maksimum Tork Kapasitesi")
kicker(s, "SERİLERE GÖRE MAKSİMUM ÇIKIŞ TORKU (Nm)")
srt = sorted(DATA, key=lambda d: d[6])
cd = CategoryChartData(); cd.categories = [d[0] for d in srt]; cd.add_series("Maks. tork (Nm)", [d[6] for d in srt])
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.35), Inches(1.3), Inches(8.6), Inches(5.75), cd)
ch = gf.chart; ch.has_legend = False; ch.has_title = False; ch.font.size = Pt(10); ch.font.name = F
pl = ch.plots[0]; pl.gap_width = 45; pl.has_data_labels = True
dl = pl.data_labels; dl.number_format = '#,##0'; dl.number_format_is_linked = False; dl.position = XL_LABEL_POSITION.OUTSIDE_END; dl.font.size = Pt(10); dl.font.bold = True
ser = pl.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = RED
for k, d in enumerate(srt):
    if d[6] < 10000:
        pt = ser.points[k]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGBColor(0x9A, 0xA3, 0xAB)
va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xE3, 0xE8)
va.tick_labels.font.size = Pt(9); va.tick_labels.number_format = '#,##0'; va.tick_labels.number_format_is_linked = False; va.maximum_scale = 80000
va.format.line.fill.background()
ch.category_axis.tick_labels.font.size = Pt(10); ch.category_axis.tick_labels.font.bold = True
KPI = [("70.000 Nm", "En yüksek çıkış torku", "M Serisi (MA/MK) monoblok"), ("560 kW", "En yüksek motor gücü", "M Serisi"),
       ("0,17 d/d", "En düşük çıkış devri", "IRK Serisi"), ("190 mm", "En büyük çıkış mili", "IRNX Serisi")]
for k, (big, a, b) in enumerate(KPI):
    y = 1.35 + k * 1.42
    rect(s, 9.35, y, 3.6, 1.25, WHITE, RGBColor(0xD5, 0xDC, 0xE2))
    rect(s, 9.35, y, 0.07, 1.25, RED)
    tb(s, big, 9.6, y + 0.12, 3.2, 0.55, 26, RED, bold=True)
    tb(s, a, 9.6, y + 0.66, 3.2, 0.25, 11, INK, bold=True)
    tb(s, b, 9.6, y + 0.92, 3.2, 0.25, 10, GREY)

# T3 anatomy (dark HUD) -------------------------------------------------------
s = new_slide("T3", "Ar-Ge Departmanı – Redüktör Anatomisi (IRK)", dark=True)
kicker(s, "KESİT GÖRÜNÜŞ  ·  GÜÇ AKIŞI  ·  MALZEMELER", color=RGBColor(0xFF, 0x4D, 0x4D))
BB = (218, 3, 1431, 664); IX, IY, IW = 1.9, 1.75, 7.6
k = IW / (BB[2] - BB[0])
from PIL import Image
im = Image.open(A + "cutaway.png"); im.crop(BB).save(A + "cutaway_crop.png")
s.shapes.add_picture(A + "cutaway_crop.png", Inches(IX), Inches(IY), Inches(IW))
P = lambda ox, oy: (IX + (ox - BB[0]) * k, IY + (oy - BB[1]) * k)
HUD = RGBColor(0xE8, 0xEC, 0xF0)
CALL = [("Havalandırma tapası", (369, 93), (0.3, 1.5)), ("Çıkış dişlisi Z6\n16MnCr5", (410, 236), (0.3, 2.35)),
        ("Kovan (çıkış mili)", (522, 360), (0.3, 3.35)), ("Yağ tapası", (286, 435), (0.3, 4.2)), ("Gövde\nGG22 dökme demir", (286, 560), (0.3, 5.0)),
        ("Rulmanlar", (497, 300), (3.3, 6.25)), ("Konik dişli çifti Z3/Z4\n16MnCr5", (621, 423), (5.0, 6.25)), ("Keçe · Viton (FKM)", (870, 323), (6.75, 6.25)),
        ("Helisel giriş kademesi\nZ1/Z2 · 16MnCr5", (795, 286), (4.6, 1.2)), ("Ara bağlantı mili · Ç1050", (895, 273), (6.9, 1.2)),
        ("Elektrik motoru", (1156, 373), (8.55, 6.25))]
for text, (ox, oy), (lx, ly) in CALL:
    px, py = P(ox, oy)
    ax = lx + 0.05 if lx > 1 else lx + 1.45
    ay = ly - 0.02 if ly > 6 else (ly + 0.33 if ly < 1.5 else ly + 0.12)
    line(s, ax, ay, px, py, RGBColor(0xFF, 0x4D, 0x4D), 1.0)
    d = rect(s, px - 0.06, py - 0.06, 0.12, 0.12, RGBColor(0xFF, 0x4D, 0x4D), WHITE, 1.0, MSO_SHAPE.OVAL)
    tb(s, text, lx, ly, 1.75 if lx < 1 else 2.3, 0.5, 9.5, HUD, bold=True, lsp=0.95)
# power-flow path
pts = [P(1156, 373), P(795, 286), P(621, 423), P(410, 236), P(522, 360)]
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    line(s, x0, y0, x1, y1, RGBColor(0xFF, 0xC2, 0x3D), 2.25, "dash")
# right panel
rect(s, 9.95, 1.2, 3.05, 5.75, RGBColor(0x1A, 0x1E, 0x22), RGBColor(0x3A, 0x41, 0x48))
tb(s, "GÜÇ AKIŞI", 10.15, 1.35, 2.7, 0.3, 11, RGBColor(0xFF, 0xC2, 0x3D), bold=True, spacing=300)
FLOW = [("1", "Elektrik motoru", "giriş: yüksek devir, düşük tork"), ("2", "Z1 / Z2 helisel kademe", "ön redüksiyon"),
        ("3", "Z3 / Z4 konik kademe", "90° yön değişimi"), ("4", "Z5 / Z6 helisel kademe", "son redüksiyon"), ("5", "Kovan çıkış mili", "düşük devir, yüksek tork")]
for i, (n_, a, b) in enumerate(FLOW):
    y = 1.75 + i * 0.62
    rect(s, 10.15, y, 0.34, 0.34, RED, None, 0.75, MSO_SHAPE.OVAL)
    tb(s, n_, 10.15, y + 0.03, 0.34, 0.3, 11, WHITE, bold=True, align=PP_ALIGN.CENTER)
    tb(s, a, 10.6, y - 0.02, 2.35, 0.25, 10, WHITE, bold=True)
    tb(s, b, 10.6, y + 0.22, 2.35, 0.25, 9, RGBColor(0x9A, 0xA3, 0xAB))
tb(s, "MALZEMELER", 10.15, 4.95, 2.7, 0.3, 11, RGBColor(0xFF, 0xC2, 0x3D), bold=True, spacing=300)
tb(s, "Dişliler: 16MnCr5 sementasyon çeliği\nGövde, flanş: GG22 dökme demir\nAra mil: Ç1050\nKeçe: Viton (FKM)", 10.15, 5.28, 2.75, 1.4, 9.5, HUD, lsp=1.15)
tb(s, "Kaynak: slayt 22 kesit çizimi (IRK serisi)", 0.35, 6.98, 6, 0.2, 8, RGBColor(0x8A, 0x91, 0x98), italic=True)


def card(s, x, y, w, h, title, formula, note, fsize=22):
    rect(s, x, y, w, h, WHITE, RGBColor(0xD5, 0xDC, 0xE2))
    rect(s, x, y, w, 0.06, RED)
    tb(s, title, x + 0.2, y + 0.18, w - 0.4, 0.3, 11, RED, bold=True, spacing=150)
    tb(s, formula, x + 0.2, y + 0.55, w - 0.4, h - 1.1, fsize, INK, font=FM, anchor=MSO_ANCHOR.MIDDLE, lsp=1.05)
    tb(s, note, x + 0.2, y + h - 0.55, w - 0.4, 0.45, 9.5, GREY, lsp=1.0)


# T4 formulas -----------------------------------------------------------------
s = new_slide("T4", "İ-MAK Redüktör – Temel Formüller")
kicker(s, "REDÜKTÖR HESAPLARINDA KULLANILAN TEMEL BAĞINTILAR")
FORM = [("TORK", "T = 9550 · P / n", "T [Nm] · P [kW] · n [d/d]"),
        ("TAHVİL ORANI", "i = n₁ / n₂ = z₂ / z₁\ni = i₁ · i₂ · i₃", "n₁ giriş, n₂ çıkış devri · z diş sayısı · çok kademede çarpılır"),
        ("VERİM", "η = η₁ · η₂ · η₃\nP₂ = P₁ · η", "η toplam verim: kademe verimleri çarpılır"),
        ("ÇIKIŞ TORKU", "T₂ = T₁ · i · η\nT₂ = 9550 · P₁ · η / n₂", "Devir düşerken tork aynı oranda artar"),
        ("SERVİS FAKTÖRÜ", "fB = T₂N / T₂ ≥ fS", "T₂N katalog nominal torku · fS uygulama faktörü"),
        ("ÇEVRESEL HIZ", "v = π · d · n / 60 000", "v [m/s] · d [mm] · n [d/d]")]
for k_, (t_, f_, n_) in enumerate(FORM):
    x = 0.35 + (k_ % 3) * 4.25; y = 1.35 + (k_ // 3) * 2.85
    card(s, x, y, 4.05, 2.65, t_, f_, n_)

# T5 worked example -------------------------------------------------------------
s = new_slide("T5", "İ-MAK Redüktör – Redüktör Seçimi: Örnek Hesap")
kicker(s, "UYGULAMA: BANT KONVEYÖR TAHRİĞİ")
rect(s, 0.35, 1.35, 3.6, 5.6, RGBColor(0x1E, 0x22, 0x26))
tb(s, "VERİLER", 0.6, 1.55, 3.1, 0.3, 11, RGBColor(0xFF, 0x4D, 0x4D), bold=True, spacing=300)
GIV = [("Motor gücü", "P₁ = 7,5 kW"), ("Motor devri", "n₁ = 1450 d/d"), ("Tambur devri", "n₂ = 45 d/d"), ("Redüktör", "2 kademeli helisel"),
       ("Kademe verimi", "η ≈ 0,98"), ("Çalışma", "16 saat/gün, orta darbe"), ("Servis faktörü", "fS = 1,4 (örnek)")]
for i, (a, b) in enumerate(GIV):
    y = 2.0 + i * 0.66
    tb(s, a, 0.6, y, 3.1, 0.25, 9.5, RGBColor(0x9A, 0xA3, 0xAB))
    tb(s, b, 0.6, y + 0.24, 3.1, 0.35, 14, WHITE, bold=True, font=FM)
STEP = [("Tahvil oranı", "i = n₁ / n₂ = 1450 / 45 ≈ 32,2"), ("Toplam verim", "η = 0,98² ≈ 0,96"),
        ("Çıkış torku", "T₂ = 9550 · 7,5 · 0,96 / 45 ≈ 1.528 Nm"), ("Gerekli nominal tork", "T₂N ≥ T₂ · fS = 1.528 · 1,4 ≈ 2.139 Nm"),
        ("Seçim", "Katalogdan i ≈ 32 ve T₂N ≥ 2.139 Nm olan gövde seçilir")]
for i, (a, b) in enumerate(STEP):
    y = 1.35 + i * 1.02
    rect(s, 4.2, y, 0.55, 0.55, RED, None, 0.75, MSO_SHAPE.OVAL)
    tb(s, str(i + 1), 4.2, y + 0.1, 0.55, 0.35, 16, WHITE, bold=True, align=PP_ALIGN.CENTER)
    tb(s, a, 4.95, y - 0.02, 4.6, 0.3, 11, RED, bold=True)
    tb(s, b, 4.95, y + 0.28, 4.7, 0.45, 15 if i < 4 else 12.5, INK, bold=i == 3, font=FM if i < 4 else F)
    if i < 4:
        line(s, 4.475, y + 0.58, 4.475, y + 1.0, RGBColor(0xC9, 0xD2, 0xDA), 1.5)
rect(s, 9.85, 1.35, 3.1, 2.3, RED)
tb(s, "SONUÇ", 10.05, 1.5, 2.7, 0.3, 11, WHITE, bold=True, spacing=300)
tb(s, "T₂N ≥ 2.139 Nm\ni ≈ 32", 10.05, 1.9, 2.8, 1.0, 22, WHITE, bold=True, font=FM, lsp=1.0)
tb(s, "Örn. IR / YP serisinden uygun gövde", 10.05, 3.05, 2.8, 0.4, 10, WHITE)
rect(s, 9.85, 3.85, 3.1, 3.1, WHITE, RGBColor(0xD5, 0xDC, 0xE2))
tb(s, "SEÇİM SONRASI KONTROLLER", 10.05, 4.0, 2.8, 0.3, 10, RED, bold=True, spacing=100)
tb(s, "✓  Termik kapasite\n✓  Çıkış mili radyal / eksenel yük\n✓  Montaj pozisyonu ve yağ miktarı\n✓  Ortam: sıcaklık, IP, Ex-proof\n✓  Kalkış sayısı ve fren ihtiyacı",
   10.05, 4.4, 2.8, 2.4, 10.5, INK, lsp=1.35)
tb(s, "Not: fS değeri uygulama tablosundan seçilir; burada örnek amaçlı 1,4 alınmıştır.", 4.2, 6.6, 5.5, 0.3, 9, GREY, italic=True)

# T6 gear geometry ----------------------------------------------------------------
s = new_slide("T6", "İ-MAK Redüktör – Dişli Geometrisi: Temel Bağıntılar")
kicker(s, "EVOLVENT DÜZ / HELİSEL DİŞLİ  ·  STANDART KAVRAMA AÇISI α = 20°")
gi = Image.open(A + "gear_light.png"); gh = 5.6; gw = gh * gi.width / gi.height
if gw > 6.2:
    gw = 6.2; gh = gw * gi.height / gi.width
s.shapes.add_picture(A + "gear_light.png", Inches(0.35), Inches(1.35), Inches(gw), Inches(gh))
GEO = [("Adım", "p = π · m"), ("Bölüm dairesi çapı", "d = m · z"), ("Helisel dişli", "d = mₙ · z / cos β"), ("Diş üstü çapı", "dₐ = d + 2m"),
       ("Diş dibi çapı", "df = d − 2,5m"), ("Eksenler arası mesafe", "a = m · (z₁ + z₂) / 2"), ("Tahvil oranı", "i = z₂ / z₁")]
x0 = 6.95
rect(s, x0, 1.35, 6.0, 3.55, WHITE, RGBColor(0xD5, 0xDC, 0xE2)); rect(s, x0, 1.35, 6.0, 0.06, RED)
for i, (a, b) in enumerate(GEO):
    y = 1.55 + i * 0.47
    tb(s, a, x0 + 0.2, y + 0.06, 2.6, 0.3, 11, GREY)
    tb(s, b, x0 + 2.9, y, 3.0, 0.4, 17, INK, font=FM)
rect(s, x0, 5.1, 6.0, 1.85, RGBColor(0x1E, 0x22, 0x26))
tb(s, "ÖRNEK: ÇİZİMDEKİ DİŞLİ ÇİFTİ", x0 + 0.2, 5.22, 5.6, 0.3, 10.5, RGBColor(0xFF, 0x4D, 0x4D), bold=True, spacing=200)
tb(s, "m = 4  ·  z₁ = 20  ·  z₂ = 48", x0 + 0.2, 5.55, 5.6, 0.35, 15, WHITE, bold=True, font=FM)
tb(s, "d₁ = 80 mm   d₂ = 192 mm\ndₐ₁ = 88 mm   dₐ₂ = 200 mm   df₁ = 70 mm   df₂ = 182 mm\na = 4 · (20 + 48) / 2 = 136 mm   ·   i = 48 / 20 = 2,4",
   x0 + 0.2, 5.95, 5.7, 0.95, 11.5, RGBColor(0xDD, 0xE3, 0xE8), font=FM, lsp=1.1)

# T7 efficiency -------------------------------------------------------------------
s = new_slide("T7", "İ-MAK Redüktör – Dişli Tiplerine Göre Tipik Verim")
kicker(s, "KADEME BAŞINA TİPİK VERİM ARALIKLARI (%)")
EFF = [("Düz / helisel dişli kademesi", 98, 99, "IR, YP, M serileri"), ("Konik dişli kademesi", 97, 98, "IRK, A/AE serileri"),
       ("Planet dişli kademesi", 97, 98, "kompakt, yüksek tork"), ("Sonsuz vida kademesi", 50, 90, "IRSD, IRS, S serileri · tahvil ve hıza bağlı")]
X0, X1, Y0 = 4.3, 12.6, 1.6
scale = lambda v: X0 + (v - 40) / 60 * (X1 - X0)
for v in range(40, 101, 10):
    x = scale(v); line(s, x, Y0 - 0.1, x, Y0 + 4 * 0.95 - 0.2, RGBColor(0xDD, 0xE3, 0xE8), 0.75)
    tb(s, f"%{v}", x - 0.3, Y0 + 4 * 0.95 - 0.12, 0.6, 0.25, 9, GREY, align=PP_ALIGN.CENTER)
for i, (name, a, b, note) in enumerate(EFF):
    y = Y0 + i * 0.95
    tb(s, name, 0.35, y + 0.02, 3.8, 0.3, 12, INK, bold=True)
    tb(s, note, 0.35, y + 0.34, 3.8, 0.3, 9.5, GREY)
    rect(s, X0, y + 0.12, X1 - X0, 0.36, RGBColor(0xEE, 0xF1, 0xF4))
    rect(s, scale(a), y + 0.12, max(0.08, scale(b) - scale(a)), 0.36, RED if b - a < 5 else RGBColor(0xE0, 0x6B, 0x6B))
    tb(s, f"%{a}–{b}", scale(b) + 0.1 if b < 95 else scale(a) - 1.15, y + 0.15, 1.05, 0.3, 11, INK, bold=True, align=PP_ALIGN.LEFT if b < 95 else PP_ALIGN.RIGHT)
CARDS = [("3 KADEMELİ HELİSEL", "η ≈ 0,98³ ≈ %94", "Kayıplar çoğunlukla dişli temasından, yataklardan ve yağ çalkalanmasından gelir."),
         ("SONSUZ VİDA", "η: %50 – 90", "Yüksek tahvil ve düşük hızda verim düşer; otoblokaj eğilimi artar."),
         ("PRATİK SONUÇ", "Pkayıp = P₁ · (1 − η)", "Kayıp güç ısıya dönüşür: termik kapasite ve soğutma bu değerle kontrol edilir.")]
for k_, (t_, f_, n_) in enumerate(CARDS):
    card(s, 0.35 + k_ * 4.25, 5.55, 4.05, 1.45, t_, f_, n_, fsize=15)
for sh in list(s.shapes)[-12:]:
    pass
tb(s, "Tipik literatür değerleridir; kesin değerler ilgili seri kataloğundan alınmalıdır.", 0.35, 7.02, 9, 0.18, 8, GREY, italic=True)

# T8 bearing life -----------------------------------------------------------------
s = new_slide("T8", "İ-MAK Redüktör – Rulman Ömrü Hesabı (ISO 281)")
kicker(s, "NOMİNAL ÖMÜR L₁₀: RULMANLARIN %90'ININ ULAŞTIĞI ÖMÜR")
BF = [("Nominal ömür", "L₁₀ = (C / P)ᵖ   [10⁶ devir]"), ("Saat cinsinden", "L₁₀h = 10⁶ / (60 · n) · L₁₀"), ("Eşdeğer yük", "P = X · Fr + Y · Fa"),
      ("Ömür üssü", "p = 3 bilyalı  ·  p = 10/3 makaralı")]
rect(s, 0.35, 1.35, 6.1, 3.0, WHITE, RGBColor(0xD5, 0xDC, 0xE2)); rect(s, 0.35, 1.35, 6.1, 0.06, RED)
for i, (a, b) in enumerate(BF):
    y = 1.55 + i * 0.68
    tb(s, a, 0.55, y, 5.7, 0.25, 10, GREY)
    tb(s, b, 0.55, y + 0.24, 5.7, 0.4, 17, INK, font=FM)
rect(s, 0.35, 4.55, 6.1, 2.4, RGBColor(0x1E, 0x22, 0x26))
tb(s, "ÖRNEK: KONİK MAKARALI RULMAN", 0.55, 4.68, 5.7, 0.3, 10.5, RGBColor(0xFF, 0x4D, 0x4D), bold=True, spacing=200)
L10 = (52 / 8) ** (10 / 3); L10h = L10 * 1e6 / (60 * 300)
tb(s, "C = 52 kN  ·  P = 8 kN  ·  n = 300 d/d  ·  p = 10/3", 0.55, 5.02, 5.7, 0.35, 13.5, WHITE, bold=True, font=FM)
tb(s, f"L₁₀ = (52 / 8)^(10/3) = 6,5^(3,33) ≈ {L10:.0f} · 10⁶ devir\nL₁₀h = {L10:.0f} · 10⁶ / (60 · 300) ≈ {tr_num(int(round(L10h, -2)))} saat",
   0.55, 5.45, 5.8, 0.8, 12.5, RGBColor(0xDD, 0xE3, 0xE8), font=FM, lsp=1.2)
tb(s, "Yük yarıya inerse ömür ≈ 2^(10/3) ≈ 10 kat artar.", 0.55, 6.45, 5.8, 0.3, 10.5, RGBColor(0xFF, 0xC2, 0x3D), bold=True)
xy = XyChartData(); se = xy.add_series("L10h")
for Pk in [6, 6.5, 7, 7.5, 8, 9, 10, 11, 12, 13, 14, 15, 16]:
    se.add_data_point(Pk, (52 / Pk) ** (10 / 3) * 1e6 / (60 * 300))
gf = s.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_SMOOTH_NO_MARKERS, Inches(6.75), Inches(1.35), Inches(6.2), Inches(5.6), xy)
ch = gf.chart; ch.has_legend = False; ch.font.size = Pt(10); ch.font.name = F
ch.has_title = True; ch.chart_title.text_frame.text = "L₁₀h – eşdeğer yük P   (C = 52 kN, n = 300 d/d)"
ch.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(11); ch.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
sr = ch.plots[0].series[0]; sr.format.line.color.rgb = RED; sr.format.line.width = Pt(2.75); sr.smooth = True
va = ch.value_axis; va.has_major_gridlines = True; va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xE3, 0xE8)
va.tick_labels.number_format = '#,##0'; va.tick_labels.number_format_is_linked = False; va.has_title = True; va.axis_title.text_frame.text = "L₁₀h [saat]"
ca = ch.category_axis; ca.minimum_scale = 6; ca.maximum_scale = 16; ca.has_title = True; ca.axis_title.text_frame.text = "P [kN]"
for ax in (va, ca):
    ax.axis_title.text_frame.paragraphs[0].runs[0].font.size = Pt(10)

# ------------------------------------------------------- order
lst = prs.slides._sldIdLst
ids = {el.get("id"): el for el in lst}
by_slide = {s.slide_id: s for s in prs.slides}
def el_of(slide):
    return next(e for e in lst if int(e.get("id")) == slide.slide_id)
AFTER = {8: ["T1", "T2"], 22: ["T3"], 91: ["T4", "T5"], 93: ["T6", "T7"], 100: ["T8"]}
order = []
for i, sid in enumerate(ORIG):
    order.append(next(e for e in lst if int(e.get("id")) == sid))
    for key in AFTER.get(i, []):
        order.append(el_of(NEW[key]))
for e in list(lst):
    lst.remove(e)
for e in order:
    lst.append(e)
prs.save(dst)
print("saved", dst, len(prs.slides), "slides")
