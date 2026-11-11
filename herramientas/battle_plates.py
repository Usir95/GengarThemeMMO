import sys
import math
import random
from PIL import Image, ImageDraw, ImageFilter

base_src, dst = sys.argv[1], sys.argv[2]
pattern_src = sys.argv[3] if len(sys.argv) > 3 else None

base = Image.open(base_src).convert("RGBA")
im = Image.open(dst).convert("RGBA")
pat = Image.open(pattern_src).convert("RGBA") if pattern_src else None


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


BODY_A = hx("#3A2160")
BODY_B = hx("#1E1233")
GOO_A = hx("#D0479A")
GOO_B = hx("#6B2E5E")
LILAC = hx("#9B78C6")
LINE = hx("#E04EC0")
OUT = hx("#120A1E")


def split_row(reg):
    w, h = reg.size
    px = reg.load()
    best = h
    for j in range(h):
        lights = sum(1 for i in range(w) if px[i, j][3] > 0 and max(px[i, j][:3]) > 150)
        if j > 2 and lights < w * 0.25:
            best = j
            break
    return best


def draw_face(d, cx, cy, s):
    e = s * 0.30
    d.polygon([(cx - s * 0.62, cy - s * 0.30), (cx - s * 0.12, cy - s * 0.06), (cx - s * 0.20, cy + s * 0.08), (cx - s * 0.55, cy - s * 0.05)], fill=hx("#FF3B6B"))
    d.polygon([(cx + s * 0.62, cy - s * 0.30), (cx + s * 0.12, cy - s * 0.06), (cx + s * 0.20, cy + s * 0.08), (cx + s * 0.55, cy - s * 0.05)], fill=hx("#FF3B6B"))
    d.ellipse([cx - s * 0.36, cy - s * 0.14, cx - s * 0.26, cy - s * 0.02], fill=hx("#FFE3F0"))
    d.ellipse([cx + s * 0.26, cy - s * 0.14, cx + s * 0.36, cy - s * 0.02], fill=hx("#FFE3F0"))
    d.chord([cx - s * 0.70, cy - s * 0.30, cx + s * 0.70, cy + s * 0.62], 15, 165, fill=hx("#F6F0FF"))
    d.chord([cx - s * 0.62, cy - s * 0.10, cx + s * 0.62, cy + s * 0.42], 15, 165, fill=hx("#1E1233"))
    for k in range(-3, 4):
        tx = cx + k * s * 0.16
        d.line([(tx, cy + s * 0.18), (tx, cy + s * 0.48)], fill=hx("#C9B8F0"), width=max(1, int(s * 0.04)))


def plate(box, face=None, seed=1):
    x, y, w, h = box
    reg = base.crop((x, y, x + w, y + h))
    alpha = reg.getchannel("A").point(lambda a: 255 if a > 0 else 0)
    rnd = random.Random(seed)
    S = 4
    W, H = w * S, h * S
    mask = alpha.resize((W, H), Image.NEAREST)
    bb = alpha.getbbox()
    top_px, bot_px = bb[1], bb[3]
    gh = max(4, int((bot_px - top_px) * 0.36))

    body = Image.new("RGBA", (W, H))
    bdr = ImageDraw.Draw(body)
    for i in range(W):
        bdr.line([(i, 0), (i, H)], fill=lerp(BODY_A, BODY_B, i / (W - 1)))
    if pat:
        tile = pat.resize((pat.width * S // 3, pat.height * S // 3), Image.BICUBIC)
        tile.putalpha(tile.getchannel("A").point(lambda a: int(a * 0.14)))
        for tx in range(0, W, tile.width):
            for ty in range(0, H, tile.height):
                body.alpha_composite(tile, (tx, ty))
    shine = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shine)
    for j in range(top_px * S, top_px * S + 6 * S):
        t = (j - top_px * S) / (6 * S)
        sd.line([(0, j), (W, j)], fill=(255, 225, 255, int(40 * (1 - t) ** 2)))
    body.alpha_composite(shine)

    goo_mask = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(goo_mask)
    base_y = (bot_px - gh) * S
    amp = gh * S * 0.45
    phase = rnd.random() * 6.28
    pts = [(0, H)]
    for i in range(0, W + 1, 2):
        t = i / W
        v = math.sin(t * 23 + phase) * 0.55 + math.sin(t * 8.1 + phase * 1.7) * 0.45
        pts.append((i, base_y + amp * 0.5 + v * amp * 0.5))
    pts.append((W, H))
    gd.polygon(pts, fill=255)
    for _ in range(max(3, w // 40)):
        cx = rnd.randint(int(W * 0.04), int(W * 0.96))
        r = rnd.uniform(1.0, 1.7) * S
        gd.ellipse([cx - r, base_y - r * 1.4, cx + r, base_y + r * 1.2], fill=255)
    goo_mask = Image.composite(goo_mask, Image.new("L", (W, H), 0), mask)

    gooimg = Image.new("RGBA", (W, H))
    gdr = ImageDraw.Draw(gooimg)
    for j in range(H):
        gdr.line([(0, j), (W, j)], fill=lerp(GOO_A, GOO_B, (j - base_y) / max(1, H - base_y)))
    for _ in range(max(4, w // 28)):
        cx = rnd.randint(0, W)
        cy = rnd.randint(int(base_y + S), H - S)
        r = rnd.uniform(0.7, 1.4) * S
        gdr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 190, 236, 190), width=max(1, S // 2))
    gooedge = goo_mask.filter(ImageFilter.MaxFilter(5))
    rim = Image.composite(Image.new("L", (W, H), 255), Image.new("L", (W, H), 0), Image.eval(goo_mask, lambda a: 255 - a))
    rim = Image.composite(gooedge, Image.new("L", (W, H), 0), rim)
    rim = Image.composite(rim, Image.new("L", (W, H), 0), mask)

    final = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    final.paste(Image.new("RGBA", (W, H), OUT), (0, 0), mask)
    inner = mask.filter(ImageFilter.MinFilter(5))
    final.paste(Image.new("RGBA", (W, H), LILAC), (0, 0), Image.composite(Image.new("L", (W, H), 255), Image.new("L", (W, H), 0), inner))
    inner2 = mask.filter(ImageFilter.MinFilter(9))
    final.paste(body, (0, 0), inner2)
    final.paste(Image.new("RGBA", (W, H), LINE), (0, 0), Image.composite(rim, Image.new("L", (W, H), 0), inner))
    final.paste(gooimg, (0, 0), Image.composite(goo_mask, Image.new("L", (W, H), 0), inner))
    acc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(acc)
    ld.line([(S * 6, top_px * S + int(S * 2.6)), (W * 0.45, top_px * S + int(S * 2.6))], fill=hx("#E04EC0", 170), width=S // 2 + 1)
    acc.putalpha(Image.composite(acc.getchannel("A"), Image.new("L", (W, H), 0), inner2))
    final.alpha_composite(acc)

    if face:
        side, size = face
        fs_ = size * S
        cx = W - fs_ * 0.9 - S * 6 if side == "r" else fs_ * 0.9 + S * 6
        cy = (top_px + (bot_px - top_px) * 0.42) * S
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gl = ImageDraw.Draw(glow)
        gl.ellipse([cx - fs_ * 1.0, cy - fs_ * 0.6, cx + fs_ * 1.0, cy + fs_ * 0.8], fill=(208, 71, 154, 110))
        glow = glow.filter(ImageFilter.GaussianBlur(S * 3))
        glow.putalpha(Image.composite(glow.getchannel("A"), Image.new("L", (W, H), 0), inner2))
        final.alpha_composite(glow)
        fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw_face(ImageDraw.Draw(fl), cx, cy, fs_)
        fl.putalpha(Image.composite(fl.getchannel("A"), Image.new("L", (W, H), 0), inner2))
        final.alpha_composite(fl)

    small = final.resize((w, h), Image.LANCZOS)
    small.putalpha(small.getchannel("A").point(lambda v: 0 if v < 20 else min(255, int(v * 1.1))))
    im.paste(Image.new("RGBA", (w, h), (0, 0, 0, 0)), (x, y))
    im.alpha_composite(small, (x, y))


plate((0, 43, 306, 20), seed=3)
plate((326, 65, 239, 28), seed=5)
plate((0, 71, 298, 33), face=("r", 22), seed=7)
plate((326, 107, 298, 20), face=("l", 14), seed=11)
plate((583, 63, 309, 30), face=("r", 18), seed=13)

im.save(dst, optimize=True)
