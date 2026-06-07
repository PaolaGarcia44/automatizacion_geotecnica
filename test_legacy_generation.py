#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json

url = "http://127.0.0.1:8000/api/generate"

# Prepare form data
data = {
    "template_ids": '["12"]',  # P-1.xls
    "proyecto_ubicacion": "Test Legacy Template P-1",
    "cliente": "Test Client",
    "fecha_registro": "2026-06-06",
    "pisos": "2",
    "perforaciones": "[]",
    "parametros": "[]"
}

# URL encode
form_data = urllib.parse.urlencode(data).encode('utf-8')

try:
    request = urllib.request.Request(url, data=form_data, method='POST')
    with urllib.request.urlopen(request) as response:
        result = response.read().decode('utf-8')
        print("Status:", response.status)
        print("Response:", result)
except Exception as e:
    print(f"Error: {e}")
