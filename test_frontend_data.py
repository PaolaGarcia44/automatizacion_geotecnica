#!/usr/bin/env python3
"""
Test script using the exact data from frontend screenshot
"""
import json
import urllib.request
import urllib.parse
import urllib.error

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000"

# Test payload - using exact data from frontend screenshot
perforaciones = [
    {
        "profundidad_z": 0.0,  # First layer, no depth specified in image
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "suelo de prueba",
        "tipo_suelo_principal": "suelo de prueba",
        "color_predominante": "Café oscuro"
    },
    {
        "profundidad_z": 1.45,
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "Suelo expansivo de color rojo",
        "tipo_suelo_principal": "Suelo expansivo de color rojo",
        "color_predominante": "Rojizo"
    },
    {
        "profundidad_z": 2.45,
        "gamma": None,
        "n_campo_spt": 0,
        "cohesion_c": None,
        "descripcion_suelo": "Arcilla arenosa color amarillo café",
        "tipo_suelo_principal": "Arcilla arenosa color amarillo café",
        "color_predominante": "Amarillo oscuro"
    }
]

form_data = {
    'proyecto_ubicacion': 'TEST FRONTEND DATA',
    'cliente': 'Cliente Test Frontend',
    'fecha_registro': '2026-06-05',
    'pisos': '3',
    'template_ids': json.dumps(['4', '5', '6']),  # P-1, P-2, P-3
    'perforaciones': json.dumps(perforaciones),
    'parametros': '[]',
}

print("=" * 80)
print("TESTING WITH FRONTEND SCREENSHOT DATA")
print("=" * 80)
print("\nPerforaciones being sent:")
for i, perf in enumerate(perforaciones, 1):
    print(f"\n  Capa {i}:")
    print(f"    Profundidad: {perf['profundidad_z']} m")
    print(f"    Tipo de suelo: {perf['tipo_suelo_principal']}")
    print(f"    Color: {perf['color_predominante']}")

print("\n" + "=" * 80)
print("Form Data Summary:")
print(f"  Proyecto: {form_data['proyecto_ubicacion']}")
print(f"  Cliente: {form_data['cliente']}")
print(f"  Pisos: {form_data['pisos']}")
print(f"  Templates: {form_data['template_ids']}")
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
        print(f"[OK] Response Status: {response.status}")
        print(f"\n[OK] Response Data:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response_data.get("success"):
            print("\n[SUCCESS] SUCCESS! Documents generated.")
            print(f"   Project ID: {response_data.get('project_id')}")
            print(f"   Download URL: {response_data.get('download_url')}")
            print("\n[INFO] Generated files should now contain Column I with:")
            print("   Row 8: 'suelo de prueba' with Cafe oscuro color")
            print("   Row 10: 'Suelo expansivo de color rojo' with Rojizo color")
            print("   Row 12: 'Arcilla arenosa color amarillo cafe' with Amarillo oscuro color")
        else:
            print(f"\n[ERROR] Error: {response_data.get('error', 'Unknown error')}")
            
except urllib.error.HTTPError as e:
    print(f"[ERROR] HTTP Error: {e.code}")
    print(f"   Response: {e.read().decode('utf-8')}")
except urllib.error.URLError as e:
    print(f"[ERROR] URL Error: {e.reason}")
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
