import sys
from PIL import Image, ImageDraw, ImageFilter

S = 4
W, H = 256, 128
out = sys.argv[1] if len(sys.argv) > 1 else "gengar-menus.png"
img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))


def grad(w, h, top, bot):
    g = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4)))
    return g


def rmask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return m


def piece(x, y, w, h, r, top, bot, border, bw=1, line=None, lw=2, glow=None, bar=None):
    x, y, w, h, r, bw, lw = x * S, y * S, w * S, h * S, r * S, bw * S, lw * S
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if glow:
        gm = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(gm).rounded_rectangle([S, S, w - 1 - S, h - 1 - S], r, outline=glow, width=3 * S)
        tile.alpha_composite(gm.filter(ImageFilter.GaussianBlur(1.5 * S)))
    body = grad(w, h, top, bot)
    if line:
        ImageDraw.Draw(body).rectangle([0, h - bw - lw, w, h - bw - 1], fill=line)
    if bar:
        ImageDraw.Draw(body).rectangle([bw, 0, bw + bar[1] * S - 1, h], fill=bar[0])
    m = rmask(w, h, r)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(body, (0, 0), m)
    ImageDraw.Draw(layer).rounded_rectangle([0, 0, w - 1, h - 1], r, outline=border, width=bw)
    tile.alpha_composite(layer)
    img.alpha_composite(tile, (x, y))


MAG = (226, 92, 190, 255)
LIL = (155, 120, 198, 255)

piece(0, 0, 48, 28, 4, (74, 44, 118, 255), (44, 26, 72, 255), (118, 86, 166, 255), line=(185, 56, 164, 255))
piece(48, 0, 48, 28, 4, (96, 62, 148, 255), (58, 34, 92, 255), (170, 136, 214, 255), line=(214, 80, 186, 255))
piece(96, 0, 48, 28, 4, (120, 70, 170, 255), (72, 38, 108, 255), MAG, line=(255, 130, 220, 255))

piece(144, 0, 16, 16, 3, (34, 22, 50, 235), (26, 17, 40, 235), (78, 58, 108, 255))
piece(160, 0, 16, 16, 3, (48, 32, 72, 240), (34, 22, 52, 240), (150, 116, 196, 255))
piece(176, 0, 16, 16, 3, (66, 38, 96, 245), (44, 26, 66, 245), MAG)
piece(192, 0, 16, 16, 3, (30, 26, 36, 200), (24, 20, 30, 200), (58, 52, 66, 255))

piece(0, 32, 64, 28, 4, (40, 26, 60, 200), (30, 19, 46, 200), (70, 52, 98, 255), bar=((92, 68, 130, 255), 3))
piece(64, 32, 64, 28, 4, (62, 40, 94, 230), (42, 26, 66, 230), (140, 106, 186, 255), bar=((160, 126, 208, 255), 3))
piece(128, 32, 64, 28, 4, (112, 64, 160, 255), (66, 34, 100, 255), MAG, bar=((255, 130, 220, 255), 4), glow=(255, 110, 215, 150))

piece(192, 32, 48, 48, 8, (52, 32, 82, 245), (24, 16, 38, 245), (128, 96, 176, 255))
d = ImageDraw.Draw(img)
d.rectangle([(192 + 8) * S, (32 + 1) * S, (192 + 40) * S, (32 + 2) * S], fill=MAG)

piece(0, 64, 48, 48, 6, (40, 24, 62, 215), (22, 14, 36, 215), (118, 86, 166, 255))
d.rectangle([(0 + 6) * S, (64 + 1) * S, (0 + 42) * S, (64 + 2) * S], fill=(185, 56, 164, 255))

img.resize((W, H), Image.LANCZOS).save(out)
