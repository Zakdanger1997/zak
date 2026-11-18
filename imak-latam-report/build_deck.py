# i.Mak ihracat erişim raporu (Latin Amerika + Orta Doğu) — düzenlenebilir PowerPoint sunumu (Türkçe).
# Kullanım: python build_deck.py [cikti.pptx]   (gerekli: pip install python-pptx)
import os, sys
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import qn

ROOT = os.path.dirname(os.path.abspath(__file__)); AS = os.path.join(ROOT, 'assets')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'iMak_Erisim_Raporu_TR_18Kasim2026.pptx')

# ----------------------------------------------------------------------------- veriler (buradan düzenle)
D = dict(
    date='18 Kasım 2026',
    la_enrolled=904, la_sent=1223, la_deliv=1200, la_leads=46, la_replies_msg=51, la_reply=5.7,
    la_bounced=23, la_bounce=1.8, la_spam=20, la_scheduled=770,
    me_sent=377, me_deliv=374, me_leads=2, me_reply=1.6, me_bounced=3, me_bounce=0.8, me_spam=0, me_last='12 Kasım',
    sent=1600, deliv=1574, leads=48, bounced=26, spam=20, reply=5.2,
    goal=2000, cap=120, projected='~1.990', topup='~300',
    wa_users='3,3 Mr+', wa_open=95, em_open=22)
DELIV = round(100 * D['deliv'] / D['sent'], 1)       # 98.4
BOUNCE = round(100 * D['bounced'] / D['sent'], 1)     # 1.6
LA_GOAL = round(100 * D['la_sent'] / D['goal'])       # 61
fmt = lambda n: f'{n:,}'.replace(',', '.')            # 1600 -> 1.600
tp = lambda x: '%' + str(x).replace('.', ',')         # 5.7 -> %5,7

# ----------------------------------------------------------------------------- stil
RED = '952414'; RED_D = '6F170C'; RED_L = 'DEAAA0'; INK = '15181E'; CHAR = '232830'; GREY = '5C6470'
MUTE = '8A919C'; LINE = 'E3DED6'; BG = 'F7F5F1'; CARD = 'FFFFFF'; GOLD = 'DDA033'; GREEN = '1F9D6B'
AMBER = 'C9881F'; BAD = 'C0392B'; TRACK = 'ECE7DF'; WHITE = 'FFFFFF'; PALE = 'C9CED6'; WA = '1FA855'
FONT = 'Calibri'
SW, SH = 13.333, 7.5; MX = 0.7; CW = SW - 2 * MX

prs = Presentation(); prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)
BLANK = prs.slide_layouts[6]
rgb = lambda h: RGBColor.from_string(h)

def flat(shape):
    st = shape._element.find(qn('p:style'))
    if st is not None:
        er = st.find(qn('a:effectRef'))
        if er is not None: er.set('idx', '0')
    return shape

def shadow(shape, blur=10, dist=3, alpha=13):
    shape.shadow.inherit = False
    eff = shape._element.spPr.find(qn('a:effectLst'))
    sh = etree.SubElement(eff, qn('a:outerShdw'), blurRad=str(int(blur * 12700)), dist=str(int(dist * 12700)),
                          dir='5400000', algn='t', rotWithShape='0')
    c = etree.SubElement(sh, qn('a:srgbClr'), val='1B1F27'); etree.SubElement(c, qn('a:alpha'), val=str(alpha * 1000))

def box(s, x, y, w, h, fill=None, line=None, lw=0.75, r=None, shape=None, sh=False):
    kind = shape or (MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE)
    b = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None: b.fill.background()
    else: b.fill.solid(); b.fill.fore_color.rgb = rgb(fill)
    if line is None: b.line.fill.background()
    else: b.line.color.rgb = rgb(line); b.line.width = Pt(lw)
    if r and kind == MSO_SHAPE.ROUNDED_RECTANGLE: b.adjustments[0] = min(0.5, r / min(w, h))
    if sh: shadow(b)
    else: b.shadow.inherit = False
    return flat(b)

def _fill_tf(tf, content, size, bold, color, align, font, spc, lsp, italic, after):
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
        if lsp: p.line_spacing = lsp
        if after is not None: p.space_after = Pt(after)
        for rt, pr in (para if isinstance(para, list) else [(para, {})]):
            run = p.add_run(); run.text = rt; f = run.font
            f.name = pr.get('font', font); f.size = Pt(pr.get('size', size)); f.bold = pr.get('bold', bold)
            f.italic = pr.get('italic', italic); f.color.rgb = rgb(pr.get('color', color))
            sp = pr.get('spc', spc)
            if sp is not None: run._r.get_or_add_rPr().set('spc', str(int(sp * 100)))

def text(s, x, y, w, h, content, size=14, bold=False, color=INK, align='l', anchor='t', font=FONT, spc=None,
         lsp=None, italic=False, after=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame
    tf.word_wrap = True; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    _fill_tf(tf, content, size, bold, color, align, font, spc, lsp, italic, after); return tb

def label_in(shape, content, size=14, bold=True, color=WHITE, align='c', anchor='m', spc=None):
    tf = shape.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
    _fill_tf(tf, content, size, bold, color, align, FONT, spc, None, False, None)

def line(s, x1, y1, x2, y2, color=LINE, w=1.0):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(w); return flat(c)

def pic(s, name, x, y, h=None, w=None):
    kw = {}
    if h: kw['height'] = Inches(h)
    if w: kw['width'] = Inches(w)
    return s.shapes.add_picture(os.path.join(AS, name), Inches(x), Inches(y), **kw)

def notes(s, t): s.notes_slide.notes_text_frame.text = t

# --- slayt geçişleri (slide transitions) --------------------------------------
def add_transition(slide, kind='push', direction='l', spd='med'):
    sld = slide.element
    for t in sld.findall(qn('p:transition')): sld.remove(t)
    tr = etree.SubElement(sld, qn('p:transition')); tr.set('spd', spd)
    eff = etree.SubElement(tr, qn('p:' + kind))
    if kind in ('push', 'cover', 'pull', 'wipe', 'cut'): eff.set('dir', direction)
    if kind == 'fade': eff.set('thruBlk', '0')
    sld.remove(tr)
    cm = sld.find(qn('p:clrMapOvr')); cs = sld.find(qn('p:cSld'))
    (cm if cm is not None else cs).addnext(tr)

PAGE = [0]
def content_slide(kicker, title):
    s = prs.slides.add_slide(BLANK); PAGE[0] += 1
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(BG)
    box(s, MX, 0.60, 0.085, 0.80, fill=RED)
    text(s, MX + 0.25, 0.55, 9.5, 0.3, kicker, size=11.5, bold=True, color=RED, spc=1.6)
    text(s, MX + 0.25, 0.80, 10.2, 0.65, title, size=30, bold=True, color=INK)
    pic(s, 'logo_red.png', SW - MX - 1.55, 0.66, h=0.39)
    line(s, MX, 6.98, SW - MX, 6.98, LINE, 0.75)
    text(s, MX, 7.07, 11.0, 0.25, f'i.Mak İhracat Ekibi   ·   İhracat erişimi: Latin Amerika & Orta Doğu   ·   {D["date"]} itibarıyla',
         size=10, color=MUTE)
    text(s, SW - MX - 1, 7.07, 1, 0.25, str(PAGE[0] + 1), size=10, color=MUTE, align='r')
    return s

def card(s, x, y, w, h, fill=CARD, r=0.12, sh=True, line_=None):
    return box(s, x, y, w, h, fill=fill, r=r, sh=sh, line=line_)

def donut(s, x, y, size, pct, color):
    cd = CategoryChartData(); cd.categories = ['value', 'rest']; cd.add_series('share', (pct, max(0.1, 100 - pct)))
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(size), Inches(size), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False
    plot = ch.plots[0]; plot.has_data_labels = False; ser = plot.series[0]
    for i, c in enumerate([color, TRACK]):
        pt = ser.points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(c); pt.format.line.fill.background()
    dn = ch._chartSpace.find('.//' + qn('c:doughnutChart'))
    hs = dn.find(qn('c:holeSize'))
    if hs is None: hs = etree.SubElement(dn, qn('c:holeSize'))
    hs.set('val', '78')
    pa = ch._chartSpace.find('.//' + qn('c:plotArea'))
    lay = pa.find(qn('c:layout'))
    if lay is None: lay = etree.Element(qn('c:layout')); pa.insert(0, lay)
    for child in list(lay): lay.remove(child)
    ml = etree.SubElement(lay, qn('c:manualLayout'))
    for tag, val in (('layoutTarget', 'inner'), ('xMode', 'edge'), ('yMode', 'edge'), ('x', '0.05'), ('y', '0.05'), ('w', '0.9'), ('h', '0.9')):
        etree.SubElement(ml, qn('c:' + tag), val=val)
    sp = etree.Element(qn('c:spPr')); etree.SubElement(sp, qn('a:noFill'))
    ln = etree.SubElement(sp, qn('a:ln')); etree.SubElement(ln, qn('a:noFill'))
    ch._chartSpace.find(qn('c:chart')).addnext(sp)
    return gf

# ============================================================================= 1 · kapak
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(INK)
fb = s.shapes.build_freeform(Inches(9.35), Inches(0))
fb.add_line_segments([(Inches(SW), Inches(0)), (Inches(SW), Inches(SH)), (Inches(8.05), Inches(SH))], close=True)
panel = fb.convert_to_shape(); panel.fill.solid(); panel.fill.fore_color.rgb = rgb(RED); panel.line.fill.background()
panel.shadow.inherit = False; flat(panel)
pic(s, 'logo_white.png', 0.8, 0.72, h=0.56)
text(s, 0.8, 2.15, 8, 0.3, f'KAMPANYA RAPORU   ·   {D["date"].upper()}', size=13, bold=True, color=GOLD, spc=2.2)
box(s, 0.8, 2.58, 0.9, 0.05, fill=GOLD)
text(s, 0.8, 2.82, 8.4, 1.9, ['Latin Amerika &', 'Orta Doğu erişimi'], size=46, bold=True, color=WHITE, lsp=0.96)
text(s, 0.8, 4.95, 7.6, 0.9, 'İki bölgenin sonuçları, dersler — ve yeni bir birebir WhatsApp kanalı',
     size=20, color=PALE, lsp=1.05)
text(s, 0.8, 6.55, 8.0, 0.3, 'i.Mak İhracat Ekibi   ·   Soğuk e-posta + WhatsApp   ·   İspanyolca & İngilizce',
     size=12, color=MUTE)
stats = [(fmt(D['sent']), 'GÖNDERİLEN'), (str(D['leads']), 'MÜŞTERİ ADAYI'),
         (tp(D['reply']), 'YANIT ORANI'), (tp(DELIV), 'İLETİLDİ')]
for i, (v, l) in enumerate(stats):
    yy = 0.95 + i * 1.42
    text(s, 9.7, yy, 3.2, 0.75, v, size=44, bold=True, color=WHITE, align='r')
    text(s, 9.5, yy + 0.74, 3.4, 0.3, l, size=11, bold=True, color='F3D9D4', align='r', spc=1.4)
    if i < 3: line(s, 11.3, yy + 1.22, 12.9, yy + 1.22, 'B8463A', 0.75)
notes(s, f'{D["date"]} itibarıyla rapor; rakamlar her iki aktif kampanyadan (Latin Amerika + Orta Doğu) Apollo üzerinden canlı çekildi. '
         f'Özet: {fmt(D["sent"])} e-posta gönderildi, {D["leads"]} müşteri adayı, {tp(DELIV)} iletildi.')

# ============================================================================= 2 · yönetici özeti
s = content_slide('YÖNETİCİ ÖZETİ', 'Tek slaytta program')
card(s, MX, 1.85, 5.55, 4.85, fill=INK, r=0.16)
text(s, MX + 0.4, 2.15, 4.8, 0.3, 'ÖZET', size=11, bold=True, color=GOLD, spc=2)
text(s, MX + 0.4, 2.5, 4.8, 1.4, [[('1.600 e-postadan ', {}), ('48 aday', {'color': GOLD}), (', iki bölge.', {})]],
     size=30, bold=True, color=WHITE, lsp=0.98)
text(s, MX + 0.4, 3.95, 4.75, 0.9, f'Latin Amerika çalışıyor ({tp(D["la_reply"])} yanıt). Orta Doğu geride kaldı ({tp(D["me_reply"])}) ve '
     f'durdu. Sıradaki kazanç birebir bir WhatsApp kanalı.', size=14.5, color=PALE, lsp=1.08)
line(s, MX + 0.4, 5.25, MX + 5.15, 5.25, '3A404B', 0.75)
for i, (v, l) in enumerate([(tp(D['la_reply']), ['Latin Amerika', 'yanıt oranı']), (tp(D['me_reply']), ['Orta Doğu', 'yanıt oranı']),
                            (D['projected'], ['LatAm tahmini', 'ay sonu'])]):
    xx = MX + 0.4 + i * 1.62
    text(s, xx, 5.42, 1.55, 0.6, v, size=27, bold=True, color=WHITE)
    text(s, xx, 6.0, 1.5, 0.6, l, size=11.5, color=MUTE, lsp=0.95)
rows = [(GREEN, 'Latin Amerika çalışıyor',
         f'{fmt(D["la_sent"])} gönderildi, {D["la_leads"]} aday {tp(D["la_reply"])} yanıtla, {tp(DELIV)} iletildi. {fmt(D["goal"])} hedefi yolunda.'),
        (AMBER, 'Orta Doğu beklentinin altında',
         f'Crane ME: {D["me_sent"]} gönderildi, {D["me_leads"]} aday ({tp(D["me_reply"])}), {D["me_last"]}’dan beri durgun. Yeniden başlat ya da bütçeyi aktar.'),
        (RED, 'Gerçek talep yanıt veriyor',
         f'Loma Negra, Socotherm ve HOC, artı {D["la_leads"] - 3} LatAm yanıtı daha — hattı beslemek için.'),
        (WA, 'Yeni hamle: birebir WhatsApp',
         'Her iki bölge de WhatsApp kullanıyor. Otomatik ama kişisel bir kanal, alıcılara yanıt verdikleri yerde ulaşır.')]
for i, (c, t, b) in enumerate(rows):
    yy = 1.85 + i * 1.235
    card(s, 6.55, yy, 6.08, 1.08, r=0.1)
    box(s, 6.55, yy + 0.12, 0.07, 0.84, fill=c)
    text(s, 6.85, yy + 0.15, 5.6, 0.32, t, size=16, bold=True, color=INK)
    text(s, 6.85, yy + 0.49, 5.65, 0.55, b, size=12.5, color=GREY, lsp=1.0)
notes(s, 'Tek slaytlık özet: Latin Amerika çalışıyor ve hedefinde; Orta Doğu (Crane ME) beklentinin altında kaldı ve durdu, '
         'dolayısıyla bir karar gerekiyor; talep gerçek; sıradaki adım birebir WhatsApp kanalı.')

# ============================================================================= 3 · tüm rakamlar
s = content_slide('SONUÇLAR', 'Tüm rakamlar — iki aktif kampanya')
tiles = [(fmt(D['sent']), 'Gönderilen e-posta', 'iki kampanya', RED),
         (fmt(D['deliv']), 'İletildi', f'{tp(DELIV)} iletim', GREEN),
         (str(D['leads']), 'Müşteri adayı', f'{tp(D["reply"])} yanıt oranı', GOLD),
         (str(D['bounced']), 'Geri dönen', f'{tp(BOUNCE)} — sağlıklı', MUTE)]
tw = (CW - 3 * 0.22) / 4
for i, (v, l, dlt, bar) in enumerate(tiles):
    xx = MX + i * (tw + 0.22)
    card(s, xx, 1.85, tw, 1.5, r=0.1)
    box(s, xx + 0.26, 2.06, 0.46, 0.06, fill=bar)
    text(s, xx + 0.26, 2.2, tw - 0.4, 0.62, v, size=34, bold=True, color=INK)
    text(s, xx + 0.26, 2.84, tw - 0.4, 0.28, l, size=12.5, color=GREY)
    text(s, xx + 0.26, 3.12, tw - 0.4, 0.24, dlt, size=11, bold=True, color=GREY)
ty = 3.72; card(s, MX, ty, CW, 2.95, r=0.14)
colx = [MX + 0.45, MX + 5.7, MX + 7.95, MX + 10.2]
heads = ['', 'LATİN AMERİKA', 'ORTA DOĞU', 'TOPLAM']
for i, h in enumerate(heads):
    text(s, colx[i], ty + 0.26, 2.3, 0.3, h, size=11.5, bold=True, color=RED if i else MUTE, align='l' if i == 0 else 'c', spc=0.5)
text(s, colx[1], ty + 0.52, 2.3, 0.25, 'i.Mak Reductores (ES)', size=9.5, color=MUTE, align='c')
text(s, colx[2], ty + 0.52, 2.3, 0.25, 'Crane ME (EN)', size=9.5, color=MUTE, align='c')
text(s, colx[3], ty + 0.52, 2.3, 0.25, 'iki kampanya', size=9.5, color=MUTE, align='c')
line(s, MX + 0.45, ty + 0.84, MX + CW - 0.45, ty + 0.84, LINE, 1)
trows = [('Gönderilen e-posta', fmt(D['la_sent']), str(D['me_sent']), fmt(D['sent'])),
         ('İletildi', fmt(D['la_deliv']), str(D['me_deliv']), fmt(D['deliv'])),
         ('Müşteri adayı (yanıt)', str(D['la_leads']), str(D['me_leads']), str(D['leads'])),
         ('Yanıt oranı', tp(D['la_reply']), tp(D['me_reply']), tp(D['reply'])),
         ('Geri dönen', str(D['la_bounced']), str(D['me_bounced']), str(D['bounced'])),
         ('Durum', 'Aktif', f'Durgun · {D["me_last"]}', '')]
for r_, (lab, a, b, c) in enumerate(trows):
    yy = ty + 0.98 + r_ * 0.315
    hot = lab in ('Müşteri adayı (yanıt)', 'Yanıt oranı')
    text(s, colx[0], yy, 2.6, 0.3, lab, size=12.5, bold=hot, color=INK if hot else GREY)
    for ci, val in ((1, a), (2, b), (3, c)):
        col = INK
        if lab == 'Durum': col = GREEN if 'Aktif' in val else AMBER
        if lab == 'Yanıt oranı' and ci == 1: col = GREEN
        if lab == 'Yanıt oranı' and ci == 2: col = AMBER
        text(s, colx[ci], yy, 2.3, 0.3, val, size=13 if hot else 12.5, bold=hot or lab == 'Durum', color=col, align='c')
    if r_ < len(trows) - 1: line(s, MX + 0.45, yy + 0.295, MX + CW - 0.45, yy + 0.295, 'EFEAE2', 0.75)
notes(s, f'İki aktif Apollo dizisi. Latin Amerika: {fmt(D["la_sent"])} gönderildi, {D["la_leads"]} aday ({tp(D["la_reply"])}). '
         f'Orta Doğu (Crane ME): {D["me_sent"]} gönderildi, {D["me_leads"]} aday ({tp(D["me_reply"])}), {D["me_last"]}’dan beri durgun. '
         'Üçüncü bir taslak dizi mevcut ama hiç çalıştırılmadı. Yanıt oranı = ulaşılan kişi başına tekil yanıtlayan.')

# ============================================================================= 4 · iki bölge (sütun grafik infografiği)
s = content_slide('SONUÇLAR', 'İki bölge, iki sonuç')
# --- infografik: bölgeye göre yanıt oranı (çizili sütunlar) ---
card(s, MX, 1.95, 6.0, 3.45, r=0.14)
text(s, MX + 0.4, 2.18, 5.2, 0.3, 'YANIT ORANI — BÖLGEYE GÖRE', size=11, bold=True, color=MUTE, spc=1.2)
cols4 = [('Latin\nAmerika', D['la_reply'], GREEN), ('Orta\nDoğu', D['me_reply'], AMBER), ('Toplam', D['reply'], RED)]
base_y = 4.78; top_y = 2.78; maxbar = base_y - top_y; scale = 6.4
line(s, MX + 0.4, base_y, MX + 5.6, base_y, 'D9D3C9', 1.2)
cxs = [MX + 1.35, MX + 3.0, MX + 4.65]
for (lab, v, c), cx in zip(cols4, cxs):
    bh = v / scale * maxbar; cw_ = 0.92
    box(s, cx - cw_ / 2, base_y - bh, cw_, bh, fill=c, r=0.06)
    text(s, cx - 0.8, base_y - bh - 0.42, 1.6, 0.35, tp(v), size=19, bold=True, color=c, align='c')
    text(s, cx - 0.9, base_y + 0.08, 1.8, 0.5, lab.replace('\n', ' '), size=12.5, bold=True, color=INK, align='c', lsp=0.9)
# --- sağ: bölge bilgi kartları ---
rx = MX + 6.25; rw = SW - MX - rx
for j, (title, tag, tagc, sent, leads, extra) in enumerate([
        ('Latin Amerika', 'AKTİF', GREEN, D['la_sent'], D['la_leads'], f'İspanyolca · {fmt(D["goal"])} hedefinde {tp(LA_GOAL)} · {D["la_scheduled"]} sırada'),
        ('Orta Doğu', 'DURGUN', AMBER, D['me_sent'], D['me_leads'], f'Crane ME · İngilizce · {D["me_last"]}’dan beri durgun')]):
    yy = 1.95 + j * 1.75
    card(s, rx, yy, rw, 1.55, r=0.12)
    text(s, rx + 0.35, yy + 0.22, 3.0, 0.3, title, size=17, bold=True, color=INK)
    chip = box(s, rx + rw - 1.5, yy + 0.24, 1.15, 0.32, fill=tagc, r=0.16); label_in(chip, tag, size=9.5, color=WHITE, spc=0.8)
    for k, (vv, ll) in enumerate([(fmt(sent), 'gönderilen'), (str(leads), 'aday'), (tp(D['la_reply'] if j == 0 else D['me_reply']), 'yanıt')]):
        xx = rx + 0.35 + k * 1.55
        text(s, xx, yy + 0.64, 1.5, 0.4, vv, size=21, bold=True, color=tagc if k == 2 else INK)
        text(s, xx, yy + 1.04, 1.5, 0.3, ll, size=10.5, color=GREY)
    text(s, rx + 0.35, yy + 1.26, rw - 0.6, 0.3, extra, size=10, color=MUTE)
card(s, MX, 5.55, CW, 1.12, fill=INK, r=0.14)
text(s, MX + 0.45, 5.72, 3.0, 0.3, 'KARAR GEREKİYOR', size=11, bold=True, color=GOLD, spc=1.8)
text(s, MX + 0.45, 6.02, CW - 0.9, 0.6,
     [[('Crane ME, LatAm’daki ', {}), (f'{tp(D["me_reply"])} ↔ {tp(D["la_reply"])}', {'bold': True, 'color': WHITE}),
       (f' yanıt verdi ve {D["me_last"]}’dan beri durgun. Ya ', {}), ('revize metin ve iletilebilirlik düzeltmesiyle yeniden başlatın', {'bold': True, 'color': WHITE}),
       (', ya da bütçesini Latin Amerika ve yeni WhatsApp kanalına aktarın.', {})]],
     size=13.5, color=PALE, lsp=1.08)
notes(s, 'İki kampanya belirgin biçimde ayrıştı: LatAm %5,7 yanıt, Orta Doğu %1,6 ve 12 Kasım’dan beri durgun. Sütun grafiği bu farkı '
         'gösteriyor; Crane ME için açık kararı (yeniden başlat / yönlendir) saklamadan sunuyoruz.')

# ============================================================================= 5 · huni & oranlar
s = content_slide('SONUÇLAR', 'Gönderimden yanıta: birleşik huni')
fcx = MX + 2.85
for (w, y, fill, big, small, tc) in [(5.7, 1.95, INK, fmt(D['sent']), 'gönderilen e-posta', WHITE),
                                     (5.3, 3.12, RED, fmt(D['deliv']), f'iletildi  ·  {tp(DELIV)}', WHITE),
                                     (2.9, 4.29, GOLD, str(D['leads']), f'aday  ·  {tp(D["reply"])}', INK)]:
    b = box(s, fcx - w / 2, y, w, 0.92, fill=fill, r=0.12)
    label_in(b, [[(big + '   ', {'size': 28}), (small, {'size': 14, 'bold': False})]], color=tc)
for y in (2.90, 4.07):
    tri = box(s, fcx - 0.16, y, 0.32, 0.19, fill=PALE, shape=MSO_SHAPE.ISOSCELES_TRIANGLE); tri.rotation = 180
text(s, MX, 5.33, 5.7, 0.3, [[(f'{D["bounced"]} geri döndü', {'bold': True, 'color': INK}), (f' ({tp(BOUNCE)})      ', {}),
                              (f'{D["spam"]} spam engeli', {'bold': True, 'color': INK}), (' iki kampanya genelinde', {})]],
     size=12, color=GREY, align='c')
dx0 = 6.9; dsz = 1.75; dgap = (SW - MX - dx0 - 3 * dsz) / 2
for i, (pct, col, name, sub) in enumerate([(DELIV, GREEN, 'İletim oranı', f'{fmt(D["deliv"])} / {fmt(D["sent"])} iletildi'),
                                           (D['reply'], RED, 'Yanıt oranı', f'{D["leads"]} aday / ulaşılan kişi'),
                                           (BOUNCE, AMBER, 'Geri dönüş oranı', f'{D["bounced"]} geri döndü — sağlıklı')]):
    xx = dx0 + i * (dsz + dgap)
    donut(s, xx, 2.0, dsz, pct, col)
    text(s, xx, 2.0, dsz, dsz, tp(pct), size=20, bold=True, color=INK, align='c', anchor='m')
    text(s, xx - 0.1, 3.92, dsz + 0.2, 0.3, name, size=15.5, bold=True, color=INK, align='c')
    text(s, xx - 0.1, 4.26, dsz + 0.2, 0.5, sub, size=11, color=GREY, align='c', lsp=1.0)
card(s, MX, 5.78, CW, 0.95, fill=INK, r=0.14)
text(s, MX + 0.4, 5.78, 6.3, 0.95, [[(f'{tp(D["reply"])} yanıt', {'color': GOLD}), (' iki bölgede birden', {})]],
     size=23, bold=True, color=WHITE, anchor='m')
text(s, MX + 6.6, 5.78, CW - 7.0, 0.95, 'Yanıt tek güvenilir sinyal — açılma takibi az mesajda çalıştı, '
     'bu yüzden yönettiğimiz rakam yanıt oranı.', size=12.5, color=PALE, anchor='m', lsp=1.0)
notes(s, 'İki aktif kampanyanın birleşik hunisi: 1.600 gönderildi, 1.574 iletildi (%98,4), 48 aday. Buradaki yanıt oranı ulaşılan '
         'kişi başına tekil yanıtlayan. Halka grafikler düzenlenebilir yerel PowerPoint grafikleridir.')

# ============================================================================= 6 · müşteri adayları
s = content_slide('MÜŞTERİ ADAYLARI', f'{D["leads"]} müşteri adayı — ve önemli isimler')
for i, (v, l, c) in enumerate([(str(D['leads']), 'Toplam aday (yanıt)', RED), (f'{D["la_leads"]} + {D["me_leads"]}', 'LatAm + Orta Doğu', INK),
                               (tp(D['reply']), 'Yanıt oranı (kişi başı)', INK)]):
    yy = 1.9 + i * 1.63
    card(s, MX, yy, 3.55, 1.45, r=0.12)
    text(s, MX + 0.35, yy + 0.2, 3.1, 0.75, v, size=40, bold=True, color=c)
    text(s, MX + 0.35, yy + 0.98, 3.1, 0.3, l, size=13, color=GREY)
tx, tw_ = 4.6, SW - MX - 4.6
card(s, tx, 1.9, tw_, 4.71, r=0.14)
text(s, tx + 0.4, 2.12, 5, 0.3, 'Öne çıkan adaylar', size=16, bold=True, color=INK)
cols = [(tx + 0.4, 'ADAY'), (tx + 3.0, 'SEKTÖR'), (tx + 6.35, 'BÖLGE')]
for cx, h in cols: text(s, cx, 2.68, 3, 0.25, h, size=10.5, bold=True, color=MUTE, spc=1.4)
line(s, tx + 0.4, 2.98, tx + tw_ - 0.4, 2.98, LINE, 1)
leads = [('Loma Negra', 'Çimento (büyük üretici)', 'Arjantin', True), ('Socotherm', 'Boru kaplama / enerji', 'Arjantin', False),
         ('HOC', 'Endüstriyel', 'Latin Amerika', False)]
for i, (n, sec, ctry, hot) in enumerate(leads):
    yy = 3.10 + i * 0.72
    if hot: box(s, tx + 0.22, yy - 0.02, tw_ - 0.44, 0.66, fill='FBEFEA', r=0.08)
    text(s, cols[0][0], yy, 2.6, 0.62, n, size=17, bold=True, color=RED if hot else INK, anchor='m')
    text(s, cols[1][0], yy, 3.3, 0.62, sec, size=14, color=CHAR, anchor='m')
    text(s, cols[2][0], yy, 1.9, 0.62, ctry, size=14, color=CHAR, anchor='m')
    if i < 2: line(s, tx + 0.4, yy + 0.68, tx + tw_ - 0.4, yy + 0.68, LINE, 0.75)
box(s, tx + 0.4, 5.4, tw_ - 0.8, 0.95, fill=BG, r=0.1)
text(s, tx + 0.62, 5.4, tw_ - 1.25, 0.95,
     [[(f'+ {D["la_leads"] - 3} Latin Amerika yanıtı daha', {'bold': True, 'color': INK}),
       (f' ve Orta Doğu’dan {D["me_leads"]} — hepsi satış hattına aktarılacak', {})]],
     size=13.5, color=GREY, anchor='m', lsp=1.05)
notes(s, 'Loma Negra (Arjantin çimento) şimdiye kadarki en yüksek değerli hesap. 46 LatAm + 2 Orta Doğu = toplam 48 aday; '
         'kalanı hatta aktarılacak.')

# ============================================================================= 7 · pazarlar & mesaj
s = content_slide('PAZARLAR & MESAJ', 'İki bölge, iki dil')
def map_card(x, w, title, mapimg, aspect, lang, sectors, subj):
    card(s, x, 1.85, w, 4.85, r=0.14)
    text(s, x + 0.35, 2.05, w - 0.7, 0.3, title, size=17, bold=True, color=INK)
    mh = 2.95; mw = mh * aspect
    pic(s, mapimg, x + (w - mw) / 2, 2.5, h=mh)
    yb = 5.62
    text(s, x + 0.35, yb, w - 0.7, 0.3, [[(lang, {'bold': True, 'color': INK}), ('  ·  ' + sectors, {})]], size=12, color=GREY)
    sb = box(s, x + 0.35, yb + 0.36, w - 0.7, 0.46, fill=INK, r=0.1)
    label_in(sb, [[('KONU  ', {'size': 9, 'color': GOLD, 'spc': 1.2}), (subj, {'size': 12.5})]], color=WHITE, align='l')
    sb.text_frame.margin_left = Inches(0.18)
map_card(MX, 5.85, 'Latin Amerika', 'latam_map.png', 1300 / 1400, 'İspanyolca', 'çimento · madencilik · çelik · gıda · su',
         'Reductores para {{company}}')
map_card(MX + 6.08, 5.85, 'Orta Doğu', 'me_map.png', 1300 / 1118, 'İngilizce', 'vinçler & ağır kaldırma',
         'Gear motors for {{company}}')
notes(s, 'Latin Amerika beş adlandırılmış pazarda İspanyolca yürütüldü (artı İspanyolca konuşan komşular; Brezilya/Portekizce hâlâ açık). '
         'Orta Doğu (Crane ME) İngilizce yürütüldü; Körfez vinç ve ağır kaldırma alıcılarını hedefledi. Harita etiketleri Türkçedir.')

# ============================================================================= 8 · araçlar
s = content_slide('ARAÇLAR', 'Kampanyanın arkasındaki program ve araçlar')
tools = [('Apollo.io', 'VERİ  ·  GÖNDERİM', ['Kişi veritabanı araması', 'E-posta zenginleştirme/bulma', 'Dizi (sequence) oluşturucu', 'Gönderim motoru', 'Analitik']),
         ('Microsoft 365 / Outlook', 'YANITLAR', ['Yanıt yönetimi', 'Yanıt taslakları', 'Kontrol için elle gönderim']),
         ('Python betikleri', 'VERİ HAZIRLIK', ['Liste oluşturma', 'Tekilleştirme: şirkete 1 kişi', 'Kişi-ID → e-posta eşleme', 'Parti (batch) seçimi']),
         ('Claude Code', 'ORKESTRASYON', ['Orkestrasyon', 'Günlük izleme', 'Yanıt eşleme', 'Raporlama ve zamanlama'])]
tw4 = (CW - 3 * 0.22) / 4
for i, (n, tag, d) in enumerate(tools):
    xx = MX + i * (tw4 + 0.22)
    card(s, xx, 1.95, tw4, 3.55, r=0.14)
    box(s, xx, 1.95, tw4, 1.28, fill=INK, r=0.14)
    box(s, xx, 2.75, tw4, 0.48, fill=INK)
    text(s, xx + 0.28, 2.17, tw4 - 0.5, 0.25, tag, size=10, bold=True, color=GOLD, spc=1.4)
    text(s, xx + 0.28, 2.47, tw4 - 0.5, 0.6, n, size=18, bold=True, color=WHITE)
    for j, item in enumerate(d):
        yj = 3.50 + j * 0.385
        box(s, xx + 0.3, yj + 0.095, 0.075, 0.075, fill=RED)
        text(s, xx + 0.5, yj, tw4 - 0.72, 0.3, item, size=12.5, color=CHAR)
card(s, MX, 5.78, CW, 0.95, fill=CARD, r=0.14)
flow = ['Bul & zenginleştir', 'Temizle & tekilleştir', 'Gönder', 'Yanıtla', 'İzle & raporla']
fw = CW / len(flow)
for i, f in enumerate(flow):
    xx = MX + i * fw
    text(s, xx + 0.12, 5.78, fw - 0.24, 0.95, [[(f'{i + 1}   ', {'color': RED, 'bold': True}), (f, {'bold': True})]], size=14, color=INK, anchor='m', align='c')
    if i < len(flow) - 1:
        box(s, xx + fw - 0.1, 6.15, 0.2, 0.21, fill=PALE, shape=MSO_SHAPE.CHEVRON)
notes(s, 'Dört araç tüm döngüyü kapsıyor: Apollo (veri + gönderim), Python (liste hazırlık), Outlook (yanıtlar), Claude Code '
         '(orkestrasyon, izleme, raporlama). WhatsApp, Apollo’nun yanına bir mesajlaşma aracı ekler.')

# ============================================================================= 9 · adım adım
s = content_slide('SÜREÇ', 'Adım adım: nasıl yürüttük')
steps = [('Hedefi tanımla', 'Bölgeye göre endüstriyel alıcılar: LatAm redüktör; Orta Doğu vinç & kaldırma.'),
         ('Kişi listeleri oluştur', 'Apollo’da bölge, sektör ve unvana göre kişi araması.'),
         ('Temizle & tekilleştir', 'Şirket başına bir kişi; tekrarlar ve geçersiz kayıtlar çıkarıldı.'),
         ('E-postaları doğrula', 'Apollo ile doğrulandı; ~500’lük partiler hazırlandı.'),
         ('Metni yaz', 'LatAm için İspanyolca, Orta Doğu için İngilizce, A/B konu başlıkları.'),
         ('Dizileri yapılandır', f'Gönderen “i.Mak Export Team”, günde {D["cap"]} sınırı, kontrollü pencereler.'),
         ('Başlat & günlük izle', 'Gönderilen, iletilen, yanıt, geri dönüş ve spam engelleri.'),
         ('İletilebilirliği koru', 'Sınır sabit tutuldu, spam eğilimi izlendi, itibar zedelenmedi.'),
         ('Adayları yönlendir', 'Her yanıtlayan kutusuna eşlendi; yanıtlar hazırlandı; Bilal CC’lendi.'),
         ('Kontrolleri otomatikleştir', 'Günlük rakamlar, yeni adaylar ve izleme kuralı.')]
cwid = CW / 5
for r_ in range(2):
    yy = 2.05 + r_ * 2.38
    line(s, MX + 0.27, yy + 0.27, MX + 4 * cwid + 0.27, yy + 0.27, 'D9D3C9', 1.5)
    for c_ in range(5):
        i = r_ * 5 + c_; xx = MX + c_ * cwid; t, d = steps[i]
        circ = box(s, xx, yy, 0.54, 0.54, fill=RED, shape=MSO_SHAPE.OVAL)
        label_in(circ, str(i + 1), size=15, color=WHITE)
        text(s, xx, yy + 0.72, cwid - 0.25, 0.32, t, size=14, bold=True, color=INK)
        text(s, xx, yy + 1.06, cwid - 0.3, 1.1, d, size=11, color=GREY, lsp=1.05)
notes(s, 'Her iki bölgede de yürütülen on tekrarlanabilir adım. 7–10. adımlar her gün çalışır.')

# ============================================================================= 10 · zorluklar
s = content_slide('DERSLER', 'Karşılaştığımız altı zorluk')
ch = [('ORTA DOĞU', BAD, 'Crane ME beklenti altında', f'LatAm’daki {tp(D["la_reply"])}’ye karşı {tp(D["me_reply"])} yanıt, {D["me_last"]}’dan beri durgun. Yeni metin ve iletilebilirlik düzeltmesi — ya da yönlendirme gerek.'),
      ('İLETİLEBİLİRLİK', BAD, 'Erken spam-engeli sıçraması', 'LatAm’da spam engelleri erken tırmandı, itibar riski. Sınırı 120’de tutarak kontrol altına alındı.'),
      ('KAPASİTE', AMBER, 'Tek kutu tavanı', 'Tek gönderen ve kutu, güvenli hacmi günde ~120 ile sınırlar — aylık erişimin tavanı.'),
      ('KİŞİLER', AMBER, 'Liste boyutu hedefi sınırlıyor', 'Hız değil, liste boyutu 2.000’e ulaşmayı sınırlıyor. Sürekli kişi temini gerekir.'),
      ('TAKİP', AMBER, 'Zayıf açılma takibi', 'Açılma takibi az mesajda çalıştı. Tek güvenilir sinyal yanıt, bu yüzden huni başı kısmen görünmez.'),
      ('KAPSAM', AMBER, 'Yalnızca İspanyolca — Brezilya yok', 'En büyük LatAm pazarı Brezilya (Portekizce) henüz ele alınmadı.')]
cw3 = (CW - 2 * 0.22) / 3
for i, (tag, col, t, d) in enumerate(ch):
    xx = MX + (i % 3) * (cw3 + 0.22); yy = 1.9 + (i // 3) * 2.46
    card(s, xx, yy, cw3, 2.26, r=0.14)
    box(s, xx, yy + 0.3, 0.07, 1.66, fill=col)
    chip = box(s, xx + 0.32, yy + 0.28, 0.42 + 0.085 * len(tag), 0.29, fill=col, r=0.145)
    label_in(chip, tag, size=9.5, color=WHITE, spc=1.0)
    text(s, xx + 0.32, yy + 0.72, cw3 - 0.6, 0.35, t, size=16, bold=True, color=INK)
    text(s, xx + 0.32, yy + 1.12, cw3 - 0.62, 1.05, d, size=11.5, color=GREY, lsp=1.06)
notes(s, 'Kırmızı etiketler en büyük iki sorun: Orta Doğu sonucu ve erken LatAm iletilebilirlik riski (kontrol altında). '
         'Sarı etiketler süregelen kısıtlar.')

# ============================================================================= 11 · YENİ — WhatsApp birebir
s = content_slide('YENİ KANAL', 'Birebir bir WhatsApp kanalı ekleyin')
card(s, MX, 1.9, 5.5, 4.08, fill=INK, r=0.16)
wb = box(s, MX + 0.4, 2.18, 0.5, 0.5, fill=WA, r=0.14); label_in(wb, 'W', size=22, color=WHITE)
text(s, MX + 1.02, 2.2, 4.0, 0.5, 'Neden WhatsApp', size=20, bold=True, color=WHITE, anchor='m')
text(s, MX + 0.4, 2.86, 4.8, 0.8, 'Her iki bölge de işini WhatsApp üzerinden yürütüyor. E-posta birkaç yüzde yanıt alır; '
     'WhatsApp’ta alıcılar dakikalar içinde yanıtlar.', size=13.5, color=PALE, lsp=1.08)
# --- infografik: açılma oranı karşılaştırma çubukları ---
text(s, MX + 0.4, 3.86, 4.8, 0.25, 'AÇILMA ORANI*', size=10, bold=True, color=GOLD, spc=1.4)
bar_x = MX + 1.45; bar_w = 3.35
for k, (nm, val, col) in enumerate([('WhatsApp', D['wa_open'], WA), ('E-posta', D['em_open'], '6B7078')]):
    yy = 4.2 + k * 0.5
    text(s, MX + 0.4, yy - 0.02, 1.0, 0.3, nm, size=12, bold=True, color=WHITE, anchor='m')
    box(s, bar_x, yy, bar_w, 0.3, fill='2C333F', r=0.15)
    fillw = bar_w * val / 100.0
    box(s, bar_x, yy, fillw, 0.3, fill=col, r=0.15)
    if k == 0: text(s, bar_x, yy, fillw - 0.15, 0.3, '~' + tp(val), size=12, bold=True, color=WHITE, align='r', anchor='m')
    else: text(s, bar_x + fillw + 0.1, yy, 1.2, 0.3, '~' + tp(val), size=12, bold=True, color=PALE, anchor='m')
line(s, MX + 0.4, 5.3, MX + 5.1, 5.3, '2C333F', 0.75)
for i, (v, l) in enumerate([(D['wa_users'], ['WhatsApp', 'kullanıcısı']), ('#1', ['iş uygulaması', 'iki bölgede de'])]):
    xx = MX + 0.4 + i * 2.45
    text(s, xx, 5.42, 2.3, 0.4, v, size=22, bold=True, color=WHITE)
    text(s, xx + (1.15 if i == 0 else 0.75), 5.46, 2.2, 0.5, l, size=10.5, color=MUTE, lsp=0.92)
text(s, MX + 0.4, 5.62, 4.9, 0.0, '', size=1)  # spacer
text(s, 6.5, 1.95, 6.2, 0.3, 'Birebir otomasyon nasıl çalışır', size=16, bold=True, color=INK)
wa_steps = [('Tetikleyici', 'Bir aday açar, tıklar veya yanıtlar — ya da doğrulanmış bir numara vardır.'),
            ('Otomatik kişisel mesaj', 'Ad, şirket ve ürün onaylı şablona işlenir, WhatsApp Business API ile gönderilir. Toplu değil, kişi gibi okunur.'),
            ('Birebir görüşme', 'Temsilci canlı devralır, İspanyolca veya İngilizce — gerçek diyalog, yayın değil.'),
            ('Hatta kaydedilir', 'Sonuç CRM’e işlenir; WhatsApp tekliflere ve siparişlere bağlanır.')]
for i, (t, d) in enumerate(wa_steps):
    yy = 2.42 + i * 0.86
    card(s, 6.5, yy, 6.13, 0.74, r=0.1)
    circ = box(s, 6.72, yy + 0.17, 0.4, 0.4, fill=WA, shape=MSO_SHAPE.OVAL); label_in(circ, str(i + 1), size=13, color=WHITE)
    text(s, 7.3, yy + 0.08, 5.2, 0.3, t, size=14, bold=True, color=INK)
    text(s, 7.3, yy + 0.37, 5.25, 0.35, d, size=11, color=GREY, lsp=1.0)
box(s, MX, 6.08, 5.5, 0.6, fill='EAF6EE', r=0.1, line='CDE8D6')
text(s, MX + 0.3, 6.08, 5.0, 0.6, [[('İZİN ODAKLI & UYUMLU   ', {'bold': True, 'color': WA, 'size': 10, 'spc': 0.6}),
     ('Business API, onaylı şablonlar, kolay çıkış — önce sıcak takip.', {'size': 10})]],
     color=GREY, anchor='m', lsp=1.0)
notes(s, 'Kampanyaya eklenecek yeni kanal: otomatik ama kişisel birebir WhatsApp. Her iki hedef bölgede de baskın iş mesajlaşma '
         'uygulaması; açılma ve yanıt oranları e-postadan çok daha yüksek. Uyumlu yürütün: WhatsApp Business API, onaylı şablonlar, '
         'çıkış hakkı ve önce etkileşime girmiş/doğrulanmış kişilere sıcak takip; canlı görüşmeyi bir temsilci yürütür. WhatsApp '
         'rakamları izin vermiş kişiler için sektör ortalamalarıdır, garanti değildir.')

# ============================================================================= 12 · büyüme kaldıraçları
s = content_slide('BÜYÜME PLANI', 'Daha fazlası için neler ekleyebiliriz')
lev = [('WhatsApp birebiri başlat', 'Alıcıların gerçekten yanıt verdiği yerde otomatik ama kişisel takip — en büyük yeni kaldıraç.', WA),
       ('Orta Doğu’ya karar ver', 'Crane ME’yi revize metin ve iletilebilirlikle yeniden başlat, ya da bütçeyi yönlendir.', AMBER),
       ('Gönderimi güvenle ölçekle', 'Daha fazla kutu ve alan adı ekle, ısıt ve döndür; 120/gün sınırını aş.', RED),
       ('Brezilya kanalını aç', 'Brezilya en büyük LatAm endüstri pazarı. Portekizce dizi erişimi katlar.', RED),
       ('Huniyi besle', 'Sürekli kişi temini (300+/ay) ve tetik tabanlı potansiyel bulma.', RED),
       ('Teklifi yerelleştir', 'İspanyolca/İngilizce açılış sayfası ve katalog, vaka çalışmaları, referanslar.', RED),
       ('Geliri izle', f'{D["leads"]} adayı CRM’e taşı ve yanıt → teklif → sipariş ölç.', RED)]
cw4 = (CW - 3 * 0.2) / 4
for i, (t, d, c) in enumerate(lev):
    xx = MX + (i % 4) * (cw4 + 0.2); yy = 1.9 + (i // 4) * 2.46
    card(s, xx, yy, cw4, 2.26, r=0.14)
    circ = box(s, xx + 0.26, yy + 0.26, 0.44, 0.44, fill=c, shape=MSO_SHAPE.OVAL); label_in(circ, str(i + 1), size=13, color=WHITE)
    text(s, xx + 0.26, yy + 0.84, cw4 - 0.45, 0.34, t, size=14, bold=True, color=INK)
    text(s, xx + 0.26, yy + 1.19, cw4 - 0.48, 1.0, d, size=11.5, color=GREY, lsp=1.05)
xx = MX + 3 * (cw4 + 0.2); yy = 1.9 + 2.46
card(s, xx, yy, cw4, 2.26, fill=INK, r=0.14)
text(s, xx + 0.28, yy + 0.26, cw4 - 0.5, 0.25, 'DÖNÜŞÜM', size=10, bold=True, color=GOLD, spc=1.8)
text(s, xx + 0.28, yy + 0.6, cw4 - 0.5, 0.75, ['Tek kanal,', 'tek bölge çalışıyor'], size=14, color=PALE, lsp=1.0)
text(s, xx + 0.28, yy + 1.22, cw4 - 0.5, 0.95, ['→ e-posta + WhatsApp,', 'iki bölge, CRM’e bağlı.'], size=15, bold=True, color=WHITE, lsp=1.05)
notes(s, 'Kaldıraçlar etkiye göre sıralı: WhatsApp öne çıkan yeni kanal; Orta Doğu bir karar gerektiriyor; geri kalanı mevcut motoru '
         'ölçekler/temizler ve geliri bağlar.')

# ============================================================================= 13 · sonraki adımlar
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(INK)
box(s, 0, 0, 0.28, SH, fill=RED)
pic(s, 'logo_white.png', SW - 0.8 - 1.75, 0.72, h=0.44)
text(s, 1.0, 0.72, 7, 0.3, 'ÖNÜMÜZDEKİ 30 GÜN', size=12.5, bold=True, color=GOLD, spc=2.2)
text(s, 1.0, 1.05, 10, 0.8, 'Önerilen sonraki adımlar', size=38, bold=True, color=WHITE)
nxt = [('WhatsApp pilotunu başlat', f'{D["leads"]} aday ve sıcak kişilere birebir WhatsApp takibi — uyumlu, temsilci yürütümlü.', WA),
       ('Orta Doğu’yu düzelt', f'Crane ME’yi revize metin ve iletilebilirlikle yeniden başlat ya da bütçeyi yönlendir. {D["me_last"]}’dan beri durgun.', GOLD),
       ('LatAm’da 2.000’i garantile', f'Ay hedefte kapansın diye {D["topup"]} kişi ekle; günlük sınırı sabit tut.', GOLD),
       ('Ölçekle & Brezilya’yı aç', 'Daha fazla kutu ısıt, sonra en büyük LatAm pazarı için Portekizce dizi başlat.', GOLD)]
for i, (t, d, nc) in enumerate(nxt):
    yy = 2.3 + i * 1.02
    text(s, 1.0, yy, 1.0, 0.8, f'0{i + 1}', size=34, bold=True, color=nc, anchor='m')
    text(s, 2.15, yy + 0.02, 3.9, 0.8, t, size=20, bold=True, color=WHITE, anchor='m')
    text(s, 6.2, yy + 0.02, 6.25, 0.8, d, size=13.5, color=PALE, anchor='m', lsp=1.03)
    if i < 3: line(s, 1.0, yy + 0.92, 12.5, yy + 0.92, '343A45', 0.75)
text(s, 1.0, 6.56, 11.6, 0.6, f'Rakamlar {D["date"]} itibarıyla iki aktif kampanyadan Apollo üzerinden canlı çekildi. Birleşik: '
     f'gönderilen {fmt(D["sent"])} · iletilen {fmt(D["deliv"])} · aday {D["leads"]} · geri dönen {D["bounced"]} · spam engeli {D["spam"]}. '
     'WhatsApp rakamları sektör ortalamalarıdır. Strateji bölümleri iç analizdir — i.Mak ihracat satış incelemesi için hazırlandı.',
     size=10, color=MUTE, lsp=1.05)
notes(s, 'Önümüzdeki 30 gün için dört öneri; başı WhatsApp pilotu ve Orta Doğu kararı çekiyor. Maliyet ve sorumlular belirlenecek.')

# --- tüm slaytlara geçiş efekti ekle -----------------------------------------
n = len(prs.slides)
for i, sl in enumerate(prs.slides):
    add_transition(sl, 'fade' if i in (0, n - 1) else 'push', 'l', 'med')

prs.save(OUT); print('kaydedildi', OUT, 'slayt:', len(prs.slides))
