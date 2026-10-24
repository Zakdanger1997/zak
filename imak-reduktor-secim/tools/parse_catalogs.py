#!/usr/bin/env python3
"""Parse i.Mak performance tables out of the public catalog PDFs into JSON for the selector.

Usage: parse_catalogs.py <catalog.pdf> <series> <out.json> [first_page] [last_page]

Three table kinds share one geometry (IR, IRK, YP, IRS/S/IRSD catalogs, 2025-2026 editions):
  motor : geared motors      P1 | n2 | i | Sf | M2 | Fr | types | size [primary] / motor | pages | kg
  worm  : IRSD geared motors P1 | n2 | i_worm | i_total | Sf | M2 | Fr | types | ...
  unit  : gear units, Sf = 1 P1 | n2 | i | M2n | Fr1 | Fr2 | types | size [primary] | pages | kg
          (input speed n1 printed once per page as "(n1=1400rpm)")
Columns are located from the unit labels in the header ([kW], [r.p.m], [Nm], [N], kg); size
groups are the shaded blocks / full-width separator rules; the type annotation sits inside its group.
"""
import json, re, sys
import pdfplumber

def num(t):
    return float(t.replace('.', '').replace(',', '.'))

def fix(t):
    return (t.replace('(cid:248)', 'I').replace('İ', 'I').replace('ø', 'I')
             .replace('(cid:51)', 'P').replace('(cid:97)', '~'))

def parse_page(page, pno):
    words = page.extract_words(x_tolerance=1.5, y_tolerance=2)
    for w in words:
        w['text'] = fix(w['text'])
    hdr = [w for w in words if 60 < w['top'] < 175]
    def find(*labels):
        return [w for w in hdr if w['text'] in labels]
    kw, rpm, nm, N = find('[kW]'), find('[r.p.m]', '[rpm]'), find('[Nm]'), find('[N]')
    if not (kw and rpm and nm and N):
        return []
    vsep = sorted(set(round(r['x0']) for r in page.rects if r['height'] > 500 and r['width'] < 2.5))
    if len(vsep) < 6:
        return []
    bounds = [0] + vsep + [page.width]
    def col(x):
        for k in range(len(bounds) - 1):
            if bounds[k] <= x < bounds[k + 1]:
                return k
        return len(bounds) - 2
    cx = lambda w: (w['x0'] + w['x1']) / 2
    c_p1, c_n2, c_m2 = col(cx(kw[0])), col(cx(rpm[0])), col(cx(nm[0]))
    c_fr = sorted(col(cx(w)) for w in N)
    ratio_cols = [c for c in range(c_n2 + 1, c_m2) if c not in ()]
    kind = 'unit' if any(w['text'].startswith('(n1=') for w in words) else ('worm' if len(ratio_cols) == 3 else 'motor')
    # motor: n2 | i | Sf | M2 ; worm: n2 | iw | it | Sf | M2 ; unit: n2 | i | M2
    if kind == 'motor' and len(ratio_cols) != 2:
        return []
    if kind == 'unit' and len(ratio_cols) != 1:
        return []
    c_types = c_fr[-1] + 1
    c_codes, c_pages, c_kg = c_types + 1, c_types + 2, c_types + 3
    n1 = None
    for w in words:
        m = re.match(r'\(n1=(\d+)rpm\)', w['text'])
        if m:
            n1 = int(m.group(1))
    # group boundaries = wide thin separator rules + edges of shaded size blocks
    ys = set()
    for r in page.rects:
        if r['height'] < 2 and r['x0'] < 140 and r['x1'] > 500 and 400 < r['x1'] - r['x0'] < 560 and r['top'] > 100:
            ys.add(round(r['top'], 1))
    for shp in list(page.rects) + list(page.curves):
        if shp['x1'] - shp['x0'] > 300 and shp['bottom'] - shp['top'] > 5 and shp['x0'] > 100 and shp['top'] > 100:
            ys.add(round(shp['top'], 1)); ys.add(round(shp['bottom'], 1))
    ys = sorted(ys)
    merged = []
    for y in ys:
        if merged and y - merged[-1] < 3:
            continue
        merged.append(y)
    groups = [(merged[k], merged[k + 1]) for k in range(len(merged) - 1)]
    def grp(y):
        for gi, (t, b) in enumerate(groups):
            if t - 1 <= y <= b + 1:
                return gi
        return None
    gw = [[] for _ in groups]
    for w in words:
        if w['top'] < 150:
            continue
        gi = grp((w['top'] + w['bottom']) / 2)
        if gi is None:
            continue
        w['col'] = col(cx(w))
        gw[gi].append(w)
    numcols = list(range(c_n2, c_fr[-1] + 1))
    out = []
    for gi, ws in enumerate(gw):
        ws.sort(key=lambda w: (round(w['top']), w['x0']))
        lines = []
        for w in ws:
            if lines and abs(lines[-1][0] - w['top']) <= 2.5:
                lines[-1][1].append(w)
            else:
                lines.append([w['top'], [w]])
        rows, types, codes, pages, weights, p1lab = [], [], [], [], [], []
        for _, lw in lines:
            bycol = {}
            for w in lw:
                bycol.setdefault(w['col'], []).append(w['text'])
            vals = [bycol.get(c, [None])[0] for c in numcols]
            p1v = bycol.get(c_p1, [None])[0]
            if all(v and re.fullmatch(r'[\d.,]+', v) for v in vals):
                try:
                    row = [num(v) for v in vals]
                    if kind == 'unit':
                        row = [num(p1v) if p1v and re.fullmatch(r'[\d.,]+', p1v) else None] + row
                    rows.append(row)
                except ValueError:
                    pass
            for t in bycol.get(c_p1, []):
                if re.fullmatch(r'\d+(,\d+)?', t) and kind != 'unit':
                    p1lab.append(num(t))
            types += [t for t in bycol.get(c_types, []) if re.search(r'[A-Z]', t)]
            codes += bycol.get(c_codes, [])
            pages += [t for t in bycol.get(c_pages, []) if re.fullmatch(r'\d+', t)]
            weights += [t for t in bycol.get(c_kg, []) if re.fullmatch(r'\d+(,\d+)?', t)]
        if not rows:
            continue
        tt = []
        for t in types:
            if t.startswith('-') and tt:
                tt[-1] += t
            else:
                tt.append(t)
        size, primary, motor = None, None, None
        s = ' '.join(codes).strip()
        if kind == 'unit':
            m = re.match(r'^(\d+)\s*(.*)$', s)
            if m:
                size, primary = m.group(1), (m.group(2).strip() or None)
        else:
            m = re.match(r'^(\d+)\s*(.*?)\s*/?\s*(\d+)\s*([A-Z]{1,2})\s*(\d[a-d]?)$', s)
            if m:
                size, primary, motor = m.group(1), (m.group(2).strip() or None), f"{m.group(3)}{m.group(4)} {m.group(5)}"
            else:
                size = s or None
        out.append({'page': pno, 'kind': kind, 'n1': n1, 'types': tt, 'size': size, 'primary': primary,
                    'motor': motor, 'p1_labels': p1lab, 'pages': pages, 'weights': weights, 'rows': rows})
    return out

def main():
    pdf_path, series, out_path = sys.argv[1:4]
    first = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    pdf = pdfplumber.open(pdf_path)
    last = int(sys.argv[5]) if len(sys.argv) > 5 else len(pdf.pages)
    groups = []
    for pno in range(first, last + 1):
        groups += parse_page(pdf.pages[pno - 1], pno)
    json.dump({'series': series, 'source': pdf_path.split('/')[-1], 'groups': groups},
              open(out_path, 'w'), ensure_ascii=False, indent=0)
    kinds = {}
    for g in groups:
        kinds[g['kind']] = kinds.get(g['kind'], 0) + 1
    print(f'{series}: {len(groups)} groups {kinds}, {sum(len(g["rows"]) for g in groups)} rows -> {out_path}')

if __name__ == '__main__':
    main()
