import fitz, csv, re
d=fitz.open('/root/.claude/uploads/d48fd1be-ce58-52ac-8944-9c90f45b7b5c/1c7d70af-I.MAK_GEARBOX__MA__MK_SERIES_EURO_PRICE_LIST_26.01.2026.pdf')
rows_out=[]
for pno in range(d.page_count):
    for ti,t in enumerate(d[pno].find_tables().tables):
        rows=[[ (c or '').replace('\n',' ').strip() for c in r] for r in t.extract()]
        rows=[r for r in rows if any(r)]
        if not rows: continue
        title=rows[0][0][:50]
        for r in rows:
            cells=[c for c in r if c]
            if len(cells)<2: continue
            rows_out.append(dict(page=pno+1,table=title,cells=' | '.join(cells)))
with open('imak_mamk_euro_options.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['page','table','cells']); w.writeheader(); w.writerows(rows_out)
print("imak_mamk_euro_options.csv:",len(rows_out),"rows")
