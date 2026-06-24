# dev.ps1 — Inicia AutoGeo en modo desarrollo
#
# Uso:
#   .\dev.ps1             -> modo escritorio: backend + Electron (archivos estaticos de out/)
#   .\dev.ps1 -Browser    -> modo navegador: backend + Next.js dev server con hot-reload
#                           Abre http://localhost:3000 — no requiere npm run build

param(
    [switch]$Browser
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
Set-Location $Root

# ─── MODO NAVEGADOR (pruebas rapidas sin reempaquetar) ───────────────────────
if ($Browser) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "   AutoGeo - Modo navegador (dev)" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Gray
    Write-Host "  Frontend: http://localhost:3000  <- abre esto en el navegador" -ForegroundColor Green
    Write-Host ""
    Write-Host "Los cambios en el codigo se reflejan automaticamente." -ForegroundColor Yellow
    Write-Host "Presiona Ctrl+C para detener todo." -ForegroundColor Yellow
    Write-Host ""

    # Iniciar backend en segundo plano
    $backendDir = Join-Path $Root "backend"
    $backendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    } -ArgumentList $backendDir

    Write-Host "Backend iniciando..." -ForegroundColor Gray

    $deadline = (Get-Date).AddSeconds(30)
    $backendReady = $false
    while ((Get-Date) -lt $deadline) {
        try {
            $null = Invoke-WebRequest http://127.0.0.1:8000/health -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
            $backendReady = $true
            break
        } catch { Start-Sleep -Milliseconds 500 }
    }

    if (-not $backendReady) {
        Write-Host "ERROR: El backend no respondio en 30 segundos." -ForegroundColor Red
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        exit 1
    }

    Write-Host "Backend listo." -ForegroundColor Green
    Write-Host ""

    # Abrir el navegador automaticamente al cabo de 3 segundos (Next.js tarda en arrancar)
    Start-Job -ScriptBlock {
        Start-Sleep 4
        Start-Process "http://localhost:3000/generate/"
    } | Out-Null

    # Ejecutar Next.js dev server en primer plano (Ctrl+C lo detiene todo)
    try {
        npm run dev
    } finally {
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -Force -ErrorAction SilentlyContinue
    }

    exit 0
}

# ─── MODO ESCRITORIO (Electron con archivos estaticos) ───────────────────────
Write-Host ""
Write-Host "Iniciando AutoGeo (modo escritorio)..." -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "out\index.html")) {
    Write-Host "Construyendo frontend (primera vez o cambios pendientes)..." -ForegroundColor Yellow
    npm run build
    if ($LASTEXITCODE -ne 0) { Write-Host "Error al construir el frontend." -ForegroundColor Red; exit 1 }
    Write-Host "Frontend listo." -ForegroundColor Green
}

Write-Host "  - Frontend: archivos estaticos en out/" -ForegroundColor Gray
Write-Host "  - Backend:  FastAPI en http://localhost:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "Presiona Ctrl+C para detener." -ForegroundColor Yellow
Write-Host ""

$backendDir = Join-Path $Root "backend"
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
} -ArgumentList $backendDir

Write-Host "Backend iniciando..." -ForegroundColor Gray

$deadline = (Get-Date).AddSeconds(30)
$backendReady = $false
while ((Get-Date) -lt $deadline) {
    try {
        $null = Invoke-WebRequest http://127.0.0.1:8000/health -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
        $backendReady = $true
        break
    } catch { Start-Sleep -Milliseconds 500 }
}

if (-not $backendReady) {
    Write-Host "El backend no respondio en 30 segundos. Verifica que Python este instalado." -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend listo en http://localhost:8000" -ForegroundColor Green

node electron/launch.js

Stop-Job $backendJob -ErrorAction SilentlyContinue
Remove-Job $backendJob -ErrorAction SilentlyContinue
