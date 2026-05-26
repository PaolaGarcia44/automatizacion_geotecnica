# Backend - Quick Start 🚀

## 1️⃣ Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

## 2️⃣ Generar Plantillas Excel

```bash
python generate_templates.py
```

Esto crea 3 plantillas de ejemplo en `templates/excel/`:
- `plantilla_categoria_1.xlsx`
- `plantilla_categoria_2.xlsx`
- `plantilla_categoria_3.xlsx`

✅ **IMPORTANTE**: Las plantillas originales **NUNCA** se modifican. Cada proyecto recibe una **copia**.

## 3️⃣ Ejecutar Backend

```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: **http://localhost:8000**

## 4️⃣ Acceder a la Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 5️⃣ Probar Endpoint /generate

### Desde Swagger UI
1. Ir a http://localhost:8000/docs
2. Buscar la sección **POST /api/generate**
3. Click en "Try it out"
4. Completar JSON:

```json
{
  "nombre_proyecto": "Estudio Geotécnico Centro Medellín",
  "municipio": "Medellín",
  "fecha_registro": "2024-05-25",
  "categoria": "1",
  "campo_n": "Suelo tipo C",
  "descripcion": "Análisis preliminar de suelos para cimentación",
  "perforaciones": [
    {
      "numero": 1,
      "profundidad": 6.0,
      "tipo_suelo": "Arena compactada",
      "observaciones": "SPT = 30"
    },
    {
      "numero": 2,
      "profundidad": 8.5,
      "tipo_suelo": "Arcilla",
      "observaciones": "Consistencia media"
    },
    {
      "numero": 3,
      "profundidad": 6.5,
      "tipo_suelo": "Arena",
      "observaciones": "SPT = 25"
    }
  ],
  "imagenes": []
}
```

5. Click en "Execute"
6. Ver respuesta:

```json
{
  "success": true,
  "message": "Documentos generados exitosamente",
  "project_id": "a1b2c3d4",
  "files": [
    "backend/generated/a1b2c3d4_categoria_1.xlsx"
  ],
  "timestamp": "2024-05-25T10:30:45.123456"
}
```

### Desde cURL

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_proyecto": "Mi Proyecto",
    "municipio": "Medellín",
    "fecha_registro": "2024-05-25",
    "categoria": "1",
    "campo_n": "Campo N",
    "descripcion": "Descripción",
    "perforaciones": [
      {
        "numero": 1,
        "profundidad": 6.0,
        "tipo_suelo": "Arena",
        "observaciones": "Test"
      }
    ],
    "imagenes": []
  }'
```

## 6️⃣ Ver Archivos Generados

Los archivos se guardan en: `backend/generated/`

Ejemplo: `a1b2c3d4_categoria_1.xlsx`

## ⚙️ Configuración

### Crear .env (Opcional)

```bash
cp .env.example .env
```

Contenido:
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
DEBUG=True
```

## 📁 Estructura

```
backend/
├── templates/excel/
│   ├── plantilla_categoria_1.xlsx  ← Original (nunca se modifica)
│   ├── plantilla_categoria_2.xlsx
│   └── plantilla_categoria_3.xlsx
├── generated/                       ← Archivos salida
│   ├── a1b2c3d4_categoria_1.xlsx   ← Copia modificada
│   ├── xyz789_categoria_2.xlsx
│   └── ...
├── app/
│   ├── api/documents.py            ← Endpoints
│   ├── services/                   ← Lógica
│   ├── models/schemas.py           ← Tipos
│   └── core/config.py              ← Config
└── main.py                         ← FastAPI app
```

## 🔄 Workflow

```
Frontend (localhost:3000)
    ↓
POST /api/generate
    ↓
DocumentService (valida)
    ↓
ExcelService (copia plantilla)
    ↓
Modifica celdas dinámicas
    ↓
Añade perforaciones
    ↓
Guarda → generated/
    ↓
Retorna ruta + project_id
    ↓
Frontend descarga
```

## 🐛 Troubleshooting

### Error: "Plantilla no encontrada"
```
Solution: Ejecutar python generate_templates.py
```

### Error: "CORS error"
```
Solution: Verificar ALLOWED_ORIGINS en .env
```

### Error: "Port 8000 already in use"
```bash
# Usar otro puerto
python -m uvicorn main:app --port 8001
```

## 📚 Documentación Completa

Ver [README.md](./README.md) para documentación completa.

## 🎯 Próximas Fases

- [ ] Generar Word automático
- [ ] Convertir a PDF
- [ ] Análisis de imágenes con IA
- [ ] Integración Firebase
- [ ] Sistema de caché
- [ ] Descarga de archivos ZIP
- [ ] Webhooks para notificaciones

---

**¡Backend listo! 🚀**
