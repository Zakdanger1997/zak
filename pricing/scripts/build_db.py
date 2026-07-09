import csv, sqlite3, os
db='/home/user/zak/pricing/data/imak_pricing.db'
os.makedirs('/home/user/zak/pricing/data',exist_ok=True)
if os.path.exists(db): os.remove(db)
con=sqlite3.connect(db); cur=con.cursor()
def load(csvf,table):
    rows=list(csv.DictReader(open(csvf,encoding='utf-8')))
    if not rows: return 0
    cols=list(rows[0].keys())
    coldef=", ".join('"%s" TEXT'%c for c in cols)
    ph=", ".join("?" for _ in cols)
    cur.execute("CREATE TABLE %s (%s)"%(table,coldef))
    cur.executemany("INSERT INTO %s VALUES (%s)"%(table,ph),[[r[c] for c in cols] for r in rows])
    return len(rows)
for csvf,table in [
    ('imak_geared_motors.csv','imak_geared_motors'),
    ('imak_iec_units.csv','imak_iec_units'),
    ('imak_simple_types.csv','imak_simple_types'),
    ('imak_mamk_euro_options.csv','imak_mamk_euro_options'),
    ('gamak_motors.csv','gamak_motors'),
    ('emf_brakes.csv','emf_brakes'),
]:
    print("  %s: %d rows"%(table,load(csvf,table)))
con.commit(); con.close()
print("DB written:",db)
# copy CSVs + scripts into repo
import shutil
os.makedirs('/home/user/zak/pricing/data',exist_ok=True)
os.makedirs('/home/user/zak/pricing/scripts',exist_ok=True)
for f in ['imak_geared_motors.csv','imak_iec_units.csv','imak_simple_types.csv','imak_mamk_euro_options.csv','gamak_motors.csv','emf_brakes.csv','imak_main_raw.json']:
    shutil.copy(f,'/home/user/zak/pricing/data/'+f)
for f in ['extract_imak.py','normalize_imak.py','extract_ge.py','extract_emf.py','extract_mamk.py','build_db.py']:
    shutil.copy(f,'/home/user/zak/pricing/scripts/'+f)
print("copied CSVs+scripts into repo")
