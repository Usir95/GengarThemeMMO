import re
import sys
from PIL import Image

MAIN = (155, 120, 198)


def weight(r, g, b):
    if r >= 1.6 * g and r >= 0.85 * b and r > 90:
        return 1.0
    ratio = max(r / MAIN[0], g / MAIN[1], b / MAIN[2])
    return max(0.0, min(1.0, (ratio - 1.0) / 0.12))


def split_png(src, dst):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    out = Image.new("RGBA", (w, h * 2), (0, 0, 0, 0))
    s, o = im.load(), out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = s[x, y]
            if not a:
                continue
            e = weight(r, g, b)
            if e < 1:
                o[x, y] = (min(255, round(r * 255 / MAIN[0])), min(255, round(g * 255 / MAIN[1])), min(255, round(b * 255 / MAIN[2])), a)
            if e > 0:
                o[x, y + h] = (r, g, b, round(a * e))
    out.save(dst)
    return h


def split_xml(path, image_file, h):
    s = open(path, encoding="utf-8").read()
    m = re.search(r'(<images file="' + re.escape(image_file) + r'"[^>]*>)(.*?)(</images>)', s, re.S)
    if not m:
        raise SystemExit("no se encontro " + image_file)

    def rep(a):
        ind, name, x, y, w, hh, rest = a.group(1), a.group(2), int(a.group(3)), int(a.group(4)), a.group(5), a.group(6), a.group(7)
        return (f'{ind}<area name="{name}.b" xywh="{x},{y},{w},{hh}"{rest} tint="main-color"/>\n'
                f'{ind}<area name="{name}.f" xywh="{x},{y + h},{w},{hh}"{rest}/>\n'
                f'{ind}<composed name="{name}"><alias ref="{name}.b"/><alias ref="{name}.f"/></composed>')

    body = re.sub(r'([ \t]*)<area name="([^"]+)" xywh="(\d+),(\d+),(\d+),(\d+)"([^/]*)/>', rep, m.group(2))
    s = s[: m.start(2)] + body + s[m.end(2):]
    open(path, "w", encoding="utf-8", newline="").write(s)


if __name__ == "__main__":
    xml, image_file, png_in, png_out = sys.argv[1:5]
    split_xml(xml, image_file, split_png(png_in, png_out))
