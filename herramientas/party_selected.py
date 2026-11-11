import sys
from PIL import Image, ImageDraw, ImageFilter

path = sys.argv[1]
im = Image.open(path).convert("RGBA")
S = 4


def tile(x0, fill_top, fill_bot, border, bw, glow, glow_a):
    W = H = 48 * S
    t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([S, S, W - S - 1, H - S - 1], radius=10 * S, fill=255)
    g = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(g)
    for j in range(H):
        k = j / (H - 1)
        gd.line([(0, j), (W, j)], fill=tuple(int(fill_top[i] + (fill_bot[i] - fill_top[i]) * k) for i in range(4)))
    t.paste(g, (0, 0), m)
    if glow:
        inner = Image.new("L", (W, H), 0)
        ImageDraw.Draw(inner).rounded_rectangle([S, S, W - S - 1, H - S - 1], radius=10 * S, outline=255, width=6 * S)
        inner = inner.filter(ImageFilter.GaussianBlur(3 * S))
        inner = Image.composite(inner, Image.new("L", (W, H), 0), m).point(lambda a: int(a * glow_a))
        gl = Image.new("RGBA", (W, H), glow)
        gl.putalpha(inner)
        t.alpha_composite(gl)
    ImageDraw.Draw(t).rounded_rectangle([S, S, W - S - 1, H - S - 1], radius=10 * S, outline=border, width=bw * S)
    t = t.resize((48, 48), Image.LANCZOS)
    im.paste(Image.new("RGBA", (48, 48), (0, 0, 0, 0)), (x0, 0))
    im.alpha_composite(t, (x0, 0))


tile(64, (120, 86, 165, 185), (96, 66, 138, 185), (190, 160, 230, 230), 1, (200, 170, 240, 255), 0.35)
tile(128, (160, 104, 210, 225), (110, 62, 160, 225), (255, 120, 220, 255), 2, (255, 110, 215, 255), 0.85)
im.save(path, optimize=True)
