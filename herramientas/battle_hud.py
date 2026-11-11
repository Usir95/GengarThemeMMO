import sys
from PIL import Image, ImageDraw, ImageFilter

src, pattern, dst = sys.argv[1], sys.argv[2], sys.argv[3]
face_src = sys.argv[4] if len(sys.argv) > 4 else None
S = 4
import numpy as np
from PIL import ImageEnhance
im = Image.open(src).convert("RGBA")
face_img = None
if face_src:
    fs = Image.open(face_src).convert("RGBA")
    fw_, fh_ = fs.size
    face_img = fs.crop((int(fw_ * 0.70), int(fh_ * 0.27), int(fw_ * 0.955), int(fh_ * 0.585)))
pat = Image.open(pattern).convert("RGBA")


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def clear(box):
    x, y, w, h = box
    im.paste(Image.new("RGBA", (w, h), (0, 0, 0, 0)), (x, y))


def rounded(box, top, bottom, border, radius, accent=None, glow=None, square=False, icon=None, face=None):
    x, y, w, h = box
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    g = Image.new("RGBA", (w * S, h * S))
    gd = ImageDraw.Draw(g)
    for i in range(h * S):
        gd.line([(0, i), (w * S, i)], fill=lerp(top, bottom, i / max(1, h * S - 1)))
    m = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(m).rounded_rectangle([S, S, w * S - S - 1, h * S - S - 1], radius=radius * S, fill=255)
    big.paste(g, (0, 0), m)
    d = ImageDraw.Draw(big)
    if glow:
        gl = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle([S, S, w * S - S - 1, h * S - S - 1], radius=radius * S, outline=glow, width=3 * S)
        big.alpha_composite(gl.filter(ImageFilter.GaussianBlur(2 * S)))
    hl = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle([2 * S, 2 * S, w * S - 2 * S - 1, (h * S) // 2], radius=radius * S, fill=(255, 255, 255, 22))
    big.alpha_composite(hl)
    if accent:
        d.rounded_rectangle([3 * S, 5 * S, 6 * S, h * S - 5 * S], radius=S, fill=accent)
    if square:
        d.rounded_rectangle([9 * S, 9 * S, (h - 9) * S + 4 * S, (h - 9) * S], radius=3 * S, fill=(18, 12, 30, 35), outline=(border[0], border[1], border[2], 60), width=S)
    d.rounded_rectangle([S, S, w * S - S - 1, h * S - S - 1], radius=radius * S, outline=border, width=S)
    small = big.resize((w, h), Image.LANCZOS)
    if face is not None and face_img is not None:
        strength, = face
        fh = h - 4
        fw = int(face_img.width * fh / face_img.height)
        f = face_img.resize((fw, fh), Image.LANCZOS)
        if strength < 0.5:
            f = ImageEnhance.Brightness(f).enhance(0.55)
        fade = Image.new("L", (fw, fh), 0)
        fd = ImageDraw.Draw(fade)
        for i in range(fw):
            fd.line([(i, 0), (i, fh)], fill=int(255 * strength * min(1, i / (fw * 0.45))))
        f.putalpha(Image.fromarray(np.minimum(np.array(f.getchannel("A")), np.array(fade)).astype(np.uint8)))
        clip = small.getchannel("A")
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        layer.alpha_composite(f, (w - fw - 3, 2))
        layer.putalpha(Image.fromarray(np.minimum(np.array(layer.getchannel("A")), np.array(clip)).astype(np.uint8)))
        small.alpha_composite(layer)
        bd = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        ImageDraw.Draw(bd).rounded_rectangle([S, S, w * S - S - 1, h * S - S - 1], radius=radius * S, outline=border, width=S)
        small.alpha_composite(bd.resize((w, h), Image.LANCZOS))
    if icon is not None:
        small.alpha_composite(icon)
    clear(box)
    im.alpha_composite(small, (x, y))


def plate(box, light1, light2, dark, line):
    x, y, w, h = box
    reg = im.crop((x, y, x + w, y + h))
    px = reg.load()
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    po = out.load()
    for j in range(h):
        for i in range(w):
            r, g, b, a = px[i, j]
            if a == 0:
                continue
            v = max(r, g, b) / 255
            if v > 0.6:
                c = lerp(light1, light2, i / max(1, w - 1))
            else:
                c = dark
            po[i, j] = (c[0], c[1], c[2], a)
    for i in range(w):
        for j in range(h):
            if px[i, j][3] > 0 and max(px[i, j][:3]) > 150:
                po[i, j] = (line[0], line[1], line[2], px[i, j][3])
                break
    clear(box)
    im.alpha_composite(out, (x, y))


def keep_icon(box, offset_x):
    x, y, w, h = box
    return im.crop((x, y, x + w, y + h)).crop((offset_x, 0, offset_x + 24, h))


L1, L2, DK, LN = hx("#D9C6FA"), hx("#9B78C6"), hx("#24163A"), hx("#E04EC0")
for b in [(0, 43, 306, 20), (0, 71, 298, 33), (326, 65, 239, 28), (326, 107, 298, 20), (583, 63, 309, 30)]:
    plate(b, L1, L2, DK, LN)

base = dict(top=hx("#5E3D90", 235), bottom=hx("#3A2460", 235), border=hx("#9B78C6"), radius=6, accent=hx("#E04EC0"))
hover = dict(top=hx("#7D52B8", 245), bottom=hx("#55367F", 245), border=hx("#F0B8FF"), radius=6, accent=hx("#FF6FD8"), glow=hx("#E04EC0", 180))
dis = dict(top=hx("#3C3546", 200), bottom=hx("#2B2633", 200), border=hx("#5A5266"), radius=6, accent=hx("#5A5266"))
dish = dict(dis, border=hx("#E04EC0"))
rounded((2, 145, 209, 52), square=True, face=(0.35,), **base)
rounded((2, 200, 209, 52), square=True, face=(1.0,), **hover)
rounded((640, 140, 209, 52), face=(0.35,), **base)
rounded((640, 196, 209, 52), face=(1.0,), **hover)
rounded((640, 252, 209, 52), **dis)
rounded((2, 257, 209, 52), square=True, **dis)
rounded((218, 257, 209, 52), square=True, **dish)

small_sets = [(218, None), (321, None), (424, None)]
icons = {}
for col, _ in small_sets:
    for row in (145, 176, 207):
        icons[(col, row)] = im.crop((col + 2, row, col + 22, row + 30)).copy() if col != 321 else None
for col, _ in small_sets:
    for row, st in ((145, base), (176, hover), (207, dis)):
        st2 = dict(st, radius=5, accent=None)
        ic = icons[(col, row)]
        icon_layer = None
        if ic is not None:
            icon_layer = Image.new("RGBA", (96, 30), (0, 0, 0, 0))
            icon_layer.alpha_composite(ic, (2, 0))
        rounded((col, row, 96, 30), icon=icon_layer, face=(1.0,) if row == 176 else None, **st2)

x, y, w, h = 6, 312, 800, 115
panel = Image.new("RGBA", (w, h))
pd = ImageDraw.Draw(panel)
for j in range(h):
    pd.line([(0, j), (w, j)], fill=lerp(hx("#2A1846", 225), hx("#140C22", 235), j / (h - 1)))
tile = pat.copy()
tile.putalpha(tile.getchannel("A").point(lambda a: int(a * 0.10)))
for tx in range(0, w, tile.width):
    for ty in range(0, h, tile.height):
        panel.alpha_composite(tile, (tx, ty))
pd = ImageDraw.Draw(panel)
pd.rectangle([0, 0, w - 1, 1], fill=LN)
pd.rectangle([0, 0, w - 1, h - 1], outline=hx("#9B78C6"))
clear((x, y, w, h))
im.alpha_composite(panel, (x, y))

x, y = 7, 445
frame = Image.new("RGBA", (800, 35))
fd = ImageDraw.Draw(frame)
for j in range(30):
    fd.line([(0, j), (800, j)], fill=lerp(hx("#3D2463", 235), hx("#24163A", 235), j / 29))
fd.rectangle([0, 28, 799, 29], fill=LN)
fd.rectangle([0, 30, 799, 34], fill=hx("#1A1128", 235))
fd.rectangle([0, 0, 799, 34], outline=hx("#9B78C6"))
clear((x, y, 800, 35))
im.alpha_composite(frame, (x, y))

im.save(dst, optimize=True)

import colorsys
im = Image.open(dst).convert("RGBA")
px = im.load()
for y in range(0, 30):
    for x in range(660, 900):
        r, g, b, a = px[x, y]
        if a == 0:
            continue
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 5 <= h * 360 <= 50 and s > 0.3:
            nr, ng, nb = colorsys.hsv_to_rgb((300 - (h * 360 - 5)) / 360, s, v)
            px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
im.save(dst, optimize=True)
