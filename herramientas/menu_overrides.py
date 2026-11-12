import sys
import xml.etree.ElementTree as ET

MAP = {
    "ui-header.background": "gm-header.background",
    "ui-table-row.background": "gm-cell.background",
    "ui-table-header.*": "gm-th.*",
    "ui-table-header.background": "gm-th.background",
    "ui-inputbox.background": "gm-cell.background",
    "ui-inputbox.default": "gm-cell.default",
    "ui-tab-vertical.*": "gm-tab-v.*",
    "ui-tab-shop.background": "gm-header.background",
    "mobile.box.dark3.50": "gm-cell.background",
}


def walk(el, path, out):
    for th in el.findall("theme"):
        p = path + [th.get("name")]
        for prm in th.findall("param"):
            img = prm.find("image")
            if img is not None and (img.text or "").strip() in MAP:
                out.setdefault(tuple(p), []).append((prm.get("name"), MAP[img.text.strip()]))
        walk(th, p, out)


def build(found):
    root = ET.Element("themes")
    nodes = {}
    for path in sorted(found):
        parent = root
        for i in range(len(path)):
            key = path[: i + 1]
            if key not in nodes:
                nodes[key] = ET.SubElement(parent, "theme", {"name": path[i], "merge": "true"})
            parent = nodes[key]
        for name, img in found[path]:
            prm = ET.SubElement(parent, "param", {"name": name})
            ET.SubElement(prm, "image").text = img
    return root


args = sys.argv[2:]
skip = set()
if args and args[0] == "-x":
    skip = set(args[1].split(","))
    args = args[2:]
found = {}
for f in args:
    walk(ET.parse(f).getroot(), [], found)
found = {k: v for k, v in found.items() if k[0] not in skip}
root = build(found)
ET.indent(root, "  ")
s = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"
open(sys.argv[1], "w", encoding="utf-8").write(s)
print(len(found), "temas")
