import fitz, re, csv
U='/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/'
def clean(s): return re.sub(r'\s+',' ',(s or '').strip())
def tq(s):
    m=re.search(r'\d+',(s or '').replace('.','')); return m.group(0) if m else ''
out=[]
def add(series,imak,brand,comp,d,h,torque):
    imak=clean(imak); comp=clean(comp)
    if not comp: return
    out.append(dict(series=series,imak_type=imak,brand=brand,comp_type=comp,comp_d=clean(d),comp_h=clean(h),max_torque_nm=tq(torque)))

# file configs: (path, series, [ (brand, type_col, d_col, h_col) ... ], imak_type_col, torque_col)
CFG=[
 ('adb7c36c-1._Helical_Gearbox__Comparison_Table__I.Mak__SEW__Nord__IR_Series.pdf','IR',2,11,
    [('SEW',5,6,7),('NORD',8,9,10)]),
 ('3b7eecef-2._Helical_Bevel_Gearbox__Comparison_Table__I.Mak__SEW__Nord__IRK_Series.pdf','IRK',2,14,
    [('SEW',6,8,9),('NORD',10,12,13)]),
 ('3b7e1273-3._Parallel_Shaft_Gearbox__Comparison_Table__I.Mak__SEW__Nord__YP_Series.pdf','YP',2,14,
    [('SEW',6,8,9),('NORD',10,12,13)]),
 ('4a069afb-4._Helical_Gearbox__Comparison_Table__I.Mak__Bonfiglioli__IR_Series.pdf','IR',2,9,
    [('Bonfiglioli',6,7,8)]),
 ('074eec31-5._Helical_Bevel_Gearbox__Comparison_Table__I.Mak__Bonfiglioli__IRK_Series.pdf','IRK',2,11,
    [('Bonfiglioli',7,9,10)]),
]
for fn,series,imak_col,tq_col,brands in CFG:
    d=fitz.open(U+fn)
    for t in d[0].find_tables().tables:
        rows=t.extract()
        for r in rows:
            c=[ (x or '').strip() for x in r]
            if len(c)<=tq_col: continue
            imak=c[imak_col] if imak_col<len(c) else ''
            # skip header rows
            if 'TYPE' in imak.upper() or 'TİP' in imak.upper() or 'I-MAK' in ' '.join(c[:3]).upper(): continue
            torque=c[tq_col] if tq_col<len(c) else ''
            for brand,tc,dc,hc in brands:
                comp=c[tc] if tc<len(c) else ''
                if comp and not re.search(r'TYPE|TİP',comp.upper()):
                    add(series,imak,brand,comp,c[dc] if dc<len(c) else '',c[hc] if hc<len(c) else '',torque)
with open('xref_gearbox.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['series','imak_type','brand','comp_type','comp_d','comp_h','max_torque_nm']); w.writeheader(); w.writerows(out)
from collections import Counter
print("xref_gearbox rows:",len(out))
print("by series x brand:",dict(Counter((o['series'],o['brand']) for o in out)))
print("with imak_type:",sum(1 for o in out if o['imak_type']))
for o in out[:3]+[x for x in out if x['brand']=='NORD'][:2]+[x for x in out if x['brand']=='Bonfiglioli'][:2]: print(o)
