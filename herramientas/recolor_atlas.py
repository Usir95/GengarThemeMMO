import sys, colorsys
from PIL import Image
src,dst=sys.argv[1],sys.argv[2]
im=Image.open(src).convert("RGBA");px=im.load()
TH=270/360
for y in range(im.height):
    for x in range(im.width):
        r,g,b,a=px[x,y]
        if a==0: continue
        h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
        hd=h*360
        if s<0.12 and v<0.9:
            nh,ns,nv=TH,0.28,min(1,v*1.02)
        elif 180<=hd<=235 and s<0.45:
            nh,ns,nv=TH,min(1,s*1.25+0.10),v
        else:
            continue
        nr,ng,nb=colorsys.hsv_to_rgb(nh,ns,nv)
        px[x,y]=(round(nr*255),round(ng*255),round(nb*255),a)
im.save(dst,optimize=True)
