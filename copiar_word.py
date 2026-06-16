"""
Copia desde E:\\EDWIN todos los Word (.doc/.docx) cuyo nombre
contenga "INFORME", hacia backend\\templates\\word.
Los originales NO se borran.
"""

import subprocess
import tempfile
import os
from pathlib import Path

ORIGEN  = r"E:\EDWIN"
DESTINO = str(Path(__file__).parent / "backend" / "templates" / "word")


def main():
    print(f"Origen : {ORIGEN}")
    print(f"Destino: {DESTINO}")
    print("Buscando archivos INFORME... (puede tardar varios minutos)\n")

    # Nota: en PowerShell 5.1, -Include con -Recurse falla silenciosamente.
    # Se usa Where-Object para filtrar por extension e "INFORME" en el nombre.
    ps_script = f"""
$origen  = '{ORIGEN}'
$destino = '{DESTINO}'

if (-not (Test-Path -LiteralPath $origen)) {{
    Write-Host "[ERROR] Origen no encontrado: $origen"
    exit 1
}}

New-Item -ItemType Directory -Force -Path $destino | Out-Null

$archivos = Get-ChildItem -LiteralPath $origen -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {{
        ($_.Extension -eq '.doc' -or $_.Extension -eq '.docx') -and
        $_.Name -like '*INFORME*'
    }}

if (-not $archivos -or $archivos.Count -eq 0) {{
    Write-Host "No se encontraron archivos INFORME Word en $origen"
    exit 0
}}

Write-Host "Encontrados: $($archivos.Count) archivo(s) INFORME"
$copiados = 0
$errores  = [System.Collections.Generic.List[string]]::new()

foreach ($f in $archivos) {{
    $nombre = $f.Name
    $dst    = Join-Path $destino $nombre

    if (Test-Path -LiteralPath $dst) {{
        $base = [System.IO.Path]::GetFileNameWithoutExtension($nombre)
        $ext  = [System.IO.Path]::GetExtension($nombre)
        $i    = 1
        do {{
            $nombre = "${{base}}_${{i}}${{ext}}"
            $dst    = Join-Path $destino $nombre
            $i++
        }} while (Test-Path -LiteralPath $dst)
    }}

    try {{
        Copy-Item -LiteralPath $f.FullName -Destination $dst -Force -ErrorAction Stop
        Write-Host "  OK   $nombre"
        $copiados++
    }} catch {{
        Write-Host "  SKIP $($f.Name)"
        $errores.Add($f.FullName)
    }}
}}

Write-Host ""
Write-Host "=============================="
Write-Host "Copiados   : $copiados"
Write-Host "No copiados: $($errores.Count)"
Write-Host "Destino    : $destino"

if ($errores.Count -gt 0) {{
    $log = Join-Path $destino "_archivos_no_copiados.txt"
    $errores | Out-File -FilePath $log -Encoding UTF8
    Write-Host "Lista de no copiados: $log"
    Write-Host "Causa probable: archivos OneDrive sin descargar (icono nube en explorador)."
    Write-Host "Solucion: seleccionalos, clic derecho > 'Mantener en este dispositivo', luego re-ejecutar."
}}
"""

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ps1", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(ps_script)
        tmp_path = tmp.name

    try:
        subprocess.run(
            [
                "powershell",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-File", tmp_path,
            ],
            timeout=3600,
        )
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
