# Prepare product textures: strip baked floor shadow/reflection, keep largest component,
# trim, and bake an optional warm back-rim (sun from upper-right behind). Straight-alpha PNG out.
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage as ndi
import os
ROOT=os.path.dirname(os.path.abspath(__file__))
# Sources (not committed): src/irnx_catalog_render.png = the 1181x1181 RGBA image embedded on page 6 of
# IRNX-Katalog-2024-Rev.00.pdf (extract with PyMuPDF); src/irk.png = the supplied IRK render (RGBA).

def largest_component(mask):
    lab,n=ndi.label(mask)
    if n<=1: return mask
    sizes=ndi.sum(mask,lab,range(1,n+1)); keep=1+int(np.argmax(sizes))
    return lab==keep

def finish(rgb,a,name):
    core=largest_component(a>=128)
    core=ndi.binary_fill_holes(core)
    grown=ndi.binary_dilation(core,iterations=1)
    a=np.where(grown,a,0).astype('uint8')
    o=Image.fromarray(np.dstack([rgb.astype('uint8'),a]),'RGBA'); bb=o.split()[3].getbbox(); o=o.crop(bb)
    o.save(f'{ROOT}/tex/{name}.png'); print(name,o.size)
    # rim-lit variant
    A=np.array(o).astype(np.float32); al=A[...,3]/255.0
    soft=ndi.gaussian_filter(al,2.0)
    def rim_dir(dx,dy,dist):
        sh=ndi.shift(soft,(dy*dist,-dx*dist),order=1,mode='constant',cval=0.0)  # sample toward (dx,-dy) in image
        return np.clip(al*(1.0-sh),0,1)
    rim=np.maximum(rim_dir(0.75,0.66,7), 0.7*rim_dir(0.2,0.98,6))          # upper-right + top
    rim=ndi.gaussian_filter(rim,1.6)
    rim=np.clip(rim*1.35,0,1)[...,None]
    warm=np.array([255,196,120],dtype=np.float32)
    rgbf=A[...,:3]
    out=255-(255-rgbf)*(1-rim*0.85*(warm/255.0))                             # screen blend
    o2=Image.fromarray(np.dstack([np.clip(out,0,255).astype('uint8'),A[...,3].astype('uint8')]),'RGBA')
    o2.save(f'{ROOT}/tex/{name}_rim.png')
    return o,o2

def clean_irnx():
    im=Image.open(ROOT+'/src/irnx_catalog_render.png').convert('RGBA')
    A=np.array(im).astype(np.int32); r,g,b,a=A[...,0],A[...,1],A[...,2],A[...,3]
    H,W=a.shape; ratio=g/np.maximum(r,1)
    prodlike=(a>=250)&((ratio<0.27)|(r>=170))
    ycut=np.full(W,-1)
    for x in range(W):
        col=np.where(prodlike[940:1040,x])[0]
        if len(col): ycut[x]=940+col.max()
    yc=ycut.astype(float); sm=yc.copy()
    for x in np.where(ycut>0)[0]:
        w=yc[max(0,x-7):x+8]; w=w[w>0]; sm[x]=np.median(w)
    below=np.zeros((H,W),bool)
    for x in range(W):
        if sm[x]>0: below[int(sm[x])+2:,x]=True
        else: below[940:,x]=True
    a2=np.where(below|(a<240)&~ndi.binary_dilation((a>=240)&~below,iterations=1),0,a)
    return finish(A[...,:3],a2,'irnx')

def clean_irk():
    im=Image.open(ROOT+'/src/irk.png').convert('RGBA')
    A=np.array(im).astype(np.int32); r,g,b,a=A[...,0],A[...,1],A[...,2],A[...,3]
    H,W=a.shape
    mx=np.maximum(np.maximum(r,g),b); sat=mx-np.minimum(np.minimum(r,g),b)
    ys=np.where((a>=235).any(axis=1))[0]; ybot=ys.max()
    zone=np.zeros((H,W),bool); zone[ybot-75:,:]=True
    shadow=zone&(mx<78)&(sat<26)                 # near-black, unsaturated floor shadow in the bottom band
    shadow=ndi.binary_opening(shadow,iterations=1)
    a2=np.where(shadow|(a<235)&~ndi.binary_dilation((a>=235)&~shadow,iterations=1),0,a)
    return finish(A[...,:3],a2,'irk')

a,a2=clean_irnx(); b,b2=clean_irk()
def prev(o,bg,th):
    c=Image.new('RGBA',(o.width+40,o.height+40),bg); c.alpha_composite(o,(20,20)); c=c.convert('RGB'); c.thumbnail(th); return c
tiles=[prev(a,(26,22,20,255),(430,560)),prev(a2,(26,22,20,255),(430,560)),prev(b,(26,22,20,255),(640,360)),prev(b2,(26,22,20,255),(640,360))]
sheet=Image.new('RGB',(430*2+640+40,580+0),(60,60,60))
sheet.paste(tiles[0],(5,5)); sheet.paste(tiles[1],(440,5)); sheet.paste(tiles[2],(880,5)); sheet.paste(tiles[3],(880,300))
sheet.save(ROOT+'/tex/_check.jpg',quality=92); print('sheet',sheet.size)
