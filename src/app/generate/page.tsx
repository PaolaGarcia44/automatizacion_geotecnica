"use client"

import { useState } from 'react'
import { generateDocuments, buildDownloadUrl, downloadGeneratedFile } from '@/services/documentService'
import { Building2, Check, AlertCircle, Download } from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// Minimal form: Proyecto, Fecha y Pisos

export default function GenerarPage() {
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [downloadUrl, setDownloadUrl] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [proyectoUbicacion, setProyectoUbicacion] = useState('')
  const [fechaRegistro, setFechaRegistro] = useState('')
  const [pisos, setPisos] = useState<number | ''>('')

  // helper removed: this minimal form doesn't parse numeric tables

  const handleSubmit = async () => {
    if (!proyectoUbicacion.trim() || !fechaRegistro) {
      setErrorMessage('Por favor complete Proyecto y Fecha')
      return
    }

    if (pisos === '' || Number(pisos) < 0) {
      setErrorMessage('Ingrese un número válido de pisos')
      return
    }

    setIsSubmitting(true)
    setErrorMessage('')
    setDownloadUrl('')

    try {
      const nPisos = Number(pisos)

      const payload = {
        // backend decidirá la plantilla según 'pisos' y generará perforaciones por defecto
        proyecto_ubicacion: proyectoUbicacion.toUpperCase(),
        fecha_registro: fechaRegistro,
        pisos: nPisos,
      }

      const response = await generateDocuments(payload)

      if (response.success) {
        setSuccessMessage(`✅ Documentos generados exitosamente!\nID: ${response.project_id}`)
        setDownloadUrl(buildDownloadUrl(response.download_url))
        setShowSuccessModal(true)

        if (response.download_url) {
          await downloadGeneratedFile(response.download_url)
        }
      } else {
        setErrorMessage(`Error: ${response.message}`)
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Error desconocido al generar documentos')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <MainLayout>
      <div className='page-padding container-main space-y-8'>
        <div>
          <h1 className='text-3xl font-bold text-gray-900 mb-2'>Automatización geotécnica</h1>
          <p className='text-gray-600'>Completa el formulario y genera una copia editable de la plantilla Excel seleccionada.</p>
        </div>

        {errorMessage && (
          <Card className='border-red-200 bg-red-50'>
            <CardContent className='pt-6 flex gap-3'>
              <AlertCircle className='h-5 w-5 text-red-600 flex-shrink-0 mt-0.5' />
              <p className='text-red-700'>{errorMessage}</p>
            </CardContent>
          </Card>
        )}

        <Card className='border-gray-200'>
          <CardHeader className='bg-gray-50 border-b border-gray-200'>
            <CardTitle className='flex items-center gap-2 text-lg'>
              <Building2 className='h-5 w-5 text-green-600' />
              Datos mínimos para generación
            </CardTitle>
          </CardHeader>
          <CardContent className='pt-6 space-y-4'>
            <div>
              <Label htmlFor='proyecto-ubicacion'>Proyecto + ubicación</Label>
              <Input
                id='proyecto-ubicacion'
                placeholder='Ej: Construcción de una casa campestre de 2 niveles ubicada en ...'
                value={proyectoUbicacion}
                onChange={(e) => setProyectoUbicacion(e.target.value)}
                className='mt-2'
              />
              <p className='mt-2 text-sm text-gray-500'>Se guardará y enviará automáticamente en mayúsculas.</p>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              <div>
                <Label htmlFor='fecha-registro'>Fecha</Label>
                <Input
                  id='fecha-registro'
                  type='date'
                  value={fechaRegistro}
                  onChange={(e) => setFechaRegistro(e.target.value)}
                  className='mt-2'
                />
              </div>
              <div>
                <Label htmlFor='pisos'>Pisos (número)</Label>
                <Input
                  id='pisos'
                  type='number'
                  step='1'
                  min='0'
                  value={pisos === '' ? '' : String(pisos)}
                  onChange={(e) => setPisos(e.target.value === '' ? '' : Number(e.target.value))}
                  className='mt-2'
                />
              </div>
              {/* Rule text removed per UX request */}
            </div>
          </CardContent>
        </Card>

        {/* Perforaciones y parámetros no se solicitan en esta vista mínima; se preservan sin cambios en la plantilla */}

        <div className='flex justify-end gap-4'>
          <Button
            variant='outline'
            onClick={() => {
              setProyectoUbicacion('')
              setFechaRegistro('')
              setPisos('')
              setDownloadUrl('')
              setErrorMessage('')
              setSuccessMessage('')
            }}
          >
            Limpiar
          </Button>

          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className='gap-2 bg-blue-600 text-white hover:bg-blue-700'
            title='Genera el Excel usando las perforaciones automáticas según pisos'
          >
            <>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Generar Excel (automatizado)
            </>
          </Button>
        </div>

        <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
          <DialogContent className='sm:max-w-md'>
            <div className='flex flex-col items-center gap-4 py-6'>
              <div className='w-12 h-12 bg-green-100 rounded-full flex items-center justify-center'>
                <Check className='h-6 w-6 text-green-600' />
              </div>
              <h2 className='text-lg font-semibold text-gray-900'>
                ¡Documentos Generados!
              </h2>
              <p className='text-center text-gray-600 whitespace-pre-line'>{successMessage}</p>
              {downloadUrl && (
                <Button onClick={() => downloadGeneratedFile(downloadUrl)} className='w-full gap-2'>
                  <Download className='h-4 w-4' />
                  Descargar Excel
                </Button>
              )}
              <Button onClick={() => setShowSuccessModal(false)} className='w-full'>
                Cerrar
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  )
}
