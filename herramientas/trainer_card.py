import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

bg_path, logo_path, dst = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 454, 287
S = 4


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


src = Image.open(bg_path).convert("RGBA")
sw, sh = src.size
cw = int(sw * 0.42)
ch = int(cw * H / W)
art = src.crop((sw - cw, 0, sw, ch)).resize((W * S, H * S), Image.LANCZOS)
art = ImageEnhance.Brightness(art).enhance(0.85)

shade = Image.new("RGBA", (W * S, H * S))
sd = ImageDraw.Draw(shade)
for x in range(W * S):
    t = x / (W * S)
    a = int(235 - 175 * max(0, (t - 0.25) / 0.75) ** 1.2) if t > 0.25 else 235
    sd.line([(x, 0), (x, H * S)], fill=(20, 12, 34, a))
card = Image.alpha_composite(art, shade)
d = ImageDraw.Draw(card)

d.rectangle([0, 0, W * S, 46 * S], fill=hx("#1A1128", 215))
d.rectangle([0, 46 * S, W * S, 47 * S + S // 2], fill=hx("#E04EC0"))
d.rounded_rectangle([6 * S, 6 * S, 290 * S, 40 * S], radius=6 * S, fill=hx("#2A1846", 200), outline=hx("#9B78C6", 160), width=S)

d.rounded_rectangle([318 * S, 50 * S, 448 * S, 70 * S], radius=10 * S, fill=hx("#2A1846", 220), outline=hx("#9B78C6", 200), width=S)

glow = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
ImageDraw.Draw(glow).rounded_rectangle([24 * S, 54 * S, 148 * S, 219 * S], radius=10 * S, outline=hx("#C77DFF", 160), width=4 * S)
card.alpha_composite(glow.filter(ImageFilter.GaussianBlur(4 * S)))
av = Image.new("RGBA", (124 * S, 165 * S))
ad = ImageDraw.Draw(av)
for y in range(165 * S):
    t = y / (165 * S)
    ad.line([(0, y), (124 * S, y)], fill=(int(58 - 30 * t), int(36 - 20 * t), int(92 - 50 * t), 225))
m = Image.new("L", av.size, 0)
ImageDraw.Draw(m).rounded_rectangle([0, 0, 124 * S - 1, 165 * S - 1], radius=10 * S, fill=255)
card.paste(av, (24 * S, 54 * S), m)
d = ImageDraw.Draw(card)
d.ellipse([44 * S, 150 * S, 128 * S, 214 * S], fill=(199, 125, 255, 40))
d.rounded_rectangle([24 * S, 54 * S, 148 * S, 219 * S], radius=10 * S, outline=hx("#9B78C6"), width=S + S // 2)

d.rectangle([0, 224 * S, W * S, H * S], fill=hx("#140C22", 230))
d.rectangle([0, 224 * S, W * S, 225 * S], fill=hx("#E04EC0"))
for i in range(8):
    x = 38 + i * 48
    d.rounded_rectangle([x * S, 233 * S, (x + 38) * S, 271 * S], radius=8 * S, fill=hx("#2A1846", 220), outline=hx("#9B78C6", 220), width=S)

logo = Image.open(logo_path).convert("RGBA")
lw = 150 * S
lh = int(logo.height * lw / logo.width)
logo = logo.resize((lw, lh), Image.LANCZOS)
card.alpha_composite(logo, (W * S - lw - 10 * S, (46 * S - lh) // 2 + S))

mask = Image.new("L", (W * S, H * S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, W * S - 1, H * S - 1], radius=14 * S, fill=255)
out = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
out.paste(card, (0, 0), mask)
ImageDraw.Draw(out).rounded_rectangle([S, S, W * S - S - 1, H * S - S - 1], radius=14 * S, outline=hx("#9B78C6"), width=2 * S)
out.resize((W, H), Image.LANCZOS).save(dst, optimize=True)

import math
import numpy as np

img = Image.open(dst).convert("RGBA").resize((W * S, H * S), Image.LANCZOS)
yy, xx = np.mgrid[0:H * S, 0:W * S].astype(np.float32) / S


def sdf_box(px, py, x0, y0, x1, y1, r):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx_, hy_ = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = np.abs(px - cx) - hx_, np.abs(py - cy) - hy_
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def noise(px, py, seed):
    rng = np.random.default_rng(seed)
    n = np.zeros_like(px)
    for f, a in ((0.045, 2.2), (0.09, 1.3), (0.21, 0.6)):
        ph = rng.uniform(0, 6.28, 4)
        n += a * (np.sin(px * f + ph[0]) * np.cos(py * f * 1.3 + ph[1]) + np.sin((px + py) * f * 0.7 + ph[2]))
    return n


wt = np.clip(yy / 30, 0.15, 1)
d_outer = sdf_box(xx, yy, 8, 2, W - 8, H - 8, 14) - noise(xx, yy, 7) * 1.4 * wt
d_inner = sdf_box(xx, yy, 12, 0, W - 12, H - 13, 10) - noise(xx, yy, 11) * 0.8 * wt
rng = np.random.default_rng(5)
for _ in range(26):
    side = int(rng.integers(1, 4))
    t = rng.uniform(0.05, 0.95)
    r = rng.uniform(2.0, 6.5)
    if side == 0:
        cx, cy = 8 + t * (W - 16), rng.uniform(1, 7)
    elif side == 1:
        cx, cy = 8 + t * (W - 16), H - rng.uniform(1, 7)
    elif side == 2:
        cx, cy = rng.uniform(1, 7), 8 + t * (H - 16)
    else:
        cx, cy = W - rng.uniform(1, 7), 8 + t * (H - 16)
    d_outer = np.minimum(d_outer, np.hypot(xx - cx, yy - cy) - r)
for cx in (70, 190, 300, 410):
    w = rng.uniform(3, 5)
    drip = np.where(yy > H - 12, np.abs(xx - cx) - w * (1 - (yy - (H - 12)) / 12) ** 0.5, 99)
    d_outer = np.minimum(d_outer, np.maximum(drip, yy - (H - 1)))

alpha_outer = np.clip(0.5 - d_outer * S, 0, 1)
alpha_inner = np.clip(0.5 - d_inner * S, 0, 1)
t = np.clip((xx + yy) / (W + H), 0, 1)
band = np.zeros((H * S, W * S, 4), np.float32)
c1, c2 = np.array(hx("#3A1F5C"), np.float32), np.array(hx("#7A2A86"), np.float32)
for k in range(3):
    band[..., k] = c1[k] + (c2[k] - c1[k]) * t
rim = np.clip(1 - np.abs(d_outer + 1.2) / 1.2, 0, 1)
for k, v in enumerate(hx("#E04EC0")[:3]):
    band[..., k] = band[..., k] * (1 - rim) + v * rim
inner_line = np.clip(1 - np.abs(d_inner) / 0.9, 0, 1)
for k, v in enumerate(hx("#C9A8F5")[:3]):
    band[..., k] = band[..., k] * (1 - inner_line) + v * inner_line
band[..., 3] = 255 * alpha_outer

arr = np.array(img, np.float32)
arr[..., 3] *= alpha_inner
a_c = arr[..., 3:4] / 255
out = band.copy()
out[..., :3] = arr[..., :3] * a_c + band[..., :3] * (1 - a_c)
out[..., 3] = np.maximum(band[..., 3], arr[..., 3])
card = Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA")

sil = Image.new("RGBA", (124 * S, 165 * S), (0, 0, 0, 0))
pts = [(8, 165), (8, 70)]
spikes = [(8, 70), (22, 26), (34, 58), (48, 14), (62, 50), (76, 14), (90, 58), (102, 26), (116, 70)]
pts = [(8, 165)] + spikes + [(116, 165)]
mask = Image.new("L", sil.size, 0)
ImageDraw.Draw(mask).polygon([(x * S, y * S) for x, y in pts], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(S))
grad = Image.new("RGBA", sil.size)
gd = ImageDraw.Draw(grad)
for y in range(165 * S):
    tt = y / (165 * S)
    gd.line([(0, y), (124 * S, y)], fill=(int(120 - 70 * tt), int(70 - 45 * tt), int(190 - 110 * tt), int(200 - 120 * tt)))
sil.paste(grad, (0, 0), mask)
glow = sil.filter(ImageFilter.GaussianBlur(5 * S))
area = card.crop((24 * S, 54 * S, 148 * S, 219 * S))
area.alpha_composite(glow)
area.alpha_composite(sil)
rm = Image.new("L", area.size, 0)
ImageDraw.Draw(rm).rounded_rectangle([2 * S, 2 * S, 122 * S, 163 * S], radius=9 * S, fill=255)
base = card.crop((24 * S, 54 * S, 148 * S, 219 * S))
base.paste(area, (0, 0), rm)
card.paste(base, (24 * S, 54 * S))
ImageDraw.Draw(card).rounded_rectangle([24 * S, 54 * S, 148 * S, 219 * S], radius=10 * S, outline=hx("#9B78C6"), width=S + S // 2)
card.resize((W, H), Image.LANCZOS).save(dst, optimize=True)

fin = Image.open(dst).convert("RGBA")
fp = fin.load()
for x in range(fin.width):
    for y in range(0, 2):
        r, g, b, a = fp[x, y]
        if a > 0:
            fp[x, y] = (201, 168, 245, a) if y == 1 else (224, 78, 192, a)
fin.save(dst, optimize=True)
