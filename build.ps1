param([switch]$SinValidar)
$ErrorActionPreference = "Stop"

if (-not $SinValidar) {
    $validar = Join-Path $PSScriptRoot "herramientas\validar.py"
    $py = Get-Command py -ErrorAction SilentlyContinue
    $pyArgs = @("-3", $validar)
    if (-not $py) {
        $py = Get-Command python -ErrorAction SilentlyContinue
        $pyArgs = @($validar)
    }
    if (-not $py) { throw "No encontré Python. Instálalo o usa .\build.ps1 -SinValidar" }
    & $py.Source @pyArgs
    if ($LASTEXITCODE -ne 0) { throw "La validación encontró errores; no se generó el paquete." }
}

$root = Join-Path $PSScriptRoot "mod"
$dist = Join-Path $PSScriptRoot "dist"
if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist | Out-Null }
$out = Join-Path $dist "GengarTheme.mod"
if (Test-Path $out) { Remove-Item $out }

$tar = Join-Path $env:SystemRoot "System32\tar.exe"
if (-not (Test-Path $tar)) { throw "No se encontro $tar" }

$files = Get-ChildItem -Path $root -Recurse -File | Where-Object { $_.Name -notlike ".*" } | ForEach-Object {
    $_.FullName.Substring($root.Length + 1).Replace("\", "/")
}
$list = Join-Path $dist "archivos.txt"
[System.IO.File]::WriteAllLines($list, [string[]]$files, (New-Object System.Text.UTF8Encoding $false))

try {
    & $tar -c --format zip --options zip:compression=store -n -f $out -C $root -T $list
    if ($LASTEXITCODE -ne 0) { throw "tar termino con codigo $LASTEXITCODE" }
}
finally {
    Remove-Item $list -ErrorAction SilentlyContinue
}
Write-Host $out
