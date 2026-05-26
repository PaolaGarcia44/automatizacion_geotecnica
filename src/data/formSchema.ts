// Form data structure for the Generate Automatización page
export interface FormData {
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

// Technical field options
export const technicalFieldOptions = [
  { value: 'geotecnia_general', label: 'Geotecnia General' },
  { value: 'mecanica_suelos', label: 'Mecánica de Suelos' },
  { value: 'cimentaciones', label: 'Cimentaciones' },
  { value: 'estabilidad_taludes', label: 'Estabilidad de Taludes' },
  { value: 'exploracion_geotecnica', label: 'Exploración Geotécnica' },
  { value: 'ensayos_laboratorio', label: 'Ensayos de Laboratorio' },
  { value: 'drenaje_impermeabilizacion', label: 'Drenaje e Impermeabilización' },
  { value: 'geotecnia_ambiental', label: 'Geotecnia Ambiental' },
]

// Document types that can be generated
export const documentTypes = [
  { id: 'informe', label: 'Informe Técnico' },
  { id: 'planos', label: 'Planos' },
  { id: 'especificaciones', label: 'Especificaciones' },
  { id: 'ensayos', label: 'Resultados de Ensayos' },
  { id: 'recomendaciones', label: 'Recomendaciones' },
]
