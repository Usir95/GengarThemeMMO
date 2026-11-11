import sys
import math
from PIL import Image, ImageDraw, ImageFilter

base_src, dst = sys.argv[1], sys.argv[2]

base = Image.open(base_src).convert("RGBA")
im = Image.open(dst).convert("RGBA")
S = 4


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def light_rows(reg):
    w, h = reg.size
    px = reg.load()
    rows = []
    for j in range(h):
        n = sum(1 for i in range(w) if px[i, j][3] > 0 and max(px[i, j][:3]) > 150)
        rows.append(n > w * 0.3)
    last = max([j for j, v in enumerate(rows) if v] or [h // 2])
    first = min([j for j, v in enumerate(rows) if v] or [0])
    return first, last + 1


def face(d, cx, cy, s):
    d.polygon([(cx - s * 0.78, cy - s * 0.36), (cx - s * 0.14, cy - s * 0.06), (cx - s * 0.26, cy + s * 0.10), (cx - s * 0.66, cy - s * 0.06)], fill=hx("#FF2E5F"))
    d.polygon([(cx + s * 0.78, cy - s * 0.36), (cx + s * 0.14, cy - s * 0.06), (cx + s * 0.26, cy + s * 0.10), (cx + s * 0.66, cy - s * 0.06)], fill=hx("#FF2E5F"))
    d.ellipse([cx - s * 0.44, cy - s * 0.15, cx - s * 0.32, cy - s * 0.03], fill=hx("#FFF4F8"))
    d.ellipse([cx + s * 0.32, cy - s * 0.15, cx + s * 0.44, cy - s * 0.03], fill=hx("#FFF4F8"))
    d.chord([cx - s * 0.80, cy - s * 0.30, cx + s * 0.80, cy + s * 0.66], 12, 168, fill=hx("#FBF6FF"))
    d.chord([cx - s * 0.70, cy - s * 0.06, cx + s * 0.70, cy + s * 0.40], 12, 168, fill=hx("#1A0F2C"))
    for k in range(-4, 5):
        tx = cx + k * s * 0.145
        d.line([(tx, cy + s * 0.20), (tx, cy + s * 0.52)], fill=hx("#C9B8F0"), width=max(1, int(s * 0.04)))


def plate(box, badge=None):
    x, y, w, h = box
    reg = base.crop((x, y, x + w, y + h))
    alpha = reg.getchannel("A").point(lambda a: 255 if a > 0 else 0)
    l0, l1 = light_rows(reg)
    W, H = w * S, h * S
    Z = Image.new("L", (W, H), 0)
    mask = alpha.resize((W, H), Image.NEAREST)

    bb = alpha.getbbox()
    bot = bb[3]
    fz = max(4, int(round((bot - bb[1]) * 0.24)))
    cut = (bot - fz) * S
    band = Image.new("L", (W, H), 0)
    ImageDraw.Draw(band).rectangle([0, 0, W, cut - 1], fill=255)
    band = Image.composite(mask, Z, band)

    spikes = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(spikes)
    depth = fz * S
    xx = W - S * 3
    k = 0
    while xx > S * 6:
        f = 0.35 + 0.65 * (xx / W)
        wv = depth * (1.5 if k % 3 == 0 else 1.0)
        dv = depth * f * (1.0 if k % 2 == 0 else 0.55)
        sd.polygon([(xx - wv, cut - S), (xx, cut - S), (xx - wv * 0.35, cut + dv)], fill=255)
        xx -= wv + S * 1.2
        k += 1
    spikes = Image.composite(spikes, Z, mask)

    full = Image.composite(Image.new("L", (W, H), 255), Z, band)
    full = Image.composite(Image.new("L", (W, H), 255), full, spikes)

    body = Image.new("RGBA", (W, H))
    bd = ImageDraw.Draw(body)
    for i in range(W):
        t = i / (W - 1)
        bd.line([(i, 0), (i, H)], fill=lerp(hx("#3B2163", 240), hx("#160C26", 240), t ** 0.8))
    sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = ImageDraw.Draw(sheen)
    for j in range(l0 * S, l0 * S + int((l1 - l0) * S * 0.45)):
        tt = (j - l0 * S) / ((l1 - l0) * S * 0.45)
        sh.line([(0, j), (W, j)], fill=(235, 205, 255, int(46 * (1 - tt))))
    for k in range(3):
        ox = S * (14 + k * 7)
        sh.polygon([(ox, l0 * S), (ox + S * 3, l0 * S), (ox + S * 3 - (l1 - l0) * S, l1 * S), (ox - (l1 - l0) * S, l1 * S)], fill=(255, 150, 230, 40 - k * 10))
    body.alpha_composite(sheen)

    sp = Image.new("RGBA", (W, H))
    spd = ImageDraw.Draw(sp)
    for j in range(H):
        spd.line([(0, j), (W, j)], fill=lerp(hx("#B8358F", 240), hx("#4A1646", 220), (j - cut) / max(1, H - cut)))

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    edge = full.filter(ImageFilter.MaxFilter(5))
    out.paste(Image.new("RGBA", (W, H), hx("#0C0614", 230)), (0, 0), Image.composite(edge, Z, mask))
    out.paste(sp, (0, 0), spikes)
    out.paste(body, (0, 0), band)

    neon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(neon)
    for i in range(0, W, 2):
        t = i / W
        nd.line([(i, l0 * S), (i + 2, l0 * S)], fill=lerp(hx("#FF5FD2"), hx("#B79CF0"), t), width=int(S * 1.6))
        nd.line([(i, l1 * S + S), (i + 2, l1 * S + S)], fill=lerp(hx("#B79CF0", 110), hx("#FF5FD2", 170), t), width=S // 2 + 1)
        nd.line([(i, cut - S), (i + 2, cut - S)], fill=lerp(hx("#FF5FD2", 230), hx("#B79CF0", 200), t), width=S)
    glow = neon.filter(ImageFilter.GaussianBlur(S * 1.5))
    for a in (glow, neon):
        a.putalpha(Image.composite(a.getchannel("A"), Z, band))
        out.alpha_composite(a)

    if badge:
        side, r = badge
        R = r * S
        cy = (bb[1] + (bot - bb[1]) * 0.45) * S
        cx = W - R - S * 8 if side == "r" else R + S * 10
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        b = ImageDraw.Draw(bl)
        b.ellipse([cx - R * 1.6, cy - R * 1.4, cx + R * 1.6, cy + R * 1.4], fill=(220, 70, 170, 120))
        bl = bl.filter(ImageFilter.GaussianBlur(S * 3))
        b = ImageDraw.Draw(bl)
        b.ellipse([cx - R, cy - R, cx + R, cy + R], fill=hx("#1A0F2C"), outline=hx("#FF5FD2"), width=int(S * 1.5))
        face(b, cx, cy + R * 0.05, R * 0.78)
        bl.putalpha(Image.composite(bl.getchannel("A"), Z, mask))
        out.alpha_composite(bl)

    small = out.resize((w, h), Image.LANCZOS)
    small.putalpha(small.getchannel("A").point(lambda v: 0 if v < 18 else min(255, int(v * 1.08))))
    im.paste(Image.new("RGBA", (w, h), (0, 0, 0, 0)), (x, y))
    im.alpha_composite(small, (x, y))


plate((0, 43, 306, 20))
plate((326, 65, 239, 28))
plate((0, 71, 298, 33), badge=("r", 12))
plate((326, 107, 298, 20), badge=("l", 8))
plate((583, 63, 309, 30), badge=("r", 10))

im.save(dst, optimize=True)
