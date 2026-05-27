/**
 * Document Generation Service
 * Conecta con FastAPI backend para generar documentos Excel
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface PerforacionData {
  profundidad_z: number
  gamma: number
  n_campo_spt: number
  cohesion_c?: number | null
  descripcion_suelo: string
}

export interface ParametroRangoData {
  rango_profundidad: string
  gamma?: number | null
  c?: number | null
  phi?: number | null
  nu?: number | null
  e?: number | null
  unidad_geologica?: string | null
}

export interface DocumentGenerationRequest {
  proyecto_ubicacion: string
  fecha_registro: string
  pisos: number
}

export interface DocumentGenerationResponse {
  success: boolean
  message: string
  project_id?: string
  files?: string[]
  download_url?: string
  timestamp?: string
}

/**
 * Generar documentos geotécnicos mediante FastAPI backend
 * Envía datos del formulario y recibe Excel modificado
 */
export const generateDocuments = async (
  request: DocumentGenerationRequest
): Promise<DocumentGenerationResponse> => {
  try {
    console.log('📤 Enviando solicitud al backend...', request)

    const response = await fetch(`${API_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Error al generar documentos')
    }

    const data: DocumentGenerationResponse = await response.json()
    console.log('✅ Documentos generados exitosamente:', data)

    return data
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Error desconocido'
    console.error('❌ Error en generación:', message)

    return {
      success: false,
      message: `Error: ${message}`,
    }
  }
}

/**
 * Obtener estado de las plantillas disponibles
 */
export const getTemplatesStatus = async (): Promise<{
  status: string
  templates?: Record<string, unknown>
  info?: Record<string, unknown>
}> => {
  try {
    const response = await fetch(`${API_URL}/api/templates/status`)

    if (!response.ok) {
      throw new Error('Error al obtener estado de plantillas')
    }

    return await response.json()
  } catch (error) {
    console.error('Error:', error)
    return { status: 'error' }
  }
}

/**
 * Verificar salud del backend
 */
export const healthCheck = async (): Promise<{
  status: string
  service?: string
  version?: string
}> => {
  try {
    const response = await fetch(`${API_URL}/api/health`)

    if (!response.ok) {
      throw new Error('Backend no disponible')
    }

    return await response.json()
  } catch (error) {
    console.error('Health check error:', error)
    return { status: 'offline' }
  }
}

export const buildDownloadUrl = (downloadUrl?: string): string => {
  if (!downloadUrl) {
    return ''
  }

  if (downloadUrl.startsWith('http://') || downloadUrl.startsWith('https://')) {
    return downloadUrl
  }

  return `${API_URL}${downloadUrl}`
}

export const downloadGeneratedFile = async (downloadUrl?: string): Promise<void> => {
  if (!downloadUrl) {
    throw new Error('No hay archivo para descargar')
  }

  const response = await fetch(buildDownloadUrl(downloadUrl))

  if (!response.ok) {
    throw new Error('No se pudo descargar el archivo generado')
  }

  const blob = await response.blob()
  const objectUrl = window.URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = objectUrl
  anchor.download = 'CORRELACIÓN GEOTÉCNICA DE PARÁMETROS GEOMECÁNICOS.xlsx'
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(objectUrl)
}
