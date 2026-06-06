#!/usr/bin/env python3
"""
Script to inspect Column I of generated P-1.xls file
"""
import sys
from pathlib import Path

# Path to the extracted file
p1_file = Path(r"C:\Users\Paola\OneDrive - Tecnologico de Antioquia Institucion Universitaria\Escritorio\Automatización geotecnica\automatizacion_geotecnica\backend\generated\TEST_FRONTEND_EXTRAIDO\P-1.xls")

if not p1_file.exists():
    print(f"[ERROR] File not found: {p1_file}")
    sys.exit(1)

print(f"[INFO] Opening file: {p1_file}")

try:
    import pythoncom
    import win32com.client
except ImportError as e:
    print(f"[ERROR] pywin32 not available: {e}")
    sys.exit(1)

pythoncom.CoInitialize()
excel_app = None
workbook = None

try:
    excel_app = win32com.client.DispatchEx("Excel.Application")
    excel_app.Visible = False
    excel_app.DisplayAlerts = False
    
    workbook = excel_app.Workbooks.Open(str(p1_file))
    worksheet = workbook.Worksheets(1)
    
    print("\n" + "=" * 80)
    print("INSPECTING COLUMN I (Descripción Macroscópica y proporción)")
    print("=" * 80 + "\n")
    
    # Check rows 8, 10, 12, 14 (data rows for up to 4 layers)
    rows_to_check = [8, 10, 12, 14]
    
    for row in rows_to_check:
        cell_ref = f"I{row}"
        cell = worksheet.Range(cell_ref)
        value = cell.Value
        color = cell.Interior.Color
        
        print(f"Row {row} (Cell {cell_ref}):")
        print(f"  Value: {value if value else '[EMPTY]'}")
        if value:
            # Try to read the color
            try:
                color_hex = f"{color:06X}"
                print(f"  Color (RGB int): {color}")
                print(f"  Color (Hex): #{color_hex}")
            except:
                print(f"  Color (RGB int): {color if color else 'None'}")
        else:
            print(f"  Color: [N/A - Cell is empty]")
        print()
    
    print("=" * 80)
    print("COMPARISON WITH EXPECTED DATA")
    print("=" * 80)
    print("\nExpected data sent:")
    print("  Row 8: 'suelo de prueba' with Cafe oscuro color")
    print("  Row 10: 'Suelo expansivo de color rojo' with Rojizo color")
    print("  Row 12: 'Arcilla arenosa color amarillo cafe' with Amarillo oscuro color")
    print("  Row 14: [empty - only 3 layers]")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    # Check what we actually got
    i8_value = worksheet.Range("I8").Value
    i10_value = worksheet.Range("I10").Value
    i12_value = worksheet.Range("I12").Value
    
    if i8_value == "suelo de prueba" or i10_value == "Suelo expansivo de color rojo":
        print("\n[SUCCESS] Data appears to be written correctly to Column I!")
        print("The frontend data is being applied to the Excel file.")
    else:
        print("\n[ERROR] Data does NOT appear to be written to Column I!")
        print("Column I still contains template data or is empty.")
        print(f"\n  I8 contains: {i8_value}")
        print(f"  I10 contains: {i10_value}")
        print(f"  I12 contains: {i12_value}")

finally:
    if workbook is not None:
        workbook.Close(SaveChanges=False)
    if excel_app is not None:
        excel_app.Quit()
    pythoncom.CoUninitialize()
