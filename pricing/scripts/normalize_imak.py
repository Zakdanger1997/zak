import json, re, csv
raw=json.load(open('imak_main_raw.json'))

def num(s):
    s=(s or '').strip()
    if not s or s in ('-','Standart'): return s
    m=re.search(r'[\d.]+,\d{2}', s)
    if m: return m.group(0).replace('.','').replace(',','.')
    return s
def kw(s):
    m=re.search(r'([\d,\.]+)\s*KW', (s or '').upper())
    return m.group(1).replace(',','.') if m else ''
def hp(s):
    m=re.search(r'([\d,\.]+)\s*HP', (s or '').upper())
    return m.group(1).replace(',','.') if m else ''

geared=[]   # geared motor SKUs
iec=[]      # IEC/PAM units
simple=[]   # type -> price

def series_of(sect):
    m=re.match(r'([A-Za-zİŞĞÜÖÇ/]+)\s+SER', sect)
    return m.group(1) if m else sect[:12]

for o in raw:
    sect=o['section']; ser=series_of(sect); pg=o['page']; rows=o['rows']
    # find header row index
    hi=next((i for i,r in enumerate(rows) if any(h in ' '.join(r).upper() for h in ('GÜÇ','TİP','TIP'))),0)
    header=[c.upper() for c in rows[hi]]
    body=rows[hi+1:]
    ncol=o['ncols']
    # GEARED MOTOR 5-col: GÜÇ DEVİR TİP foot flange
    if ncol==5 and 'GÜÇ' in ' '.join(header):
        cur_kw=cur_hp=''
        for r in body:
            g,dev,tip,p1,p2=[ (r[i] if i<len(r) else '') for i in range(5)]
            if kw(g): cur_kw=kw(g)
            if hp(g): cur_hp=hp(g)
            if not tip.strip(): continue
            parts=tip.split('/')
            gearbox=parts[0].strip()
            motor='/'.join(parts[1:]).strip() if len(parts)>1 else ''
            geared.append(dict(series=ser,page=pg,power_kw=cur_kw,power_hp=cur_hp,
                output_rpm=dev.strip(),type_full=tip.strip(),gearbox=gearbox,motor=motor,
                price_foot_tl=num(p1),price_flange_tl=num(p2)))
    # IEC/PAM 4-col: TİP  IEC flange  foot flange
    elif ncol==4 and ('IEC' in ' '.join(header) or ser.endswith('P')):
        cur_tip=''
        for r in body:
            tip,iecf,p1,p2=[ (r[i] if i<len(r) else '') for i in range(4)]
            if tip.strip(): cur_tip=tip.strip()
            if not iecf.strip() and not p1.strip(): continue
            iec.append(dict(series=ser,page=pg,gearbox=cur_tip,iec_flange=iecf.strip(),
                price_foot_tl=num(p1),price_flange_tl=num(p2)))
    # SIMPLE 2-col: TİP FİYAT
    elif ncol==2:
        for r in body:
            a,b=[ (r[i] if i<len(r) else '') for i in range(2)]
            if not a.strip(): continue
            simple.append(dict(series=ser,page=pg,type=a.strip(),price_tl=num(b)))
    # 8-col doubled hoist: split
    elif ncol==8:
        for r in body:
            for half in (r[:4], r[4:8]):
                tip,gd,dd,pr=[ (half[i] if i<len(half) else '') for i in range(4)]
                if not tip.strip() or 'Güç' in gd: continue
                m=re.search(r'([\d,\.]+)\s*kW',gd); rpm=re.search(r'(\d+)\s*d/d',gd)
                geared.append(dict(series=ser,page=pg,power_kw=(m.group(1).replace(',','.') if m else ''),
                    power_hp='',output_rpm=dd.strip(),type_full=tip.strip(),
                    gearbox=tip.split('/')[0].strip(),motor=('/'.join(tip.split('/')[1:]).strip()),
                    price_foot_tl=num(pr),price_flange_tl=''))

def dump(fn,rows,cols):
    with open(fn,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"{fn}: {len(rows)} rows")

dump('imak_geared_motors.csv',geared,['series','page','power_kw','power_hp','output_rpm','type_full','gearbox','motor','price_foot_tl','price_flange_tl'])
dump('imak_iec_units.csv',iec,['series','page','gearbox','iec_flange','price_foot_tl','price_flange_tl'])
dump('imak_simple_types.csv',simple,['series','page','type','price_tl'])
print("\nseries in geared:",sorted(set(r['series'] for r in geared)))
print("sample geared:",geared[3])
print("sample iec:",iec[0] if iec else None)
