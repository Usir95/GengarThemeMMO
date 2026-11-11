import sys
from PIL import Image, ImageDraw, ImageFont

font_path, dst = sys.argv[1], sys.argv[2]
S = 8
W, H = 104, 196
cells = {"1": (1, 1), "2": (53, 1), "3": (1, 50), "4": (53, 50), "5": (1, 99), "!": (53, 99), "+": (1, 148)}
fills = {"1": ("#EC939F", 0.2), "2": ("#E6C082", 0.4), "3": ("#E6C082", 0.6), "4": ("#83D2AD", 0.8), "5": ("#83D2AD", 1.0), "!": ("#EC939F", 0.08), "+": ("#A9B8FF", 1.0)}


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


big = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
font = ImageFont.truetype(font_path, 13 * S)
for label, (cx, cy) in cells.items():
    x0, y0, x1, y1 = (cx + 1) * S, (cy + 8) * S, (cx + 46) * S, (cy + 38) * S
    card = Image.new("RGBA", (x1 - x0, y1 - y0))
    cd = ImageDraw.Draw(card)
    top, bot = hx("#3D2463", 240), hx("#1A1128", 240)
    for i in range(card.height):
        t = i / (card.height - 1)
        cd.line([(0, i), (card.width, i)], fill=tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(4)))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius=7 * S, fill=255)
    big.paste(card, (x0, y0), m)
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=7 * S, outline=hx("#9B78C6"), width=S)
    d.line([(x0 + 8 * S, y0 + S), (x1 - 8 * S, y0 + S)], fill=hx("#E04EC0"), width=S)
    tx = (x0 + x1) // 2
    d.text((tx + S // 2, y0 + 11 * S + S // 2), label, font=font, fill=(0, 0, 0, 140), anchor="mm")
    d.text((tx, y0 + 11 * S), label, font=font, fill=hx("#F3ECFF"), anchor="mm")
    bx0, bx1, by0, by1 = x0 + 6 * S, x1 - 6 * S, y0 + 21 * S, y0 + 25 * S
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=2 * S, fill=hx("#120C1E"), outline=hx("#5D4585"), width=S // 2)
    col, frac = fills[label]
    fx1 = bx0 + max(4 * S, int((bx1 - bx0) * frac))
    d.rounded_rectangle([bx0 + S // 2, by0 + S // 2, fx1 - S // 2, by1 - S // 2], radius=2 * S, fill=hx(col))
img = big.resize((W, H), Image.LANCZOS)
img.save(dst, optimize=True)
