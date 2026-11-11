import sys
from PIL import Image, ImageDraw, ImageEnhance

dst, pattern = sys.argv[1], sys.argv[2]
im = Image.open(dst).convert("RGBA")
pat = Image.open(pattern).convert("RGBA")


def hx(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


x, y, w, h = 6, 312, 800, 115
panel = Image.new("RGBA", (w, h))
pd = ImageDraw.Draw(panel)
for j in range(h):
    pd.line([(0, j), (w, j)], fill=lerp(hx("#2A1846", 172), hx("#140C22", 192), j / (h - 1)))
tile = ImageEnhance.Brightness(pat).enhance(1.9)
tile = tile.resize((tile.width * 2 // 3, tile.height * 2 // 3), Image.LANCZOS)
tile.putalpha(tile.getchannel("A").point(lambda a: int(a * 0.32)))
for tx in range(0, w, tile.width):
    for ty in range(-tile.height // 3, h, tile.height):
        panel.alpha_composite(tile, (tx, ty))
pd = ImageDraw.Draw(panel)
pd.rectangle([0, 0, w - 1, 1], fill=hx("#E04EC0"))
pd.rectangle([0, 0, w - 1, h - 1], outline=hx("#9B78C6"))
im.paste(Image.new("RGBA", (w, h), (0, 0, 0, 0)), (x, y))
im.alpha_composite(panel, (x, y))
im.save(dst, optimize=True)
