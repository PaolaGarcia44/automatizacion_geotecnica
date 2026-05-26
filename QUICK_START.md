# 🚀 INICIO RÁPIDO - Frontend + Backend Integrado

## ✅ Sistema Completo Listo

### Estado Actual
✅ **Frontend Next.js** - Página generación integrada con backend
✅ **Backend FastAPI** - API de generación de Excel funcionando
✅ **Integración** - Frontend conecta con backend en localhost:8000

---

## ⚡ Ejecución en 5 minutos

### Terminal 1: Backend (FastAPI)

```bash
cd backend
python -m uvicorn main:app --reload
```

**Esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Frontend (Next.js)

```bash
npm.cmd run dev
```

**Esperado:**
```
▲ Next.js 14.2.35
- Local: http://localhost:3000
```

---

## ✅ Verificar Funcionamiento

### 1. Abrir Frontend
```
http://localhost:3000
```

Deberías ver:
- Página "Generar" con formulario
- Página "Historial" con tabla
- Página "Chat IA"

### 2. Abrir Backend Docs
```
http://localhost:8000/docs
```

Deberías ver:
- Swagger UI con 3 endpoints
- POST /api/generate
- GET /api/templates/status
- GET /api/health

### 3. Test Health Check
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

## 📝 Cómo Usar

### 1. Formulario (http://localhost:3000/generate)

Completa:
- **Nombre Proyecto** - "Estudio Centro Medellín"
- **Municipio** - Selecciona de la lista
- **Fecha Registro** - Selecciona fecha (Final se calcula automáticamente +20 días)
- **Campo N** - "Suelo tipo C"
- **Categoría** - Elige 1, 2 o 3
- **Perforaciones** - Agrega al menos 3

### 2. Generar

Click en "Generar Documentos"

Frontend hará:
1. Validar datos
2. Enviar POST a `http://localhost:8000/api/generate`
3. Mostrar "Generando..."
4. Recibir respuesta con project_id

### 3. Resultado

Verás modal de éxito:
```
✅ ¡Documentos Generados!
ID: a1b2c3d4
```

El archivo se guarda en:
```
backend/generated/a1b2c3d4_categoria_1.xlsx
```

---

## 🔍 Verificación de Archivos

### Backend

Verifica que existen las plantillas:
```bash
ls backend/templates/excel/
```

Deberías ver:
```
plantilla_categoria_1.xlsx
plantilla_categoria_2.xlsx
plantilla_categoria_3.xlsx
```

### Frontend

Verifica que existe .env.local:
```bash
cat .env.local
```

Deberías ver:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐛 Si Algo Falla

### Error: Backend no responde

```bash
# 1. Verifica que está corriendo
curl http://localhost:8000/api/health

# 2. Si no responde, reinicia
# En Terminal 1:
Ctrl+C
python -m uvicorn main:app --reload
```

### Error: Frontend muestra error

```bash
# 1. Verifica que está corriendo
# Abre http://localhost:3000

# 2. Si falla, reinicia
# En Terminal 2:
Ctrl+C
npm.cmd run dev
```

### Error: CORS en consola

```bash
# 1. Verifica que .env.local existe
cat .env.local

# 2. Si no tiene la URL, añádela:
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# 3. Reinicia frontend
```

### Error: Plantillas no encontradas

```bash
cd backend
python generate_templates.py
cd ..
```

---

## 📚 Documentación Completa

- **Guía Completa**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Backend Docs**: [backend/README.md](backend/README.md)
- **Arquitectura**: [backend/ARCHITECTURE.py](backend/ARCHITECTURE.py)

---

## 💾 Estructura de Proyecto

```
automatizacion_geotecnica/
├── src/
│   ├── app/
│   │   ├── generate/page.tsx    ✨ Formulario integrado
│   │   ├── history/page.tsx
│   │   └── ai/page.tsx
│   ├── services/
│   │   └── documentService.ts   ✨ Conecta con API
│   ├── components/...
│   └── ...
├── backend/
│   ├── app/api/documents.py     ✨ Endpoints API
│   ├── app/services/...
│   ├── templates/excel/...      ✨ Plantillas
│   ├── generated/               ✨ Archivos de salida
│   ├── main.py
│   └── requirements.txt
├── .env.local                    ✨ Config Frontend
├── INTEGRATION_GUIDE.md          ✨ Guía completa
└── QUICK_START.md               ✨ Este archivo
```

---

## 🎯 Checklist de Verificación

- [ ] Backend corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 3000
- [ ] .env.local con NEXT_PUBLIC_API_URL configurado
- [ ] Plantillas Excel existen en backend/templates/excel/
- [ ] Swagger UI accesible en localhost:8000/docs
- [ ] Formulario accesible en localhost:3000/generate
- [ ] Health check responde correctamente

---

## ✨ ¡Listo para Usar!

**Sistema Completo:**
- ✅ Frontend Next.js
- ✅ Backend FastAPI  
- ✅ Integración funcionando
- ✅ Generación de Excel automática

**¡A generar documentos geotécnicos! 🎉**

- [ ] **Leer README.md** — Documentación completa del proyecto
- [ ] **Explorar las 3 páginas**:
  - [x] http://localhost:3000/generate (Formulario principal)
  - [x] http://localhost:3000/history (Historial con datos simulados)
  - [x] http://localhost:3000/ai (Chat AI simulado)
- [ ] **Configurar Firebase** (opcional):
  - Copiar `.env.local.example` → `.env.local`
  - Agregar credenciales Firebase
- [ ] **Revisar estructura** en `src/`:
  - `/app` — Pages (Next.js App Router)
  - `/components` — Componentes reutilizables
  - `/hooks` — Custom hooks
  - `/lib` — Utilities y config
  - `/services` — Service layer
  - `/data` — Data files

---

## 🎯 Puntos Clave

### Formulario (/generate)
- ✅ Validación en tiempo real
- ✅ Autocomplete de municipios con búsqueda
- ✅ Drag & drop para imágenes
- ✅ Fecha final auto-calculada
- ✅ Botón de "Generar" con estado de carga

### Historial (/history)
- ✅ 3 tarjetas de estadísticas
- ✅ Búsqueda por nombre de proyecto
- ✅ Filtro por municipio
- ✅ Tabla con 8 proyectos simulados
- ✅ Acciones: Ver y Descargar

### Chat IA (/ai)
- ✅ Interfaz moderna tipo WhatsApp
- ✅ Burbujas diferenciadas (usuario/asistente)
- ✅ Sugerencias de preguntas (clickeables)
- ✅ Respuestas simuladas con delay
- ✅ Indicador de carga (typing animation)

---

## 🛠️ Comandos Útiles

```powershell
# Entrar al proyecto
cd "c:\Users\Paola\OneDrive - Tecnologico de Antioquia Institucion Universitaria\Escritorio\Automatización geotecnica\automatizacion_geotecnica"

# Desarrollo (ya está corriendo)
npm.cmd run dev

# Build
npm.cmd run build

# Lint
npm.cmd run lint

# Lint + Fix
npm.cmd run lint -- --fix
```

---

## 📁 Estructura Importante

```
src/
├── app/
│   ├── generate/page.tsx  ← Formulario principal
│   ├── history/page.tsx   ← Historial + tabla
│   ├── ai/page.tsx        ← Chat IA
│   ├── layout.tsx         ← Root layout
│   └── globals.css        ← Estilos globales
├── components/
│   ├── ui/                ← Button, Input, Card, etc. (shadcn-style)
│   ├── shared/            ← Sidebar, Header
│   ├── forms/             ← ImageDropzone, MunicipioAutocomplete
│   └── history/           ← StatCard
├── hooks/
│   ├── useFormData.ts
│   ├── useSidebar.ts
│   └── useImageUpload.ts
├── lib/
│   ├── firebase/          ← Config, auth, firestore, storage
│   └── utils.ts           ← cn() helper
├── services/
│   ├── documentService.ts ← Preparado para FastAPI
│   └── aiService.ts       ← Preparado para LLM
└── data/
    ├── municipios.ts      ← 200+ municipios de Antioquia
    └── formSchema.ts      ← Tipos y opciones
```

---

## 🎨 Diseño & Colores

- **Primary (Acción)**: Verde esmeralda (emerald-600)
- **Secondary (Texto/Fondo)**: Gris neutral (slate)
- **Font**: Poppins (Google Fonts)
- **Responsive**: Mobile-first, optimizado para todos los tamaños

---

## 🔐 Firebase (Opcional)

### Si NO necesitas Firebase:
✅ El proyecto funciona perfectamente sin configuración

### Si necesitas Firebase:
1. Crear proyecto en [Firebase Console](https://console.firebase.google.com)
2. Copiar credenciales
3. Crear archivo `.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=xxx
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=xxx
NEXT_PUBLIC_FIREBASE_PROJECT_ID=xxx
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=xxx
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=xxx
NEXT_PUBLIC_FIREBASE_APP_ID=xxx
```

Los servicios se activarán automáticamente.

---

## 🔗 Próximas Integraciones

### 1. Backend FastAPI
El servicio `documentService.ts` espera:
```typescript
POST /api/generate
{
  nombre_proyecto: string,
  municipio: string,
  campo_n: string,
  imagenes: File[]
}
```

### 2. IA (OpenAI / Anthropic)
El servicio `aiService.ts` espera:
```typescript
POST /api/ask
{
  question: string,
  projectId?: string
}
```

### 3. Autenticación
Firebase Auth está preparado en `lib/firebase/auth.ts`:
```typescript
signUp(email, password)
signIn(email, password)
signOut()
getCurrentUser()
resetPassword(email)
```

---

## 📊 Datos de Prueba

### Municipios
- 200+ municipios de Antioquia (incluye Medellín, Envigado, Bello, etc.)
- Autocomplete inteligente con búsqueda

### Proyectos (Historial)
8 proyectos simulados con:
- Nombres realistas
- Municipios variados
- Documentos generados (Informe, Planos, Ensayos, etc.)
- Estadísticas de descargas

---

## ✨ Características Premium

✅ **Sidebar Colapsable**: Con animaciones suaves, icono y persistencia
✅ **Responsive Design**: Funciona en móvil, tablet, desktop
✅ **TypeScript Estricto**: Máxima seguridad de tipos
✅ **Validación**: Formularios validados en cliente
✅ **Performance**: Code splitting, lazy loading automático
✅ **Modern UI**: Glassmorphism, animaciones, accesibilidad

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `npm.cmd not found` | Usa `npm.cmd install` en Windows PowerShell |
| Port 3000 ocupado | Cambia puerto: `npm.cmd run dev -- -p 3001` |
| Archivos no aparecen | Haz `npm.cmd install` nuevamente |
| Build fallido | Verifica que no hay errores de TypeScript: `npm.cmd run lint` |

---

## 📚 Recursos

- [Next.js Docs](https://nextjs.org/docs)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Radix UI Components](https://www.radix-ui.com/docs)
- [Firebase Docs](https://firebase.google.com/docs)
- [lucide-react Icons](https://lucide.dev)

---

## 🎉 ¡Listo!

El proyecto está **100% funcional y listo para desarrollo**.

### Próximos pasos:
1. Explorar las páginas en http://localhost:3000
2. Revisar el código en la estructura `/src`
3. Implementar backend FastAPI
4. Conectar Firebase Auth
5. Integrar LLM para el chat IA

---

**Frontend SaaS - Automatización Documental Geotécnica**  
Optimizado para agentes de código con Claude Haiku 4.5  
🚀 **Servidor corriendo → http://localhost:3000**
