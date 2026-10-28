# Build a single-file Windows EXE on a Windows computer with Python 3.12+.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "EpisodeFlow" --icon "assets/episodeflow.ico" --add-data "assets;assets" --paths "src" "src/main.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Build complete: $root\dist\EpisodeFlow.exe"
