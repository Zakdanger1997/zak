import fitz, re, csv
d=fitz.open('/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/9a38ef4d-AEMOT_09.07.2026_TAR_HL__F_YAT_L_STES_.pdf')
def isprice(l): return l.startswith('₺')
def pval(l):
    m=re.search(r'[\d.]+,\d{2}',l); return m.group(0).replace('.','').replace(',','.') if m else ''
def isnum(l): return bool(re.match(r'^[\d.,/\-]+$',l)) and '₺' not in l
def istype(l): return bool(re.search(r'[A-Za-z]',l)) and bool(re.search(r'\d',l))
motors=[]
for pno in range(d.page_count):
    L=[l.strip() for l in d[pno].get_text().splitlines() if l.strip()]
    cur_kw=cur_hp=''
    i=0
    while i<len(L):
        l=L[i]
        # kW/HP header: two numeric lines followed by a type
        if isnum(l) and i+2<len(L) and isnum(L[i+1]) and istype(L[i+2]):
            cur_kw=l.replace(',','.'); cur_hp=L[i+1]; i+=2; continue
        # type + price pair
        if istype(l) and i+1<len(L) and isprice(L[i+1]):
            motors.append(dict(page=pno+1,power_kw=cur_kw,power_hp=cur_hp,
                motor_type=l,price_tl=pval(L[i+1]))); i+=2; continue
        i+=1
with open('aemot_motors.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['page','power_kw','power_hp','motor_type','price_tl']); w.writeheader(); w.writerows(motors)
print("aemot_motors.csv:",len(motors))
from collections import Counter
print("prefixes:",dict(Counter(re.match(r'[A-Z]+',m['motor_type']).group(0) for m in motors if re.match(r'[A-Z]+',m['motor_type']))))
for m in motors[:5]: print(m)
print("...kW range:",sorted(set(m['power_kw'] for m in motors),key=lambda x:float(x) if x.replace('.','').isdigit() else 0)[:6])
