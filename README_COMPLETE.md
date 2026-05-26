# AutoGeo - Automatización Documental Geotécnica 🏗️

## 📋 Visión General

**AutoGeo** es una plataforma SaaS completa para automatizar la generación de documentos geotécnicos. Combina un frontend moderno con un backend robusto que modifica plantillas Excel automáticamente.

```
Frontend (Next.js)                Backend (FastAPI)
localhost:3000                    localhost:8000
     ↓                                  ↓
  [Formulario] ----JSON---→ [API /generate]
  [Historial] ←----ZIP---- [Generador Excel]
  [Chat IA]                [Plantillas]
```

## 🏗️ Arquitectura Completa

### Frontend (Next.js 14)
```
src/
├── app/
│   ├── generate/   → Formulario para generar documentos
│   ├── history/    → Tabla de proyectos generados
│   └── ai/         → Asistente con IA
├── components/
│   ├── ui/         → 9 componentes base (Button, Input, etc)
│   ├── shared/     → Sidebar, Header, MainLayout
│   └── forms/      → ImageDropzone, MunicipioAutocomplete
├── hooks/          → useFormData, useSidebar, useImageUpload
└── services/       → Firebase, Document API (prepared)
```

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/        → POST /generate, /templates/status, /health
│   ├── services/   → ExcelService, DocumentService, TemplateService
│   ├── utils/      → field_mapping (centralizado)
│   ├── models/     → Pydantic schemas
│   └── core/       → Configuración
├── templates/
│   └── excel/      → plantilla_categoria_1/2/3.xlsx
├── generated/      → Archivos de salida (copias de trabajo)
└── main.py         → FastAPI app
```

## 🚀 Quick Start

### 1. Frontend

```bash
# Instalar dependencias
npm.cmd install

# Ejecutar en desarrollo
npm.cmd run dev

# Acceso: http://localhost:3000
```

### 2. Backend

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Generar plantillas de ejemplo
python generate_templates.py

# Ejecutar servidor
python -m uvicorn main:app --reload

# Acceso: http://localhost:8000/docs
```

## 🎯 Flujo de Uso

### 1️⃣ Usuario llena formulario (Frontend)
```
Nombre Proyecto: "Estudio Geotécnico Centro"
Municipio: "Medellín"
Fecha: "2024-05-25"
Categoría: "1"
Campo N: "Suelo tipo C"
Perforaciones: 
  - Perf 1: 6.0m, Arena
  - Perf 2: 8.5m, Arcilla
  - Perf 3: 6.5m, Arena
```

### 2️⃣ Frontend envía datos al Backend
```json
POST /api/generate
{
  "nombre_proyecto": "...",
  "municipio": "...",
  "categoria": "1",
  "perforaciones": [...]
}
```

### 3️⃣ Backend procesa
```
DocumentService
  ├─ Valida categoría (1, 2 o 3)
  ├─ Verifica requisitos (mín perforaciones)
  └─ ExcelService
      ├─ Copia plantilla → generated/
      ├─ Field Mapping obtiene ubicaciones
      ├─ Modifica celdas dinámicas
      ├─ Añade tabla de perforaciones
      └─ Guarda archivo
```

### 4️⃣ Backend retorna archivo
```json
{
  "success": true,
  "project_id": "a1b2c3d4",
  "files": ["backend/generated/a1b2c3d4_categoria_1.xlsx"],
  "timestamp": "2024-05-25T10:30:45"
}
```

### 5️⃣ Frontend descarga
```
El usuario descarga el archivo Excel completamente generado
```

## 🔑 Características Principales

### Frontend
✅ **Responsive Design**: Funciona en desktop, tablet, mobile
✅ **Formulario Validado**: Validación en tiempo real
✅ **Upload de Imágenes**: Drag & drop, preview, validación
✅ **Autocomplete**: 200+ municipios de Antioquia
✅ **Historial**: Tabla con búsqueda, filtros y estadísticas
✅ **Chat IA**: Interfaz conversacional (preparada)
✅ **Sidebar Colapsable**: Persiste estado en localStorage
✅ **Glassmorphism UI**: Diseño moderno y premium

### Backend
✅ **Generación Automática**: Completa Excel en segundos
✅ **Plantillas Inteligentes**: 3 categorías, 3 plantillas
✅ **Field Mapping Centralizado**: Fácil de mantener
✅ **Preserva Fórmulas**: Mantiene lógica Excel original
✅ **Perforaciones Automáticas**: Rellena tabla dinámicamente
✅ **Validación de Categorías**: Verifica requisitos
✅ **Copia de Plantillas**: Nunca modifica originales
✅ **API RESTful**: Documentación interactiva en /docs

## 📊 Categorías de Proyectos

| Categoría | Pisos | Carga | Perforaciones | Profundidad |
|-----------|-------|-------|---------------|-------------|
| 1         | Hasta 3 | 500 kN | mín 3 | 6m |
| 2         | Hasta 10 | 4000 kN | 4 | 15m |
| 3         | >10 | >4000 kN | 4 | 25m |

## 🔧 Configuración

### Variables de Entorno

**Frontend** (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`.env`):
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
DEBUG=True
```

## 📦 Dependencias

### Frontend
- Next.js 14.2.35
- React 18.3.1
- TypeScript 5.3.3
- TailwindCSS 3.4.1
- Radix UI
- Firebase 10.7.0
- lucide-react

### Backend
- FastAPI 0.104.1
- Uvicorn
- openpyxl 3.11.0
- Pydantic 2.5.0
- python-docx 0.8.11

## 🔄 Workflow Técnico

```
FRONTEND                          BACKEND
  ↓                                 ↓
[Form] → JSON → HTTP POST → [FastAPI]
  ↓                            ↓
[Input]                  [Validate]
  ↓                            ↓
[Search                 [Copy Template]
 Municipios]                   ↓
  ↓                    [Field Mapping]
[Upload                       ↓
 Images]              [Modify Cells]
  ↓                            ↓
[Validation]          [Add Data Table]
  ↓                            ↓
[Summary]                [Save File]
  ↓←───────JSON Response───←   ↓
[Download]      project_id + files
```

## 📚 Documentación

- **Frontend**: [src/README.md](./src/README.md)
- **Backend**: [backend/README.md](./backend/README.md)
- **Backend Quick Start**: [backend/QUICK_START.md](./backend/QUICK_START.md)
- **Arquitectura Detallada**: [backend/ARCHITECTURE.py](./backend/ARCHITECTURE.py)

## 🎯 Próximas Fases

### Fase 2 (Backend Avanzado)
- [ ] Generación de Word automático
- [ ] Conversión a PDF
- [ ] Descarga en ZIP
- [ ] Análisis de imágenes con IA

### Fase 3 (Firebase)
- [ ] Autenticación con Firebase Auth
- [ ] Almacenamiento en Cloud Storage
- [ ] Base de datos Firestore
- [ ] Sistema de usuarios

### Fase 4 (IA y ML)
- [ ] Integración con OpenAI/Anthropic
- [ ] Análisis de imágenes de perforaciones
- [ ] Generación automática de descripción
- [ ] Predicción de categoría

### Fase 5 (Mejoras)
- [ ] Sistema de caché
- [ ] WebSocket para progreso
- [ ] Reportes y estadísticas
- [ ] Tests (Jest, pytest)
- [ ] CI/CD con GitHub Actions

## 🐛 Troubleshooting

### Frontend
```bash
# Port 3000 en uso
lsof -i :3000  # Mac/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess  # Windows

# Error TypeScript
npm run lint  # Ver errores
```

### Backend
```bash
# Port 8000 en uso
lsof -i :8000  # Mac/Linux

# Plantillas no encontradas
python generate_templates.py

# CORS error
Verificar ALLOWED_ORIGINS en .env
```

## 📞 Support

Para reportar problemas o sugerencias:
1. Verificar que ambos servidores están corriendo
2. Revisar logs en consola
3. Acceder a documentación interactiva: http://localhost:8000/docs

## 📄 Licencia

Proyecto desarrollado para propósitos educativos.

---

**🚀 ¡AutoGeo está listo para revolucionar la automatización geotécnica!**

Powered by:
- **Frontend**: Next.js + TypeScript + TailwindCSS
- **Backend**: FastAPI + Python + openpyxl
- **UI**: Radix UI + shadcn/ui
- **Icons**: lucide-react
