"use client"

import { useState } from 'react'
import { generateDocuments, buildDownloadUrl, downloadGeneratedFile, type PerforacionData } from '@/services/documentService'
import { Building2, Check, AlertCircle, Download, Plus, X } from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useSoilTypes } from '@/hooks/useSoilTypes'

// Expanded color options - much broader selection
const SOIL_COLOR_OPTIONS = [
  'Beige',
  'Café',
  'Café oscuro',
  'Café claro',
  'Café rojizo',
  'Amarillo',
  'Amarillo claro',
  'Amarillo oscuro',
  'Amarillo café',
  'Rojizo',
  'Rojo oscuro',
  'Blanco',
  'Blanco sucio',
  'Gris',
  'Gris claro',
  'Gris oscuro',
  'Gris azuloso',
  'Gris amarillento',
  'Naranja',
  'Naranja claro',
  'Naranja oscuro',
  'Verde',
  'Verde claro',
  'Verde oscuro',
  'Negro',
  'Negro verdoso',
  'Marrón',
  'Marrón claro',
  'Marrón oscuro',
  'Marrón rojizo',
  'Rojo',
  'Rosa',
  'Púrpura',
  'Violeta',
  'Azul',
  'Azul claro',
  'Azul oscuro',
  'Turquesa',
  'Cian',
  'Beis',
  'Crema',
  'Mostaza',
  'Ocre',
  'Siena',
  'Tostado',
  'Leonado',
  'Grisáceo',
  'Pardusco',
  'Oscuro',
  'Claro',
]

interface SoilLayerForm {
  profundidad_z: string
  tipo_suelo_principal: string
  color_predominante: string
}

const DEFAULT_SOIL_LAYERS: SoilLayerForm[] = [
  { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' },
  { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' },
  { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' },
]

export default function GenerarPage() {
  const { soilTypes, addSoilType, removeSoilType, isLoaded } = useSoilTypes()
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [downloadUrl, setDownloadUrl] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [proyectoUbicacion, setProyectoUbicacion] = useState('')
  const [cliente, setCliente] = useState('')
  const [fechaRegistro, setFechaRegistro] = useState('')
  const [pisos, setPisos] = useState<number | ''>('')
  const [soilLayers, setSoilLayers] = useState<SoilLayerForm[]>(DEFAULT_SOIL_LAYERS)
  const [images, setImages] = useState<File[] | null>(null)
  const [newSoilType, setNewSoilType] = useState('')
  const [showCustomSoilInput, setShowCustomSoilInput] = useState(false)

  const addSoilLayer = () => {
    setSoilLayers((prev) => [...prev, { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' }])
  }

  const removeSoilLayer = (index: number) => {
    setSoilLayers((prev) => prev.filter((_, i) => i !== index))
  }

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
      const perforaciones = soilLayers
        .map<PerforacionData | null>((layer, index) => {
          const profundidad = Number(layer.profundidad_z)
          const tipo = layer.tipo_suelo_principal.trim()
          const color = layer.color_predominante.trim()

          if (!tipo && !color && !layer.profundidad_z.trim()) {
            return null
          }

          const descripcion = tipo.trim()

          return {
            profundidad_z: Number.isFinite(profundidad) && profundidad > 0 ? profundidad : index + 1,
            gamma: null,
            n_campo_spt: 0,
            cohesion_c: null,
            descripcion_suelo: descripcion || color,
            tipo_suelo_principal: tipo || null,
            color_predominante: color || null,
          }
        })
        .filter((item): item is PerforacionData => item !== null)

      const payload = {
        // backend decidirá la plantilla según 'pisos' y generará perforaciones por defecto
        proyecto_ubicacion: proyectoUbicacion.toUpperCase(),
        cliente: cliente.trim(),
        fecha_registro: fechaRegistro,
        pisos: nPisos,
        template_ids: nPisos <= 3 ? ['4', '5', '6'] : ['4', '5', '6', '7'],
        perforaciones,
      }

      const response = await generateDocuments(payload, images ?? undefined)

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
      <div className='page-padding container-main min-h-full'>
        <div className='mx-auto flex max-w-4xl flex-col gap-8 py-4 sm:py-8'>
          <div className='text-center space-y-3'>
            <span className='inline-flex items-center rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 shadow-sm'>
              Generación automática
            </span>
            <h1 className='text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl'>Automatización geotécnica</h1>
            <p className='mx-auto max-w-2xl text-base text-gray-600 sm:text-lg'>
              Completa el formulario y genera una copia editable de la plantilla Excel seleccionada.
            </p>
          </div>

          {errorMessage && (
            <Card className='border-red-200 bg-red-50 shadow-sm'>
              <CardContent className='pt-6 flex gap-3'>
                <AlertCircle className='h-5 w-5 text-red-600 flex-shrink-0 mt-0.5' />
                <p className='text-red-700'>{errorMessage}</p>
              </CardContent>
            </Card>
          )}

          <Card className='border-gray-200 shadow-lg shadow-slate-200/50 overflow-hidden'>
            <CardHeader className='border-b border-gray-200 bg-slate-50/80'>
              <CardTitle className='text-center text-lg'>Imágenes</CardTitle>
            </CardHeader>
            <CardContent className='p-6 sm:p-8'>
              <p className='text-sm text-slate-500 mb-4'>
                Selecciona una carpeta con las imágenes del sondeo. Se incluirán en la carpeta ZIP dentro de la carpeta <em>imagenes</em>.
              </p>

              <div className='flex flex-col gap-3'>
                <input
                  id='imagenes-carpeta'
                  type='file'
                  multiple
                  accept='image/*'
                  {...({ webkitdirectory: '', directory: '' } as any)}
                  onChange={(e) => {
                    const files = e.target.files
                    if (!files) return
                    setImages(Array.from(files))
                  }}
                  className='sr-only'
                />

                <label
                  htmlFor='imagenes-carpeta'
                  className='inline-flex w-fit cursor-pointer items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50'
                >
                  Seleccionar carpeta de imágenes
                </label>

                <p className='text-sm text-slate-600'>
                  {images?.length ? `${images.length} imágenes seleccionadas` : 'Ninguna carpeta seleccionada aún'}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className='border-gray-200 shadow-xl shadow-slate-200/60 overflow-hidden'>
            <CardHeader className='border-b border-gray-200 bg-gradient-to-r from-slate-50 via-white to-emerald-50'>
              <CardTitle className='flex items-center justify-center gap-2 text-lg'>
                <Building2 className='h-5 w-5 text-green-600' />
                Datos mínimos para generación
              </CardTitle>
            </CardHeader>
            <CardContent className='space-y-6 p-6 sm:p-8'>
              <div className='space-y-2'>
                <Label htmlFor='proyecto-ubicacion'>Proyecto + ubicación</Label>
                <Input
                  id='proyecto-ubicacion'
                  placeholder='Ej: Construcción de una casa campestre de 2 niveles ubicada en ...'
                  value={proyectoUbicacion}
                  onChange={(e) => setProyectoUbicacion(e.target.value)}
                  className='h-12 rounded-xl border-slate-200 bg-white/90 shadow-sm'
                />
                <p className='text-sm text-gray-500'>Se guardará y enviará automáticamente en mayúsculas.</p>
              </div>

              <div className='space-y-2'>
                <Label htmlFor='cliente'>Cliente</Label>
                <Input
                  id='cliente'
                  placeholder='Ej: Constructora ABC S.A.S.'
                  value={cliente}
                  onChange={(e) => setCliente(e.target.value)}
                  className='h-12 rounded-xl border-slate-200 bg-white/90 shadow-sm'
                />
              </div>

              <div className='grid grid-cols-1 gap-4 sm:grid-cols-2'>
                <div className='space-y-2'>
                  <Label htmlFor='fecha-registro'>Fecha</Label>
                  <Input
                    id='fecha-registro'
                    type='date'
                    value={fechaRegistro}
                    onChange={(e) => setFechaRegistro(e.target.value)}
                    className='h-12 rounded-xl border-slate-200 bg-white/90 shadow-sm'
                  />
                </div>
                <div className='space-y-2'>
                  <Label htmlFor='pisos'>Pisos (número)</Label>
                  <Input
                    id='pisos'
                    type='number'
                    step='1'
                    min='0'
                    value={pisos === '' ? '' : String(pisos)}
                    onChange={(e) => setPisos(e.target.value === '' ? '' : Number(e.target.value))}
                    className='h-12 rounded-xl border-slate-200 bg-white/90 shadow-sm'
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className='border-slate-200/80 bg-white/90 shadow-lg shadow-slate-200/50 overflow-hidden'>
            <CardHeader className='border-b border-slate-200 bg-slate-50/80'>
              <CardTitle className='text-center text-lg'>Capas de suelo</CardTitle>
            </CardHeader>
            <CardContent className='space-y-4 p-6 sm:p-8'>
              <p className='text-center text-sm text-slate-500'>Selecciona el tipo de suelo y su color predominante para cada capa.</p>

              {/* Custom Soil Type Input */}
              <div className='bg-blue-50 border border-blue-200 rounded-lg p-4'>
                <button
                  type='button'
                  onClick={() => setShowCustomSoilInput(!showCustomSoilInput)}
                  className='inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700'
                >
                  <Plus className='h-4 w-4' />
                  {showCustomSoilInput ? 'Cancelar' : 'Agregar tipo de suelo personalizado'}
                </button>

                {showCustomSoilInput && (
                  <div className='mt-3 space-y-2'>
                    <Input
                      type='text'
                      placeholder='Ej: Arena roja con fragmentos de mica'
                      value={newSoilType}
                      onChange={(e) => setNewSoilType(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && newSoilType.trim()) {
                          addSoilType(newSoilType)
                          setNewSoilType('')
                          setShowCustomSoilInput(false)
                        }
                      }}
                      className='h-10 rounded-lg border-blue-300 bg-white text-sm'
                    />
                    <div className='flex gap-2'>
                      <Button
                        onClick={() => {
                          if (newSoilType.trim()) {
                            addSoilType(newSoilType)
                            setNewSoilType('')
                            setShowCustomSoilInput(false)
                          }
                        }}
                        className='h-8 bg-blue-600 text-white text-xs'
                      >
                        Guardar tipo
                      </Button>
                      <Button
                        onClick={() => setShowCustomSoilInput(false)}
                        className='h-8 bg-gray-300 text-gray-700 text-xs'
                      >
                        Cancelar
                      </Button>
                    </div>
                    <p className='text-xs text-gray-600'>
                      Se guardará automáticamente en tu navegador para futuras sesiones.
                    </p>
                  </div>
                )}
              </div>

              <div className='flex items-center justify-center mb-2'>
                <Button onClick={addSoilLayer} className='h-9 rounded-lg bg-emerald-600 text-white px-3 shadow-sm'>Agregar capa</Button>
              </div>
              <div className='grid gap-4'>
                {soilLayers.map((layer, index) => (
                  <div key={index} className='relative grid gap-3 rounded-2xl border border-slate-200 bg-slate-50/70 p-4 shadow-sm sm:grid-cols-[1.2fr_0.8fr]'>
                    <div className='absolute right-3 top-3'>
                      <button
                        type='button'
                        onClick={() => removeSoilLayer(index)}
                        className='inline-flex items-center justify-center rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700 hover:bg-red-100'
                        aria-label={`Eliminar capa ${index + 1}`}
                      >
                        Eliminar
                      </button>
                    </div>
                    <div className='space-y-2 sm:col-span-2'>
                      <Label htmlFor={`profundidad-${index}`}>Profundidad final (m) - Capa {index + 1}</Label>
                      <Input
                        id={`profundidad-${index}`}
                        type='number'
                        step='0.01'
                        min='0'
                        placeholder='Ej: 0.45'
                        value={layer.profundidad_z}
                        onChange={(e) => {
                          const next = [...soilLayers]
                          const current = next[index] ?? { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' }
                          next[index] = {
                            profundidad_z: e.target.value,
                            tipo_suelo_principal: current.tipo_suelo_principal,
                            color_predominante: current.color_predominante,
                          }
                          setSoilLayers(next)
                        }}
                        className='h-12 rounded-xl border-slate-200 bg-white shadow-sm'
                      />
                    </div>

                    <div className='space-y-2'>
                      <Label htmlFor={`tipo-suelo-${index}`}>Tipo de suelo - Capa {index + 1}</Label>
                      <select
                        id={`tipo-suelo-${index}`}
                        value={layer.tipo_suelo_principal}
                        onChange={(e) => {
                          const next = [...soilLayers]
                          const current = next[index] ?? { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' }
                          next[index] = {
                            profundidad_z: current.profundidad_z,
                            tipo_suelo_principal: e.target.value,
                            color_predominante: current.color_predominante,
                          }
                          setSoilLayers(next)
                        }}
                        disabled={!isLoaded}
                        className='h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm shadow-sm outline-none transition focus:border-blue-500 disabled:opacity-50'
                      >
                        <option value=''>{isLoaded ? 'Selecciona un tipo de suelo' : 'Cargando...'}</option>
                        {soilTypes.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className='space-y-2'>
                      <Label htmlFor={`color-suelo-${index}`}>Color predominante</Label>
                      <select
                        id={`color-suelo-${index}`}
                        value={layer.color_predominante}
                        onChange={(e) => {
                          const next = [...soilLayers]
                          const current = next[index] ?? { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' }
                          next[index] = {
                            profundidad_z: current.profundidad_z,
                            tipo_suelo_principal: current.tipo_suelo_principal,
                            color_predominante: e.target.value,
                          }
                          setSoilLayers(next)
                        }}
                        className='h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm shadow-sm outline-none transition focus:border-blue-500'
                      >
                        <option value=''>Selecciona un color</option>
                        {SOIL_COLOR_OPTIONS.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Perforaciones y parámetros no se solicitan en esta vista mínima; se preservan sin cambios en la plantilla */}

          <div className='flex flex-col items-center justify-center gap-3 sm:flex-row'>
            <Button
              variant='outline'
              onClick={() => {
                setProyectoUbicacion('')
                setFechaRegistro('')
                setPisos('')
                setSoilLayers(DEFAULT_SOIL_LAYERS.map((layer) => ({ ...layer })))
                setDownloadUrl('')
                setErrorMessage('')
                setSuccessMessage('')
              }}
              className='h-12 min-w-40 rounded-xl border-slate-300 bg-white/90 px-6 shadow-sm'
            >
              Limpiar
            </Button>

            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className='h-12 min-w-56 gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-slate-900 px-6 text-white shadow-lg shadow-blue-200 hover:from-blue-500 hover:to-slate-800'
              title='Genera una carpeta ZIP con varios Excel según el número de pisos'
            >
                <span className='inline-flex items-center gap-2'>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Generar carpeta ZIP
                </span>
            </Button>
          </div>
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
                  Descargar ZIP
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
