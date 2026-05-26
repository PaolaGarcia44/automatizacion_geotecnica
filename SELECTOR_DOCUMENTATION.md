# Selector Dependiente Departamento-Municipio ✅

## Características Implementadas

### 1. ✅ Datos Locales Completos
- **Archivo**: `src/data/colombia.ts`
- **Contenido**: Todos los 32 departamentos + municipios de Colombia
- **Estructura**: Array de departamentos con municipios anidados
- **Optimización**: Búsqueda rápida sin tildes (normalize)

### 2. ✅ Componente Reutilizable
- **Archivo**: `src/components/forms/DepartmentMunicipalitySelector.tsx`
- **Props**:
  ```typescript
  interface DepartmentMunicipalityProps {
    value: DepartmentMunicipalityValue
    onChange: (value: DepartmentMunicipalityValue) => void
    label?: string
    placeholder?: string
  }
  ```

### 3. ✅ Funcionalidades

#### Selector Dependiente
- Departamento se selecciona primero en dropdown
- Municipio se filtra automáticamente según departamento
- Municipio deshabilitado hasta que se seleccione departamento

#### Autocomplete Elegante
- Campo de búsqueda con icono de lupa
- Búsqueda en tiempo real (case-insensitive)
- Normalize de tildes para mejor UX
- Dropdown con resultados filtrados
- Dropdown se cierra al seleccionar

#### Responsive & Moderno
- Grid 1 columna en mobile, 2 en desktop
- Diseño limpio con bordes y hover states
- Iconos de UI clara (MapPin, ChevronDown, Search)
- Colores verde para estados seleccionados
- Display de selección confirmada

### 4. ✅ Integración en Formulario

#### useFormData Hook
- Nueva función: `updateDepartmentMunicipality()`
- Guarda: `{departamento, departamento_name, municipio, municipio_name}`
- Validación incluye departamento y municipio

#### FormData Interface
```typescript
interface FormData {
  nombre_proyecto: string
  departamento: string
  departamento_name: string
  municipio: string
  municipio_name: string
  fecha_inicio: string
  fecha_final: string
  descripcion?: string
  campo_n: string
  imagenes: File[]
}
```

#### Generate Page
- Importa `DepartmentMunicipalitySelector`
- Reemplaza el antiguo `MunicipioAutocomplete`
- Llama a `updateDepartmentMunicipality()` al cambiar
- Envía `municipio_name` al backend (no el ID)

### 5. ✅ Preparado para Firestore

La arquitectura está diseñada para futura migración a Firestore:

```typescript
// Actualmente: datos locales en colombia.ts
export const COLOMBIA_DEPARTMENTS: Department[] = [...]

// Futuro: reemplazar con llamadas a Firestore
const getDepartmentsFromFirestore = async () => {
  const snapshot = await db.collection('departments').getDocs()
  return snapshot.docs.map(doc => doc.data())
}
```

El componente solo necesita:
- Array de departamentos con `{ id, name }`
- Array de municipios con `{ id, name, department_id }`
- Las funciones `getDepartments()` y `getMunicipalitiesByDepartment()`

**La API del componente no cambiará**, solo cambiarán las fuentes de datos.

### 6. ✅ API Utility Functions

Archivos: `src/data/colombia.ts`

```typescript
// Obtener todos los departamentos
getDepartments() → { id, name }[]

// Obtener municipios de un departamento
getMunicipalitiesByDepartment(deptId) → Municipality[]

// Buscar municipios (sin tildes)
searchMunicipalities(searchTerm, deptId?) → Municipality[]

// Información completa de un municipio
getMunicipalityInfo(munId) → { ...municipality, department_name }
```

---

## Estructura de Datos

### Departamento
```typescript
interface Department {
  id: string              // 'antioquia'
  name: string            // 'Antioquia'
  municipalities: Municipality[]
}
```

### Municipio
```typescript
interface Municipality {
  id: string              // 'medellin'
  name: string            // 'Medellín'
  department_id: string   // 'antioquia'
}
```

### Valor Seleccionado
```typescript
interface DepartmentMunicipalityValue {
  departamento: string        // 'antioquia'
  departamento_name: string   // 'Antioquia'
  municipio: string           // 'medellin'
  municipio_name: string      // 'Medellín'
}
```

---

## Flujo de Uso

### 1. Usuario selecciona Departamento
```
Dropdown abierto → Selecciona "Antioquia"
→ Municipios se filtran automáticamente
→ Campo de municipio se habilita
```

### 2. Usuario busca y selecciona Municipio
```
Escribe "Med" → Se filtra a "Medellín"
→ Click en "Medellín"
→ Se guarda: {
     departamento: 'antioquia',
     departamento_name: 'Antioquia',
     municipio: 'medellin',
     municipio_name: 'Medellín'
   }
```

### 3. En el formulario se muestra
```
✓ Confirmación visual: "Medellín - Antioquia"
✓ Enviado al backend como municipio_name
```

---

## Performance

✅ **Búsqueda rápida**: O(n) con normalize (sin tildes)
✅ **Renderizado eficiente**: Usa useMemo para filtrados
✅ **Sin re-renderizados innecesarios**: Callback memoizado
✅ **Responsive**: 1 columna móvil, 2 desktop

---

## Archivos Creados/Modificados

### Nuevos ✨
- `src/data/colombia.ts` - Base de datos de departamentos
- `src/components/forms/DepartmentMunicipalitySelector.tsx` - Componente reutilizable

### Modificados 🔄
- `src/hooks/useFormData.ts` - Agregó `updateDepartmentMunicipality()`
- `src/data/formSchema.ts` - Agregó campos de departamento
- `src/app/generate/page.tsx` - Integración del componente

---

## Próximos Pasos (Opcionales)

### Phase 2: Conexión Firestore
```typescript
// Reemplazar en colombia.ts
import { db } from '@/config/firebase'

export const getDepartments = async () => {
  const snapshot = await db.collection('departments').getDocs()
  return snapshot.docs.map(doc => ({
    id: doc.id,
    name: doc.data().name
  }))
}
```

### Phase 3: Caché Local
```typescript
// Guardar en localStorage después de traer de Firestore
const departments = await getDepartmentsFromFirestore()
localStorage.setItem('colombia_departments', JSON.stringify(departments))
```

### Phase 4: Sincronización Real-time
```typescript
// Escuchar cambios en Firestore
onSnapshot(collection(db, 'departments'), (snapshot) => {
  // Actualizar componente automáticamente
})
```

---

## Testing

Para verificar que funciona:

```bash
# 1. Abrir formulario
http://localhost:3000/generate

# 2. Interactuar con selector
- Click en "Selecciona departamento"
- Selecciona "Antioquia"
- En municipio, escribe "Med"
- Selecciona "Medellín"

# 3. Verificar datos guardados
- Consola: console.log(formData)
- Debe mostrar:
  {
    departamento: 'antioquia',
    departamento_name: 'Antioquia',
    municipio: 'medellin',
    municipio_name: 'Medellín'
  }
```

---

## ✅ Requisitos Completados

✅ Selector dependiente Departamento → Municipio
✅ JSON local con TODOS los departamentos y municipios de Colombia
✅ Municipio depende del departamento seleccionado
✅ Autocomplete elegante (búsqueda sin tildes)
✅ Componente reutilizable
✅ Preparado para futura conexión Firestore
✅ Guarda {departamento, municipio, y nombres}
✅ Interfaz moderna, rápida y responsive

---

## 🎉 ¡Listo para usar!

El selector está completamente integrado en el formulario de generación.
