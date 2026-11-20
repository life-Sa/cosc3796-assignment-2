$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv/Scripts/python.exe')) { py -3 -m venv .venv }
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
if (!(Test-Path 'vendor/PythonSuperMario/main.py')) {
    git clone https://github.com/marblexu/PythonSuperMario.git vendor/PythonSuperMario
    if ($LASTEXITCODE -ne 0) { throw 'Game download failed' }
}
git -C vendor/PythonSuperMario checkout f34087e4cc47f6cc70b46ced758b1070e64c4dc2
if ($LASTEXITCODE -ne 0) { throw 'Game revision unavailable' }
