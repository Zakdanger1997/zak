import fitz, re, csv
U="/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/"
def price(s):
    s=(s or '')
    m=re.search(r'[\d.]+,\d{2}',s)
    if m: return m.group(0).replace('.','').replace(',','.')
    m=re.search(r'\d[\d,]*\.\d{2}',s)
    if m: return m.group(0).replace(',','')
    m=re.search(r'\d[\d.,]*',s)
    return m.group(0).replace('.','').replace(',','.') if m else ''

# ---------- MA/MK all 3 currencies (semi-structured options) ----------
MAMK={"TL":U+"5b8282d3-M..._SERS_FYAT_LSTES_R01__26.01.2026.pdf",
      "EUR":U+"1c7d70af-I.MAK_GEARBOX__MA__MK_SERIES_EURO_PRICE_LIST_26.01.2026.pdf",
      "USD":U+"0295ba67-I.MAK_GEARBOX_MA__MK_SERIES_DOLLAR_PRICE_LIST_26.01.2026.pdf"}
mamk=[]
for cur,f in MAMK.items():
    d=fitz.open(f)
    for pno in range(d.page_count):
        for t in d[pno].find_tables().tables:
            rows=[[ (c or '').replace('\n',' ').strip() for c in r] for r in t.extract()]
            rows=[r for r in rows if any(r)]
            if not rows: continue
            title=rows[0][0][:45]
            for r in rows:
                cells=[c for c in r if c]
                if len(cells)<2: continue
                mamk.append(dict(currency=cur,page=pno+1,table=title,cells=' | '.join(cells)))

# ---------- Planetary IPR/IPRK matrix (EUR) ----------
d=fitz.open(U+"d9e54d90-I.MAK_GEARBOX_PLANETARY_SERIES_EURO_26.02.2026.pdf")
plan=[]
stage_map=['IPR|S1','IPR|S2','IPR|S3','IPR|S4','IPRK|S2','IPRK|S3','IPRK|S4','IPRK|S5']
for pno in range(d.page_count):
    for t in d[pno].find_tables().tables:
        rows=[[ (c or '').replace('\n',' ').strip() for c in r] for r in t.extract()]
        size=''
        for r in rows:
            if not any(r): continue
            # size appears in col0 as a number like 101/121/141...
            if re.match(r'^\d{2,3}$', r[0].strip()): size=r[0].strip()
            cfg=r[1].strip() if len(r)>1 else ''
            prices=[c for c in r[2:] if '€' in c or re.search(r'\d',c)]
            if cfg and re.match(r'^[A-Z]{1,3}$',cfg) and prices:
                for i,p in enumerate(prices[:8]):
                    sr,st=(stage_map[i].split('|') if i<len(stage_map) else ('?','?'))
                    plan.append(dict(size=size,series=sr,stage=st,input_config=cfg,price_eur=price(p),page=pno+1))

# ---------- CEMA (customer, USD) ----------
d=fitz.open(U+"043f6627-Price_Lst_for_CEMA__01.01.2023.pdf")
cema=[]
for pno in range(d.page_count):
    for t in d[pno].find_tables().tables:
        for r in t.extract():
            r=[ (c or '').replace('\n',' ').strip() for c in r]
            cells=[c for c in r if c]
            if len(cells)>=2 and any('$' in c for c in r) and not r[0].upper().startswith('TYPE'):
                cema.append(dict(page=pno+1,cells=' | '.join(cells)))

# ---------- Redservis Russia (distributor, S-series EUR) ----------
d=fitz.open(U+"bdc21235-REDSERVISRUSSIA_S_SERIES__EURO_PRICE_LIST_01.12.2024.pdf")
red=[]
for pno in range(d.page_count):
    for t in d[pno].find_tables().tables:
        rows=[[ (c or '').strip() for c in r] for r in t.extract()]
        hdr=rows[0] if rows else []
        for r in rows[1:]:
            if r and r[0] and re.search(r'\d',' '.join(r)):
                red.append(dict(page=pno+1,type=r[0],
                    gearbox=price(r[1]) if len(r)>1 else '',flange=price(r[2]) if len(r)>2 else '',
                    single_shaft=price(r[3]) if len(r)>3 else '',double_shaft=price(r[4]) if len(r)>4 else '',
                    torque_arm=price(r[5]) if len(r)>5 else ''))

# ---------- Kaplin couplings ----------
d=fitz.open(U+"61a9cb1f-Kaplin_Fiyatlar_1.pdf")
kap=[]
for pno in range(d.page_count):
    for t in d[pno].find_tables().tables:
        for r in t.extract():
            r=[ (c or '').replace('\n',' ').strip() for c in r]
            cells=[c for c in r if c]
            if len(cells)>=2 and re.search(r'\d',' '.join(cells)):
                kap.append(dict(page=pno+1,cells=' | '.join(cells)))

def dump(fn,rows,cols):
    with open(fn,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in cols})
    print("%s: %d"%(fn,len(rows)))
dump('imak_mamk_options.csv',mamk,['currency','page','table','cells'])
dump('imak_planetary.csv',plan,['size','series','stage','input_config','price_eur','page'])
dump('cema_customer_options.csv',cema,['page','cells'])
dump('redservis_s_series.csv',red,['page','type','gearbox','flange','single_shaft','double_shaft','torque_arm'])
dump('kaplin_couplings.csv',kap,['page','cells'])
print("planetary sizes:",sorted(set(p['size'] for p in plan if p['size']))[:20])
print("planetary sample:",plan[0] if plan else None)
