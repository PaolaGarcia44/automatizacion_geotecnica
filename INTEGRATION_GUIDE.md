# Guía de Integración Frontend + Backend

## 🎯 Objetivo
Ejecutar simultáneamente el Frontend (Next.js) y Backend (FastAPI) para que funcionen conjuntamente.

---

## 📋 Requisitos Previos

✅ Node.js 18+ instalado (para Frontend)
✅ Python 3.10+ instalado (para Backend)
✅ npm o yarn (para Frontend)
✅ pip (para Backend)

---

## 🚀 Paso 1: Preparar el Backend

### 1.1 Instalar dependencias Python

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Generar plantillas Excel de ejemplo

```bash
python generate_templates.py
```

Esto crea 3 plantillas en `backend/templates/excel/`:
- `plantilla_categoria_1.xlsx`
- `plantilla_categoria_2.xlsx`
- `plantilla_categoria_3.xlsx`

---

## 🎨 Paso 2: Preparar el Frontend

### 2.1 Instalar dependencias Node

```bash
cd ..  # Volver a raíz del proyecto
npm.cmd install
```

### 2.2 Configurar variable de entorno

Crear o verificar `.env.local` en la raíz del proyecto:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ▶️ Paso 3: Ejecutar Ambos Servidores

### Opción A: En dos terminales separadas (RECOMENDADO)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm.cmd run dev
```

### Opción B: En una sola terminal (con background)

**Windows PowerShell:**
```powershell
# Iniciar backend en background
Start-Job -ScriptBlock { cd backend; python -m uvicorn main:app --reload }

# Esperar 3 segundos
Start-Sleep -Seconds 3

# Iniciar frontend
npm.cmd run dev
```

---

## ✅ Verificar que Todo Funciona

### 1. Frontend
Abre en navegador:
```
http://localhost:3000
```

Deberías ver:
- ✅ Página de Generar (con formulario)
- ✅ Página de Historial (con tabla)
- ✅ Página de Chat IA

### 2. Backend API
Abre en navegador:
```
http://localhost:8000/docs
```

Deberías ver:
- ✅ Documentación Swagger UI
- ✅ 3 Endpoints: `/api/generate`, `/api/templates/status`, `/api/health`

### 3. Health Check
```bash
curl http://localhost:8000/api/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "service": "AutoGeo Backend",
  "version": "1.0.0"
}
```

---

## 🔄 Flujo de Uso Integrado

### 1. Rellenar formulario en Frontend

En http://localhost:3000/generate:
- ✏️ Nombre Proyecto
- 📍 Municipio
- 📅 Fecha
- 📊 Categoría (1, 2 o 3)
- ⛏️ Perforaciones

### 2. Click en "Generar Documentos"

El Frontend:
1. Valida el formulario
2. Envía datos a `POST /api/generate`
3. Muestra estado "Generando..."
4. Recibe respuesta del Backend

### 3. Backend procesa

El Backend:
1. Recibe solicitud JSON
2. Valida categoría y requisitos
3. Copia plantilla Excel
4. Modifica celdas dinámicas
5. Añade datos de perforaciones
6. Guarda archivo en `generated/`
7. Retorna respuesta con project_id

### 4. Mostrar éxito

Frontend muestra:
```
✅ ¡Documentos Generados!
ID: a1b2c3d4
```

El archivo se encuentra en:
```
backend/generated/a1b2c3d4_categoria_1.xlsx
```

---

## 📊 Ejemplo de Solicitud Completa

### Request (Frontend → Backend)
```json
POST http://localhost:8000/api/generate

{
  "nombre_proyecto": "Estudio Geotécnico Centro Medellín",
  "municipio": "Medellín",
  "fecha_registro": "2024-05-25",
  "categoria": "1",
  "campo_n": "Suelo tipo C",
  "descripcion": "Análisis preliminar de suelos",
  "perforaciones": [
    {
      "numero": 1,
      "profundidad": 6.0,
      "tipo_suelo": "Arena",
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

### Response (Backend → Frontend)
```json
{
  "success": true,
  "message": "Documentos generados exitosamente",
  "project_id": "a1b2c3d4",
  "files": ["backend/generated/a1b2c3d4_categoria_1.xlsx"],
  "timestamp": "2024-05-25T10:30:45.123456"
}
```

---

## 🐛 Troubleshooting

### Error: "Connection refused" o "localhost:8000 no responde"

```bash
# Verificar que backend está corriendo
curl http://localhost:8000/api/health

# Si falla, iniciar backend manualmente
cd backend
python -m uvicorn main:app --reload
```

### Error: "CORS error"

Verificar `.env.local` tenga:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Reiniciar frontend:
```bash
npm.cmd run dev
```

### Error: "Plantillas no encontradas"

```bash
cd backend
python generate_templates.py
```

### Error: "Port 8000 already in use"

Cambiar puerto:
```bash
python -m uvicorn main:app --reload --port 8001
```

Y actualizar `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## 📁 Estructura de Archivos

```
automatizacion_geotecnica/
├── src/                          # Frontend (Next.js)
│   ├── app/
│   │   ├── generate/page.tsx    # ✨ ACTUALIZADO - Conecta con backend
│   │   ├── history/page.tsx
│   │   └── ai/page.tsx
│   ├── services/
│   │   └── documentService.ts   # ✨ ACTUALIZADO - Conecta con API
│   └── ...
│
├── backend/                       # Backend (FastAPI)
│   ├── app/
│   │   ├── api/documents.py
│   │   ├── services/
│   │   └── ...
│   ├── templates/
│   │   └── excel/
│   │       ├── plantilla_categoria_1.xlsx
│   │       ├── plantilla_categoria_2.xlsx
│   │       └── plantilla_categoria_3.xlsx
│   ├── generated/                # Archivos de salida
│   ├── main.py
│   └── requirements.txt
│
├── .env.local                     # ✨ NUEVO - Variable de entorno
└── package.json

```

---

## 🎯 Checklist de Verificación

- [ ] Backend instalado y corriendo en puerto 8000
- [ ] Frontend instalado y corriendo en puerto 3000
- [ ] `.env.local` tiene `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Plantillas Excel existen en `backend/templates/excel/`
- [ ] POST /api/generate funciona en Swagger UI
- [ ] Formulario en Frontend se envía sin errores
- [ ] Excel se genera correctamente en `backend/generated/`

---

## 📚 Documentación Relacionada

- **Frontend README**: Instrucciones completas del frontend
- **Backend README**: [backend/README.md](backend/README.md)
- **Backend QUICK_START**: [backend/QUICK_START.md](backend/QUICK_START.md)
- **Arquitectura Detallada**: [backend/ARCHITECTURE.py](backend/ARCHITECTURE.py)

---

## 🎉 ¡Listo!

Ahora tienes:
- ✅ Frontend en localhost:3000
- ✅ Backend en localhost:8000
- ✅ Ambos comunicándose correctamente
- ✅ Generación automática de documentos Excel funcional

**¡A generar documentos geotécnicos! 🚀**
