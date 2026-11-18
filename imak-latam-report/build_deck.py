# Builds the i.Mak Latin America campaign report as an editable PowerPoint deck.
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
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'iMak_LatAm_Campaign_Report_18Nov2026.pptx')

# ----------------------------------------------------------------------------- data (edit here, rebuild)
D = dict(date='18 Nov 2026', sent=1223, delivered=1200, replies=51, bounced=23, spam=20, scheduled=770,
         goal=2000, cap=120, projected='~1,990', topup='~300')
PCT_DELIV = round(100 * D['delivered'] / D['sent'], 1)        # 98.1
PCT_REPLY = round(100 * D['replies'] / D['sent'], 1)          # 4.2
PCT_BOUNCE = round(100 * D['bounced'] / D['sent'], 1)         # 1.9
PCT_GOAL = round(100 * D['sent'] / D['goal'])                 # 61
PER_REPLY = round(D['sent'] / D['replies'])                   # 24
fmt = lambda n: f'{n:,}'

# ----------------------------------------------------------------------------- style
RED = '952414'; RED_D = '6F170C'; RED_L = 'DEAAA0'; INK = '15181E'; CHAR = '232830'; GREY = '5C6470'
MUTE = '8A919C'; LINE = 'E3DED6'; BG = 'F7F5F1'; CARD = 'FFFFFF'; GOLD = 'DDA033'; GREEN = '1F9D6B'
AMBER = 'C9881F'; BAD = 'C0392B'; TRACK = 'ECE7DF'; WHITE = 'FFFFFF'; PALE = 'C9CED6'
FONT = 'Calibri'
SW, SH = 13.333, 7.5; MX = 0.7; CW = SW - 2 * MX

prs = Presentation(); prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)
BLANK = prs.slide_layouts[6]
rgb = lambda h: RGBColor.from_string(h)

def flat(shape):
    st = shape._element.find(qn('p:style'))                       # drop the theme's built-in shadow reference
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
    text(s, MX, 7.07, 9, 0.25, f'i.Mak Export Team   ·   Latin America Outreach Campaign   ·   Report as of {D["date"]}',
         size=10, color=MUTE)
    text(s, SW - MX - 1, 7.07, 1, 0.25, str(PAGE[0] + 1), size=10, color=MUTE, align='r')
    return s

def card(s, x, y, w, h, fill=CARD, r=0.12, sh=True, line_=None):
    return box(s, x, y, w, h, fill=fill, r=r, sh=sh, line=line_)

def donut(s, x, y, size, pct, color):
    cd = CategoryChartData(); cd.categories = ['value', 'rest']; cd.add_series('share', (pct, 100 - pct))
    gf = s.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(x), Inches(y), Inches(size), Inches(size), cd)
    ch = gf.chart; ch.has_legend = False; ch.has_title = False
    plot = ch.plots[0]; plot.has_data_labels = False; ser = plot.series[0]
    for i, c in enumerate([color, TRACK]):
        pt = ser.points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = rgb(c); pt.format.line.fill.background()
    dn = ch._chartSpace.find('.//' + qn('c:doughnutChart'))
    hs = dn.find(qn('c:holeSize'))
    if hs is None: hs = etree.SubElement(dn, qn('c:holeSize'))
    hs.set('val', '78')
    pa = ch._chartSpace.find('.//' + qn('c:plotArea'))                     # make the ring fill its frame in every renderer
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
text(s, 0.8, 2.25, 7, 0.3, f'CAMPAIGN REPORT   ·   {D["date"].upper()}', size=13, bold=True, color=GOLD, spc=2.2)
box(s, 0.8, 2.68, 0.9, 0.05, fill=GOLD)
text(s, 0.8, 2.95, 7.6, 1.9, ['Latin America', 'Outreach Campaign'], size=50, bold=True, color=WHITE, lsp=0.95)
text(s, 0.8, 4.85, 7.0, 0.5, 'Results, lessons and the plan to grow', size=22, color=PALE)
text(s, 0.8, 6.55, 7.4, 0.3, 'i.Mak Export Team   ·   Cold email program   ·   Spanish-speaking Latin America',
     size=12, color=MUTE)
stats = [(fmt(D['sent']), 'emails sent'), (str(D['replies']), 'replies'),
         (f'{PCT_REPLY}%', 'reply rate'), (f'{PCT_DELIV}%', 'delivered')]
for i, (v, l) in enumerate(stats):
    yy = 0.95 + i * 1.42
    text(s, 10.0, yy, 2.9, 0.75, v, size=44, bold=True, color=WHITE, align='r')
    text(s, 10.0, yy + 0.74, 2.9, 0.3, l.upper(), size=11.5, bold=True, color='F3D9D4', align='r', spc=1.8)
    if i < 3: line(s, 11.3, yy + 1.22, 12.9, yy + 1.22, 'B8463A', 0.75)
notes(s, f'Report as of {D["date"]}. Figures pulled live from Apollo. Headline: {fmt(D["sent"])} emails sent, '
         f'{D["replies"]} replies ({PCT_REPLY}%), {PCT_DELIV}% delivered.')

# ============================================================================= 2 · executive summary
s = content_slide('EXECUTIVE SUMMARY', 'The campaign in one slide')
card(s, MX, 1.85, 5.55, 4.85, fill=INK, r=0.16)
text(s, MX + 0.4, 2.15, 4.8, 0.3, 'HEADLINE', size=11, bold=True, color=GOLD, spc=2)
text(s, MX + 0.4, 2.5, 4.8, 1.4, [[(f'{D["replies"]} replies', {'color': GOLD}), (f' from {fmt(D["sent"])} emails.', {})]],
     size=32, bold=True, color=WHITE, lsp=0.95)
text(s, MX + 0.4, 3.75, 4.75, 0.9, f'One reply for every {PER_REPLY} emails sent — cold outreach, in Spanish, '
     f'held at a safe {D["cap"]} emails a day.', size=15, color=PALE, lsp=1.05)
line(s, MX + 0.4, 4.95, MX + 5.15, 4.95, '3A404B', 0.75)
for i, (v, l) in enumerate([(f'{PCT_GOAL}%', f'of the {fmt(D["goal"])} goal'), (f'{PCT_DELIV}%', 'delivered'),
                            (D['projected'], 'projected at month-end')]):
    xx = MX + 0.4 + i * 1.62
    text(s, xx, 5.15, 1.55, 0.6, v, size=28, bold=True, color=WHITE)
    text(s, xx, 5.75, 1.45, 0.6, ['projected at', 'month-end'] if l.startswith('projected') else l, size=11.5, color=MUTE, lsp=0.95)
rows = [(GREEN, 'On track for the goal',
         f'{PCT_GOAL}% of {fmt(D["goal"])} sent. With {D["scheduled"]} still queued, the month lands at {D["projected"]}.'),
        (GREEN, 'Deliverability is healthy',
         f'{PCT_DELIV}% delivered and {PCT_BOUNCE}% bounce. Spam blocks flattened to +1 a day.'),
        (RED, 'Real demand is replying',
         f'Loma Negra, Socotherm and HOC, plus {D["replies"] - 3} more replies to triage into the pipeline.'),
        (GOLD, 'Growth is a capacity question',
         'More inboxes, a Brazil / Portuguese track and multichannel follow-up unlock the next step.')]
for i, (c, t, b) in enumerate(rows):
    yy = 1.85 + i * 1.235
    card(s, 6.55, yy, 6.08, 1.08, r=0.1)
    box(s, 6.55, yy + 0.12, 0.07, 0.84, fill=c)
    text(s, 6.85, yy + 0.16, 5.6, 0.32, t, size=16, bold=True, color=INK)
    text(s, 6.85, yy + 0.50, 5.6, 0.52, b, size=12.5, color=GREY, lsp=1.0)
notes(s, 'One-slide summary for readers who stop here: on track for the monthly goal, healthy deliverability, '
         'named leads replying, and growth now depends on sending capacity and market coverage.')

# ============================================================================= 3 · full numbers
s = content_slide('RESULTS', f'The full numbers — live on {D["date"][:6]}')
tiles = [(fmt(D['sent']), 'Emails sent', f'{PCT_GOAL}% of {fmt(D["goal"])} goal', GREEN, RED),
         (fmt(D['delivered']), 'Delivered', f'{PCT_DELIV}% delivery', GREEN, GREEN),
         (str(D['replies']), 'Replies', f'{PCT_REPLY}% reply rate', GREEN, GOLD),
         (str(D['bounced']), 'Bounced', f'{PCT_BOUNCE}% — healthy', GREY, MUTE),
         (str(D['spam']), 'Spam blocked', 'flattened (+1/day)', GREY, MUTE),
         (str(D['scheduled']), 'Still scheduled', 'pipeline remaining', GREY, INK)]
tw = (CW - 5 * 0.18) / 6
for i, (v, l, dlt, dc, bar) in enumerate(tiles):
    xx = MX + i * (tw + 0.18)
    card(s, xx, 1.9, tw, 1.78, r=0.1)
    box(s, xx + 0.22, 2.12, 0.42, 0.06, fill=bar)
    text(s, xx + 0.22, 2.27, tw - 0.3, 0.62, v, size=34, bold=True, color=INK)
    text(s, xx + 0.22, 2.92, tw - 0.3, 0.28, l, size=13, color=GREY)
    text(s, xx + 0.22, 3.22, tw - 0.3, 0.28, dlt, size=11.5, bold=True, color=dc)
card(s, MX, 3.95, CW, 2.78, r=0.14)
text(s, MX + 0.35, 4.16, 6, 0.3, 'Progress to the monthly goal', size=16, bold=True, color=INK)
text(s, SW - MX - 4.35, 4.16, 4, 0.3, [[(fmt(D['sent']), {'color': RED}), (f' / {fmt(D["goal"])} sent', {'color': GREY})]],
     size=16, bold=True, align='r')
bx, bw, by, bh = MX + 0.35, CW - 0.7, 4.72, 0.44
box(s, bx, by, bw, bh, fill=TRACK, r=0.22)
w_sent = bw * D['sent'] / D['goal']; w_sch = bw * D['scheduled'] / D['goal']
box(s, bx, by, w_sent + w_sch, bh, fill=RED_L, r=0.22)
box(s, bx, by, w_sent, bh, fill=RED, r=0.22)
text(s, bx + 0.18, by, w_sent - 0.3, bh, f'Sent  {fmt(D["sent"])}  ·  {PCT_GOAL}%', size=13, bold=True, color=WHITE, anchor='m')
text(s, bx + w_sent + 0.18, by, w_sch - 0.3, bh, f'Scheduled  {D["scheduled"]}', size=13, bold=True, color=RED_D, anchor='m')
text(s, bx, by + 0.52, bw, 0.25, f'Goal  {fmt(D["goal"])}', size=11.5, bold=True, color=GREY, align='r')
text(s, bx, by + 0.52, 6, 0.25, f'Daily cap: {D["cap"]} emails a day', size=11.5, color=MUTE)
text(s, bx, 5.72, bw, 0.85,
     [[('With ', {}), (f'{D["scheduled"]} emails still queued', {'bold': True, 'color': INK}),
       (', the campaign projects to land at ', {}), (D['projected'], {'bold': True, 'color': INK}),
       (' by month-end — essentially on target.', {})],
      [('The limit is ', {}), ('contacts, not sending speed', {'bold': True, 'color': RED}),
       (f': a small top-up of {D["topup"]} contacts secures the {fmt(D["goal"])} and keeps momentum.', {})]],
     size=13.5, color=GREY, lsp=1.05, after=3)
notes(s, f'Sent {fmt(D["sent"])}, delivered {fmt(D["delivered"])} ({PCT_DELIV}%), replies {D["replies"]} ({PCT_REPLY}%), '
         f'bounced {D["bounced"]} ({PCT_BOUNCE}%), spam-blocked {D["spam"]}, still scheduled {D["scheduled"]}. '
         f'Sent plus scheduled is {fmt(D["sent"] + D["scheduled"])}, so the month closes at about {D["projected"]}.')

# ============================================================================= 4 · funnel & rates
s = content_slide('RESULTS', 'From send to reply: a healthy funnel')
fcx = MX + 2.85
for (w, y, fill, big, small, tc) in [(5.7, 1.95, INK, fmt(D['sent']), 'emails sent', WHITE),
                                     (5.3, 3.12, RED, fmt(D['delivered']), f'delivered  ·  {PCT_DELIV}%', WHITE),
                                     (2.9, 4.29, GOLD, str(D['replies']), f'replies  ·  {PCT_REPLY}%', INK)]:
    b = box(s, fcx - w / 2, y, w, 0.92, fill=fill, r=0.12)
    label_in(b, [[(big + '   ', {'size': 28}), (small, {'size': 14, 'bold': False})]], color=tc)
for y in (2.90, 4.07):
    tri = box(s, fcx - 0.16, y, 0.32, 0.19, fill=PALE, shape=MSO_SHAPE.ISOSCELES_TRIANGLE); tri.rotation = 180
text(s, MX, 5.33, 5.7, 0.3, [[(f'{D["bounced"]} bounced', {'bold': True, 'color': INK}), (f' ({PCT_BOUNCE}%)      ', {}),
                              (f'{D["spam"]} spam-blocked', {'bold': True, 'color': INK}), (' (flattened to +1/day)', {})]],
     size=12, color=GREY, align='c')
dx0 = 6.9; dsz = 1.75; dgap = (SW - MX - dx0 - 3 * dsz) / 2
for i, (pct, col, name, sub) in enumerate([(PCT_DELIV, GREEN, 'Delivery rate', f'{fmt(D["delivered"])} of {fmt(D["sent"])} delivered'),
                                           (PCT_REPLY, RED, 'Reply rate', f'{D["replies"]} replies received'),
                                           (PCT_BOUNCE, AMBER, 'Bounce rate', f'{D["bounced"]} bounced — healthy')]):
    xx = dx0 + i * (dsz + dgap)
    donut(s, xx, 2.0, dsz, pct, col)
    text(s, xx, 2.0, dsz, dsz, f'{pct}%', size=21, bold=True, color=INK, align='c', anchor='m')
    text(s, xx - 0.1, 3.92, dsz + 0.2, 0.3, name, size=15.5, bold=True, color=INK, align='c')
    text(s, xx - 0.1, 4.26, dsz + 0.2, 0.5, sub, size=11.5, color=GREY, align='c', lsp=1.0)
card(s, MX, 5.78, CW, 0.95, fill=INK, r=0.14)
text(s, MX + 0.4, 5.78, 5.6, 0.95, [[('1 reply', {'color': GOLD}), (f' for every {PER_REPLY} emails sent', {})]],
     size=23, bold=True, color=WHITE, anchor='m')
text(s, MX + 6.2, 5.78, CW - 6.6, 0.95, f'Replies are the one reliable signal: open tracking fired on few messages, '
     f'so the {PCT_REPLY}% reply rate is the number to manage.', size=12.5, color=PALE, anchor='m', lsp=1.0)
notes(s, 'Funnel blocks are labelled, not drawn to scale. Delivery, reply and bounce rates are each a share of emails sent. '
         'Doughnut charts are native PowerPoint charts and can be edited.')

# ============================================================================= 5 · leads
s = content_slide('LEADS', f'{D["replies"]} leads — and names that matter')
for i, (v, l, c) in enumerate([(str(D['replies']), 'Total leads (replies)', RED), (f'{PCT_REPLY}%', 'Reply rate', INK),
                               (f'1 : {PER_REPLY}', 'Replies per emails sent', INK)]):
    yy = 1.9 + i * 1.63
    card(s, MX, yy, 3.55, 1.45, r=0.12)
    text(s, MX + 0.35, yy + 0.2, 3.0, 0.75, v, size=42, bold=True, color=c)
    text(s, MX + 0.35, yy + 0.98, 3.0, 0.3, l, size=13, color=GREY)
tx, tw_ = 4.6, SW - MX - 4.6
card(s, tx, 1.9, tw_, 4.71, r=0.14)
text(s, tx + 0.4, 2.12, 5, 0.3, 'Notable leads', size=16, bold=True, color=INK)
cols = [(tx + 0.4, 'LEAD'), (tx + 3.0, 'SECTOR'), (tx + 6.35, 'COUNTRY')]
for cx, h in cols: text(s, cx, 2.68, 3, 0.25, h, size=10.5, bold=True, color=MUTE, spc=1.4)
line(s, tx + 0.4, 2.98, tx + tw_ - 0.4, 2.98, LINE, 1)
leads = [('Loma Negra', 'Cement (major producer)', 'Argentina', True), ('Socotherm', 'Pipe coating / energy', 'Argentina', False),
         ('HOC', 'Industrial', 'LatAm', False)]
for i, (n, sec, ctry, hot) in enumerate(leads):
    yy = 3.10 + i * 0.72
    if hot: box(s, tx + 0.22, yy - 0.02, tw_ - 0.44, 0.66, fill='FBEFEA', r=0.08)
    text(s, cols[0][0], yy, 2.6, 0.62, n, size=17, bold=True, color=RED if hot else INK, anchor='m')
    text(s, cols[1][0], yy, 3.3, 0.62, sec, size=14, color=CHAR, anchor='m')
    text(s, cols[2][0], yy, 1.5, 0.62, ctry, size=14, color=CHAR, anchor='m')
    if i < 2: line(s, tx + 0.4, yy + 0.68, tx + tw_ - 0.4, yy + 0.68, LINE, 0.75)
box(s, tx + 0.4, 5.45, tw_ - 0.8, 0.86, fill=BG, r=0.1)
text(s, tx + 0.62, 5.45, tw_ - 1.25, 0.86,
     [[(f'+ {D["replies"] - 3} further replies', {'bold': True, 'color': INK}),
       (' across the South America contact lists — to be triaged into the sales pipeline.', {})]],
     size=13.5, color=GREY, anchor='m', lsp=1.0)
notes(s, 'Loma Negra is a major Argentine cement producer and the highest-value account so far. Socotherm and HOC are the other '
         'named leads; the remaining replies still need triage.')

# ============================================================================= 6 · market & message
s = content_slide('MARKET & MESSAGE', 'Where we spoke, and in what language')
mx0, my0, mh = MX + 0.05, 1.8, 4.6; mw = mh * 1300 / 1400
pic(s, 'latam_map.png', mx0, my0, h=mh)
def geo(lon, lat): return (mx0 + (lon + 119.0) / 87.0 * mw, my0 + (34.0 - lat) / 90.5 * mh)
def maplabel(name, at, to, align):
    lx, ly = geo(*at); px, py = geo(*to)
    line(s, lx, ly, px, py, '8A919C', 0.75)
    dot = box(s, px - 0.03, py - 0.03, 0.06, 0.06, fill=INK, shape=MSO_SHAPE.OVAL)
    if align == 'r': text(s, lx - 1.3 - 0.05, ly - 0.13, 1.3, 0.26, name, size=12, bold=True, color=INK, align='r', anchor='m')
    else: text(s, lx + 0.05, ly - 0.13, 1.3, 0.26, name, size=12, bold=True, color=INK, anchor='m')
maplabel('Mexico', (-110.0, 14.5), (-103.0, 21.0), 'r')
maplabel('Colombia', (-85.0, 2.0), (-75.5, 4.0), 'r')
maplabel('Peru', (-87.5, -11.0), (-76.5, -9.5), 'r')
maplabel('Chile', (-80.0, -31.0), (-71.3, -30.5), 'r')
maplabel('Argentina', (-52.5, -42.5), (-64.0, -38.0), 'l')
bxp, byp = geo(-52.0, -9.5)
text(s, bxp - 0.75, byp - 0.2, 1.5, 0.24, 'Brazil', size=12.5, bold=True, color='7A4E0A', align='c', anchor='m')
text(s, bxp - 0.75, byp + 0.03, 1.5, 0.22, 'Portuguese — next', size=9.5, color='7A4E0A', align='c', anchor='m')
lg = [(RED, 'Named target markets', 0.0), (RED_L, 'Spanish-speaking neighbours', 1.72), ('E8BE6E', 'Brazil — not yet addressed', 3.72)]
for c, l, off in lg:
    box(s, MX + off, 6.58, 0.16, 0.16, fill=c, r=0.03)
    text(s, MX + off + 0.23, 6.54, 1.9, 0.25, l, size=10, color=GREY)
rx, rw = 6.3, SW - MX - 6.3
card(s, rx, 1.85, rw, 2.42, r=0.14)
text(s, rx + 0.35, 2.03, 4, 0.3, 'Target area', size=16, bold=True, color=INK)
text(s, rx + 0.35, 2.42, rw - 0.7, 0.95,
     [[('Spanish-speaking Latin America: ', {'bold': True, 'color': INK}), ('Argentina, Chile, Peru, Colombia, Mexico and neighbours.', {})],
      [('Lists: ', {'bold': True, 'color': INK}), ('“South America” (481 contacts) plus curated sa-latam / sam / sa2 batches.', {})]],
     size=12.5, color=GREY, lsp=1.03, after=4)
text(s, rx + 0.35, 3.42, 4, 0.25, 'INDUSTRIAL BUYERS IN', size=10, bold=True, color=MUTE, spc=1.4)
chips = ['Cement', 'Mining', 'Steel', 'Food processing', 'Water treatment']; cxp = rx + 0.35
for ctext in chips:
    cwid = 0.26 + 0.072 * len(ctext)
    b = box(s, cxp, 3.74, cwid, 0.34, fill='FBEFEA', r=0.17, line='EBC9C1', lw=0.75)
    label_in(b, ctext, size=11, bold=True, color=RED); cxp += cwid + 0.1
card(s, rx, 4.47, rw, 2.26, r=0.14)
text(s, rx + 0.35, 4.65, 4, 0.3, 'Language & message', size=16, bold=True, color=INK)
text(s, rx + 0.35, 5.04, rw - 0.7, 0.3, [[('All outreach in ', {}), ('Spanish', {'bold': True, 'color': INK}),
                                           (', personalised by company name.', {})]], size=12.5, color=GREY)
sb = box(s, rx + 0.35, 5.42, rw - 0.7, 0.5, fill=INK, r=0.1)
label_in(sb, [[('SUBJECT   ', {'size': 9.5, 'color': GOLD, 'spc': 1.5}), ('Reductores para {{company}}', {'size': 14.5}),
               ('   ·  A/B tested', {'size': 10.5, 'bold': False, 'color': PALE})]], color=WHITE, align='l')
sb.text_frame.margin_left = Inches(0.2)
text(s, rx + 0.35, 6.08, rw - 0.7, 0.3, [[('Replies handled in Spanish', {'bold': True, 'color': INK}), (', with Bilal CC’d.', {})]],
     size=12.5, color=GREY)
notes(s, 'Named target markets are the five listed in the report. Lighter countries are the other Spanish-speaking markets the lists '
         'cover as neighbours. Brazil speaks Portuguese and is not yet addressed.')

# ============================================================================= 7 · tools
s = content_slide('TOOLS', 'Programs and tools behind the campaign')
tools = [('Apollo.io', 'DATA  ·  SENDING', ['Contact database search', 'Email enrichment and reveal', 'Sequence builder', 'Sending engine', 'Analytics']),
         ('Microsoft 365 / Outlook', 'REPLIES', ['Reply handling', 'Draft replies', 'Sent manually to keep control']),
         ('Python scripts', 'DATA PREP', ['List building', 'De-dup: one per company', 'Contact-ID to email mapping', 'Batch selection']),
         ('Claude Code', 'ORCHESTRATION', ['Orchestration', 'Daily monitoring', 'Reply mapping', 'Reporting and scheduling'])]
tw4 = (CW - 3 * 0.22) / 4
for i, (n, tag, d) in enumerate(tools):
    xx = MX + i * (tw4 + 0.22)
    card(s, xx, 1.95, tw4, 3.55, r=0.14)
    top = box(s, xx, 1.95, tw4, 1.28, fill=INK, r=0.14)
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
notes(s, 'Four tools cover the whole loop: Apollo for data and sending, Python for list preparation, Outlook for replies, '
         'Claude Code for orchestration, monitoring and reporting.')

# ============================================================================= 8 · step by step
s = content_slide('PROCESS', 'Step by step: how we ran it')
steps = [('Define the target', 'LatAm industrial gearbox and reducer buyers: cement, mining, steel, food and water.'),
         ('Build contact lists', 'Apollo people search by region, industry and title.'),
         ('Clean & de-duplicate', 'One contact per company; repeats and invalid records removed.'),
         ('Enrich & verify emails', 'Verified through Apollo; batches of about 500 prepared.'),
         ('Write the Spanish email', 'Personalised copy with A/B subject variants.'),
         ('Configure the sequence', f'Sender “i.Mak Export Team”, cap {D["cap"]} a day, controlled send windows.'),
         ('Launch & monitor daily', 'Sent, delivered, replies, bounces and spam blocks.'),
         ('Protect deliverability', 'Cap held steady, spam-block trend watched, no reputation damage.'),
         ('Route the leads', 'Every replier mapped to their inbox; Spanish replies drafted; Bilal CC’d.'),
         ('Automate check-ins', 'Daily numbers, new leads and the watch rule.')]
cwid = CW / 5
for r_ in range(2):
    yy = 2.05 + r_ * 2.38
    line(s, MX + 0.27, yy + 0.27, MX + 4 * cwid + 0.27, yy + 0.27, 'D9D3C9', 1.5)
    for c_ in range(5):
        i = r_ * 5 + c_; xx = MX + c_ * cwid; t, d = steps[i]
        circ = box(s, xx, yy, 0.54, 0.54, fill=RED if i not in (8,) else RED, shape=MSO_SHAPE.OVAL)
        label_in(circ, str(i + 1), size=15, color=WHITE)
        text(s, xx, yy + 0.72, cwid - 0.25, 0.32, t, size=14.5, bold=True, color=INK)
        text(s, xx, yy + 1.06, cwid - 0.3, 1.1, d, size=11.5, color=GREY, lsp=1.05)
notes(s, 'Ten steps from defining the ideal customer profile to automated daily check-ins. Steps 7 to 10 run every day.')

# ============================================================================= 9 · challenges
s = content_slide('LESSONS', 'Six challenges we faced')
ch = [('DELIVERABILITY', BAD, 'Early spam-block spike', 'Spam blocks escalated early (+3 / +3 / +3 / +5), a reputation risk. Contained by holding the cap at 120 rather than scaling up.'),
      ('CAPACITY', AMBER, 'Single-inbox ceiling', 'One sender and inbox caps safe volume at about 120 a day — the ceiling on monthly reach.'),
      ('CONTACTS', AMBER, 'List size limits the goal', 'Reaching 2,000 is limited by list size, not speed. It needs ongoing contact sourcing.'),
      ('TRACKING', AMBER, 'Weak open tracking', 'Open tracking fired on few messages. Replies are the only reliable signal, so top-of-funnel engagement is partly blind.'),
      ('HYGIENE', AMBER, 'Bounce rate to maintain', f'About {PCT_BOUNCE}% bounce — acceptable, but list quality needs continuous maintenance.'),
      ('COVERAGE', BAD, 'Spanish only — no Brazil yet', 'Brazil (Portuguese), the largest LatAm market, is not yet addressed.')]
cw3 = (CW - 2 * 0.22) / 3
for i, (tag, col, t, d) in enumerate(ch):
    xx = MX + (i % 3) * (cw3 + 0.22); yy = 1.9 + (i // 3) * 2.46
    card(s, xx, yy, cw3, 2.26, r=0.14)
    box(s, xx, yy + 0.3, 0.07, 1.66, fill=col)
    chip = box(s, xx + 0.32, yy + 0.28, 0.42 + 0.092 * len(tag), 0.29, fill=col, r=0.145)
    label_in(chip, tag, size=9.5, color=WHITE, spc=1.3)
    text(s, xx + 0.32, yy + 0.72, cw3 - 0.6, 0.35, t, size=16.5, bold=True, color=INK)
    text(s, xx + 0.32, yy + 1.12, cw3 - 0.62, 1.05, d, size=12, color=GREY, lsp=1.06)
notes(s, 'Red tags are the two issues with the biggest impact: early deliverability risk, now contained, and no Brazil coverage. '
         'Amber tags are ongoing constraints to manage.')

# ============================================================================= 10 · growth levers
s = content_slide('GROWTH PLAN', 'Seven levers to gain more')
lev = [('Scale sending safely', 'Add and warm up more inboxes and domains, then rotate sends. Lifts the 120-a-day ceiling without hurting reputation.'),
       ('Open a Brazil track', 'Brazil is the largest LatAm industrial market. A dedicated Portuguese sequence multiplies reach.'),
       ('Go multichannel', 'LinkedIn multithreading and phone follow-up on repliers and high-value accounts such as Loma Negra.'),
       ('Feed the funnel', 'Continuous contact sourcing (300+ a month) plus trigger-based prospecting: expansions, plant projects, job changes.'),
       ('Localise the offer', 'Spanish landing page and catalogue link, case studies and references to lift the reply-to-quote rate.'),
       ('Optimise the message', 'Pre-send validation to cut bounces, spintax and subject A/B tests, tuned follow-up cadence.'),
       ('Track to revenue', f'Push the {D["replies"]} leads into a CRM pipeline and measure replies → quotes → orders.')]
cw4 = (CW - 3 * 0.2) / 4
for i, (t, d) in enumerate(lev):
    xx = MX + (i % 4) * (cw4 + 0.2); yy = 1.9 + (i // 4) * 2.46
    card(s, xx, yy, cw4, 2.26, r=0.14)
    circ = box(s, xx + 0.26, yy + 0.26, 0.44, 0.44, fill=RED, shape=MSO_SHAPE.OVAL); label_in(circ, str(i + 1), size=13, color=WHITE)
    text(s, xx + 0.26, yy + 0.84, cw4 - 0.45, 0.34, t, size=14.5, bold=True, color=INK)
    text(s, xx + 0.26, yy + 1.19, cw4 - 0.48, 1.0, d, size=11.5, color=GREY, lsp=1.05)
xx = MX + 3 * (cw4 + 0.2); yy = 1.9 + 2.46
card(s, xx, yy, cw4, 2.26, fill=INK, r=0.14)
text(s, xx + 0.28, yy + 0.26, cw4 - 0.5, 0.25, 'THE SHIFT', size=10, bold=True, color=GOLD, spc=1.8)
text(s, xx + 0.28, yy + 0.6, cw4 - 0.5, 0.75, ['One inbox, one language,', 'one channel'], size=14, color=PALE, lsp=1.0)
text(s, xx + 0.28, yy + 1.22, cw4 - 0.5, 0.95, ['→ more inboxes, two languages, three channels.'], size=15, bold=True, color=WHITE, lsp=1.0)
notes(s, 'Levers 1 and 2 raise volume and reach. Lever 3 raises conversion on the leads already won. Levers 4 to 6 keep the funnel '
         'full and clean. Lever 7 connects the campaign to closed business.')

# ============================================================================= 11 · next steps
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(INK)
box(s, 0, 0, 0.28, SH, fill=RED)
pic(s, 'logo_white.png', SW - 0.8 - 1.75, 0.72, h=0.44)
text(s, 1.0, 0.72, 7, 0.3, 'NEXT 30 DAYS', size=12.5, bold=True, color=GOLD, spc=2.2)
text(s, 1.0, 1.05, 9, 0.8, 'Proposed next steps', size=40, bold=True, color=WHITE)
nxt = [('Secure the 2,000', f'Top up {D["topup"]} contacts so the month closes on target.'),
       ('Lift the ceiling', f'Add and warm up more inboxes and domains, then rotate sends above {D["cap"]} a day.'),
       ('Open Brazil', 'Launch a dedicated Portuguese sequence for the largest LatAm market.'),
       (f'Convert the {D["replies"]}', 'Move every reply into a CRM pipeline; add LinkedIn and phone follow-up on Loma Negra and other high-value accounts.')]
for i, (t, d) in enumerate(nxt):
    yy = 2.3 + i * 1.02
    text(s, 1.0, yy, 1.0, 0.8, f'0{i + 1}', size=34, bold=True, color=GOLD, anchor='m')
    text(s, 2.15, yy + 0.02, 3.6, 0.8, t, size=21, bold=True, color=WHITE, anchor='m')
    text(s, 5.75, yy + 0.02, 6.7, 0.8, d, size=14.5, color=PALE, anchor='m', lsp=1.03)
    if i < 3: line(s, 1.0, yy + 0.92, 12.5, yy + 0.92, '343A45', 0.75)
text(s, 1.0, 6.62, 11.5, 0.5, f'Figures pulled live from Apollo on {D["date"]}: sent {fmt(D["sent"])} · delivered {fmt(D["delivered"])} · '
     f'replies {D["replies"]} · bounced {D["bounced"]} · spam blocked {D["spam"]} · scheduled {D["scheduled"]}. '
     'Strategy sections are internal analysis. Prepared for i.Mak export sales review.', size=10.5, color=MUTE, lsp=1.0)
notes(s, 'The four proposed steps are drawn from the growth levers and ordered by how quickly they pay back. '
         'Costs and owners are still to be agreed.')

prs.save(OUT); print('saved', OUT, 'slides:', len(prs.slides))
