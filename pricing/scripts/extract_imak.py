import fitz, json, re
f="/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/0cdcc621-.Mak_Redktr_Fiyat_Listesi__R02_26.01.2026.pdf"
d=fitz.open(f)
out=[]
for pno in range(d.page_count):
    pg=d[pno]
    txt=pg.get_text()
    lines=[l.strip() for l in txt.splitlines() if l.strip()]
    # section title = a line containing 'SERİSİ' or a header keyword
    sect=next((l for l in lines if 'SER' in l.upper() and ('İSİ' in l or 'ISI' in l.upper() or 'SERI' in l.upper())), "")
    tabs=pg.find_tables()
    for t in tabs.tables:
        rows=t.extract()
        rows=[[ (c or "").replace("\n"," ").strip() for c in r] for r in rows]
        rows=[r for r in rows if any(c for c in r)]
        if not rows: continue
        out.append({"page":pno+1,"section":sect,"nrows":len(rows),"ncols":len(rows[0]),"rows":rows})
json.dump(out, open("imak_main_raw.json","w"), ensure_ascii=False)
# summary: unique section titles + page ranges
from collections import defaultdict
secpages=defaultdict(list)
for o in out: secpages[o["section"]].append(o["page"])
print("=== sections found ===")
for s,ps in secpages.items():
    print(f"[{min(ps)}-{max(ps)}] {s!r}  ({len(ps)} tables)")
print("\ntotal tables:", len(out), "| total data rows:", sum(o['nrows'] for o in out))
