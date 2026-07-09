import fitz, re, csv, json
e=fitz.open('/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/004bbf73-EMF_FREN_FIYAT_LISTESI_26.01.2026__REV.340.pdf')
def cur(s):
    s=s or ''
    if '€' in s: return 'EUR'
    if '₺' in s or 'TL' in s.upper(): return 'TL'
    return ''
def val(s):
    m=re.search(r'([\d.]+)(?:,(\d{2}))?',(s or '').replace(' ',''))
    if not m: return ''
    return m.group(1).replace('.','')+('.'+m.group(2) if m.group(2) else '')
tables_out=[]
brakes=[]
for pno in range(e.page_count):
    lines=[l.strip() for l in e[pno].get_text().splitlines() if l.strip()]
    for t in e[pno].find_tables().tables:
        rows=[[ (c or '').replace('\n',' ').strip() for c in r] for r in t.extract()]
        rows=[r for r in rows if any(r)]
        if not rows: continue
        # locate header row containing KOD
        hi=next((i for i,r in enumerate(rows) if any('KOD' in (c or '').upper() for c in r)),None)
        if hi is None: continue
        header=rows[hi]; title=rows[0][0] if hi>0 else ''
        for r in rows[hi+1:]:
            code=r[0].strip()
            if not code or not re.match(r'^[A-Za-zÇĞİÖŞÜ]{2,}\s*\d', code): continue
            torque=next((c for c in r if re.search(r'\d+\s*-\s*\d+',c or '')),'')
            # each remaining numeric+currency cell => a price variant keyed by header
            for ci,c in enumerate(r):
                if c and ('₺' in c or '€' in c):
                    label=(header[ci] if ci<len(header) else f'col{ci}').strip()
                    brakes.append(dict(page=pno+1,family=title[:40],code=code,torque_nm=torque,
                        price_variant=label,currency=cur(c),price=val(c)))
with open('emf_brakes.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['page','family','code','torque_nm','price_variant','currency','price'])
    w.writeheader(); w.writerows(brakes)
print("emf_brakes.csv:",len(brakes),"price points")
from collections import Counter
print("families:",dict(Counter(b['family'] for b in brakes)))
print("currencies:",dict(Counter(b['currency'] for b in brakes)))
for b in brakes[:4]: print(b)
