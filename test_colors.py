#!/usr/bin/env python3
"""
Test script to verify color application in Excel Column I
Uses urllib with form data encoding
"""
import json
import urllib.request
import urllib.parse
import urllib.error

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Test payload - as form data
perforaciones = [
    {
        "profundidad_z": 1.0,
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "Arcilla limosa color café oscuro de consistencia media",
        "tipo_suelo_principal": "Arcilla limosa color café oscuro de consistencia media",
        "color_predominante": "Café"
    },
    {
        "profundidad_z": 2.0,
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "Arena limosa color amarillo café medianamente compacta",
        "tipo_suelo_principal": "Arena limosa color amarillo café medianamente compacta",
        "color_predominante": "Amarillo"
    },
    {
        "profundidad_z": 3.5,
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "Grava limosa de compacidad media",
        "tipo_suelo_principal": "Grava limosa de compacidad media",
        "color_predominante": "Gris claro"
    },
    {
        "profundidad_z": 5.0,
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "Suelo arcilloso personalizado rojo oscuro",
        "tipo_suelo_principal": "Suelo arcilloso personalizado rojo oscuro",
        "color_predominante": "Rojizo"
    }
]

form_data = {
    'proyecto_ubicacion': 'TEST COLORES EXCEL',
    'cliente': 'Cliente Test',
    'fecha_registro': '2026-06-05',
    'pisos': '5',
    'template_ids': json.dumps(['4', '5', '6', '7']),
    'perforaciones': json.dumps(perforaciones),
    'parametros': '[]',
}

print("=" * 80)
print("TESTING COLOR APPLICATION IN EXCEL - Column I")
print("=" * 80)
print("\nForm Data:")
for key, value in form_data.items():
    if key in ['perforaciones', 'template_ids']:
        print(f"  {key}: {value[:100]}... (truncated)")
    else:
        print(f"  {key}: {value}")
print("\n" + "=" * 80)
print("Sending request to backend...")
print("=" * 80 + "\n")

try:
    # Prepare form data
    encoded_data = urllib.parse.urlencode(form_data).encode('utf-8')
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/generate",
        data=encoded_data,
        method='POST'
    )
    
    # Send request
    with urllib.request.urlopen(req, timeout=120) as response:
        response_data = json.loads(response.read().decode('utf-8'))
        print(f"✓ Response Status: {response.status}")
        print(f"✓ Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response_data.get("success"):
            print("\n✅ SUCCESS! Documents generated.")
            print(f"   Project ID: {response_data.get('project_id')}")
            print(f"   Download URL: {response_data.get('download_url')}")
            print("\n📝 Next steps:")
            print("   1. Download the ZIP file from the provided URL")
            print("   2. Extract and open P-1.xls (or any P-*.xls file)")
            print("   3. Look at Column I ('Descripción Macroscópica y proporción')")
            print("   4. Verify that cells have:")
            print("      - Soil type descriptions (from 'tipo_suelo_principal')")
            print("      - Background colors (Café, Amarillo, Gris claro, Rojizo)")
            print("      - Appropriate text color (black or white for contrast)")
        else:
            print(f"\n❌ Error: {response_data.get('message')}")
            
except urllib.error.HTTPError as e:
    error_body = e.read().decode('utf-8')
    print(f"❌ HTTP Error {e.code}: {error_body}")
except urllib.error.URLError as e:
    print(f"❌ URL Error: {e.reason}")
except json.JSONDecodeError:
    print(f"❌ Invalid JSON response")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
