import fitz, re, csv
U="/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/"
STD={
 "TL":U+"0cdcc621-.Mak_Redktr_Fiyat_Listesi__R02_26.01.2026.pdf",
 "EUR":U+"aef5d987-I.MAK_GEARBOX_STANDARD_SERIES_EURO_PRICE_LIST__26.01.2026.pdf",
 "USD":U+"13703750-I.MAK_GEARBOX_DOLLAR_PRICE_LIST__26.01.2026.pdf",
}
def num(s):
    s=(s or '').strip()
    if not s or s in ('-','Standart','Standard'): return s
    m=re.search(r'[\d.]+,\d{2}', s)
    if m: return m.group(0).replace('.','').replace(',','.')
    m=re.search(r'\d[\d,]*\.\d{2}', s)  # english 1,234.00
    if m: return m.group(0).replace(',','')
    return s
def kw(s):
    m=re.search(r'([\d,\.]+)\s*KW',(s or '').upper()); return m.group(1).replace(',','.') if m else ''
def hp(s):
    m=re.search(r'([\d,\.]+)\s*HP',(s or '').upper()); return m.group(1).replace(',','.') if m else ''
def series_of(sect):
    m=re.match(r'([A-Za-zİŞĞÜÖÇ/]+)\s+SER',sect); return m.group(1) if m else sect[:12]

geared=[]; iec=[]; simple=[]
for curcy,f in STD.items():
    d=fitz.open(f)
    for pno in range(d.page_count):
        pg=d[pno]; lines=[l.strip() for l in pg.get_text().splitlines() if l.strip()]
        sect=next((l for l in lines if 'SER' in l.upper()),"")
        ser=series_of(sect)
        for t in pg.find_tables().tables:
            rows=[[ (c or '').replace('\n',' ').strip() for c in r] for r in t.extract()]
            rows=[r for r in rows if any(r)]
            if not rows: continue
            hi=next((i for i,r in enumerate(rows) if any(h in ' '.join(r).upper() for h in ('GÜÇ','POWER','TİP','TYPE'))),0)
            header=' '.join(rows[hi]).upper(); body=rows[hi+1:]; ncol=len(rows[0])
            if ncol==5 and ('GÜÇ' in header or 'POWER' in header):
                ck=ch=''
                for r in body:
                    g,dev,tip,p1,p2=[(r[i] if i<len(r) else '') for i in range(5)]
                    if kw(g): ck=kw(g)
                    if hp(g): ch=hp(g)
                    if not tip.strip(): continue
                    parts=tip.split('/')
                    geared.append(dict(currency=curcy,series=ser,page=pno+1,power_kw=ck,power_hp=ch,
                        output_rpm=dev.strip(),type_full=tip.strip(),gearbox=parts[0].strip(),
                        motor=('/'.join(parts[1:]).strip() if len(parts)>1 else ''),
                        price_foot=num(p1),price_flange=num(p2)))
            elif ncol==4 and ('IEC' in header or ser.endswith('P')):
                ct=''
                for r in body:
                    tip,iecf,p1,p2=[(r[i] if i<len(r) else '') for i in range(4)]
                    if tip.strip(): ct=tip.strip()
                    if not iecf.strip() and not p1.strip(): continue
                    iec.append(dict(currency=curcy,series=ser,page=pno+1,gearbox=ct,iec_flange=iecf.strip(),
                        price_foot=num(p1),price_flange=num(p2)))
            elif ncol==2:
                for r in body:
                    a,b=[(r[i] if i<len(r) else '') for i in range(2)]
                    if not a.strip(): continue
                    simple.append(dict(currency=curcy,series=ser,page=pno+1,type=a.strip(),price=num(b)))
            elif ncol==8:
                for r in body:
                    for half in (r[:4],r[4:8]):
                        tip,gd,dd,pr=[(half[i] if i<len(half) else '') for i in range(4)]
                        if not tip.strip() or 'Güç' in gd or 'Power' in gd: continue
                        m=re.search(r'([\d,\.]+)\s*kW',gd)
                        geared.append(dict(currency=curcy,series=ser,page=pno+1,
                            power_kw=(m.group(1).replace(',','.') if m else ''),power_hp='',
                            output_rpm=dd.strip(),type_full=tip.strip(),gearbox=tip.split('/')[0].strip(),
                            motor=('/'.join(tip.split('/')[1:]).strip()),price_foot=num(pr),price_flange=''))
def dump(fn,rows,cols):
    with open(fn,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in cols})
    print("%s: %d"%(fn,len(rows)))
dump('imak_geared_motors.csv',geared,['currency','series','page','power_kw','power_hp','output_rpm','type_full','gearbox','motor','price_foot','price_flange'])
dump('imak_iec_units.csv',iec,['currency','series','page','gearbox','iec_flange','price_foot','price_flange'])
dump('imak_simple_types.csv',simple,['currency','series','page','type','price'])
from collections import Counter
print("geared by currency:",dict(Counter(r['currency'] for r in geared)))
