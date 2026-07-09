import fitz, re, csv, time
def dec(s): return ''.join(chr(ord(c)+29) if 33<=ord(c)<=90 else c for c in (s or ''))
def norm(s): return (s or '').replace('ø','İ').replace('\x81','Ü')
def num(s):
    s=(s or '').strip().replace('.','').replace(',','.')
    try: return float(s)
    except: return None
KEY={'n2':['devir','devr','aevr'],'i':['ratio','oatio','tahvil','qahvil'],
     'sf':['servis','pervis','fak','cak'],'m2':['mome','jome','moment'],
     'f':['rad','oad','yük','yÜk','ql/2','nl'],'p1':['power','mower','güç','dÜç','guc']}
def colmap(header):
    m={}
    for ci,cell in enumerate(header):
        blob=((cell or '')+' '+dec(cell)).lower()
        for k,kws in KEY.items():
            if k in m: continue
            if any(w in blob for w in kws): m[k]=ci
    return m
def extract(path, series, p0, p1):
    d=fitz.open(path); out=[]
    for pno in range(p0,min(p1,d.page_count)):
        for t in d[pno].find_tables().tables:
            rows=t.extract()
            if not rows or len(rows[0])<8: continue
            cm=colmap(rows[0])
            if not ('n2' in cm and 'm2' in cm and 'i' in cm): continue
            cur_kw=cur_type=''
            fcol=cm.get('f')
            for r in rows[1:]:
                c=[ (x or '').strip() for x in r]
                def g(k):
                    j=cm.get(k); return c[j] if (j is not None and j<len(c)) else ''
                if num(g('p1')) is not None: cur_kw=num(g('p1'))
                typ=norm(' '.join(c[(fcol+1):]) if fcol is not None else ' '.join(c[-3:]))
                tm=re.search(r'İR[A-Z0-9]*\s*\d+.*?/\s*[\dA-Za-z ]+', typ) or re.search(r'[A-Z]{1,3}\s*\d+.*?/\s*[\dA-Za-z ]+', typ)
                if tm: cur_type=re.sub(r'\s+',' ',tm.group(0)).strip()
                m2,i,n2,sf,f=num(g('m2')),num(g('i')),num(g('n2')),num(g('sf')),num(g('f'))
                if m2 is None or i is None: continue
                out.append(dict(series=series,page=pno+1,power_kw=cur_kw,n2_rpm=n2,
                    ratio_i=i,service_factor=sf,torque_nm=m2,radial_load_n=f,model=cur_type))
    return out
CAT=[('İR','IR_Katalog_2026_Rev.01.pdf',40,196),
     ('İRK','IRK-Katalog-web.pdf',46,141),
     ('YP','YP-Katalog-2026.pdf',42,138),
     ('İRS','IRS_IRSD_Katalog_2026_Rev.01.pdf',42,168)]
allrows=[]; t0=time.time()
for s,fn,p0,p1 in CAT:
    r=extract('/home/user/zak/pricing/catalogues/'+fn,s,p0,p1)
    allrows+=r; print("%s: %d rows (%.0fs)"%(s,len(r),time.time()-t0),flush=True)
with open('imak_ratings.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['series','page','power_kw','n2_rpm','ratio_i','service_factor','torque_nm','radial_load_n','model'])
    w.writeheader(); w.writerows(allrows)
from collections import Counter
print("TOTAL ratings:",len(allrows))
print("by series:",dict(Counter(x['series'] for x in allrows)))
print("with model:",sum(1 for x in allrows if x['model']))
print("DONE %.0fs"%(time.time()-t0))
