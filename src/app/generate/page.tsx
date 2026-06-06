"use client"

import { useState } from 'react'
import { generateDocuments, buildDownloadUrl, downloadGeneratedFile, type PerforacionData } from '@/services/documentService'
import { Building2, Check, AlertCircle, Download } from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// Minimal form: Proyecto, Fecha y Pisos

const SOIL_TYPE_OPTIONS = [
  // Capas vegetales y materia orgánica
  'Capa vegetal con raíces y material orgánico',
  'Capa vegetal húmeda con presencia de raíces finas',
  'Material orgánico color negro de consistencia blanda',
  'Capa de turba oscura con alto contenido orgánico',
  'Materia orgánica descompuesta de color marrón',
  'Suelo orgánico con presencia de raicillas',
  
  // Arcillas y variantes
  'Arcilla limosa color café oscuro de consistencia media',
  'Arcilla limosa color café rojizo de consistencia firme',
  'Arcilla limosa húmeda de color gris oscuro',
  'Arcilla arenosa color amarillo café',
  'Arcilla arenosa color rojizo de consistencia media',
  'Arcilla arenosa compacta con fragmentos de roca',
  'Arcilla de alta plasticidad color café oscuro',
  'Arcilla firme parcialmente meteorizada',
  'Arcilla blanda con vetas limosas',
  'Arcilla gris azulosa de consistencia firme',
  'Arcilla con presencia de óxidos de hierro',
  'Arcilla roja de alta plasticidad',
  'Arcilla verdosa con laminaciones',
  'Arcilla compacta color gris claro',
  'Arcilla consolidada con fracturas minerales',
  'Arcilla expansiva de color rojo oscuro',
  'Arcilla café amarillenta de consistencia rígida',
  'Arcilla gris con vetas de arena',
  'Arcilla plástica con fragmentos de mica',
  
  // Arenas y variantes
  'Arena limosa color amarillo café medianamente compacta',
  'Arena limosa fina de color beige claro',
  'Arena limosa húmeda con contenido de grava fina',
  'Arena fina compacta color amarillo claro',
  'Arena fina color café claro de compacidad media',
  'Arena fina limosa con humedad moderada',
  'Arena gruesa con contenido de grava',
  'Arena gruesa compacta color café amarillento',
  'Arena arcillosa color naranja de compacidad media',
  'Arena arcillosa húmeda con fragmentos de roca',
  'Arena media compacta color beige',
  'Arena suelta con contenido limoso',
  'Arena fina beige con grava dispersa',
  'Arena limosa compacta de color amarillo oscuro',
  'Arena arcillosa medianamente compacta',
  'Arena fina con presencia de ceniza volcánica',
  'Arena muy fina color gris claro',
  'Arena con mica plateada',
  'Arena rojiza con óxidos de hierro',
  'Arena cuarcítica blanca compacta',
  'Arena negra con minerales magnéticos',
  'Arena silícea medianamente densa',
  
  // Limos y variantes
  'Limo arenoso color gris amarillento',
  'Limo arenoso húmedo de baja plasticidad',
  'Limo arcilloso color café claro',
  'Limo orgánico húmedo color negro',
  'Limo fino saturado de color gris oscuro',
  'Limo color marrón claro de baja compacidad',
  'Limo arenoso con mica fina',
  'Material limo arcilloso parcialmente saturado',
  'Suelo limo arenoso de baja plasticidad',
  
  // Gravas y variantes
  'Grava arenosa con cantos rodados pequeños',
  'Grava limosa de compacidad media',
  'Grava fina mezclada con arena amarilla',
  'Grava gruesa subangular color café',
  'Grava con matriz arenosa color gris',
  'Grava subredondeada con contenido de limo',
  'Grava bien gradada color marrón oscuro',
  'Grava de cantos rodados con arena fina',
  'Grava arenosa compacta color beige',
  'Grava limosa con contenido de arcilla',
  
  // Materiales granulares y rellenos
  'Material granular húmedo y compacto',
  'Material granular con humedad natural moderada',
  'Material aluvial compuesto por arena y grava',
  'Material de relleno heterogéneo con fragmentos pétreos',
  'Material de relleno con presencia de escombros',
  'Material de relleno color café con residuos',
  'Material de relleno compactado regularmente',
  'Material granular sin tratar color gris',
  'Relleno de demolición con ladrillo y concreto',
  'Relleno sanitario compactado',
  
  // Rocas y material meteorizado
  'Suelo residual de roca meteorizada',
  'Suelo residual arenoso de origen ígneo',
  'Suelo residual arcilloso color naranja',
  'Suelo residual con fragmentos de cuarzo',
  'Suelo residual parcialmente meteorizado',
  'Roca meteorizada color café amarillento',
  'Roca fracturada parcialmente meteorizada',
  'Roca alterada con presencia de humedad',
  'Roca gneis parcialmente descompuesta',
  'Roca esquisto descompuesta color gris',
  'Roca granito meteorizado con feldespato',
  'Roca arenisca descompuesta color rojizo',
  'Material residual compacto con gravas finas',
  'Saprolito de roca cristalina',
  'Roca sedimentaria meteorizada',
  
  // Cenizas volcánicas
  'Ceniza volcánica mezclada con arena fina',
  'Ceniza volcánica pura color gris claro',
  'Ceniza volcánica consolidada',
  'Ceniza volcánica con presencia de pómez',
  
  // Suelos especiales
  'Suelo con alto contenido de sílice',
  'Suelo con presencia de calcita',
  'Suelo con cementación débil',
  'Suelo con contenido de sal marina',
  'Suelo expansivo de color rojo',
]

const SOIL_COLOR_OPTIONS = [
  'Beige',
  'Café',
  'Café oscuro',
  'Amarillo',
  'Amarillo claro',
  'Amarillo oscuro',
  'Rojizo',
  'Naranja',
  'Naranja oscuro',
  'Blanco',
  'Gris claro',
  'Gris oscuro',
  'Verde',
  'Marrón',
  'Marrón oscuro',
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
  const [customSoilType, setCustomSoilType] = useState('')
  const [customSoilTypes, setCustomSoilTypes] = useState<string[]>([])
  const [images, setImages] = useState<File[] | null>(null)

  const addSoilLayer = () => {
    setSoilLayers((prev) => [...prev, { profundidad_z: '', tipo_suelo_principal: '', color_predominante: '' }])
  }

  const removeSoilLayer = (index: number) => {
    setSoilLayers((prev) => prev.filter((_, i) => i !== index))
  }

  const addCustomSoilType = () => {
    const trimmed = customSoilType.trim()
    if (trimmed && !customSoilTypes.includes(trimmed)) {
      setCustomSoilTypes((prev) => [...prev, trimmed])
      setCustomSoilType('')
    }
  }

  const removeCustomSoilType = (index: number) => {
    setCustomSoilTypes((prev) => prev.filter((_, i) => i !== index))
  }

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
        custom_soil_types: customSoilTypes,
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
              <CardTitle className='text-center text-lg'>Tipos de suelo personalizados</CardTitle>
            </CardHeader>
            <CardContent className='space-y-4 p-6 sm:p-8'>
              <p className='text-center text-sm text-slate-500'>Agrega tipos de suelo adicionales no incluidos en la lista predeterminada.</p>
              <div className='flex gap-2'>
                <Input
                  placeholder='Ej: Suelo arenoso con grava gruesa'
                  value={customSoilType}
                  onChange={(e) => setCustomSoilType(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addCustomSoilType()
                    }
                  }}
                  className='h-12 rounded-xl border-slate-200 bg-white shadow-sm'
                />
                <Button 
                  onClick={addCustomSoilType} 
                  className='h-12 rounded-xl bg-blue-600 text-white px-4 shadow-sm'
                >
                  Agregar
                </Button>
              </div>
              {customSoilTypes.length > 0 && (
                <div className='flex flex-wrap gap-2 pt-2'>
                  {customSoilTypes.map((type, index) => (
                    <span 
                      key={index}
                      className='inline-flex items-center gap-2 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700'
                    >
                      {type}
                      <button
                        type='button'
                        onClick={() => removeCustomSoilType(index)}
                        className='hover:text-blue-900'
                        aria-label='Remover'
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className='border-slate-200/80 bg-white/90 shadow-lg shadow-slate-200/50 overflow-hidden'>
            <CardHeader className='border-b border-slate-200 bg-slate-50/80'>
              <CardTitle className='text-center text-lg'>Capas de suelo</CardTitle>
            </CardHeader>
            <CardContent className='space-y-4 p-6 sm:p-8'>
              <p className='text-center text-sm text-slate-500'>Selecciona el tipo de suelo y su color predominante para cada capa.</p>
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
                        className='h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm shadow-sm outline-none transition focus:border-blue-500'
                      >
                        <option value=''>Selecciona un tipo de suelo</option>
                        <optgroup label='Tipos predefinidos'>
                          {SOIL_TYPE_OPTIONS.map((option) => (
                            <option key={option} value={option}>{option}</option>
                          ))}
                        </optgroup>
                        {customSoilTypes.length > 0 && (
                          <optgroup label='Tipos personalizados'>
                            {customSoilTypes.map((option) => (
                              <option key={option} value={option}>{option}</option>
                            ))}
                          </optgroup>
                        )}
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
                          <option key={option} value={option}>{option}</option>
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
