$ErrorActionPreference = "Stop"

$python = Get-Command py -ErrorAction SilentlyContinue
$pythonArgs = @("-3")
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    $pythonArgs = @()
}
if (-not $python) { throw "Se requiere Python 3 para generar el mod." }

$package = @"
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from zipfile import ZIP_STORED, ZipFile

project = Path(sys.argv[1])
root = project / "mod"
dist = project / "dist"
out = dist / "GengarTheme.mod"
allowed = {".xml", ".png", ".ogg", ".wav", ".ttf", ".ttc"}
if not (root / "info.xml").is_file():
    raise SystemExit("Falta mod/info.xml")
dist.mkdir(exist_ok=True)
with TemporaryDirectory(dir=dist) as temporary:
    archive_path = Path(temporary) / out.name
    with ZipFile(archive_path, "w", ZIP_STORED) as archive:
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            if path.is_file() and path.suffix.lower() in allowed and not any(part.startswith(".") for part in relative.parts):
                archive.write(path, relative.as_posix())
    archive_path.replace(out)
print(out)
"@

$package | & $python.Source @pythonArgs - $PSScriptRoot
if ($LASTEXITCODE -ne 0) { throw "No se pudo generar el mod." }