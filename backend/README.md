# Backend - AutoGeo

Backend FastAPI para generación automatizada de documentos geotécnicos.

## Estructura

```
backend/
├── app/
│   ├── api/              # Endpoints REST
│   ├── services/         # Lógica de negocio
│   ├── utils/            # Utilidades (field_mapping, etc)
│   ├── models/           # Schemas Pydantic
│   └── core/             # Configuración
├── templates/            # Plantillas originales (NUNCA se modifican)
│   ├── excel/            # Plantillas Excel
│   └── word/             # Plantillas Word
├── generated/            # Archivos generados (cópias de trabajo)
├── main.py               # FastAPI app
└── requirements.txt      # Dependencias
```

## Características principales

### 1. Manejo de plantillas
- Las plantillas originales **NUNCA se modifican directamente**
- Se crea una **copia** para cada proyecto
- Se trabaja sobre la copia, conservando:
  - Fórmulas originales
  - Estilos y formatos
  - Diseño y estructura
  - Referencias cruzadas

### 2. Field Mapping Centralizado
- Cada categoría tiene su propio mapeo de campos
- `app/utils/field_mapping.py` controla:
  - Qué celdas contienen qué datos
  - Ubicación de tablas de perforaciones
  - Campos dinámicos vs estáticos

### 3. Categorías de proyectos

**Categoría 1** (Hasta 3 pisos)
- Carga: 500 kN
- Mínimo 3 perforaciones
- Profundidad: 6m

**Categoría 2** (Hasta 10 pisos)
- Carga: 4000 kN
- 4 perforaciones
- Profundidad: 15m

**Categoría 3** (Más de 10 pisos)
- Carga: >4000 kN
- 4 perforaciones
- Profundidad: 25m

## Configuración

### Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### Variables de entorno

Crear `.env` en la carpeta backend:

```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
DEBUG=True
```

## Ejecución

### Desarrollo

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
cd backend
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## API Endpoints

### POST /api/generate
Genera documentos Excel para un proyecto

**Request:**
```json
{
  "nombre_proyecto": "Estudio Geotécnico Centro",
  "municipio": "Medellín",
  "fecha_registro": "2024-05-25",
  "categoria": "1",
  "campo_n": "Suelo tipo C",
  "descripcion": "Análisis de suelos",
  "perforaciones": [
    {
      "numero": 1,
      "profundidad": 6.0,
      "tipo_suelo": "Arena",
      "observaciones": "Compactada"
    }
  ],
  "imagenes": []
}
```

**Response:**
```json
{
  "success": true,
  "message": "Documentos generados exitosamente",
  "project_id": "a1b2c3d4",
  "files": ["/ruta/al/archivo.xlsx"],
  "timestamp": "2024-05-25T10:30:00"
}
```

### GET /api/templates/status
Verifica disponibilidad de plantillas

### GET /api/health
Health check del servicio

## Servicios

### ExcelService (`app/services/excel_service.py`)
- Copia plantillas
- Modifica celdas dinámicas
- Gestiona perforaciones
- Preserva fórmulas y estilos

### DocumentService (`app/services/document_service.py`)
- Valida categorías
- Verifica requisitos
- Orquesta generación completa

### TemplateService (`app/services/template_service.py`)
- Gestiona búsqueda de plantillas
- Retorna información de templates

## Próximas implementaciones

- [ ] Generación de Word automático
- [ ] Conversión a PDF
- [ ] Integración con IA (análisis de imágenes)
- [ ] Integración con Firebase para almacenamiento
- [ ] Sistema de caché
- [ ] Reportes y estadísticas
- [ ] API de descarga de archivos
- [ ] WebSocket para progreso de generación

## Buenas prácticas aplicadas

✅ Separación de responsabilidades (servicios, utils, api)
✅ Configuración centralizada
✅ Logging completo
✅ Validación de entrada
✅ Manejo de errores robusto
✅ Documentación de código
✅ Type hints
✅ CORS configurado
✅ Estructuras modulares y reutilizables
