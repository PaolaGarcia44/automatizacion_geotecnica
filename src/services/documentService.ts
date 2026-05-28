/**
 * Document Generation Service
 * Conecta con FastAPI backend para generar documentos Excel
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface PerforacionData {
  profundidad_z: number
  gamma?: number | null
  n_campo_spt: number
  cohesion_c?: number | null
  descripcion_suelo: string
  tipo_suelo_principal?: string | null
  color_predominante?: string | null
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
  perforaciones?: PerforacionData[]
  template_id?: string
  template_ids?: string[]
}

export interface DocumentGenerationResponse {
  success: boolean
  message: string
  project_id?: string
  files?: string[]
  download_url?: string
  timestamp?: string
}

function formatApiError(detail: unknown): string {
  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }

        if (item && typeof item === 'object') {
          const message = (item as { msg?: unknown; message?: unknown; loc?: unknown }).msg ?? (item as { msg?: unknown; message?: unknown; loc?: unknown }).message
          const location = (item as { loc?: unknown }).loc
          const locationText = Array.isArray(location) ? location.join(' > ') : ''
          if (typeof message === 'string' && locationText) {
            return `${locationText}: ${message}`
          }
          if (typeof message === 'string') {
            return message
          }
        }

        return JSON.stringify(item)
      })
      .join(' | ')
  }

  if (detail && typeof detail === 'object') {
    const maybeMessage = (detail as { detail?: unknown; message?: unknown }).detail ?? (detail as { message?: unknown }).message
    if (maybeMessage) {
      return formatApiError(maybeMessage)
    }
    return JSON.stringify(detail)
  }

  return 'Error desconocido al generar documentos'
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
      throw new Error(formatApiError(error.detail ?? error.message ?? error))
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
  const urlPath = (() => {
    try {
      return new URL(buildDownloadUrl(downloadUrl)).pathname
    } catch {
      return downloadUrl
    }
  })()
  const filename = decodeURIComponent(urlPath.split('/').pop() || 'CORRELACIÓN GEOTÉCNICA DE PARÁMETROS GEOMECÁNICOS.zip')
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.URL.revokeObjectURL(objectUrl)
}
