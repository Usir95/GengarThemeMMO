$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Join-Path $PSScriptRoot "mod"
$dist = Join-Path $PSScriptRoot "dist"
if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist | Out-Null }
$out = Join-Path $dist "GengarTheme.mod"
if (Test-Path $out) { Remove-Item $out }

$zip = [System.IO.Compression.ZipFile]::Open($out, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    Get-ChildItem -Path $root -Recurse -File | Where-Object { $_.Name -notlike ".*" } | ForEach-Object {
        $entry = $_.FullName.Substring($root.Length + 1).Replace("\", "/")
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $entry, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
}
finally {
    $zip.Dispose()
}
Write-Host $out
