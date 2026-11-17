from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np, os
RED=(154,24,16); REDB=(183,20,20); INK=(20,16,14); WHITE=(248,246,242)
FO='fonts/Oswald.ttf'; FI='fonts/Inter.ttf'
def font(path,size,wght):
    f=ImageFont.truetype(path,size)
    try:f.set_variation_by_axes([wght] if path==FO else [14,wght])
    except Exception: pass
    return f
def cover(im,W,H):
    s=max(W/im.width,H/im.height); im=im.resize((int(im.width*s+1),int(im.height*s+1)),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; return im.crop((x,y,x+W,y+H))
def shadow(layer,blur,off,op):
    a=layer.split()[3]
    sh=Image.new('RGBA',layer.size,(0,0,0,0)); sh.putalpha(a.point(lambda v:int(v*op)))
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); return sh,off
def paste_prod(canvas,prod,cx,by,h):
    scale=h/prod.height; p=prod.resize((int(prod.width*scale),h),Image.LANCZOS)
    x=int(cx-p.width/2); y=int(by-p.height)
    # ground shadow ellipse
    el=Image.new('RGBA',canvas.size,(0,0,0,0)); d=ImageDraw.Draw(el)
    ew=int(p.width*0.9); eh=int(p.height*0.14)
    d.ellipse([x+p.width//2-ew//2, by-eh//2, x+p.width//2+ew//2, by+eh//2],fill=(0,0,0,120))
    el=el.filter(ImageFilter.GaussianBlur(18)); canvas.alpha_composite(el)
    sh,off=shadow(p,16,(10,16),0.40); canvas.alpha_composite(sh,(x+off[0],y+off[1]))
    canvas.alpha_composite(p,(x,y)); return x,y,p
def grad_scrim(size, pts):
    # pts: list of (frac0..1 along given direction) -> alpha ; vertical from bottom
    W,H=size; g=Image.new('L',(1,H))
    for y in range(H):
        f=y/H; a=0
        for (f0,a0,f1,a1) in pts:
            if f0<=f<=f1:
                a=int(a0+(a1-a0)*((f-f0)/max(1e-6,f1-f0)))
        g.putpixel((0,y),a)
    g=g.resize((W,H)); sc=Image.new('RGBA',(W,H),(8,6,5,0)); sc.putalpha(g); return sc
def diag_scrim(size,maxa=200):
    W,H=size; arr=np.zeros((H,W),dtype=np.uint8)
    yy,xx=np.mgrid[0:H,0:W]
    # dark bottom-left -> clear top-right
    d=(1-(xx/W))*0.6+(yy/H)*0.7; d=np.clip(d,0,1)
    arr=(d*maxa).astype('uint8')
    sc=Image.new('RGBA',(W,H),(8,6,5,0)); sc.putalpha(Image.fromarray(arr,'L')); return sc
def warm(im,r=1.10,g=1.0,b=0.84,bri=1.02,con=1.06,sat=1.08):
    a=np.array(im).astype('float32'); a[:,:,0]*=r; a[:,:,1]*=g; a[:,:,2]*=b
    im=Image.fromarray(np.clip(a,0,255).astype('uint8'))
    im=ImageEnhance.Brightness(im).enhance(bri); im=ImageEnhance.Contrast(im).enhance(con)
    im=ImageEnhance.Color(im).enhance(sat); return im
def sunglow(im,cx,cy,rad,strength=120):
    W,H=im.size; ov=Image.new('L',(W,H),0); d=ImageDraw.Draw(ov)
    d.ellipse([cx-rad,cy-rad,cx+rad,cy+rad],fill=strength); ov=ov.filter(ImageFilter.GaussianBlur(rad*0.5))
    glow=Image.new('RGBA',(W,H),(255,196,120,0)); glow.putalpha(ov); im=im.convert('RGBA'); im.alpha_composite(glow); return im
def text(d,xy,s,fnt,fill,anchor='la',ls=0,shadow_=None):
    if shadow_:
        d.text((xy[0]+shadow_[0],xy[1]+shadow_[1]),s,font=fnt,fill=(0,0,0,170),anchor=anchor)
    d.text(xy,s,font=fnt,fill=fill,anchor=anchor)
def logo_chip(canvas,logo,x,y,h):
    s=h/logo.height; lg=logo.resize((int(logo.width*s),h),Image.LANCZOS)
    padx,pady=26,18
    chip=Image.new('RGBA',(lg.width+2*padx,lg.height+2*pady),(0,0,0,0))
    d=ImageDraw.Draw(chip); d.rounded_rectangle([0,0,chip.width-1,chip.height-1],radius=18,fill=(255,255,255,235))
    chip.alpha_composite(lg,(padx,pady))
    sh,off=shadow(chip,10,(0,6),0.30); canvas.alpha_composite(sh,(x+off[0],y+off[1])); canvas.alpha_composite(chip,(x,y))
    return chip.width,chip.height

W,H=1500,900
logo=Image.open('work/logo_cut.png').convert('RGBA')
irk=Image.open('work/irk_cut.png').convert('RGBA')
irnx=Image.open('work/irnx_cut.png').convert('RGBA')

def strip_width(d,items,fh):
    fb=font(FO,fh,700); fsep=font(FO,fh,400); w=0
    for i,it in enumerate(items):
        if i: w+=d.textlength('   ·   ',font=fsep)
        w+=d.textlength(it,font=fb)
    return w
def stat_bar(d,hx,ytop,items,fh=28,h=54):
    w=strip_width(d,items,fh)
    d.rounded_rectangle([hx-4,ytop,hx+28+w,ytop+h],radius=10,fill=(154,24,16,238))
    fb=font(FO,fh,700); fsep=font(FO,fh,400); cx=hx+18; y=ytop+h//2
    for i,it in enumerate(items):
        if i:
            text(d,(cx,y),'   ·   ',fsep,(255,210,120,255),anchor='lm'); cx+=d.textlength('   ·   ',font=fsep)
        text(d,(cx,y),it,fb,(255,255,255,255),anchor='lm'); cx+=d.textlength(it,font=fb)

# ---------------- IMG 1 : IRNX / silos-sunset ----------------
def img1():
    bg=cover(Image.open('bg/raw/silos1.jpg').convert('RGB'),W,H)
    bg=warm(bg); bg=sunglow(bg,int(W*0.72),int(H*0.20),420,110).convert('RGB')
    c=bg.convert('RGBA')
    c.alpha_composite(diag_scrim((W,H),205))
    # red accent bar along bottom
    d=ImageDraw.Draw(c)
    paste_prod(c,irnx,int(W*0.80),int(H*0.90),430)
    d=ImageDraw.Draw(c)
    lw,lh=logo_chip(c,logo,46,40,58)
    # headline block bottom-left
    hx=60
    text(d,(hx,H-346),'ENGINEERING THE FUTURE',font(FO,62,700),(255,255,255,255),shadow_=(2,3))
    text(d,(hx,H-282),'OF GLOBAL MILLING',font(FO,62,700),(255,210,120,255),shadow_=(2,3))
    text(d,(hx,H-198),'Robust power transmission for grain, flour & feed plants worldwide.',
         font(FI,26,500),(240,237,232,255),shadow_=(1,2))
    stat_bar(d,hx,H-150,['50+ YEARS','140+ COUNTRIES','1,000,000+ CONFIGURATIONS'],28)
    text(d,(hx,H-58),'www.imakreduktor.com',font(FI,24,700),(255,255,255,255),shadow_=(1,1))
    text(d,(W-14,H-16),'Background: rawpixel · CC0',font(FI,15,400),(230,225,218,210),anchor='rs')
    # product label
    text(d,(int(W*0.80),int(H*0.92)),'IRNX Series · Shaft-Mounted Gearbox',font(FI,20,600),(255,255,255,255),anchor='ma',shadow_=(1,1))
    c.convert('RGB').save('out_img1_irnx_silos.jpg',quality=92)
    print('img1 done')

# ---------------- IMG 2 : IRK / conveyor ----------------
def img2():
    bg=cover(Image.open('bg/raw/conv0.jpg').convert('RGB'),W,H)
    bg=warm(bg,r=1.03,g=1.0,b=0.95,bri=0.98,con=1.08,sat=1.02)
    c=bg.convert('RGBA'); c.alpha_composite(diag_scrim((W,H),210))
    d=ImageDraw.Draw(c)
    paste_prod(c,irk,int(W*0.66),int(H*0.86),470)
    d=ImageDraw.Draw(c)
    logo_chip(c,logo,46,40,58)
    hx=60
    text(d,(hx,H-356),'BUILT TO DRIVE',font(FO,64,700),(255,255,255,255),shadow_=(2,3))
    text(d,(hx,H-292),'THE MILLING LINE',font(FO,64,700),(255,210,120,255),shadow_=(2,3))
    text(d,(hx,H-206),'IRK helical-bevel geared motors for conveyors, elevators & mixers.',
         font(FI,26,500),(240,237,232,255),shadow_=(1,2))
    stat_bar(d,hx,H-158,['50+ YEARS','140+ COUNTRIES','HIGH-EFFICIENCY'],28)
    text(d,(hx,H-64),'www.imakreduktor.com',font(FI,24,700),(255,255,255,255),shadow_=(1,1))
    text(d,(W-14,H-16),'Background: rawpixel · CC0',font(FI,15,400),(235,230,224,210),anchor='rs')
    text(d,(int(W*0.66),int(H*0.88)),'IRK Series · Helical-Bevel Geared Motor',font(FI,20,600),(255,255,255,255),anchor='ma',shadow_=(1,1))
    c.convert('RGB').save('out_img2_irk_conveyor.jpg',quality=92)
    print('img2 done')
img1(); img2()
