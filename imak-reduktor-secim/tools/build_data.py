#!/usr/bin/env python3
"""Merge the raw per-catalog JSON (from parse_catalogs.py) into data/catalog.js.

Resolves the rated motor power P1 of every geared-motor group. The catalogs print P1 once
per power block, not per size group, so P1 is resolved per *motor code* (e.g. "63M 4a"):
every group with that code is the same motor. For each code we combine
  * the kW labels printed inside its groups (Hp labels are recognised and ignored),
  * the back-calculated shaft power M2*n2/9550 of its rows.
and report any code where the two disagree.

Usage: build_data.py <out.js> <raw1.json> [<raw2.json> ...]
"""
import json, re, sys, datetime, math, collections

IEC_POWERS = [0.06, 0.09, 0.12, 0.18, 0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11, 15, 18.5, 22,
              30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315]
POLES_RPM = {2: 3000, 4: 1500, 6: 1000, 8: 750}

def family_of(series, types):
    t = types[0] if types else ''
    if series == 'IRS':
        if t.startswith('IRSD'):
            return 'IRSD'
        if t.startswith('IRS'):
            return 'IRS'
        if t.startswith('S'):
            return 'S'
    return series

def nearest(p, choices):
    return min(choices, key=lambda s: abs(math.log(s / p)))

def main():
    out_path, raws = sys.argv[1], sys.argv[2:]
    raw_groups, sources = [], {}
    for raw in raws:
        d = json.load(open(raw))
        sources[d['series']] = d['source']
        for g in d['groups']:
            g['series'] = d['series']
            raw_groups.append(g)

    # ---- resolve P1 per motor code (the same motor code is the same motor in every family) ----
    HELICAL = ('IR', 'IRK', 'YP')
    labels = collections.defaultdict(list)   # code -> labels seen (kW or Hp) in any family
    calc = collections.defaultdict(list)     # code -> back-calculated shaft powers, helical families only
    for g in raw_groups:
        if g['kind'] == 'unit' or not g.get('motor'):
            continue
        fam = family_of(g['series'], g['types'])
        code = g['motor']
        labels[code] += [lab for lab in g['p1_labels'] if lab > 0]
        if fam in HELICAL:
            m2i = 3 if g['kind'] == 'motor' else 4
            calc[code] += [r[m2i] * r[0] / 9550 for r in g['rows']]
    def hp_to_kw(v):
        k = nearest(v / 1.36, IEC_POWERS)
        return k if abs(k * 1.36 / v - 1) < 0.08 else None
    p1_of, report_lines = {}, []
    for code in sorted(set(labels) | set(calc)):
        labs = collections.Counter(labels[code])
        p2 = sorted(calc[code])
        est = nearest(p2[len(p2) // 2] / 0.93, IEC_POWERS) if p2 else None
        cands = set()
        for v in labs:
            if v in IEC_POWERS:
                cands.add(v)
            k = hp_to_kw(v)
            if k:
                cands.add(k)
        if est is not None and cands:
            p1 = min(cands, key=lambda c: abs(math.log(c / est)))
            note = '' if p1 == est else f'  (calc {est}, labels decide)'
        elif est is not None:
            p1, note = est, '  (back-calculation only)'
        elif cands:
            top = [v for v, _ in labs.most_common(2)]
            if len(top) == 2 and abs(max(top) / min(top) - 1.36) < 0.05:
                p1 = min(top)
            else:
                p1 = top[0] if top[0] in IEC_POWERS else min(cands)
            note = '  (labels only, no helical data)'
        else:
            continue
        p1_of[code] = p1
        report_lines.append(f"{code:9s} -> {p1:>6} kW   labels={dict(labs)} est={est}{note}")
    print('\n'.join(report_lines), file=sys.stderr)

    # ---- assemble groups ----
    groups, stats = [], collections.Counter()
    prev = None
    for g in raw_groups:
        if not g.get('size') or not re.fullmatch(r'\d+', g['size']):
            stats['nosize'] += 1
            print(f"  skipped (no size): {g['series']} p{g['page']} {g['types']} {g['size']!r}", file=sys.stderr)
            continue
        fam = family_of(g['series'], g['types'])
        if g['kind'] == 'unit':
            rows = [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in g['rows'] if r[0] is not None]
            rec = {'k': 'unit', 'f': fam, 's': g['series'], 't': g['types'], 'z': g['size'], 'pr': g.get('primary'),
                   'n1': g.get('n1'), 'pg': [int(x) for x in g['pages']], 'kg': g['weights'], 'cp': g['page'], 'r': rows}
            key = ('unit', fam, tuple(g['types']), g['size'], g.get('primary'), g.get('n1'))
        else:
            poles = int(re.search(r'\s(\d)[a-d]?$', g['motor']).group(1)) if g.get('motor') else None
            p1 = p1_of.get(g['motor'])
            if p1 is None:
                stats['no_p1'] += 1
                continue
            if g['kind'] == 'worm':
                rows = [[r[0], r[2], r[3], r[4], r[5], r[1]] for r in g['rows']]  # n2, i_total, sf, m2, fr, i_worm
            else:
                rows = [list(r) for r in g['rows']]
            rec = {'k': 'motor', 'f': fam, 's': g['series'], 't': g['types'], 'z': g['size'], 'pr': g.get('primary'),
                   'm': g['motor'], 'p1': p1, 'pl': poles, 'pg': [int(x) for x in g['pages']], 'kg': g['weights'],
                   'cp': g['page'], 'r': rows}
            key = ('motor', fam, tuple(g['types']), g['size'], g.get('primary'), g['motor'])
        if not rec['r']:
            continue
        if prev and prev[0] == key:
            prev[1]['r'] += rec['r']
            stats['merged'] += 1
        else:
            groups.append(rec)
            prev = (key, rec)
    for g in groups:
        seen, rows = set(), []
        for r in g['r']:
            k = tuple(r)
            if k not in seen:
                seen.add(k); rows.append(r)
        g['r'] = rows
        stats['rows'] += len(rows)
    stats['groups'] = len(groups)
    payload = {'generated': datetime.date.today().isoformat(), 'sources': sources, 'groups': groups}
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('/* generated by tools/build_data.py from the public i.Mak catalogs; do not edit by hand */\n')
        f.write('window.IMAK_CATALOG = ')
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print(json.dumps(stats), file=sys.stderr)
    for fam in sorted({g['f'] for g in groups}):
        gs = [g for g in groups if g['f'] == fam]
        for kind in ('motor', 'unit'):
            ks = [g for g in gs if g['k'] == kind]
            if not ks:
                continue
            extra = f"P1={sorted({g['p1'] for g in ks})} poles={sorted({g['pl'] for g in ks if g['pl']})}" if kind == 'motor' else f"n1={sorted({g['n1'] for g in ks if g['n1']})}"
            print(f"{fam}/{kind}: {len(ks)} groups, {sum(len(g['r']) for g in ks)} rows, sizes={sorted({g['z'] for g in ks}, key=int)}, "
                  f"types={sorted({t for g in ks for t in g['t']})}, {extra}", file=sys.stderr)

if __name__ == '__main__':
    main()
