from PIL import Image, ImageDraw, ImageFilter
import numpy as np
def trim(im):
    a=im.split()[3]; bb=a.getbbox(); return im.crop(bb) if bb else im
def key_white(path,thresh=60,pad=30,feather=1.0):
    im=Image.open(path).convert('RGB'); W,H=im.size
    c=Image.new('RGB',(W+2*pad,H+2*pad),(255,255,255)); c.paste(im,(pad,pad))
    for s in [(0,0),(c.width-1,0),(0,c.height-1),(c.width-1,c.height-1),(c.width//2,0),(c.width//2,c.height-1)]:
        ImageDraw.floodfill(c,s,(255,0,255),thresh=thresh)
    arr=np.array(c); mask=(arr[:,:,0]==255)&(arr[:,:,1]==0)&(arr[:,:,2]==255)
    out=c.convert('RGBA'); A=Image.fromarray(np.where(mask,0,255).astype('uint8'),'L')
    if feather: A=A.filter(ImageFilter.GaussianBlur(feather))
    out.putalpha(A); return trim(out)
def use_alpha(path):
    return trim(Image.open(path).convert('RGBA'))
Image.fromarray  # noop
irk=use_alpha('work/irk_src.png');   irk.save('work/irk_cut.png');   print('irk',irk.size)
logo=use_alpha('work/logo.png');     logo.save('work/logo_cut.png'); print('logo',logo.size)
irnx=key_white('work/irnx_src.jpg',60); irnx.save('work/irnx_cut.png'); print('irnx',irnx.size)
def checker(sz,s=16):
    im=Image.new('RGB',sz,(235,235,235)); d=ImageDraw.Draw(im)
    for y in range(0,sz[1],s):
        for x in range(0,sz[0],s):
            if (x//s+y//s)%2: d.rectangle([x,y,x+s,y+s],fill=(203,203,203))
    return im
tiles=[]
for o in ['work/irk_cut.png','work/irnx_cut.png','work/logo_cut.png']:
    im=Image.open(o).convert('RGBA'); im.thumbnail((520,400))
    bg=checker(im.size).convert('RGBA'); bg.alpha_composite(im); tiles.append(bg.convert('RGB'))
tw=max(t.width for t in tiles); sheet=Image.new('RGB',(tw,sum(t.height for t in tiles)+16),(20,20,20)); y=0
for t in tiles: sheet.paste(t,(0,y)); y+=t.height+8
sheet.save('work/cut_check.png'); print('ok')
