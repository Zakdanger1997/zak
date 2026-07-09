import fitz, re, csv
# ---------- GAMAK motors ----------
d=fitz.open('/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/9724226f-Gamak__18_mays_2026_153.pdf')
ie_re=re.compile(r'^IE[\d\-]$'); kw_re=re.compile(r'^\d{1,3},\d{1,2}(/\d{1,3},\d{1,2})?$')
price_re=re.compile(r'^\d{1,3}(\.\d{3})*(,\d{2})?$'); type_re=re.compile(r'[A-Za-z].*\d')
motors=[]
for pno in range(d.page_count):
    lines=[l.strip() for l in d[pno].get_text().splitlines() if l.strip()]
    i=0
    while i < len(lines)-3:
        if ie_re.match(lines[i]) and kw_re.match(lines[i+1]) and type_re.search(lines[i+2]) and price_re.match(lines[i+3]):
            motors.append(dict(page=pno+1,ie_class=lines[i],power_kw=lines[i+1].replace(',','.'),
                motor_type=lines[i+2],price_tl=lines[i+3].replace('.','').replace(',','.')))
            i+=4
        else:
            i+=1
# ---------- EMF brakes ----------
e=fitz.open('/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/004bbf73-EMF_FREN_FIYAT_LISTESI_26.01.2026__REV.340.pdf')
brakes=[]
for pno in range(e.page_count):
    for t in e[pno].find_tables().tables:
        rows=[[ (c or '').replace('\n',' ').strip() for c in r] for r in t.extract()]
        # find header
        for r in rows:
            if not any(r): continue
            joined=' '.join(r).upper()
            if 'KOD' in joined or 'TORK' in joined or 'FİYAT' in joined.replace('I','İ'): 
                hdr=r; continue
            # data row: code, torque, motor, price
            cells=[c for c in r if c]
            if len(cells)>=2 and re.search(r'\d',' '.join(cells)):
                code=cells[0]
                price=next((c for c in cells if '€' in c or re.match(r'^[\d.]+$',c)), '')
                torque=next((c for c in cells if re.search(r'\d+\s*-\s*\d+',c)), '')
                motor=next((c for c in cells if re.match(r'^\d{2,3}$',c)), '')
                brakes.append(dict(page=pno+1,code=code,torque_nm=torque,motor_frame=motor,
                    price=price.replace('.','').replace(',','.').replace('€','').strip()))
def dump(fn,rows,cols):
    with open(fn,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in cols})
    print(f"{fn}: {len(rows)} rows")
dump('gamak_motors.csv',motors,['page','ie_class','power_kw','motor_type','price_tl'])
dump('emf_brakes.csv',brakes,['page','code','torque_nm','motor_frame','price'])
print("\nGAMAK IE classes:",sorted(set(m['ie_class'] for m in motors)))
print("sample motor:",motors[0] if motors else None)
print("sample brake:",brakes[0] if brakes else None)
print("EMF brake codes sample:",[b['code'] for b in brakes[:6]])
