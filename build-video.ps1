param([string]$PythonPath = '')
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if ($PythonPath) { $python = (Resolve-Path $PythonPath).Path }
if (!(Test-Path $python)) { throw 'Follow README setup first.' }
& $python -m PyInstaller --noconfirm --workpath video-build --distpath video-dist --onedir --name MarioConsentDemo --paths vendor/PythonSuperMario --collect-submodules source --add-data 'vendor/PythonSuperMario/resources:vendor/PythonSuperMario/resources' --add-data 'vendor/PythonSuperMario/source/data:vendor/PythonSuperMario/source/data' launch_mario.py
if ($LASTEXITCODE -ne 0) { throw 'Mario build failed' }
& $python -m PyInstaller --noconfirm --workpath video-build --distpath video-dist --onedir --name SharingCompanion client.py
if ($LASTEXITCODE -ne 0) { throw 'Companion build failed' }
& $python -m PyInstaller --noconfirm --workpath video-build --distpath video-dist --onedir --name ScreenshotReceiver receiver.py
if ($LASTEXITCODE -ne 0) { throw 'Receiver build failed' }
Write-Host 'Keep all three app folders as siblings inside dist. Receiver and companion share dist/demo-data. Start receiver first.'

