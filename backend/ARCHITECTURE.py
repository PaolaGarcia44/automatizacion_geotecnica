"""
ARQUITECTURA BACKEND - VISIÓN GENERAL

AutoGeo Backend - Sistema de Generación Automatizada de Documentos Geotécnicos
"""

ARQUITECTURA = """
╔════════════════════════════════════════════════════════════════════════════╗
║                     AUTOMATIZACIÓN GEOTÉCNICA BACKEND                      ║
║                           Architecture Overview                            ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js - localhost:3000)                                       │
│ ├─ /generate → form con datos proyecto                                    │
│ ├─ /history → tabla de proyectos                                          │
│ └─ /ai → chat con asistente                                               │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                   POST /api/generate (JSON)
                    {nombre, municipio, fecha,
                     categoría, perforaciones}
                               │
                               ↓
┌──────────────────────────────────────────────────────────────────────────┐
│ FASTAPI BACKEND (localhost:8000)                                          │
│                                                                            │
│ ┌─ API Routes (app/api/documents.py) ────────────────────────────────┐   │
│ │                                                                      │   │
│ │  POST /api/generate                                                 │   │
│ │  │  ↓ RequestValidation (Pydantic)                                  │   │
│ │  └──→ DocumentService.generate_documents()                          │   │
│ │       │                                                             │   │
│ │       ├─ Validar categoría                                         │   │
│ │       ├─ Verificar requisitos                                      │   │
│ │       ├─ Generar project_id único                                  │   │
│ │       └─ ExcelService.generate_excel()                             │   │
│ │           │                                                         │   │
│ │           ├─ Copiar plantilla → /generated/                        │   │
│ │           ├─ Abrir copia con openpyxl                              │   │
│ │           ├─ FieldMapping obtener mapeo                            │   │
│ │           ├─ Modificar celdas dinámicas                            │   │
│ │           ├─ Añadir perforaciones a tabla                          │   │
│ │           └─ Guardar archivo                                       │   │
│ │                                                                      │   │
│ │       └─ Retornar respuesta                                         │   │
│ │           {success, project_id, files, timestamp}                   │   │
│ │                                                                      │   │
│ │  GET /api/templates/status                                          │   │
│ │  GET /api/health                                                    │   │
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│ ┌─ Services Layer ──────────────────────────────────────────────────┐   │
│ │                                                                    │   │
│ │ DocumentService (document_service.py)                             │   │
│ │  └─ generate_documents()                                          │   │
│ │  └─ validate_categoria()                                          │   │
│ │  └─ validate_category_requirements()                              │   │
│ │                                                                    │   │
│ │ ExcelService (excel_service.py)                                   │   │
│ │  └─ generate_excel()                                              │   │
│ │  └─ _copy_template()         [KEY: No modifica original]          │   │
│ │  └─ _set_cell_value()                                             │   │
│ │  └─ _add_perforaciones()                                          │   │
│ │  └─ verify_templates()                                            │   │
│ │                                                                    │   │
│ │ TemplateService (template_service.py)                             │   │
│ │  └─ get_available_excel_templates()                               │   │
│ │  └─ get_template_info()                                           │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│ ┌─ Utils Layer ─────────────────────────────────────────────────────┐   │
│ │                                                                    │   │
│ │ field_mapping.py [CENTRALIZADO]                                   │   │
│ │  ├─ FIELD_MAPPING_CATEGORIA_1                                     │   │
│ │  ├─ FIELD_MAPPING_CATEGORIA_2                                     │   │
│ │  ├─ FIELD_MAPPING_CATEGORIA_3                                     │   │
│ │  ├─ PERFORACION_MAPPING_CATEGORIA_1                               │   │
│ │  ├─ PERFORACION_MAPPING_CATEGORIA_2                               │   │
│ │  ├─ PERFORACION_MAPPING_CATEGORIA_3                               │   │
│ │  └─ get_field_mapping(categoria)                                  │   │
│ │  └─ get_perforacion_mapping(categoria)                            │   │
│ │                                                                    │   │
│ │ Ejemplo:                                                           │   │
│ │  "nombre_proyecto": ["B5", "D10", "F2"]    ← Celdas a modificar  │   │
│ │  "municipio": ["C7", "E12"]                ← Puede estar en varias│   │
│ │  "tabla_inicio_row": 27                    ← Dónde va la tabla    │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│ ┌─ Models Layer ────────────────────────────────────────────────────┐   │
│ │                                                                    │   │
│ │ schemas.py (Pydantic)                                             │   │
│ │  ├─ PerforacionData                                               │   │
│ │  ├─ DocumentGenerationRequest                                     │   │
│ │  ├─ DocumentGenerationResponse                                    │   │
│ │  └─ CategoryRule                                                  │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│ ┌─ Core Layer ──────────────────────────────────────────────────────┐   │
│ │                                                                    │   │
│ │ config.py (Settings)                                              │   │
│ │  ├─ BASE_DIR                                                      │   │
│ │  ├─ TEMPLATES_DIR                                                 │   │
│ │  ├─ GENERATED_DIR                                                 │   │
│ │  ├─ ALLOWED_ORIGINS (CORS)                                        │   │
│ │  └─ TEMPLATES_CONFIG                                              │   │
│ └────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│ main.py (FastAPI)                                                    │
│  ├─ app = FastAPI()                                                  │
│ │  ├─ Add CORSMiddleware                                             │
│ │  ├─ Include routers                                                │
│ │  ├─ Startup/Shutdown events                                        │
│ │  └─ Exception handlers                                             │
│ │                                                                    │
│ │ uvicorn.run(                                                       │
│ │     "main:app",                                                    │
│ │     host="0.0.0.0", port=8000,                                     │
│ │     reload=DEBUG                                                   │
│ │ )                                                                  │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ↓                      ↓                      ↓
  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │ PLANTILLAS   │      │ GENERADOS    │      │ CONFIGURACIÓN│
  │ (ORIGINALES) │      │ (COPIAS)     │      │              │
  ├──────────────┤      ├──────────────┤      ├──────────────┤
  │ templates/   │      │ generated/   │      │ .env         │
  │  excel/      │      │              │      │              │
  │   ├─ P1.xlsx │      │ ├─ abc123_1  │      │ requirements │
  │   ├─ P2.xlsx │      │ ├─ def456_2  │      │ .txt         │
  │   └─ P3.xlsx │      │ └─ ghi789_3  │      │              │
  │              │      │              │      │ .gitignore   │
  │ [NUNCA MOD]  │      │ [SALIDA]     │      │              │
  └──────────────┘      └──────────────┘      └──────────────┘


╔════════════════════════════════════════════════════════════════════════════╗
║                           FLUJO DE DATOS DETALLADO                         ║
╚════════════════════════════════════════════════════════════════════════════╝

1. FRONTEND ENVÍA SOLICITUD
   ────────────────────────
   {
     "nombre_proyecto": "Estudio Geotécnico Centro",
     "municipio": "Medellín",
     "fecha_registro": "2024-05-25",
     "categoria": "1",
     "campo_n": "Suelo tipo C",
     "descripcion": "Análisis preliminar",
     "perforaciones": [
       {"numero": 1, "profundidad": 6.0, "tipo_suelo": "Arena", ...},
       {"numero": 2, "profundidad": 8.5, "tipo_suelo": "Arcilla", ...}
     ],
     "imagenes": []
   }


2. DOCUMENTSERVICE VALIDA
   ────────────────────────
   ✓ Categoría válida (1, 2 o 3)
   ✓ Requisitos cumplidos:
     - Categoría 1: min 3 perforaciones
     - Categoría 2: min 4 perforaciones
     - Categoría 3: min 4 perforaciones
   ✓ Genera project_id único (ej: a1b2c3d4)


3. EXCELSERVICE COPIA PLANTILLA
   ───────────────────────────────
   Original: templates/excel/plantilla_categoria_1.xlsx
   Copia:    generated/a1b2c3d4_categoria_1.xlsx
   [ORIGINAL NO SE TOCA]


4. FIELDMAPPING OBTIENE UBICACIONES
   ────────────────────────────────────
   Busca en FIELD_MAPPING_CATEGORIA_1:
   {
     "nombre_proyecto": ["B5", "D10", "F2"],
     "municipio": ["C7", "E12"],
     "fecha_registro": ["H3", "B15"],
     ...
   }


5. EXCELSERVICE MODIFICA CELDAS
   ──────────────────────────────
   Abre copia con openpyxl
   Para cada campo en field_mapping:
     - ws["B5"] = "Estudio Geotécnico Centro"
     - ws["D10"] = "Estudio Geotécnico Centro"
     - ws["F2"] = "Estudio Geotécnico Centro"
     - ws["C7"] = "Medellín"
     - ws["E12"] = "Medellín"
     ...
   
   ✓ Conserva fórmulas originales
   ✓ Conserva formatos/estilos
   ✓ Conserva referencias cruzadas


6. EXCELSERVICE AÑADE PERFORACIONES
   ──────────────────────────────────
   Tabla en fila 27 (según PERFORACION_MAPPING):
   
   │ Número │ Profundidad │ Tipo Suelo    │ Observaciones │
   │ 1      │ 6.0         │ Arena         │ SPT=30        │
   │ 2      │ 8.5         │ Arcilla       │ Consistencia  │
   │ ...    │ ...         │ ...           │ ...           │


7. EXCELSERVICE GUARDA ARCHIVO
   ────────────────────────────
   workbook.save(generated/a1b2c3d4_categoria_1.xlsx)
   ✓ Archivo generado con todos los datos


8. BACKEND RETORNA RESPUESTA
   ───────────────────────────
   {
     "success": true,
     "message": "Documentos generados exitosamente",
     "project_id": "a1b2c3d4",
     "files": ["backend/generated/a1b2c3d4_categoria_1.xlsx"],
     "timestamp": "2024-05-25T10:30:45.123456"
   }


9. FRONTEND DESCARGA ARCHIVO
   ──────────────────────────
   GET /download/a1b2c3d4_categoria_1.xlsx
   [Implementar en fase siguiente]


╔════════════════════════════════════════════════════════════════════════════╗
║                            MAPEO DE CATEGORÍAS                            ║
╚════════════════════════════════════════════════════════════════════════════╝

CATEGORÍA 1 (Hasta 3 pisos)
──────────────────────────
├─ Carga: 500 kN
├─ Mínimo 3 perforaciones
├─ Profundidad mínima: 6m
├─ Plantilla: plantilla_categoria_1.xlsx
├─ Field mapping: FIELD_MAPPING_CATEGORIA_1
└─ Tabla perforaciones: fila 27

CATEGORÍA 2 (Hasta 10 pisos)
────────────────────────────
├─ Carga: 4000 kN
├─ Mínimo 4 perforaciones
├─ Profundidad: 15m
├─ Plantilla: plantilla_categoria_2.xlsx
├─ Field mapping: FIELD_MAPPING_CATEGORIA_2
└─ Tabla perforaciones: fila 24

CATEGORÍA 3 (Más de 10 pisos)
──────────────────────────────
├─ Carga: >4000 kN
├─ Mínimo 4 perforaciones
├─ Profundidad: 25m
├─ Plantilla: plantilla_categoria_3.xlsx
├─ Field mapping: FIELD_MAPPING_CATEGORIA_3
└─ Tabla perforaciones: fila 25


╔════════════════════════════════════════════════════════════════════════════╗
║                         PRINCIPIOS DE ARQUITECTURA                        ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ SEPARACIÓN DE RESPONSABILIDADES
   - API routes solo manejan HTTP
   - Services contienen lógica de negocio
   - Utils tienen funciones reutilizables
   - Models definen tipos de datos

✅ FIELD MAPPING CENTRALIZADO
   - Un único archivo define dónde van los datos
   - Fácil de mantener y actualizar
   - No hardcoded en servicios

✅ PLANTILLAS INMUTABLES
   - Las originales NUNCA se modifican
   - Se crean copias para cada proyecto
   - Permite reutilizar plantillas

✅ VALIDACIÓN DE ENTRADA
   - Pydantic valida antes de procesar
   - Categorías validadas
   - Requisitos verificados

✅ MANEJO DE ERRORES ROBUSTO
   - Try/except en cada servicio
   - Logging completo
   - Respuestas HTTP consistentes

✅ CONFIGURACIÓN CENTRALIZADA
   - config.py maneja todas las rutas
   - Variables de entorno en .env
   - Fácil de cambiar según ambiente

"""

print(ARQUITECTURA)
