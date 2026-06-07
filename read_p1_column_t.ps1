# Read P-1.xls Column T
Write-Host "Starting script..."

try {
    $xls = (Resolve-Path "backend\generated\test_legacy_extract\P-1.xls").Path
    Write-Host "File path: $xls"
    Write-Host "File exists: $(Test-Path $xls)"
    
    $excel = New-Object -ComObject "Excel.Application"
    Write-Host "Excel COM object created"
    
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    
    Write-Host "Opening workbook..."
    # Simplified open: just pass filename
    $wb = $excel.Workbooks.Open($xls)
    Write-Host "Workbook opened successfully"
    
    $ws = $wb.Worksheets(1)
    Write-Host "Worksheet selected"
    
    Write-Host ""
    Write-Host "[INFO] Reading Column T values from P-1.xls"
    Write-Host "=================================================="
    
    for ($r=13; $r -le 19; $r++) {
        $cell = $ws.Range("T$r")
        $val = if ($null -ne $cell.Value) { $cell.Value.ToString() } else { "[empty]" }
        Write-Host "  T$r : $val"
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] Verification complete"
    
    $wb.Close($false)
    Write-Host "Workbook closed"
    
    $excel.Quit()
    Write-Host "Excel quit"
    
} catch {
    Write-Host "ERROR: $_"
    Write-Host $_.Exception.Message
} finally {
    Write-Host "Script completed"
}
