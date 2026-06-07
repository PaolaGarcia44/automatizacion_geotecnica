Dim excel, wb, ws, r, val

Set excel = CreateObject("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

Dim xls_path
xls_path = CreateObject("WScript.Shell").CurrentDirectory & "\backend\generated\test_legacy_extract\P-2.xls"

On Error Resume Next

Set wb = excel.Workbooks.Open(xls_path)

If Err.Number <> 0 Then
    WScript.Echo "ERROR opening workbook: " & Err.Description
    excel.Quit
    WScript.Quit 1
End If

Set ws = wb.Worksheets(1)

WScript.Echo "[INFO] Reading Column T values from P-2.xls (template 2 has 16 SPT values)"
WScript.Echo "========================================================================="

For r = 13 To 28
    val = ws.Range("T" & r).Value
    If IsNull(val) Or val = "" Then
        WScript.Echo "  T" & r & " : [empty]"
    Else
        WScript.Echo "  T" & r & " : " & val
    End If
Next

WScript.Echo ""
WScript.Echo "[SUCCESS] P-2.xls verification complete"

wb.Close False
excel.Quit
