import re
import sys

TINT = "#70FFFFFF"


def patch(path, names, add_pattern=False):
    s = open(path, encoding="utf-8").read()
    for n in names:
        m = re.search(r'<grid name="' + re.escape(n) + r'"([^>]*)>(.*?)</grid>', s, re.S)
        if not m:
            print("missing", n)
            continue
        attrs, body = m.group(1), m.group(2)
        wx = [int(v) for v in re.search(r'weightsX="([^"]+)"', attrs).group(1).split(",")]
        wy = [int(v) for v in re.search(r'weightsY="([^"]+)"', attrs).group(1).split(",")]
        cells = re.findall(r'<(?:area|alias)[^>]*/>', body)
        dims = []
        for c in cells:
            mm = re.search(r'xywh="(\d+),(\d+),(\d+),(\d+)"', c)
            dims.append((int(mm.group(3)), int(mm.group(4))) if mm else (0, 0))
        cols = len(wx)
        rows = [dims[r * cols] for r in range(len(wy))] if len(dims) >= cols * len(wy) else []
        if rows:
            top = 0
            for r, w in enumerate(wy):
                if w:
                    break
                top += rows[r][1]
            bot = 0
            for r in range(len(wy) - 1, -1, -1):
                if wy[r]:
                    break
                bot += rows[r][1]
            left = dims[0][0] if wx[0] == 0 else 0
            right = dims[cols - 1][0] if wx[-1] == 0 else 0
        else:
            top = bot = left = right = 6
        inset = f"{top},{max(left, 2)},{max(bot, 2)},{max(right, 2)}"
        base = n + ".plain"
        new_grid = '<grid name="' + base + '"' + attrs + '>' + body + '</grid>'
        comp = ('\n\t\t<composed name="' + n + '"><alias ref="' + base + '"/>'
                '<alias ref="gengar-bgpat" inset="' + inset + '" tint="' + TINT + '"/></composed>')
        s = s[:m.start()] + new_grid + comp + s[m.end():]
        print(n, inset)
    if add_pattern:
        block = ('<themes>\n\t<images file="res/gengar-panel-pattern.png" filter="linear">\n'
                 '\t\t<area name="gengar-bgpat" xywh="0,0,192,192" repeatX="true" repeatY="true"/>\n\t</images>')
        s = s.replace("<themes>", block, 1)
    open(path, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    pass
