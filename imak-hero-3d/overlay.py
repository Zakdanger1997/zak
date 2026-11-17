# Typography / crops for the hero render. Usage: python overlay.py <hero.png> <outdir> <product: irnx|irk>
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
ROOT=os.path.dirname(os.path.abspath(__file__))
FO=ROOT+'/fonts/Oswald.ttf'; FI=ROOT+'/fonts/Inter.ttf'
hero_path, outdir, product = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
def font(p, size, w):
    f=ImageFont.truetype(p, int(size))
    try: f.set_variation_by_axes([w] if p==FO else [14, w])
    except Exception: pass
    return f
logo=Image.open(ROOT+'/assets/logo.png').convert('RGBA'); bb=logo.split()[3].getbbox(); logo=logo.crop(bb)
def logo_white(h):
    s=h/logo.height; lg=logo.resize((int(logo.width*s), int(h)), Image.LANCZOS)
    a=lg.split()[3]; w=Image.new('RGBA', lg.size, (255,252,246,0)); w.putalpha(a); return w
def shadowed(base, layer, blur, op):
    a=layer.split()[3].point(lambda v:int(v*op)); sh=Image.new('RGBA', layer.size, (0,0,0,0)); sh.putalpha(a)
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); base.alpha_composite(sh); base.alpha_composite(layer)
def vgrad(size, y0, y1, a0, a1):
    W,H=size; g=np.zeros((H,1),np.float32); ys=np.arange(H)
    t=np.clip((ys-y0)/max(1,(y1-y0)),0,1); g[:,0]=a0+(a1-a0)*t
    m=Image.fromarray((np.clip(g,0,1)*255).astype('uint8')).resize((W,H))
    o=Image.new('RGBA',(W,H),(6,4,3,0)); o.putalpha(m); return o
COPY={'irnx':('IRNX SERIES  ·  SHAFT-MOUNTED GEARBOXES','For bucket elevators, conveyors & mills'),
      'irk': ('IRK SERIES  ·  HELICAL-BEVEL GEARED MOTORS','For conveyors, mixers & elevators')}[product]
GOLD=(255,200,112,255); WHITE=(255,252,246,255)

def ad(img, layout='top'):
    W,H=img.size; u=W/1920.0 if W/H>1.5 else (W/1300.0 if W/H>0.9 else W/1120.0)
    c=img.convert('RGBA')
    c.alpha_composite(vgrad((W,H), 0, int(H*0.30), 0.46, 0.0))             # darken the top for the title
    c.alpha_composite(vgrad((W,H), int(H*0.80), H, 0.0, 0.62))             # and the bottom for the tagline
    t=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(t)
    lg=logo_white(54*u); t.alpha_composite(lg,(int(64*u), int(50*u)))
    d.text((int(66*u), int(50*u+lg.height+10*u)), 'GEARBOXES AND DRIVES', font=font(FI,17.5*u,600), fill=(255,252,246,235))
    cx=W//2; a_='THE POWER BEHIND '; b_='GLOBAL MILLING'
    if W/H > 1.5:                                                           # wide: one line across the sky
        size=80*u; f1=font(FO, size, 700)
        while d.textlength(a_+b_,font=f1) > W*0.58: size*=0.97; f1=font(FO, size, 700)
        wa=d.textlength(a_,font=f1); wb=d.textlength(b_,font=f1); y=int(H*0.070)
        x0=cx-(wa+wb)/2; d.text((x0,y), a_, font=f1, fill=WHITE); d.text((x0+wa,y), b_, font=f1, fill=GOLD)
    else:                                                                   # square / portrait: two lines
        size=84*u; f1=font(FO, size, 700)
        while d.textlength(a_.strip(),font=f1) > W*0.80: size*=0.97; f1=font(FO, size, 700)
        wa=d.textlength(a_.strip(),font=f1); wb=d.textlength(b_,font=f1); y=int(H*0.082)
        d.text((cx-wa/2, y), a_.strip(), font=f1, fill=WHITE); d.text((cx-wb/2, y+int(size*1.13)), b_, font=f1, fill=GOLD)
    f2=font(FO, 30*u, 600); f3=font(FI, 23*u, 500)
    w2=d.textlength(COPY[0],font=f2); d.text((cx-w2/2, int(H-112*u)), COPY[0], font=f2, fill=WHITE)
    line=COPY[1]+'   ·   Powering 140+ countries   ·   1,000,000+ configurations'
    w3=d.textlength(line,font=f3)
    if w3 > W*0.92: line=COPY[1]+'  ·  Powering 140+ countries'; w3=d.textlength(line,font=f3)
    if w3 > W*0.92: line=COPY[1]; w3=d.textlength(line,font=f3)
    d.text((cx-w3/2, int(H-68*u)), line, font=f3, fill=(255,252,246,235))
    f4=font(FI, 21*u, 700); w4=d.textlength('www.imakreduktor.com',font=f4)
    d.text((W-int(64*u)-w4, int(58*u)), 'www.imakreduktor.com', font=f4, fill=WHITE)
    shadowed(c, t, 5*u, 0.75)
    return c.convert('RGB')

hero=Image.open(hero_path).convert('RGB'); W,H=hero.size
def save(im, name, maxw=None, q=93):
    if maxw and im.width>maxw: im=im.resize((maxw, int(im.height*maxw/im.width)), Image.LANCZOS)
    im.save(os.path.join(outdir,name), quality=q, subsampling=0); print(name, im.size)
if W/H > 1.5:
    save(hero, f'{product}_hero_clean_16x9.jpg', 1920)
    save(ad(hero), f'{product}_ad_16x9.jpg', 1920)
    sq=hero.crop(((W-H)//2, 0, (W-H)//2+H, H)); save(sq, f'{product}_hero_clean_1x1.jpg', 1440)
    save(ad(sq), f'{product}_ad_1x1_linkedin.jpg', 1200)
else:
    save(hero, f'{product}_hero_clean_4x5.jpg', 1440)
    save(ad(hero), f'{product}_ad_4x5_linkedin_feed.jpg', 1080)
