# Builds the i.Mak export-outreach report (Latin America + Middle East) as an editable PowerPoint deck.
# Usage: python build_deck.py [out.pptx]      (needs: pip install python-pptx)
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
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'iMak_Outreach_Report_18Nov2026.pptx')

# ----------------------------------------------------------------------------- data (edit here, rebuild)
D = dict(
    date='18 Nov 2026',
    # Latin America (active)
    la_enrolled=904, la_sent=1223, la_deliv=1200, la_leads=46, la_replies_msg=51, la_reply=5.7,
    la_bounced=23, la_bounce=1.8, la_spam=20, la_scheduled=770,
    # Middle East — Crane ME 2026 (active but stalled since 12 Nov)
    me_sent=377, me_deliv=374, me_leads=2, me_reply=1.6, me_bounced=3, me_bounce=0.8, me_spam=0, me_last='12 Nov',
    # combined (both live campaigns)
    sent=1600, deliv=1574, leads=48, bounced=26, spam=20, reply=5.2,
    goal=2000, cap=120, projected='~1,990', topup='~300',
    # WhatsApp channel (industry benchmarks — opted-in contacts)
    wa_users='3.3B+', wa_open='~95%', em_open='~22%')
DELIV = round(100 * D['deliv'] / D['sent'], 1)       # 98.4
BOUNCE = round(100 * D['bounced'] / D['sent'], 1)     # 1.6
LA_GOAL = round(100 * D['la_sent'] / D['goal'])       # 61
fmt = lambda n: f'{n:,}'

# ----------------------------------------------------------------------------- style
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

PAGE = [0]
def content_slide(kicker, title):
    s = prs.slides.add_slide(BLANK); PAGE[0] += 1
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(BG)
    box(s, MX, 0.60, 0.085, 0.80, fill=RED)
    text(s, MX + 0.25, 0.55, 9.5, 0.3, kicker, size=11.5, bold=True, color=RED, spc=1.6)
    text(s, MX + 0.25, 0.80, 9.9, 0.65, title, size=30, bold=True, color=INK)
    pic(s, 'logo_red.png', SW - MX - 1.55, 0.66, h=0.39)
    line(s, MX, 6.98, SW - MX, 6.98, LINE, 0.75)
    text(s, MX, 7.07, 10.5, 0.25, f'i.Mak Export Team   ·   Export outreach: Latin America & Middle East   ·   Report as of {D["date"]}',
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

# ============================================================================= 1 · title
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(INK)
fb = s.shapes.build_freeform(Inches(9.35), Inches(0))
fb.add_line_segments([(Inches(SW), Inches(0)), (Inches(SW), Inches(SH)), (Inches(8.05), Inches(SH))], close=True)
panel = fb.convert_to_shape(); panel.fill.solid(); panel.fill.fore_color.rgb = rgb(RED); panel.line.fill.background()
panel.shadow.inherit = False; flat(panel)
pic(s, 'logo_white.png', 0.8, 0.72, h=0.56)
text(s, 0.8, 2.15, 8, 0.3, f'CAMPAIGN REPORT   ·   {D["date"].upper()}', size=13, bold=True, color=GOLD, spc=2.2)
box(s, 0.8, 2.58, 0.9, 0.05, fill=GOLD)
text(s, 0.8, 2.82, 8.2, 1.9, ['Latin America', '& Middle East outreach'], size=46, bold=True, color=WHITE, lsp=0.96)
text(s, 0.8, 4.95, 7.4, 0.9, 'Two-region results, the lessons — and a new 1-on-1 WhatsApp channel',
     size=20, color=PALE, lsp=1.05)
text(s, 0.8, 6.55, 7.4, 0.3, 'i.Mak Export Team   ·   Cold email + WhatsApp   ·   Spanish & English',
     size=12, color=MUTE)
stats = [(fmt(D['sent']), 'emails sent'), (str(D['leads']), 'leads'),
         (f'{D["reply"]}%', 'reply rate'), (f'{DELIV}%', 'delivered')]
for i, (v, l) in enumerate(stats):
    yy = 0.95 + i * 1.42
    text(s, 10.0, yy, 2.9, 0.75, v, size=44, bold=True, color=WHITE, align='r')
    text(s, 10.0, yy + 0.74, 2.9, 0.3, l.upper(), size=11.5, bold=True, color='F3D9D4', align='r', spc=1.8)
    if i < 3: line(s, 11.3, yy + 1.22, 12.9, yy + 1.22, 'B8463A', 0.75)
notes(s, f'Report as of {D["date"]}, figures pulled live from Apollo across both live campaigns (Latin America + Middle East). '
         f'Headline: {fmt(D["sent"])} emails sent, {D["leads"]} leads, {DELIV}% delivered.')

# ============================================================================= 2 · executive summary
s = content_slide('EXECUTIVE SUMMARY', 'The program in one slide')
card(s, MX, 1.85, 5.55, 4.85, fill=INK, r=0.16)
text(s, MX + 0.4, 2.15, 4.8, 0.3, 'HEADLINE', size=11, bold=True, color=GOLD, spc=2)
text(s, MX + 0.4, 2.5, 4.8, 1.4, [[(f'{D["leads"]} leads', {'color': GOLD}), (f' from {fmt(D["sent"])} emails,', {}), (' two regions.', {})]],
     size=31, bold=True, color=WHITE, lsp=0.96)
text(s, MX + 0.4, 3.95, 4.75, 0.9, f'Latin America is working ({D["la_reply"]}% reply). The Middle East lagged ({D["me_reply"]}%) and '
     f'stalled. The next gain is a 1-on-1 WhatsApp channel.', size=14.5, color=PALE, lsp=1.08)
line(s, MX + 0.4, 5.25, MX + 5.15, 5.25, '3A404B', 0.75)
for i, (v, l) in enumerate([(f'{D["la_reply"]}%', ['Latin America', 'reply rate']), (f'{D["me_reply"]}%', ['Middle East', 'reply rate']),
                            (D['projected'], ['LatAm projected', 'at month-end'])]):
    xx = MX + 0.4 + i * 1.62
    text(s, xx, 5.42, 1.55, 0.6, v, size=27, bold=True, color=WHITE)
    text(s, xx, 6.0, 1.5, 0.6, l, size=11.5, color=MUTE, lsp=0.95)
rows = [(GREEN, 'Latin America is working',
         f'{fmt(D["la_sent"])} sent, {D["la_leads"]} leads at {D["la_reply"]}% reply, {DELIV}% delivered. On track for the {fmt(D["goal"])} goal.'),
        (AMBER, 'The Middle East underperformed',
         f'Crane ME: {D["me_sent"]} sent, {D["me_leads"]} leads ({D["me_reply"]}%), idle since {D["me_last"]}. Relaunch or redirect its budget.'),
        (RED, 'Real demand is replying',
         f'Loma Negra, Socotherm and HOC, plus {D["la_leads"] - 3} more LatAm replies to triage into the pipeline.'),
        (WA, 'The new move: 1-on-1 WhatsApp',
         'Both regions run on WhatsApp. An automated-but-personal channel reaches buyers where they actually reply.')]
for i, (c, t, b) in enumerate(rows):
    yy = 1.85 + i * 1.235
    card(s, 6.55, yy, 6.08, 1.08, r=0.1)
    box(s, 6.55, yy + 0.12, 0.07, 0.84, fill=c)
    text(s, 6.85, yy + 0.15, 5.6, 0.32, t, size=16, bold=True, color=INK)
    text(s, 6.85, yy + 0.49, 5.65, 0.55, b, size=12.5, color=GREY, lsp=1.0)
notes(s, 'One-slide summary: Latin America works and is on track; the Middle East (Crane ME) underperformed and stalled, so it needs a '
         'decision; demand is real; and the next step is a 1-on-1 WhatsApp channel.')

# ============================================================================= 3 · full numbers (two campaigns)
s = content_slide('RESULTS', 'The full numbers — two live campaigns')
tiles = [(fmt(D['sent']), 'Emails sent', 'both campaigns', RED),
         (f'{fmt(D["deliv"])}', 'Delivered', f'{DELIV}% delivery', GREEN),
         (str(D['leads']), 'Leads (replies)', f'{D["reply"]}% reply rate', GOLD),
         (f'{D["bounced"]}', 'Bounced', f'{BOUNCE}% — healthy', MUTE)]
tw = (CW - 3 * 0.22) / 4
for i, (v, l, dlt, bar) in enumerate(tiles):
    xx = MX + i * (tw + 0.22)
    card(s, xx, 1.85, tw, 1.5, r=0.1)
    box(s, xx + 0.26, 2.06, 0.46, 0.06, fill=bar)
    text(s, xx + 0.26, 2.2, tw - 0.4, 0.62, v, size=34, bold=True, color=INK)
    text(s, xx + 0.26, 2.84, tw - 0.4, 0.28, l, size=12.5, color=GREY)
    text(s, xx + 0.26, 3.12, tw - 0.4, 0.24, dlt, size=11, bold=True, color=GREY)
# comparison table
ty = 3.72; card(s, MX, ty, CW, 2.95, r=0.14)
colx = [MX + 0.45, MX + 5.7, MX + 7.95, MX + 10.2]
heads = ['', 'LATIN AMERICA', 'MIDDLE EAST', 'COMBINED']
for i, h in enumerate(heads):
    text(s, colx[i], ty + 0.26, 2.3, 0.3, h, size=11.5, bold=True, color=RED if i else MUTE, align='l' if i == 0 else 'c', spc=0.6)
text(s, colx[1], ty + 0.52, 2.3, 0.25, 'i.Mak Reductores (ES)', size=9.5, color=MUTE, align='c')
text(s, colx[2], ty + 0.52, 2.3, 0.25, 'Crane ME (EN)', size=9.5, color=MUTE, align='c')
text(s, colx[3], ty + 0.52, 2.3, 0.25, 'both live', size=9.5, color=MUTE, align='c')
line(s, MX + 0.45, ty + 0.84, MX + CW - 0.45, ty + 0.84, LINE, 1)
trows = [('Emails sent', fmt(D['la_sent']), str(D['me_sent']), fmt(D['sent'])),
         ('Delivered', f'{fmt(D["la_deliv"])}', str(D['me_deliv']), fmt(D['deliv'])),
         ('Leads (replies)', str(D['la_leads']), str(D['me_leads']), str(D['leads'])),
         ('Reply rate', f'{D["la_reply"]}%', f'{D["me_reply"]}%', f'{D["reply"]}%'),
         ('Bounced', str(D['la_bounced']), str(D['me_bounced']), str(D['bounced'])),
         ('Status', 'Active', f'Stalled · {D["me_last"]}', '')]
for r_, (lab, a, b, c) in enumerate(trows):
    yy = ty + 0.98 + r_ * 0.315
    hot = lab in ('Leads (replies)', 'Reply rate')
    text(s, colx[0], yy, 2.3, 0.3, lab, size=12.5, bold=hot, color=INK if hot else GREY)
    for ci, val in ((1, a), (2, b), (3, c)):
        col = INK
        if lab == 'Status':
            col = GREEN if 'Active' in val else AMBER
        if lab == 'Reply rate' and ci == 1: col = GREEN
        if lab == 'Reply rate' and ci == 2: col = AMBER
        text(s, colx[ci], yy, 2.3, 0.3, val, size=13 if hot else 12.5, bold=hot or lab == 'Status', color=col, align='c')
    if r_ < len(trows) - 1: line(s, MX + 0.45, yy + 0.295, MX + CW - 0.45, yy + 0.295, 'EFEAE2', 0.75)
notes(s, f'Two live Apollo sequences. Latin America: {fmt(D["la_sent"])} sent, {D["la_leads"]} leads ({D["la_reply"]}%). '
         f'Middle East (Crane ME): {D["me_sent"]} sent, {D["me_leads"]} leads ({D["me_reply"]}%), stalled since {D["me_last"]}. '
         f'A third template sequence exists but was never run. Reply rate is unique repliers per contact reached.')

# ============================================================================= 4 · two regions, two results
s = content_slide('RESULTS', 'Two regions, two results')
def region_card(x, title, tag, tagcol, sent, leads, reply, bar_frac, sub):
    w = 5.55; card(s, x, 1.95, w, 3.1, r=0.14)
    text(s, x + 0.4, 2.2, 3.5, 0.3, title, size=20, bold=True, color=INK)
    chip = box(s, x + w - 1.95, 2.24, 1.55, 0.34, fill=tagcol, r=0.17)
    label_in(chip, tag, size=10, color=WHITE, spc=0.8)
    text(s, x + 0.4, 2.78, 2, 0.75, reply, size=46, bold=True, color=tagcol)
    text(s, x + 0.4, 3.62, 3, 0.3, 'reply rate (per contact)', size=12, color=GREY)
    box(s, x + 0.4, 4.0, w - 0.8, 0.14, fill=TRACK, r=0.07)
    box(s, x + 0.4, 4.0, (w - 0.8) * bar_frac, 0.14, fill=tagcol, r=0.07)
    for j, (v, l) in enumerate([(fmt(sent), 'emails sent'), (str(leads), 'leads')]):
        xx = x + 3.0 + j * 1.25
        text(s, xx, 2.78, 1.2, 0.4, v, size=24, bold=True, color=INK)
        text(s, xx, 3.2, 1.2, 0.3, l, size=11, color=GREY)
    text(s, x + 0.4, 4.4, w - 0.8, 0.5, sub, size=12, color=GREY, lsp=1.05)
region_card(MX, 'Latin America', 'ACTIVE', GREEN, D['la_sent'], D['la_leads'], f'{D["la_reply"]}%', D['la_reply'] / 6.0,
            f'Spanish, {LA_GOAL}% to the {fmt(D["goal"])} goal, {D["la_scheduled"]} still queued.')
region_card(MX + 5.83, 'Middle East', 'STALLED', AMBER, D['me_sent'], D['me_leads'], f'{D["me_reply"]}%', D['me_reply'] / 6.0,
            f'Crane ME, English. Idle since {D["me_last"]} — only {D["me_sent"]} sent.')
card(s, MX, 5.35, CW, 1.35, fill=INK, r=0.14)
text(s, MX + 0.45, 5.58, 3.0, 0.3, 'DECISION NEEDED', size=11, bold=True, color=GOLD, spc=1.8)
text(s, MX + 0.45, 5.9, CW - 0.9, 0.7,
     [[('Crane ME replied at ', {}), (f'{D["me_reply"]}% vs {D["la_reply"]}%', {'bold': True, 'color': WHITE}),
       (' in LatAm and has been idle since ', {}), (D['me_last'], {'bold': True, 'color': WHITE}),
       ('. Either ', {}), ('relaunch with revised copy and a deliverability fix', {'bold': True, 'color': WHITE}),
       (', or fold its budget into Latin America and the new WhatsApp channel.', {})]],
     size=14, color=PALE, lsp=1.08)
notes(s, 'The two campaigns diverged sharply: LatAm 5.7% reply, Middle East 1.6% and stalled since 12 Nov. The slide frames the open '
         'decision on Crane ME — relaunch vs redirect — rather than hiding the weak result.')

# ============================================================================= 5 · funnel & rates (combined)
s = content_slide('RESULTS', 'From send to reply: the combined funnel')
fcx = MX + 2.85
for (w, y, fill, big, small, tc) in [(5.7, 1.95, INK, fmt(D['sent']), 'emails sent', WHITE),
                                     (5.3, 3.12, RED, fmt(D['deliv']), f'delivered  ·  {DELIV}%', WHITE),
                                     (2.9, 4.29, GOLD, str(D['leads']), f'leads  ·  {D["reply"]}%', INK)]:
    b = box(s, fcx - w / 2, y, w, 0.92, fill=fill, r=0.12)
    label_in(b, [[(big + '   ', {'size': 28}), (small, {'size': 14, 'bold': False})]], color=tc)
for y in (2.90, 4.07):
    tri = box(s, fcx - 0.16, y, 0.32, 0.19, fill=PALE, shape=MSO_SHAPE.ISOSCELES_TRIANGLE); tri.rotation = 180
text(s, MX, 5.33, 5.7, 0.3, [[(f'{D["bounced"]} bounced', {'bold': True, 'color': INK}), (f' ({BOUNCE}%)      ', {}),
                              (f'{D["spam"]} spam-blocked', {'bold': True, 'color': INK}), (' across both campaigns', {})]],
     size=12, color=GREY, align='c')
dx0 = 6.9; dsz = 1.75; dgap = (SW - MX - dx0 - 3 * dsz) / 2
for i, (pct, col, name, sub) in enumerate([(DELIV, GREEN, 'Delivery rate', f'{fmt(D["deliv"])} of {fmt(D["sent"])} delivered'),
                                           (D['reply'], RED, 'Reply rate', f'{D["leads"]} leads / contacts reached'),
                                           (BOUNCE, AMBER, 'Bounce rate', f'{D["bounced"]} bounced — healthy')]):
    xx = dx0 + i * (dsz + dgap)
    donut(s, xx, 2.0, dsz, pct, col)
    text(s, xx, 2.0, dsz, dsz, f'{pct}%', size=21, bold=True, color=INK, align='c', anchor='m')
    text(s, xx - 0.1, 3.92, dsz + 0.2, 0.3, name, size=15.5, bold=True, color=INK, align='c')
    text(s, xx - 0.1, 4.26, dsz + 0.2, 0.5, sub, size=11, color=GREY, align='c', lsp=1.0)
card(s, MX, 5.78, CW, 0.95, fill=INK, r=0.14)
text(s, MX + 0.4, 5.78, 6.3, 0.95, [[(f'{D["reply"]}% reply', {'color': GOLD}), (' across both regions', {})]],
     size=23, bold=True, color=WHITE, anchor='m')
text(s, MX + 6.6, 5.78, CW - 7.0, 0.95, 'Replies are the one reliable signal — open tracking fired on few messages, '
     'so the reply rate is the number we manage.', size=12.5, color=PALE, anchor='m', lsp=1.0)
notes(s, 'Combined funnel across both live campaigns: 1,600 sent, 1,574 delivered (98.4%), 48 leads. Reply rate here is unique '
         'repliers over contacts reached. Doughnuts are native, editable PowerPoint charts.')

# ============================================================================= 6 · leads
s = content_slide('LEADS', f'{D["leads"]} leads — and names that matter')
for i, (v, l, c) in enumerate([(str(D['leads']), 'Total leads (replies)', RED), (f'{D["la_leads"]} + {D["me_leads"]}', 'LatAm + Middle East', INK),
                               (f'{D["reply"]}%', 'Reply rate (per contact)', INK)]):
    yy = 1.9 + i * 1.63
    card(s, MX, yy, 3.55, 1.45, r=0.12)
    text(s, MX + 0.35, yy + 0.2, 3.1, 0.75, v, size=40, bold=True, color=c)
    text(s, MX + 0.35, yy + 0.98, 3.1, 0.3, l, size=13, color=GREY)
tx, tw_ = 4.6, SW - MX - 4.6
card(s, tx, 1.9, tw_, 4.71, r=0.14)
text(s, tx + 0.4, 2.12, 5, 0.3, 'Notable leads', size=16, bold=True, color=INK)
cols = [(tx + 0.4, 'LEAD'), (tx + 3.0, 'SECTOR'), (tx + 6.35, 'REGION')]
for cx, h in cols: text(s, cx, 2.68, 3, 0.25, h, size=10.5, bold=True, color=MUTE, spc=1.4)
line(s, tx + 0.4, 2.98, tx + tw_ - 0.4, 2.98, LINE, 1)
leads = [('Loma Negra', 'Cement (major producer)', 'Argentina', True), ('Socotherm', 'Pipe coating / energy', 'Argentina', False),
         ('HOC', 'Industrial', 'Latin America', False)]
for i, (n, sec, ctry, hot) in enumerate(leads):
    yy = 3.10 + i * 0.72
    if hot: box(s, tx + 0.22, yy - 0.02, tw_ - 0.44, 0.66, fill='FBEFEA', r=0.08)
    text(s, cols[0][0], yy, 2.6, 0.62, n, size=17, bold=True, color=RED if hot else INK, anchor='m')
    text(s, cols[1][0], yy, 3.3, 0.62, sec, size=14, color=CHAR, anchor='m')
    text(s, cols[2][0], yy, 1.9, 0.62, ctry, size=14, color=CHAR, anchor='m')
    if i < 2: line(s, tx + 0.4, yy + 0.68, tx + tw_ - 0.4, yy + 0.68, LINE, 0.75)
box(s, tx + 0.4, 5.4, tw_ - 0.8, 0.95, fill=BG, r=0.1)
text(s, tx + 0.62, 5.4, tw_ - 1.25, 0.95,
     [[(f'+ {D["la_leads"] - 3} more Latin America replies', {'bold': True, 'color': INK}),
       (f' and {D["me_leads"]} from the Middle East — all to be triaged into the sales pipeline', {})]],
     size=13.5, color=GREY, anchor='m', lsp=1.05)
notes(s, 'Loma Negra (Argentine cement) is the highest-value account so far. 46 LatAm + 2 Middle East = 48 leads total; the rest need '
         'triage into the pipeline.')

# ============================================================================= 7 · markets & message (two maps)
s = content_slide('MARKETS & MESSAGE', 'Two regions, two languages')
def map_card(x, w, title, mapimg, aspect, lang, sectors, subj):
    card(s, x, 1.85, w, 4.85, r=0.14)
    text(s, x + 0.35, 2.05, w - 0.7, 0.3, title, size=17, bold=True, color=INK)
    mh = 2.95; mw = mh * aspect
    pic(s, mapimg, x + (w - mw) / 2, 2.5, h=mh)
    yb = 5.62
    text(s, x + 0.35, yb, w - 0.7, 0.3, [[(lang, {'bold': True, 'color': INK}), ('  ·  ' + sectors, {})]], size=12, color=GREY)
    sb = box(s, x + 0.35, yb + 0.36, w - 0.7, 0.46, fill=INK, r=0.1)
    label_in(sb, [[('SUBJECT  ', {'size': 9, 'color': GOLD, 'spc': 1.2}), (subj, {'size': 12.5})]], color=WHITE, align='l')
    sb.text_frame.margin_left = Inches(0.18)
map_card(MX, 5.85, 'Latin America', 'latam_map.png', 1300 / 1400, 'Spanish', 'cement · mining · steel · food · water',
         'Reductores para {{company}}')
map_card(MX + 6.08, 5.85, 'Middle East', 'me_map.png', 1300 / 1118, 'English', 'cranes & heavy lifting',
         'Gear motors for {{company}}')
notes(s, 'Latin America ran in Spanish across five named markets (plus Spanish-speaking neighbours; Brazil/Portuguese still open). '
         'The Middle East (Crane ME) ran in English, targeting GCC crane and heavy-lifting buyers.')

# ============================================================================= 8 · tools
s = content_slide('TOOLS', 'Programs and tools behind the campaign')
tools = [('Apollo.io', 'DATA  ·  SENDING', ['Contact database search', 'Email enrichment and reveal', 'Sequence builder', 'Sending engine', 'Analytics']),
         ('Microsoft 365 / Outlook', 'REPLIES', ['Reply handling', 'Draft replies', 'Sent manually to keep control']),
         ('Python scripts', 'DATA PREP', ['List building', 'De-dup: one per company', 'Contact-ID to email mapping', 'Batch selection']),
         ('Claude Code', 'ORCHESTRATION', ['Orchestration', 'Daily monitoring', 'Reply mapping', 'Reporting and scheduling'])]
tw4 = (CW - 3 * 0.22) / 4
for i, (n, tag, d) in enumerate(tools):
    xx = MX + i * (tw4 + 0.22)
    card(s, xx, 1.95, tw4, 3.55, r=0.14)
    box(s, xx, 1.95, tw4, 1.28, fill=INK, r=0.14)
    box(s, xx, 2.75, tw4, 0.48, fill=INK)
    text(s, xx + 0.28, 2.17, tw4 - 0.5, 0.25, tag, size=10, bold=True, color=GOLD, spc=1.6)
    text(s, xx + 0.28, 2.47, tw4 - 0.5, 0.6, n, size=19, bold=True, color=WHITE)
    for j, item in enumerate(d):
        yj = 3.50 + j * 0.385
        box(s, xx + 0.3, yj + 0.095, 0.075, 0.075, fill=RED)
        text(s, xx + 0.5, yj, tw4 - 0.7, 0.3, item, size=13, color=CHAR)
card(s, MX, 5.78, CW, 0.95, fill=CARD, r=0.14)
flow = ['Find & enrich', 'Clean & de-dup', 'Send', 'Reply', 'Monitor & report']
fw = CW / len(flow)
for i, f in enumerate(flow):
    xx = MX + i * fw
    text(s, xx + 0.15, 5.78, fw - 0.3, 0.95, [[(f'{i + 1}   ', {'color': RED, 'bold': True}), (f, {'bold': True})]], size=14.5, color=INK, anchor='m', align='c')
    if i < len(flow) - 1:
        box(s, xx + fw - 0.1, 6.15, 0.2, 0.21, fill=PALE, shape=MSO_SHAPE.CHEVRON)
notes(s, 'Four tools cover the whole loop: Apollo (data + sending), Python (list prep), Outlook (replies), Claude Code (orchestration, '
         'monitoring, reporting). WhatsApp would add a messaging tool alongside Apollo.')

# ============================================================================= 9 · step by step
s = content_slide('PROCESS', 'Step by step: how we ran it')
steps = [('Define the target', 'Industrial buyers by region: LatAm reducers; Middle East crane & lifting.'),
         ('Build contact lists', 'Apollo people search by region, industry and title.'),
         ('Clean & de-duplicate', 'One contact per company; repeats and invalid records removed.'),
         ('Enrich & verify emails', 'Verified through Apollo; batches of about 500 prepared.'),
         ('Write the copy', 'Spanish for LatAm, English for the Middle East, A/B subjects.'),
         ('Configure the sequences', f'Sender “i.Mak Export Team”, cap {D["cap"]} a day, controlled windows.'),
         ('Launch & monitor daily', 'Sent, delivered, replies, bounces and spam blocks.'),
         ('Protect deliverability', 'Cap held steady, spam-block trend watched, no reputation damage.'),
         ('Route the leads', 'Every replier mapped to their inbox; replies drafted; Bilal CC’d.'),
         ('Automate check-ins', 'Daily numbers, new leads and the watch rule.')]
cwid = CW / 5
for r_ in range(2):
    yy = 2.05 + r_ * 2.38
    line(s, MX + 0.27, yy + 0.27, MX + 4 * cwid + 0.27, yy + 0.27, 'D9D3C9', 1.5)
    for c_ in range(5):
        i = r_ * 5 + c_; xx = MX + c_ * cwid; t, d = steps[i]
        circ = box(s, xx, yy, 0.54, 0.54, fill=RED, shape=MSO_SHAPE.OVAL)
        label_in(circ, str(i + 1), size=15, color=WHITE)
        text(s, xx, yy + 0.72, cwid - 0.25, 0.32, t, size=14.5, bold=True, color=INK)
        text(s, xx, yy + 1.06, cwid - 0.3, 1.1, d, size=11.5, color=GREY, lsp=1.05)
notes(s, 'Ten repeatable steps, run across both regions. Steps 7 to 10 run every day.')

# ============================================================================= 10 · challenges
s = content_slide('LESSONS', 'Six challenges we faced')
ch = [('MIDDLE EAST', BAD, 'Crane ME underperformed', f'{D["me_reply"]}% reply vs {D["la_reply"]}% in LatAm, and idle since {D["me_last"]}. Needs new copy and a deliverability fix — or redirect.'),
      ('DELIVERABILITY', BAD, 'Early spam-block spike', 'Spam blocks escalated early in LatAm, a reputation risk. Contained by holding the cap at 120 rather than scaling up.'),
      ('CAPACITY', AMBER, 'Single-inbox ceiling', 'One sender and inbox caps safe volume at about 120 a day — the ceiling on monthly reach.'),
      ('CONTACTS', AMBER, 'List size limits the goal', 'Reaching 2,000 is limited by list size, not speed. It needs ongoing contact sourcing.'),
      ('TRACKING', AMBER, 'Weak open tracking', 'Open tracking fired on few messages. Replies are the only reliable signal, so top-of-funnel is partly blind.'),
      ('COVERAGE', AMBER, 'Spanish only — no Brazil yet', 'Brazil (Portuguese), the largest LatAm market, is not yet addressed.')]
cw3 = (CW - 2 * 0.22) / 3
for i, (tag, col, t, d) in enumerate(ch):
    xx = MX + (i % 3) * (cw3 + 0.22); yy = 1.9 + (i // 3) * 2.46
    card(s, xx, yy, cw3, 2.26, r=0.14)
    box(s, xx, yy + 0.3, 0.07, 1.66, fill=col)
    chip = box(s, xx + 0.32, yy + 0.28, 0.42 + 0.088 * len(tag), 0.29, fill=col, r=0.145)
    label_in(chip, tag, size=9.5, color=WHITE, spc=1.2)
    text(s, xx + 0.32, yy + 0.72, cw3 - 0.6, 0.35, t, size=16.5, bold=True, color=INK)
    text(s, xx + 0.32, yy + 1.12, cw3 - 0.62, 1.05, d, size=12, color=GREY, lsp=1.06)
notes(s, 'Red tags are the two biggest issues: the Middle East result, and the early LatAm deliverability risk (now contained). '
         'Amber tags are ongoing constraints.')

# ============================================================================= 11 · NEW — WhatsApp 1-on-1
s = content_slide('NEW CHANNEL', 'Add a 1-on-1 WhatsApp channel')
# left: why
card(s, MX, 1.9, 5.5, 4.05, fill=INK, r=0.16)
wb = box(s, MX + 0.4, 2.18, 0.5, 0.5, fill=WA, r=0.14)
label_in(wb, 'W', size=22, color=WHITE)
text(s, MX + 1.02, 2.2, 4.0, 0.5, 'Why WhatsApp', size=20, bold=True, color=WHITE, anchor='m')
text(s, MX + 0.4, 2.92, 4.75, 1.0, 'Both Latin America and the Middle East run their business on WhatsApp. '
     'Email earns a few per-cent reply; on WhatsApp, buyers answer in minutes.', size=14, color=PALE, lsp=1.1)
line(s, MX + 0.4, 4.15, MX + 5.1, 4.15, '2C333F', 0.75)
for i, (v, l) in enumerate([(D['wa_users'], ['WhatsApp', 'users']), (D['wa_open'], ['open rate*', f'(email {D["em_open"]})']),
                            ('#1', ['business app', 'in both regions'])]):
    xx = MX + 0.4 + i * 1.62
    text(s, xx, 4.32, 1.55, 0.5, v, size=26, bold=True, color=WA if i == 1 else WHITE)
    text(s, xx, 4.9, 1.55, 0.6, l, size=11, color=MUTE, lsp=0.95)
text(s, MX + 0.4, 5.62, 4.9, 0.3, '*opted-in contacts; industry benchmarks', size=9.5, italic=True, color=MUTE)
# right: how it works
text(s, 6.5, 1.95, 6.2, 0.3, 'How the 1-on-1 automation works', size=16, bold=True, color=INK)
wa_steps = [('Trigger', 'A lead opens, clicks or replies — or a verified mobile number exists.'),
            ('Auto-personalised message', 'Name, company and product merged into an approved template, sent via the WhatsApp Business API. Reads like a person, not a blast.'),
            ('1-on-1 conversation', 'The rep takes over live, in Spanish or English — a real back-and-forth, not a broadcast.'),
            ('Logged to the pipeline', 'Outcome synced to the CRM so WhatsApp maps to quotes and orders.')]
for i, (t, d) in enumerate(wa_steps):
    yy = 2.42 + i * 0.86
    card(s, 6.5, yy, 6.13, 0.74, r=0.1)
    circ = box(s, 6.72, yy + 0.17, 0.4, 0.4, fill=WA, shape=MSO_SHAPE.OVAL); label_in(circ, str(i + 1), size=13, color=WHITE)
    text(s, 7.3, yy + 0.08, 5.2, 0.3, t, size=14, bold=True, color=INK)
    text(s, 7.3, yy + 0.37, 5.25, 0.35, d, size=11, color=GREY, lsp=1.0)
# guardrail strip
gb = card(s, MX, 6.02, 5.5, 0.66, fill='EAF6EE', r=0.1, sh=False, line_='CDE8D6')
text(s, MX + 0.3, 6.02, 5.0, 0.66, [[('OPT-IN & COMPLIANT   ', {'bold': True, 'color': WA, 'size': 10.5, 'spc': 0.8}),
     ('Business API, approved templates, easy opt-out — warm follow-up first, not cold blasts.', {'size': 10.5})]],
     color=GREY, anchor='m', lsp=1.0)
notes(s, 'The new channel the campaign should add: automated-but-personal 1-on-1 WhatsApp. It is the dominant business-messaging app in '
         'both target regions, with far higher open and reply rates than email. Run it compliant: WhatsApp Business API, approved '
         'templates, opt-out, and warm follow-up on engaged/verified contacts first — a human rep handles the live conversation. '
         'WhatsApp stats are industry benchmarks for opted-in contacts, not guarantees.')

# ============================================================================= 12 · growth levers
s = content_slide('GROWTH PLAN', 'What we can add to gain more')
lev = [('Launch WhatsApp 1-on-1', 'Automated-but-personal follow-up where buyers actually reply — the biggest new lever.', WA),
       ('Decide on the Middle East', 'Relaunch Crane ME with revised copy and deliverability, or redirect its budget.', AMBER),
       ('Scale sending safely', 'Add and warm up more inboxes and domains, then rotate sends above the 120-a-day cap.', RED),
       ('Open a Brazil track', 'Brazil is the largest LatAm industrial market. A Portuguese sequence multiplies reach.', RED),
       ('Feed the funnel', 'Continuous contact sourcing (300+ a month) plus trigger-based prospecting.', RED),
       ('Localise the offer', 'Spanish/English landing page and catalogue, case studies and references.', RED),
       ('Track to revenue', f'Push the {D["leads"]} leads into a CRM and measure replies → quotes → orders.', RED)]
cw4 = (CW - 3 * 0.2) / 4
for i, (t, d, c) in enumerate(lev):
    xx = MX + (i % 4) * (cw4 + 0.2); yy = 1.9 + (i // 4) * 2.46
    card(s, xx, yy, cw4, 2.26, r=0.14)
    circ = box(s, xx + 0.26, yy + 0.26, 0.44, 0.44, fill=c, shape=MSO_SHAPE.OVAL); label_in(circ, str(i + 1), size=13, color=WHITE)
    text(s, xx + 0.26, yy + 0.84, cw4 - 0.45, 0.34, t, size=14.5, bold=True, color=INK)
    text(s, xx + 0.26, yy + 1.19, cw4 - 0.48, 1.0, d, size=11.5, color=GREY, lsp=1.05)
xx = MX + 3 * (cw4 + 0.2); yy = 1.9 + 2.46
card(s, xx, yy, cw4, 2.26, fill=INK, r=0.14)
text(s, xx + 0.28, yy + 0.26, cw4 - 0.5, 0.25, 'THE SHIFT', size=10, bold=True, color=GOLD, spc=1.8)
text(s, xx + 0.28, yy + 0.6, cw4 - 0.5, 0.75, ['One channel,', 'one region working'], size=14, color=PALE, lsp=1.0)
text(s, xx + 0.28, yy + 1.22, cw4 - 0.5, 0.95, ['→ email + WhatsApp,', 'both regions, into a CRM.'], size=15, bold=True, color=WHITE, lsp=1.05)
notes(s, 'Levers ordered by impact: WhatsApp is the headline new channel; the Middle East needs a decision; the rest scale and clean the '
         'existing engine and connect it to revenue.')

# ============================================================================= 13 · next steps
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(INK)
box(s, 0, 0, 0.28, SH, fill=RED)
pic(s, 'logo_white.png', SW - 0.8 - 1.75, 0.72, h=0.44)
text(s, 1.0, 0.72, 7, 0.3, 'NEXT 30 DAYS', size=12.5, bold=True, color=GOLD, spc=2.2)
text(s, 1.0, 1.05, 9, 0.8, 'Proposed next steps', size=40, bold=True, color=WHITE)
nxt = [('Launch the WhatsApp pilot', f'1-on-1 WhatsApp follow-up on the {D["leads"]} leads and warm contacts — compliant, rep-handled.', WA),
       ('Fix the Middle East', f'Relaunch Crane ME with revised copy and deliverability, or redirect its budget. Idle since {D["me_last"]}.', GOLD),
       ('Secure the 2,000 in LatAm', f'Top up {D["topup"]} contacts so the month closes on target; keep the daily cap steady.', GOLD),
       ('Scale & open Brazil', 'Warm up more inboxes, then launch a Portuguese sequence for the largest LatAm market.', GOLD)]
for i, (t, d, nc) in enumerate(nxt):
    yy = 2.3 + i * 1.02
    text(s, 1.0, yy, 1.0, 0.8, f'0{i + 1}', size=34, bold=True, color=nc, anchor='m')
    text(s, 2.15, yy + 0.02, 3.7, 0.8, t, size=20, bold=True, color=WHITE, anchor='m')
    text(s, 6.0, yy + 0.02, 6.45, 0.8, d, size=14, color=PALE, anchor='m', lsp=1.03)
    if i < 3: line(s, 1.0, yy + 0.92, 12.5, yy + 0.92, '343A45', 0.75)
text(s, 1.0, 6.58, 11.5, 0.6, f'Figures pulled live from Apollo on {D["date"]} across two live campaigns. Combined: sent {fmt(D["sent"])} · '
     f'delivered {fmt(D["deliv"])} · leads {D["leads"]} · bounced {D["bounced"]} · spam blocked {D["spam"]}. '
     'WhatsApp figures are industry benchmarks. Strategy sections are internal analysis — prepared for i.Mak export sales review.',
     size=10, color=MUTE, lsp=1.05)
notes(s, 'Four proposed moves for the next 30 days, led by the WhatsApp pilot and the Middle East decision. Costs and owners to be agreed.')

prs.save(OUT); print('saved', OUT, 'slides:', len(prs.slides))
