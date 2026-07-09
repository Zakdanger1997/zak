import csv, sqlite3, os, shutil
DATA='/home/user/zak/pricing/data'; SCR='/home/user/zak/pricing/scripts'
os.makedirs(DATA,exist_ok=True); os.makedirs(SCR,exist_ok=True)
db=DATA+'/imak_pricing.db'
if os.path.exists(db): os.remove(db)
con=sqlite3.connect(db); cur=con.cursor()
def load(csvf,table):
    p=csvf if os.path.isabs(csvf) else csvf
    rows=list(csv.DictReader(open(p,encoding='utf-8')))
    if not rows: 
        print("  (empty) "+table); return 0
    cols=list(rows[0].keys())
    cur.execute("CREATE TABLE %s (%s)"%(table,", ".join('"%s" TEXT'%c for c in cols)))
    cur.executemany("INSERT INTO %s VALUES (%s)"%(table,", ".join("?" for _ in cols)),
                    [[r[c] for c in cols] for r in rows])
    print("  %-26s %d"%(table,len(rows))); return len(rows)
tables=[
 ('imak_geared_motors.csv','imak_geared_motors'),
 ('imak_iec_units.csv','imak_iec_units'),
 ('imak_simple_types.csv','imak_simple_types'),
 ('imak_mamk_options.csv','imak_mamk_options'),
 ('imak_planetary.csv','imak_planetary'),
 ('gamak_motors.csv','gamak_motors'),
 ('emf_brakes.csv','emf_brakes'),
 ('cema_customer_options.csv','cema_customer_options'),
 ('redservis_s_series.csv','redservis_s_series'),
 ('kaplin_couplings.csv','kaplin_couplings'),
]
tot=0
for f,t in tables: tot+=load(f,t)
con.commit(); con.close()
print("TOTAL rows:",tot,"-> DB:",db)
# copy csvs + scripts
for f,_ in tables: shutil.copy(f,DATA+'/'+f)
shutil.copy('imak_main_raw.json',DATA+'/imak_main_raw.json')
for s in ['gen_std.py','batch_rest.py','extract_ge.py','extract_emf.py','rebuild_all.py']:
    if os.path.exists(s): shutil.copy(s,SCR+'/'+s)
print("copied to repo")
