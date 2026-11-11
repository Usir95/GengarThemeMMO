import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

base_path, mist_path, dst = sys.argv[1], sys.argv[2], sys.argv[3]
S = 4
X0, Y0, W, H = 5, 193, 509, 318


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def vgrad(w, h, c1, c2):
    g = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(4)))
    return g



import colorsys


def recolor_px(img, box, fn):
    px = img.load()
    x0, y0, w, h = box
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            px[x, y] = fn(r, g, b, a)


def lum_tint(col):
    def f(r, g, b, a):
        l = (0.3 * r + 0.59 * g + 0.11 * b) / 255
        k = min(1.0, 0.55 + l * 1.6)
        return (int(col[0] * k), int(col[1] * k), int(col[2] * k), a)
    return f


def purple_general(r, g, b, a):
    h, s_, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if s_ < 0.18 or 180 <= h * 360 <= 235 or 80 <= h * 360 <= 160:
        nr, ng, nb = colorsys.hsv_to_rgb(272 / 360, 0.30 + 0.25 * (1 - v), v)
        return (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return (r, g, b, a)


def shape_fill(img, box, top, bot, edge):
    x0, y0, w, h = box
    reg = img.crop((x0, y0, x0 + w, y0 + h))
    alpha = reg.getchannel("A")
    g = vgrad(w, h, top, bot)
    g.putalpha(alpha)
    er = alpha.filter(ImageFilter.MinFilter(3))
    edge_mask = Image.eval(Image.merge("L", [alpha]).point(lambda v: v), lambda v: v)
    edge_layer = Image.new("RGBA", (w, h), edge)
    out = g.copy()
    rim = Image.fromarray((np.array(alpha, np.int16) - np.array(er, np.int16)).clip(0, 255).astype(np.uint8))
    out.paste(edge_layer, (0, 0), rim)
    hl = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    ImageDraw.Draw(hl).rectangle([0, 0, w, h // 2], fill=(255, 255, 255, 22))
    hl.putalpha(Image.fromarray(np.minimum(np.array(hl.getchannel("A")), np.array(er)).astype(np.uint8)))
    out.alpha_composite(hl)
    img.paste(Image.new("RGBA", (w, h), (0, 0, 0, 0)), (x0, y0))
    img.alpha_composite(out, (x0, y0))


def pill(img, box, fill, border, radius=5, glow=None):
    x0, y0, w, h = box
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([S, S, w * S - S - 1, h * S - S - 1], radius=radius * S, fill=fill, outline=border, width=S + S // 2)
    if glow:
        d.line([(radius * S, 2 * S), (w * S - radius * S, 2 * S)], fill=glow, width=S)
    img.paste(Image.new("RGBA", (w, h), (0, 0, 0, 0)), (x0, y0))
    img.alpha_composite(big.resize((w, h), Image.LANCZOS), (x0, y0))


def style_header_icons(img):
    for x in (5, 31, 56, 85, 112, 138, 158, 243, 263):
        recolor_px(img, (x, 6, 20, 20), lambda r, g, b, a: (255, 225, 249, a))
        recolor_px(img, (x, 32, 20, 20), lambda r, g, b, a: (216, 193, 246, a))

    for y, fill, outline in (
        (6, "#49245F", "#A47AC6"),
        (26, "#743675", "#F4A9E6"),
        (46, "#321842", "#E04EC0"),
    ):
        tile = Image.new("RGBA", (18 * S, 18 * S))
        draw = ImageDraw.Draw(tile)
        draw.rounded_rectangle((0, 0, 18 * S - 1, 18 * S - 1), radius=4 * S,
                               fill=hx(fill), outline=hx(outline), width=S)
        draw.line((5 * S, 5 * S, 12 * S, 12 * S), fill=hx("#FFF1FC"), width=2 * S)
        draw.line((12 * S, 5 * S, 5 * S, 12 * S), fill=hx("#FFF1FC"), width=2 * S)
        img.paste(tile.resize((18, 18), Image.LANCZOS), (290, y))


def style_small(img):
    recolor_px(img, (0, 0, img.width, 190), purple_general)
    style_header_icons(img)
    recolor_px(img, (5, 58, 18, 24), lum_tint((201, 168, 245)))
    pill(img, (25, 58, 125, 25), hx("#1E1230", 225), hx("#9B78C6"), 5)
    pill(img, (7, 101, 165, 17), hx("#2A1846", 225), hx("#9B78C6"), 4)
    star = img.crop((222, 24, 236, 38)).copy()
    pill(img, (181, 21, 57, 47), hx("#1E1230", 225), hx("#9B78C6"), 6)
    img.alpha_composite(star, (222, 24))
    pill(img, (386, 57, 125, 25), hx("#2A1A16", 230), hx("#E6C082"), 5, glow=hx("#E6C082", 120))
    pill(img, (386, 82, 125, 25), hx("#2A141C", 230), hx("#EC939F"), 5, glow=hx("#EC939F", 110))
    shape_fill(img, (22, 118, 164, 42), hx("#4A2E78", 235), hx("#2A1846", 235), hx("#9B78C6"))
    shape_fill(img, (203, 117, 165, 42), hx("#4A2E78", 235), hx("#2A1846", 235), hx("#9B78C6"))
    shape_fill(img, (203, 75, 165, 42), hx("#9A3FB0", 240), hx("#5E2A86", 240), hx("#FFB8F0"))
    return img

L = lambda v: int(v * S)
card = Image.new("RGBA", (L(W), L(H)), (0, 0, 0, 0))
card.alpha_composite(vgrad(L(274), L(H), hx("#2E1A4A", 245), hx("#140C22", 245)), (0, 0))

spikes = [(0, 300), (0, 120), (30, 40), (52, 100), (88, 18), (118, 92), (160, 10), (186, 96), (226, 34), (240, 118), (262, 70), (274, 150), (274, 300)]
sil = Image.new("L", card.size, 0)
ImageDraw.Draw(sil).polygon([(L(x), L(y + 20)) for x, y in spikes], fill=255)
sil = sil.filter(ImageFilter.GaussianBlur(L(1.5)))
sg = vgrad(L(W), L(H), (110, 62, 170, 120), (40, 22, 70, 40))
layer = Image.new("RGBA", card.size, (0, 0, 0, 0))
layer.paste(sg, (0, 0), sil)
card.alpha_composite(layer.filter(ImageFilter.GaussianBlur(L(6))))
card.alpha_composite(layer)
gl = Image.new("RGBA", card.size, (0, 0, 0, 0))
ImageDraw.Draw(gl).ellipse([L(-40), L(240), L(220), L(350)], fill=(199, 125, 255, 40))
card.alpha_composite(gl.filter(ImageFilter.GaussianBlur(L(10))))

mist = Image.open(mist_path).convert("RGBA")
mw, mh = mist.size
cw = int(mw * 0.30)
crop = mist.crop((int(mw * 0.62), int(mh * 0.12), int(mw * 0.62) + cw, int(mh * 0.12) + int(cw * 231 / 234)))
crop = ImageEnhance.Brightness(crop.resize((L(234), L(231)), Image.LANCZOS)).enhance(0.42)
card.alpha_composite(crop, (L(274), L(33)))
card.alpha_composite(vgrad(L(234), L(231), (20, 12, 34, 40), (20, 12, 34, 150)), (L(274), L(33)))

d = ImageDraw.Draw(card)
d.rectangle([L(274), 0, L(W), L(33)], fill=hx("#2A1846", 235))
d.rectangle([L(274), L(31), L(W), L(33)], fill=hx("#E04EC0"))
d.rectangle([L(274), L(264), L(W), L(H)], fill=hx("#1A1128", 240))
d.rectangle([L(274), L(264), L(W), L(265)], fill=hx("#E04EC0"))
d.line([(L(274), 0), (L(274), L(H))], fill=hx("#9B78C6"), width=L(1))
d.rounded_rectangle([L(461), L(270), L(497), L(306)], radius=L(6), fill=hx("#2A1846", 230), outline=hx("#9B78C6"), width=L(1))

yy, xx = np.mgrid[0:L(H), 0:L(W)].astype(np.float32) / S


def sdf_box(px, py, x0, y0, x1, y1, r):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx_, hy_ = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = np.abs(px - cx) - hx_, np.abs(py - cy) - hy_
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def noise(px, py, seed):
    rng = np.random.default_rng(seed)
    n = np.zeros_like(px)
    for f, a in ((0.04, 2.4), (0.085, 1.4), (0.2, 0.6)):
        ph = rng.uniform(0, 6.28, 3)
        n += a * (np.sin(px * f + ph[0]) * np.cos(py * f * 1.3 + ph[1]) + np.sin((px + py) * f * 0.7 + ph[2]))
    return n


heavy = np.clip((280 - xx) / 280, 0, 1)
wt = np.clip(yy / 40, 0.1, 1)
d_outer = sdf_box(xx, yy, 8, 1, W - 3, H - 3, 14) - noise(xx, yy, 3) * (0.6 + 1.4 * heavy) * wt
d_inner = sdf_box(xx, yy, 12, 0, W - 6, H - 7, 9) - noise(xx, yy, 9) * (0.3 + 0.8 * heavy) * wt
rng = np.random.default_rng(21)
for _ in range(30):
    side = int(rng.integers(1, 4))
    t = rng.uniform(0.03, 0.97)
    if side == 2 or (side in (0, 1) and t < 0.55):
        r = rng.uniform(2.5, 7.5)
    else:
        r = rng.uniform(1.5, 4)
    if side == 0:
        cx, cy = 8 + t * (W - 12), rng.uniform(1.5, 7)
    elif side == 1:
        cx, cy = 8 + t * (W - 12), H - rng.uniform(1.5, 6)
    elif side == 2:
        cx, cy = rng.uniform(1.5, 7), 8 + t * (H - 12)
    else:
        cx, cy = W - rng.uniform(1, 3), 8 + t * (H - 12)
    d_outer = np.minimum(d_outer, np.hypot(xx - cx, yy - cy) - r)

ao = np.clip(0.5 - d_outer * S, 0, 1)
ai = np.clip(0.5 - d_inner * S, 0, 1)
band = np.zeros((L(H), L(W), 4), np.float32)
t = np.clip((xx * 0.6 + yy) / (W * 0.6 + H), 0, 1)
c1, c2 = np.array(hx("#3A1F5C"), np.float32), np.array(hx("#7A2A86"), np.float32)
for k in range(3):
    band[..., k] = c1[k] + (c2[k] - c1[k]) * t
rim = np.clip(1 - np.abs(d_outer + 1.2) / 1.2, 0, 1)
for k, v in enumerate(hx("#E04EC0")[:3]):
    band[..., k] = band[..., k] * (1 - rim) + v * rim
il = np.clip(1 - np.abs(d_inner) / 0.9, 0, 1)
for k, v in enumerate(hx("#C9A8F5")[:3]):
    band[..., k] = band[..., k] * (1 - il) + v * il
band[..., 3] = 255 * ao
arr = np.array(card, np.float32)
arr[..., 3] *= ai
ac = arr[..., 3:4] / 255
out = band.copy()
out[..., :3] = arr[..., :3] * ac + band[..., :3] * (1 - ac)
out[..., 3] = np.maximum(band[..., 3], arr[..., 3])
frame = Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA").resize((W, H), Image.LANCZOS)

img = Image.open(base_path).convert("RGBA")
img = style_small(img)
img.paste(Image.new("RGBA", (W + 2, H + 2), (0, 0, 0, 0)), (X0 - 1, Y0 - 1))
img.alpha_composite(frame, (X0, Y0))
img.save(dst, optimize=True)

fin = Image.open(dst).convert("RGBA")
fp = fin.load()
for x in range(X0, X0 + W):
    for y in range(Y0, Y0 + 2):
        r, g, b, a = fp[x, y]
        if a > 0:
            fp[x, y] = (201, 168, 245, a) if y == Y0 + 1 else (224, 78, 192, a)
fin.save(dst, optimize=True)
