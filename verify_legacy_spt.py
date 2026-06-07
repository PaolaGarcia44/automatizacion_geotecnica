#!/usr/bin/env python3
"""Convert .xls to .xlsx and read Column T"""

import sys
from pathlib import Path
import subprocess

xls_path = Path("backend/generated/test_legacy_extract/P-1.xls")

if not xls_path.exists():
    print(f"ERROR: File not found: {xls_path}")
    sys.exit(1)

print(f"Reading {xls_path.name} using Excel COM...")

# PowerShell script to read using Excel COM
ps_script = f"""
$xls = '{xls_path.resolve()}'

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

$workbook = $excel.Workbooks.Open($xls, [Type]::Missing, [Type]::Missing, [Type]::Missing, [Type]::Missing, [Type]::Missing, [Type]::Missing, 4)

Write-Host "[INFO] Successfully opened .xls file"
Write-Host "[INFO] Reading Column T values (SPT Data):"
Write-Host "================================================================"

$sheet = $workbook.Worksheets(1)

for ($row = 13; $row -le 19; $row++) {{
    $cell_ref = "T$row"
    $value = $sheet.Range($cell_ref).Value
    Write-Host "  $cell_ref : $value"
}}

Write-Host ""
Write-Host "[SUCCESS] Column T verification complete"

$workbook.Close($false)
$excel.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
"""

# Save and run PowerShell script
ps_file = Path("temp_convert.ps1")
ps_file.write_text(ps_script)

try:
    result = subprocess.run(
        ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)],
        capture_output=True,
        text=True,
        timeout=30
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
finally:
    ps_file.unlink(missing_ok=True)
