import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
bh = Image.open(src).convert("RGBA")
out = Image.new("RGBA", (400, 192), (0, 0, 0, 0))
for k, x in enumerate((0, 205, 410)):
    t = bh.crop((x, 486, x + 200, 516)).resize((400, 60), Image.LANCZOS)
    out.alpha_composite(t, (0, k * 64))
out.save(dst, optimize=True)
