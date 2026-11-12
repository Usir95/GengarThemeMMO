import argparse
import os
import sys
import xml.etree.ElementTree as ET

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPIOS = ("gm-", "gengar-")
IMG_TAGS = {"area", "select", "alias", "composed", "grid", "animation", "gradient", "cursor"}


class Validador:
    def __init__(self, mod, bases):
        self.mod = os.path.abspath(mod)
        self.bases = [os.path.abspath(b) for b in bases if b and os.path.isdir(b)]
        self.errores = []
        self.avisos = []
        self.cache = {}

    def err(self, msg):
        self.errores.append(msg)

    def aviso(self, msg):
        self.avisos.append(msg)

    def rel(self, p):
        for r in [self.mod] + self.bases:
            if p.startswith(r):
                return os.path.relpath(p, os.path.dirname(r)).replace(os.sep, "/")
        return p

    def parse(self, path):
        if path not in self.cache:
            try:
                self.cache[path] = ET.parse(path).getroot()
            except ET.ParseError as e:
                self.err(f"XML mal formado: {self.rel(path)}: {e}")
                self.cache[path] = None
        return self.cache[path]

    def resolver(self, fn, base_dir):
        marca = "../../data/themes/"
        if fn.startswith(marca):
            resto = fn[len(marca):]
            for b in self.bases:
                p = os.path.join(b, resto)
                if os.path.exists(p):
                    return p, True
            return None, True
        return os.path.normpath(os.path.join(base_dir, fn)), False

    def es_mod(self, p):
        return p.startswith(self.mod)

    def revisar_xml_sueltos(self):
        for d, _, fs in os.walk(self.mod):
            for f in fs:
                p = os.path.join(d, f)
                if f.endswith(".xml"):
                    self.parse(p)
                if f.startswith("."):
                    continue
                if f.lower().endswith(".txt"):
                    self.err(f"Archivo .txt dentro de mod/ (rompe la importación): {self.rel(p)}")

    def revisar_info(self):
        p = os.path.join(self.mod, "info.xml")
        r = self.parse(p)
        if r is None:
            return []
        temas = []
        for t in r.iter("theme"):
            tp = t.get("path", "")
            d = os.path.join(self.mod, tp)
            tx = os.path.join(d, "theme.xml")
            if not os.path.exists(tx):
                self.err(f"info.xml: no existe {tp}theme.xml")
            else:
                temas.append((t.get("name"), tx))
        for s in r.iter("string"):
            sp = os.path.join(self.mod, s.get("path", ""))
            if not os.path.exists(sp):
                self.err(f"info.xml: no existe {s.get('path')}")
        return temas

    def revisar_tema(self, nombre, theme_xml):
        orden = []
        imagenes = {}
        fuentes = set()
        constantes = set()
        sin_base = [False]

        def cargar(path, visto):
            if path in visto:
                self.err(f"[{nombre}] include circular: {self.rel(path)}")
                return
            r = self.parse(path)
            if r is None:
                return
            visto = visto | {path}
            d = os.path.dirname(path)
            for el in r:
                if el.tag == "include":
                    fn = el.get("filename", "")
                    if fn == "hud_kit":
                        for esc in ("1x", "2x"):
                            hp = os.path.join(d, "hud", esc, "hud.xml")
                            if os.path.exists(hp):
                                cargar(hp, visto)
                        continue
                    p, de_base = self.resolver(fn, d)
                    if p is None:
                        sin_base[0] = True
                        continue
                    if not os.path.exists(p):
                        self.err(f"[{nombre}] {self.rel(path)}: include inexistente {fn}")
                        continue
                    cargar(p, visto)
                elif el.tag == "constantDef":
                    constantes.add(el.get("name"))
                elif el.tag == "fontDef":
                    fuentes.add(el.get("name"))
                    self.revisar_archivo(nombre, path, el.get("filename"), "fuente")
                    for fb in el.iter("fallbackFontDef"):
                        self.revisar_archivo(nombre, path, fb.get("filename"), "fuente")
                elif el.tag == "images":
                    if el.get("file"):
                        self.revisar_archivo(nombre, path, el.get("file"), "imagen")
                    self.revisar_bloque(nombre, path, el, imagenes, constantes)
                elif el.tag == "theme":
                    orden.append((el, path))

        cargar(theme_xml, set())
        if sin_base[0]:
            self.aviso(f"[{nombre}] no encontré el tema base del juego; no se revisaron merge ni nombres del juego")
        self.revisar_merges(nombre, orden, sin_base[0])
        self.revisar_referencias(nombre, orden, imagenes, fuentes, sin_base[0])

    def revisar_archivo(self, nombre, xml_path, fn, tipo):
        if not fn or fn.endswith("_lang") or not self.es_mod(xml_path):
            return
        p, de_base = self.resolver(fn, os.path.dirname(xml_path))
        if p is None:
            return
        if not os.path.exists(p) and not de_base:
            self.err(f"[{nombre}] {self.rel(xml_path)}: {tipo} inexistente {fn}")

    def revisar_bloque(self, nombre, path, bloque, imagenes, constantes):
        def nombres_ref(el):
            for sub in el.iter():
                if sub is el:
                    continue
                ref = sub.get("ref")
                if ref:
                    yield ref

        for el in bloque:
            if el.tag not in IMG_TAGS:
                continue
            n = el.get("name")
            ref = el.get("ref")
            refs = list(nombres_ref(el)) + ([ref] if ref else [])
            if self.es_mod(path):
                for rf in refs:
                    if rf != "none" and rf not in imagenes:
                        self.err(f"[{nombre}] {self.rel(path)}: '{n or el.tag}' usa '{rf}' antes de definirse")
                for sub in el.iter():
                    t = sub.get("tint")
                    if t and not t.startswith("#") and t not in constantes:
                        self.err(f"[{nombre}] {self.rel(path)}: tinte '{t}' no es una constante definida")
            if n:
                imagenes[n] = path

    def revisar_merges(self, nombre, orden, sin_base):
        defs = {}
        for el, path in orden:
            n = el.get("name")
            if el.get("merge") == "true":
                base = defs.get(n)
                if base is None:
                    if not sin_base or self.es_mod(path):
                        if not sin_base:
                            self.err(f"[{nombre}] {self.rel(path)}: merge sobre '{n}', que no existe antes")
                    continue
                self.merge_hijos(nombre, path, el, base, [n])
            else:
                defs[n] = el

    def merge_hijos(self, nombre, path, mio, base, ruta):
        for ch in mio.findall("theme"):
            if ch.get("merge") != "true":
                continue
            cand = [c for c in base.findall("theme") if c.get("name") == ch.get("name")]
            r = ruta + [ch.get("name")]
            if not cand:
                self.err(f"[{nombre}] {self.rel(path)}: merge sobre '{'/'.join(r)}', que no existe en la versión final de '{ruta[0]}'")
            else:
                self.merge_hijos(nombre, path, ch, cand[-1], r)

    def revisar_referencias(self, nombre, orden, imagenes, fuentes, sin_base):
        for el, path in orden:
            if not self.es_mod(path):
                continue
            for sub in el.iter():
                if sub.tag == "image" and sub.text:
                    v = sub.text.strip()
                    if v == "none":
                        continue
                    if v.endswith(".*"):
                        pre = v[:-1]
                        ok = any(k.startswith(pre) for k in imagenes)
                    else:
                        ok = v in imagenes
                    if not ok and (v.startswith(PROPIOS) or not sin_base):
                        msg = f"[{nombre}] {self.rel(path)}: imagen '{v}' no está definida"
                        (self.err if v.startswith(PROPIOS) else self.aviso)(msg)
                elif sub.tag == "font" and sub.text:
                    v = sub.text.strip()
                    if v not in fuentes and (v.startswith(PROPIOS) or not sin_base):
                        msg = f"[{nombre}] {self.rel(path)}: fuente '{v}' no está definida"
                        (self.err if v.startswith(PROPIOS) else self.aviso)(msg)

    def correr(self):
        self.revisar_xml_sueltos()
        for nombre, tx in self.revisar_info():
            self.revisar_tema(nombre, tx)
        for a in self.avisos:
            print("AVISO  " + a)
        for e in self.errores:
            print("ERROR  " + e)
        print(f"Validación: {len(self.errores)} errores, {len(self.avisos)} avisos")
        return 1 if self.errores else 0


def main():
    ap = argparse.ArgumentParser(description="Valida el mod antes de empaquetarlo.")
    ap.add_argument("--mod", default=os.path.join(RAIZ, "mod"))
    ap.add_argument("--juego", default=os.environ.get("POKEMMO_DIR", r"C:\Program Files\PokeMMO"))
    a = ap.parse_args()
    bases = [os.path.join(a.juego, "data", "themes"), os.path.join(RAIZ, "fuentes", "tema-base")]
    sys.exit(Validador(a.mod, bases).correr())


if __name__ == "__main__":
    main()
