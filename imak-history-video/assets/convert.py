import json, os
base='/home/user/zak/imak-history-video/assets'
topo=json.load(open(os.path.join(base,'world-110m.json')))
sx,sy=topo['transform']['scale']; tx,ty=topo['transform']['translate']
def dec(arc):
    x=y=0; out=[]
    for dx,dy in arc:
        x+=dx; y+=dy
        out.append([round((x*sx+tx)*10)/10, round((y*sy+ty)*10)/10])
    return out
decoded=[dec(a) for a in topo['arcs']]
def ring(ids):
    c=[]
    for idx in ids:
        a=decoded[idx] if idx>=0 else decoded[-1-idx][::-1]
        c.extend(a[1:] if c else a)
    return c
geoms=topo['objects']['countries']['geometries']
land=[]; turkey=[]
tnames=[]
for g in geoms:
    nm=(g.get('properties') or {}).get('name','')
    gid=str(g.get('id',''))
    isT = (nm.lower() in ('turkey','türkiye','turkiye')) or gid=='792'
    if isT: tnames.append((nm,gid))
    t=g['geometry']['type'] if 'geometry' in g else g['type']
    arcs = g.get('arcs') if 'arcs' in g else g['geometry']['arcs']
    polys = [arcs] if t=='Polygon' else arcs
    for poly in polys:
        for rr in poly:
            coords=ring(rr)
            # drop consecutive dups
            out=[]; last=None
            for p in coords:
                if last is None or last!=p: out.append(p)
                last=p
            if len(out)>2:
                (turkey if isT else land).append(out)
json.dump({'land':land,'turkey':turkey}, open(os.path.join(base,'world.json'),'w'))
print('land rings',len(land),'turkey rings',len(turkey),'turkey match',tnames)
print('bytes', os.path.getsize(os.path.join(base,'world.json')))
