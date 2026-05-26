/**
 * Document Generation Service
 * Conecta con FastAPI backend para generar documentos Excel
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface PerforacionData {
  numero: number
  profundidad: number
  tipo_suelo?: string
  observaciones?: string
}

export interface DocumentGenerationRequest {
  nombre_proyecto: string
  municipio: string
  fecha_registro: string
  categoria: string
  campo_n: string
  descripcion?: string
  perforaciones: PerforacionData[]
  imagenes?: string[]
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
