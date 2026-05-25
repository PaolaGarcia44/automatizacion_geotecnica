# 👨‍💻 GUÍA DE DESARROLLO

## Para Desarrolladores - Extender el Proyecto

---

## 🏗️ Arquitectura

### App Router (Next.js 14)
```
app/
├── (root)
│   ├── page.tsx         → redirect /generate
│   ├── layout.tsx       → RootLayout + metadata
│   └── globals.css
├── generate/
│   └── page.tsx         → GeneratePage con MainLayout
├── history/
│   └── page.tsx         → HistoryPage con MainLayout
└── ai/
    └── page.tsx         → AIPage con MainLayout
```

Cada página usa `<MainLayout>` que envuelve el contenido en Sidebar + Header.

### Server vs Client Components
```typescript
// Server Component (default)
export default function Page() { }

// Client Component (interactivity)
'use client'
import { useState } from 'react'
```

El proyecto usa Server Components donde es posible, Client Components solo para:
- Form state
- Sidebar state
- Chat messages
- Modal opens

---

## 📦 Agregar Nuevos Componentes

### 1. Componente UI Simple (shadcn-style)

```typescript
// src/components/ui/MyComponent.tsx
import * as React from 'react'
import { cn } from '@/lib/utils'

interface MyComponentProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outline'
}

const MyComponent = React.forwardRef<HTMLDivElement, MyComponentProps>(
  ({ className, variant = 'default', ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-md border',
        variant === 'default' && 'bg-primary-600 text-white',
        variant === 'outline' && 'border-secondary-200 bg-white',
        className
      )}
      {...props}
    />
  )
)
MyComponent.displayName = 'MyComponent'

export { MyComponent }
```

### 2. Componente con Lógica

```typescript
// src/components/forms/MyForm.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function MyForm() {
  const [data, setData] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Lógica aquí
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Contenido */}
    </form>
  )
}
```

### 3. Custom Hook

```typescript
// src/hooks/useMyHook.ts
'use client'

import { useState, useCallback } from 'react'

export const useMyHook = () => {
  const [state, setState] = useState(false)

  const toggle = useCallback(() => {
    setState(prev => !prev)
  }, [])

  return { state, toggle }
}
```

---

## 🔄 Agregar Nueva Página

### 1. Crear carpeta y archivo
```bash
src/app/my-page/page.tsx
```

### 2. Implementar página
```typescript
'use client'

import { MainLayout } from '@/layouts/MainLayout'

export default function MyPage() {
  return (
    <MainLayout>
      <div className='page-padding container-main'>
        <h1 className='text-3xl font-bold'>Mi Página</h1>
      </div>
    </MainLayout>
  )
}
```

### 3. Actualizar Sidebar
En `src/components/shared/Sidebar.tsx`, agregar item:
```typescript
const navItems = [
  {
    title: 'Mi Página',
    href: '/my-page',
    icon: MyIcon,
    description: 'Descripción',
  },
  // ... resto
]
```

---

## 🎨 Sistema de Colores

### Usar en CSS
```tsx
className='bg-primary-600 text-primary-50 hover:bg-primary-700'
```

### Paleta Disponible
```
primary-{50,100,200,300,400,500,600,700,800,900}
secondary-{50,100,200,300,400,500,600,700,800,900}
accent-{50,100,200,300,400,500,600,700,800,900}
```

### Agregar Nuevo Color
Editar `tailwind.config.ts`:
```typescript
colors: {
  mycolor: {
    50: '#f5f3ff',
    100: '#ede9fe',
    // ... continuar
  }
}
```

---

## 🔌 Conectar a API

### Servicio existente
```typescript
// src/services/myService.ts
export interface MyRequest {
  name: string
}

export interface MyResponse {
  id: string
  message: string
}

export const myFunction = async (req: MyRequest): Promise<MyResponse> => {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/my-endpoint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })

  if (!res.ok) throw new Error('API error')
  return res.json()
}
```

### Usar en componente
```typescript
'use client'

import { myFunction } from '@/services/myService'

export function MyComponent() {
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      const result = await myFunction({ name: 'Test' })
      console.log(result)
    } finally {
      setLoading(false)
    }
  }

  return <button onClick={handleClick}>{loading ? '...' : 'Click'}</button>
}
```

---

## 🔒 Formularios Validados

### Con validación en cliente
```typescript
'use client'

import { useFormData } from '@/hooks/useFormData'

export function MyForm() {
  const { formData, updateField, isFormValid } = useFormData()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!isFormValid()) {
      alert('Completa el formulario')
      return
    }
    // Enviar...
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input
        value={formData.nombre}
        onChange={(e) => updateField('nombre', e.target.value)}
      />
      <Button disabled={!isFormValid()}>Enviar</Button>
    </form>
  )
}
```

---

## 🗄️ Data Management

### Estado local (useState)
```typescript
const [count, setCount] = useState(0)
```

### Estado global (preparado Zustand)
```typescript
// src/store/myStore.ts
import { create } from 'zustand'

interface MyStore {
  count: number
  increment: () => void
}

export const useMyStore = create<MyStore>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
}))
```

### Usar en componente
```typescript
'use client'

import { useMyStore } from '@/store/myStore'

export function Counter() {
  const { count, increment } = useMyStore()
  return <button onClick={increment}>{count}</button>
}
```

---

## 🧪 Testing (Próximo)

### Setup Jest + React Testing Library
```bash
npm.cmd install --save-dev jest @testing-library/react @testing-library/jest-dom
```

### Test ejemplo
```typescript
// __tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '@/components/ui/button'

describe('Button', () => {
  it('renders button text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

---

## 📱 Responsive Design

### Breakpoints (TailwindCSS)
```
sm:  640px
md:  768px
lg:  1024px
xl:  1280px
2xl: 1536px
```

### Uso
```tsx
<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3'>
  {/* 1 col en mobile, 2 en tablet, 3 en desktop */}
</div>
```

---

## 🎯 Tipado TypeScript

### Props component
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline'
  size?: 'sm' | 'md' | 'lg'
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant, size, ...props }, ref) => {
    // Implementación
  }
)
```

### Response API
```typescript
interface ApiResponse<T> {
  success: boolean
  data: T
  error?: string
}

const getProject = async (id: string): Promise<ApiResponse<Project>> => {
  // ...
}
```

---

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm.cmd install -g vercel
vercel
```

### Firebase Hosting
```bash
npm.cmd install -g firebase-tools
firebase init
firebase deploy
```

### Build
```bash
npm.cmd run build
npm.cmd start
```

---

## 📋 Checklist para Nueva Feature

- [ ] Crear componente/servicio en carpeta apropiada
- [ ] Agregar tipos TypeScript
- [ ] Implementar lógica
- [ ] Importar en página/componente
- [ ] Probar manualmente
- [ ] Actualizar sidebar si es nueva página
- [ ] Agregar estilos Tailwind (no CSS raw)
- [ ] Verificar responsive
- [ ] Test con `npm.cmd run lint`
- [ ] Commit a git

---

## 🐛 Debug

### Console logs
```typescript
console.log('Value:', data)
console.error('Error:', error)
```

### React DevTools
- Instalar extensión de navegador
- Inspeccionar componentes
- Ver props y state

### Network
- F12 → Network tab
- Ver requests/responses
- Check headers y status

---

## 📚 Referencias Internas

```typescript
// Imports correctos
import { Button } from '@/components/ui/button'       // UI
import { MainLayout } from '@/layouts/MainLayout'     // Layout
import { useFormData } from '@/hooks/useFormData'      // Hook
import { municipios } from '@/data/municipios'        // Data
import { generateDocuments } from '@/services/...'    // Service
import { cn } from '@/lib/utils'                      // Utils
```

---

## ✅ Best Practices

1. **Archivos pequeños**: Max 300-400 líneas por archivo
2. **Nombres descriptivos**: `getUserProjects()` no `getData()`
3. **Comments importantes**: Explicar "por qué", no "qué"
4. **Error handling**: Try/catch en funciones async
5. **TypeScript**: Nunca usar `any`, siempre tipar
6. **Componentes funcionales**: Use hooks, no clases
7. **Reutilizar componentes**: Preferir existentes a crear nuevos
8. **Responsive**: Mobile-first siempre

---

## 🔗 Git Workflow

```bash
# Crear rama
git checkout -b feature/new-feature

# Hacer cambios y commit
git add .
git commit -m "feat: add new feature"

# Push
git push origin feature/new-feature

# Pull request en GitHub
```

---

## 🎓 Aprendizaje Recomendado

- Next.js App Router
- React Hooks
- TypeScript Basics
- TailwindCSS Utilities
- Component Composition

---

**Buena suerte con el desarrollo! 🚀**

Para preguntas, revisa el README.md o la estructura de código existente.
