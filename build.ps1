# build.ps1 — Genera el instalador de distribucion de AutoGeo
#
# Uso:
#   .\build.ps1               → build completo (frontend + backend + instalador)
#   .\build.ps1 -SkipBackend  → reutiliza backend/dist/ existente
#   .\build.ps1 -SkipFrontend → reutiliza out/ existente
#
# Resultado: dist_electron\AutoGeo Setup X.X.X.exe
#
# NOTA sobre plantillas Word (~11 GB):
#   NO se incluyen en el instalador base (lo harian demasiado grande).
#   Tras instalar AutoGeo, copiarlas a:
#   %LOCALAPPDATA%\Programs\AutoGeo\resources\backend\templates\word\
#   o ejecutar: instalar_plantillas.bat

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Venv = Join-Path $Root ".venv\Scripts"
$PyInstaller = Join-Path $Venv "pyinstaller.exe"

Set-Location $Root

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   AutoGeo - Build para distribucion" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ─── Verificar herramientas ──────────────────────────────────────────────────
Write-Host "Verificando herramientas..." -ForegroundColor Gray

if (-not (Test-Path (Join-Path $Venv "python.exe"))) {
    Write-Host "ERROR: No se encontro el entorno virtual en .venv\" -ForegroundColor Red
    Write-Host "Crea el venv con: python -m venv .venv" -ForegroundColor Yellow; exit 1
}
if (-not (Test-Path $PyInstaller)) {
    Write-Host "  Instalando PyInstaller en .venv..." -ForegroundColor Yellow
    & "$Venv\pip.exe" install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: No se pudo instalar PyInstaller" -ForegroundColor Red; exit 1 }
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js no encontrado." -ForegroundColor Red; exit 1
}

$piVer = & $PyInstaller --version 2>&1
Write-Host "  OK: Node $(node --version), PyInstaller $piVer" -ForegroundColor Green

# ─── PASO 1: Build Frontend ──────────────────────────────────────────────────
if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "[1/3] Construyendo frontend Next.js -> out/ ..." -ForegroundColor Yellow

    if (Test-Path "out")   { Remove-Item "out"   -Recurse -Force }
    if (Test-Path ".next") { Remove-Item ".next" -Recurse -Force }

    npm run build
    if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: next build fallo" -ForegroundColor Red; exit 1 }

    $nFiles = (Get-ChildItem "out" -Recurse -File).Count
    Write-Host "      OK — out/ generado ($nFiles archivos)" -ForegroundColor Green
} else {
    if (-not (Test-Path "out\index.html")) {
        Write-Host "ERROR: out\index.html no existe. Ejecuta sin -SkipFrontend." -ForegroundColor Red; exit 1
    }
    Write-Host "[1/3] Frontend: usando out/ existente" -ForegroundColor Gray
}

# ─── PASO 2: Build Backend (PyInstaller) ────────────────────────────────────
if (-not $SkipBackend) {
    Write-Host ""
    Write-Host "[2/3] Empaquetando backend con PyInstaller..." -ForegroundColor Yellow

    Set-Location "$Root\backend"

    if (Test-Path "dist\autogeo_backend") { Remove-Item "dist\autogeo_backend" -Recurse -Force }
    if (Test-Path "build\autogeo_backend") { Remove-Item "build\autogeo_backend" -Recurse -Force }

    & $PyInstaller autogeo.spec --noconfirm
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: PyInstaller fallo. Revisa el log anterior." -ForegroundColor Red
        Set-Location $Root; exit 1
    }

    if (-not (Test-Path "dist\autogeo_backend\autogeo_backend.exe")) {
        Write-Host "ERROR: No se genero autogeo_backend.exe" -ForegroundColor Red
        Set-Location $Root; exit 1
    }

    # Copiar plantillas Excel al raiz del dist
    # (PyInstaller 6 pone los datas en _internal/, pero config.py busca en exe.parent)
    $srcExcel = "templates\excel"
    $dstExcel = "dist\autogeo_backend\templates\excel"
    if (Test-Path $srcExcel) {
        Copy-Item $srcExcel $dstExcel -Recurse -Force
        Write-Host "      Plantillas Excel copiadas a templates/excel/" -ForegroundColor Gray
    }

    # Crear directorio de plantillas Word (vacio — se copian con instalar_plantillas.bat)
    $wordDir = "dist\autogeo_backend\templates\word"
    if (-not (Test-Path $wordDir)) { New-Item -ItemType Directory $wordDir -Force | Out-Null }

    $exeMB = [math]::Round((Get-ChildItem "dist\autogeo_backend" -Recurse -File |
        Measure-Object -Property Length -Sum).Sum / 1MB, 0)
    Write-Host "      OK — backend/dist/autogeo_backend/ ($exeMB MB)" -ForegroundColor Green

    Set-Location $Root
} else {
    if (-not (Test-Path "backend\dist\autogeo_backend\autogeo_backend.exe")) {
        Write-Host "ERROR: backend\dist\autogeo_backend\autogeo_backend.exe no existe." -ForegroundColor Red; exit 1
    }
    Write-Host "[2/3] Backend: usando dist/ existente" -ForegroundColor Gray
}

# ─── PASO 3: Generar instalador ──────────────────────────────────────────────
Write-Host ""
Write-Host "[3/3] Generando instalador Windows con electron-builder..." -ForegroundColor Yellow
Write-Host "      (Puede tardar varios minutos)" -ForegroundColor Gray

if (Test-Path "dist_electron") { Remove-Item "dist_electron" -Recurse -Force }

npx electron-builder --win --x64
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: electron-builder fallo" -ForegroundColor Red; exit 1 }

# ─── Resultado ───────────────────────────────────────────────────────────────
$installer = Get-ChildItem "dist_electron\*.exe" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notlike "*unpacked*" } | Select-Object -First 1

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "   BUILD COMPLETADO" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

if ($installer) {
    $sizeMB = [math]::Round($installer.Length / 1MB, 0)
    Write-Host ""
    Write-Host "  Instalador: $($installer.Name)" -ForegroundColor White
    Write-Host "  Ruta:       $($installer.FullName)" -ForegroundColor Cyan
    Write-Host "  Tamano:     $sizeMB MB" -ForegroundColor White
    Write-Host ""
    Write-Host "  SIGUIENTE PASO — Plantillas Word:" -ForegroundColor Yellow
    Write-Host "  1. Instala AutoGeo ejecutando el .exe anterior" -ForegroundColor White
    Write-Host "  2. Copia las plantillas Word con: .\instalar_plantillas.bat" -ForegroundColor White
    Write-Host "     o manualmente a:" -ForegroundColor Gray
    Write-Host "     %LOCALAPPDATA%\Programs\AutoGeo\resources\backend\templates\word\" -ForegroundColor Gray
}
