import sys
import math
from PIL import Image, ImageDraw, ImageFilter

dst = sys.argv[1]
pattern = Image.open(sys.argv[2]).convert("RGBA")
S = 4
OUT = Image.new("RGBA", (512, 256), (0, 0, 0, 0))


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def rr_mask(W, H, pad, r):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([pad, pad, W - pad - 1, H - pad - 1], radius=r, fill=255)
    return m


def command(state):
    w, h = 209, 52
    W, H = w * S, h * S
    m = rr_mask(W, H, S, 9 * S)
    top, bot, border, bw, accent, glow, pat_a = {
        "default": (hx("#4B2D78", 235), hx("#24143D", 235), hx("#9B78C6", 220), 1, hx("#E04EC0"), 0.0, 0.10),
        "hover": (hx("#7A48B8", 245), hx("#3A1E5E", 245), hx("#FF6FD8"), 2, hx("#FF8FE2"), 0.55, 0.16),
        "disabled": (hx("#3A3346", 200), hx("#25202D", 200), hx("#5A5266", 200), 1, hx("#5A5266"), 0.0, 0.05),
    }[state]
    g = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(g)
    for j in range(H):
        d.line([(0, j), (W, j)], fill=lerp(top, bot, j / (H - 1)))
    t = pattern.resize((pattern.width * S // 3, pattern.height * S // 3), Image.BICUBIC)
    t.putalpha(t.getchannel("A").point(lambda a: int(a * pat_a)))
    for tx in range(0, W, t.width):
        for ty in range(0, H, t.height):
            g.alpha_composite(t, (tx, ty))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for j in range(int(H * 0.45)):
        sd.line([(0, j), (W, j)], fill=(255, 230, 255, int(38 * (1 - j / (H * 0.45)))))
    g.alpha_composite(sh)
    if glow:
        e = Image.new("L", (W, H), 0)
        ImageDraw.Draw(e).rounded_rectangle([S, S, W - S - 1, H - S - 1], radius=9 * S, outline=255, width=7 * S)
        e = e.filter(ImageFilter.GaussianBlur(4 * S)).point(lambda a: int(a * glow))
        gl = Image.new("RGBA", (W, H), hx("#FF5FD2"))
        gl.putalpha(e)
        g.alpha_composite(gl)
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o.paste(g, (0, 0), m)
    od = ImageDraw.Draw(o)
    od.rounded_rectangle([S, S, W - S - 1, H - S - 1], radius=9 * S, outline=border, width=bw * S)
    od.rounded_rectangle([S * 4, S * 10, S * 7, H - S * 10], radius=S * 2, fill=accent)
    return down(o, w, h)


def icon_fight(d, s):
    for k in range(3):
        x = s * (0.28 + k * 0.2)
        d.line([(x, s * 0.18), (x + s * 0.22, s * 0.82)], fill=(255, 255, 255, 255), width=int(s * 0.09))


def icon_bag(d, s):
    d.rounded_rectangle([s * 0.18, s * 0.32, s * 0.82, s * 0.86], radius=s * 0.12, fill=(255, 255, 255, 255))
    d.arc([s * 0.32, s * 0.12, s * 0.68, s * 0.48], 180, 360, fill=(255, 255, 255, 255), width=int(s * 0.07))
    d.rectangle([s * 0.18, s * 0.50, s * 0.82, s * 0.56], fill=(0, 0, 0, 0))
    d.rounded_rectangle([s * 0.42, s * 0.46, s * 0.58, s * 0.62], radius=s * 0.03, fill=(255, 255, 255, 255))


def icon_ball(d, s):
    d.ellipse([s * 0.14, s * 0.14, s * 0.86, s * 0.86], fill=(255, 255, 255, 255))
    d.rectangle([s * 0.14, s * 0.47, s * 0.86, s * 0.53], fill=(0, 0, 0, 0))
    d.ellipse([s * 0.38, s * 0.38, s * 0.62, s * 0.62], fill=(0, 0, 0, 0))
    d.ellipse([s * 0.43, s * 0.43, s * 0.57, s * 0.57], fill=(255, 255, 255, 255))


def icon_run(d, s):
    pts = [(s * 0.30, s * 0.20)]
    for k in range(9):
        a = math.pi * (1.0 - k / 8)
        pts.append((s * 0.50 + math.cos(a) * s * 0.22, s * 0.40 - math.sin(a) * s * 0.22))
    body = [(s * 0.28, s * 0.40), (s * 0.72, s * 0.40), (s * 0.72, s * 0.80), (s * 0.62, s * 0.70), (s * 0.52, s * 0.82), (s * 0.42, s * 0.70), (s * 0.32, s * 0.82), (s * 0.28, s * 0.80)]
    d.ellipse([s * 0.28, s * 0.18, s * 0.72, s * 0.62], fill=(255, 255, 255, 255))
    d.polygon([(s * 0.30, s * 0.32), (s * 0.30, s * 0.06), (s * 0.44, s * 0.22)], fill=(255, 255, 255, 255))
    d.polygon([(s * 0.70, s * 0.32), (s * 0.70, s * 0.06), (s * 0.56, s * 0.22)], fill=(255, 255, 255, 255))
    d.polygon([(s * 0.66, s * 0.30), (s * 0.86, s * 0.24), (s * 0.72, s * 0.42)], fill=(255, 255, 255, 255))
    d.polygon(body, fill=(255, 255, 255, 255))
    d.polygon([(s * 0.34, s * 0.34), (s * 0.47, s * 0.40), (s * 0.40, s * 0.44)], fill=(0, 0, 0, 0))
    d.polygon([(s * 0.66, s * 0.34), (s * 0.53, s * 0.40), (s * 0.60, s * 0.44)], fill=(0, 0, 0, 0))
    d.chord([s * 0.36, s * 0.38, s * 0.64, s * 0.58], 15, 165, fill=(0, 0, 0, 0))
    for k in range(3):
        y = s * (0.38 + k * 0.14)
        d.line([(s * 0.04, y), (s * 0.20, y)], fill=(255, 255, 255, 255), width=int(s * 0.05))


def icon(fn, color, alpha):
    n = 40
    s = n * S
    m = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    fn(ImageDraw.Draw(m), s)
    a = m.getchannel("A").point(lambda v: int(v * alpha))
    col = Image.new("RGBA", (s, s), color)
    col.putalpha(a)
    gl = Image.new("RGBA", (s, s), hx("#FF5FD2"))
    gl.putalpha(m.getchannel("A").filter(ImageFilter.GaussianBlur(S * 2)).point(lambda v: int(v * alpha * 0.6)))
    o = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    o.alpha_composite(gl)
    o.alpha_composite(col)
    return down(o, n, n)


def panel():
    n = 48
    W = n * S
    m = rr_mask(W, W, S, 8 * S)
    g = Image.new("RGBA", (W, W))
    d = ImageDraw.Draw(g)
    for j in range(W):
        d.line([(0, j), (W, j)], fill=lerp(hx("#1E1132", 215), hx("#120A1E", 225), j / (W - 1)))
    o = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    o.paste(g, (0, 0), m)
    od = ImageDraw.Draw(o)
    od.rounded_rectangle([S, S, W - S - 1, W - S - 1], radius=8 * S, outline=hx("#9B78C6", 230), width=S)
    od.line([(S * 10, S * 2), (W - S * 10, S * 2)], fill=hx("#E04EC0"), width=S)
    return down(o, n, n)


def confirm(state, kind):
    w, h = 120, 30
    W, H = w * S, h * S
    m = rr_mask(W, H, S, 7 * S)
    top, bot, border, bw = {
        "default": (hx("#4B2D78", 240), hx("#2A1846", 240), hx("#9B78C6"), 1),
        "hover": (hx("#7A48B8", 250), hx("#46256E", 250), hx("#FF6FD8"), 2),
        "disabled": (hx("#3A3346", 210), hx("#25202D", 210), hx("#5A5266"), 1),
    }[state]
    g = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(g)
    for j in range(H):
        d.line([(0, j), (W, j)], fill=lerp(top, bot, j / (H - 1)))
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o.paste(g, (0, 0), m)
    od = ImageDraw.Draw(o)
    od.rounded_rectangle([S, S, W - S - 1, H - S - 1], radius=7 * S, outline=border, width=bw * S)
    cx, cy, r = S * 15, H // 2, S * 10
    badge = hx("#E04EC0") if kind == "confirm" else hx("#C9B8F0")
    if state == "disabled":
        badge = hx("#5A5266")
    od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=badge, outline=hx("#FFFFFF", 200), width=S)
    if kind == "confirm":
        od.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.38)], fill=hx("#FFFFFF"), width=int(S * 2.2), joint="curve")
    return down(o, w, h)


OUT.alpha_composite(command("default"), (0, 0))
OUT.alpha_composite(command("hover"), (0, 54))
OUT.alpha_composite(command("disabled"), (0, 108))
for k, (fn, col) in enumerate([(icon_fight, hx("#F3E6FF")), (icon_bag, hx("#F3E6FF")), (icon_ball, hx("#F3E6FF")), (icon_run, hx("#F3E6FF"))]):
    OUT.alpha_composite(icon(fn, col, 0.30), (214 + k * 42, 0))
    OUT.alpha_composite(icon(fn, col, 0.85), (214 + k * 42, 42))
OUT.alpha_composite(panel(), (214, 90))
for k, st in enumerate(["default", "hover", "disabled"]):
    OUT.alpha_composite(confirm(st, "confirm"), (0, 164 + k * 31))
OUT.save(dst, optimize=True)
