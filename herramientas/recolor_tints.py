import re,sys,colorsys
def mapc(rgb):
    r,g,b=[int(rgb[i:i+2],16)/255 for i in (0,2,4)]
    h,s,v=colorsys.rgb_to_hsv(r,g,b);hd=h*360
    if 200<=hd<=245 and s<0.6:
        nh,ns,nv=275/360,min(1,s*1.15+0.08),v
    elif 35<=hd<=55 and s>0.4:
        nh,ns,nv=292/360,0.55,min(1,v*1.0)
    else:
        return rgb
    r,g,b=colorsys.hsv_to_rgb(nh,ns,nv)
    return "%02X%02X%02X"%(round(r*255),round(g*255),round(b*255))
def sub(m):
    s=m.group(1)
    if len(s)==8: return "#"+s[:2]+mapc(s[2:])
    return "#"+mapc(s)
for f in sys.argv[1:]:
    t=open(f,encoding="utf8").read()
    n=re.sub(r'#([0-9A-Fa-f]{8}|[0-9A-Fa-f]{6})\b',sub,t)
    open(f,"w",encoding="utf8").write(n)
