# AutoGeo - Frontend SaaS Platform
## Automatización Documental Geotécnica

Una plataforma moderna SaaS para automatización de documentos geotécnicos con inteligencia artificial, construida con Next.js 14, TypeScript, TailwindCSS y Firebase.

---

## 🚀 Características

### ✅ Implementado
- **Interfaz Premium Moderna**: Diseño profesional con glassmorphism y animaciones suaves
- **3 Páginas Principales**:
  - 📋 **Generar**: Formulario inteligente con autocomplete de municipios y carga de imágenes
  - 🕐 **Historial**: Tabla con estadísticas, búsqueda y filtros
  - 🤖 **Asistente IA**: Chat moderno con mensajes simulados (preparado para integración real)

- **Componentes UI Personalizados**: Basados en Radix UI con TailwindCSS
- **Sidebar Colapsable**: Con animaciones suaves y estado persistente
- **Responsive Design**: Totalmente optimizado para móvil, tablet y desktop
- **Dark Mode Ready**: Arquitectura preparada para tema oscuro
- **TypeScript Estricto**: 100% tipado para máxima seguridad

### 🔧 Preparado Para
- Firebase Authentication
- Firestore Database
- Firebase Storage
- Backend FastAPI
- Integración con LLM (OpenAI, Anthropic, etc.)

---

## 📁 Estructura del Proyecto

```
/src
  /app
    /generate          → Página: Generar Automatización
    /history           → Página: Historial
    /ai                → Página: IA / Chat
    /layout.tsx        → Layout global
    /page.tsx          → Redirect a /generate
    /globals.css       → Estilos globales

  /components
    /ui                → Componentes base (Button, Input, Card, etc.)
    /shared            → Sidebar, Header, shared layouts
    /forms             → ImageDropzone, MunicipioAutocomplete, FormCard
    /history           → StatCard

  /layouts
    /MainLayout.tsx    → Layout con sidebar + header

  /hooks
    /useFormData.ts    → Manejo de estado del formulario
    /useSidebar.ts     → Control de sidebar
    /useImageUpload.ts → Gestión de imágenes

  /lib
    /firebase
      /config.ts       → Configuración Firebase (safe-guards)
      /auth.ts         → Firebase Auth (preparado)
      /firestore.ts    → Firestore (preparado)
      /storage.ts      → Firebase Storage (preparado)
    /utils.ts          → Utilidades (cn function)

  /services
    /documentService.ts → Servicio de generación (preparado para FastAPI)
    /aiService.ts       → Servicio IA (preparado para LLM)

  /data
    /municipios.ts     → Lista completa de municipios de Antioquia
    /formSchema.ts     → Esquema y opciones del formulario

  /assets
    (Ready for images)
```

---

## 🛠️ Stack Tecnológico

| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| Next.js | 14.2.35 | Framework React con SSR |
| React | 18.3.1 | UI Library |
| TypeScript | 5.3.3 | Type Safety |
| TailwindCSS | 3.4.1 | Styling |
| Radix UI | ^1.0 | Headless Components |
| lucide-react | 0.294.0 | Iconos |
| Firebase SDK | 10.7.0 | Backend (preparado) |
| Zustand | 4.4.7 | State Management (ready) |

---

## 🚀 Inicio Rápido

### Requisitos
- Node.js 18+ 
- npm o yarn

### Instalación

1. **Clonar repositorio**
```bash
cd automatizacion_geotecnica
```

2. **Instalar dependencias**
```bash
npm.cmd install
# o
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.local.example .env.local
```
Edita `.env.local` con tus credenciales de Firebase (opcional para desarrollo)

4. **Ejecutar servidor de desarrollo**
```bash
npm.cmd run dev
# o
npm run dev
```

5. **Abrir en navegador**
```
http://localhost:3000
```

---

## 📝 Scripts Disponibles

```bash
# Desarrollo
npm.cmd run dev           # Inicia servidor en localhost:3000

# Build
npm.cmd run build         # Compilación optimizada para producción
npm.cmd start             # Ejecuta aplicación compilada

# Linting
npm.cmd run lint          # Verifica código con ESLint
npm.cmd run lint:fix      # Corrige problemas automáticos

# Información
npm.cmd list              # Lista dependencias instaladas
```

---

## 🎨 Sistema de Diseño

### Paleta de Colores
- **Primary**: Verde esmeralda (emerald-600) - Acciones principales
- **Secondary**: Gris neutral (slate) - Fondos y textos
- **Success**: Verde
- **Warning**: Amarillo  
- **Error**: Rojo

### Tipografía
- **Font**: Poppins (Google Fonts)
- **Weights**: 400, 500, 600, 700

### Componentes Base Disponibles
- Button (5 variantes)
- Input, Textarea
- Card, Label, Badge
- Select, Dialog
- Separator

---

## 🔐 Seguridad & Configuración

### Firebase (Opcional)
Las credenciales de Firebase se cargan solo si están disponibles en variables de entorno. El proyecto incluye "safe-guards" que evitan errores si no están configuradas.

**Para activar Firebase:**
1. Crea proyecto en [Firebase Console](https://console.firebase.google.com)
2. Copia las credenciales en `.env.local`
3. Las funciones se activarán automáticamente

### Validaciones Implementadas
- ✅ Formularios con validación en cliente
- ✅ Tipos TypeScript estrictos
- ✅ ESLint configurado
- ✅ Máximo tamaño de imágenes (10MB)
- ✅ Máximo número de imágenes (5)

---

## 🔗 Integración Futura

### Backend FastAPI
El servicio `documentService.ts` está preparado para conectar con:
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL
// Preparado para: POST /generate, GET /status/:taskId
```

### Inteligencia Artificial
El servicio `aiService.ts` está tipado para:
- OpenAI GPT-4
- Anthropic Claude
- Custom LLM backend

### Autenticación
Firebase Auth está preparado en `lib/firebase/auth.ts`:
- Sign up / Sign in
- Password reset
- Current user management

---

## 📊 Datos Simulados

### Historial (8 proyectos)
- Proyectos con municipios reales de Antioquia
- Documentos generados (Informe, Planos, Ensayos, etc.)
- Estadísticas por mes

### Chat IA
- Mensaje inicial del asistente
- 4 sugerencias de preguntas
- Conversación simulada con respuestas en tiempo real

---

## ✨ Funcionalidades Implementadas

### Página Generate
✅ Formulario con 3 secciones (General, Técnica, Imágenes)
✅ Autocomplete inteligente de municipios
✅ Date picker con cálculo automático (+20 días)
✅ Drag & drop para imágenes
✅ Validación en tiempo real
✅ Botón con estado de carga
✅ Modal de éxito

### Página History
✅ 3 tarjetas de estadísticas
✅ Búsqueda por nombre
✅ Filtro por municipio
✅ Tabla con 8 proyectos simulados
✅ Botones de Ver y Descargar
✅ Estado vacío elegante

### Página AI
✅ Interfaz de chat moderna
✅ Burbujas diferenciadas usuario/asistente
✅ 4 chips de sugerencias
✅ Input con envío por Enter
✅ Respuestas simuladas con delay
✅ Indicador de carga (typing animation)

---

## 🚦 Status del Proyecto

| Componente | Status | Nota |
|-----------|--------|------|
| Frontend UI | ✅ Completo | Premium y totalmente funcional |
| Formularios | ✅ Completo | Validación incluida |
| Navegación | ✅ Completo | Sidebar + Header + Routing |
| Firebase Config | ✅ Preparado | Safe-guards implementados |
| Servicios Backend | ✅ Preparado | Stubs listos para FastAPI |
| Autenticación | ⏳ Preparado | Estructura lista |
| Inteligencia Artificial | ⏳ Preparado | Services tipadas |

---

## 📝 Notas de Desarrollo

### Windows PowerShell
En Windows, usa `npm.cmd` en lugar de `npm`:
```powershell
npm.cmd install
npm.cmd run dev
npm.cmd run build
```

Esto evita problemas de ejecución de scripts.

### Performance
- Code splitting automático por rutas
- Imágenes optimizadas (Next.js Image)
- Lazy loading de componentes
- CSS purging automático

### Testing (Próximo)
Preparado para agregar:
- Jest + React Testing Library
- E2E con Playwright
- Vitest para unit tests

---

## 📞 Soporte y Documentación

### Documentación Externa
- [Next.js 14](https://nextjs.org/docs)
- [TailwindCSS](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/docs)
- [Firebase](https://firebase.google.com/docs)

### Estructura de Carpetas
Cada carpeta tiene un propósito específico. Los imports siguen el patrón:
```typescript
import { Component } from '@/components/...'
import { useHook } from '@/hooks/...'
import { data } from '@/data/...'
```

---

## 🎯 Próximos Pasos

1. **Conectar Firebase**: Agregar credenciales en `.env.local`
2. **Implementar Backend**: Crear API FastAPI para `/generate`
3. **Integrar IA**: Conectar con OpenAI o Anthropic
4. **Autenticación**: Implementar Firebase Auth
5. **Tests**: Agregar cobertura de testing
6. **Deploy**: Publicar en Firebase Hosting o Vercel

---

## 📄 Licencia

Proyecto SaaS - Automatización Documental Geotécnica  
Tecnológico de Antioquia Institución Universitaria

---

## 👨‍💻 Autor

Frontend SaaS - Automatización Geotécnica  
Optimizado para agentes de código con Claude Haiku 4.5

---

**¡Bienvenido a AutoGeo! 🚀**

El proyecto está listo para desarrollo. Próximas integraciones: Backend FastAPI, Firebase, LLM.
