"use client"

import { useState, useEffect, useRef } from 'react'
import { generateDocuments, getWordMunicipios, buildDownloadUrl, downloadGeneratedFile, type PerforacionData, type WordMunicipio } from '@/services/documentService'
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

const USCS_OPTIONS = [
  { value: '',   label: 'Automático (valores genéricos)' },
  { value: 'ML', label: 'ML — Limo de baja plasticidad (LL ≤ 50, bajo la línea A)' },
  { value: 'MH', label: 'MH — Limo de alta plasticidad (LL > 50, bajo la línea A)' },
  { value: 'CL', label: 'CL — Arcilla de baja plasticidad (LL ≤ 50, sobre la línea A)' },
  { value: 'CH', label: 'CH — Arcilla de alta plasticidad (LL > 50, sobre la línea A)' },
  { value: 'SM', label: 'SM / C — Arena limosa / Suelo no plástico (IP < 4)' },
]

interface ClasificacionesPorLab {
  lab1: string
  lab2: string
  lab3: string
  lab4: string
}

const DEFAULT_CLASIFICACIONES: ClasificacionesPorLab = { lab1: '', lab2: '', lab3: '', lab4: '' }

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

const FORM_STORAGE_KEY = 'autogeo-form'

// Static fallback list — works without backend connection
const MUNICIPIOS_ESTATICOS: string[] = [
  'Abejorral','Abriaquí','Alejandría','Amagá','Andes','Angostura','Anzá',
  'Apartadó','Arboletes','Argelia','Barbosa','Bello','Betania','Betulia',
  'Briceño','Buriticá','Cáceres','Caicedo','Caldas','Campamento','Cañasgordas',
  'Caracolí','Caramanta','Carepa','El Carmen','El Carmen de Viboral',
  'Carolina','Caucasia','Chigorodó','Cisneros','Cocorná','Concepción',
  'Concordia','Copacabana','Dabeiba','Don Matías','Ebéjico','El Bagre',
  'Entrerríos','Envigado','Fredonia','Frontino','Giraldo','Girardota',
  'Gómez Plata','Granada','Guadalupe','Guarne','Guatapé','Heliconia',
  'Hispania','Itagüí','Ituango','Jardín','Jericó','La Ceja','La Estrella',
  'La Pintada','La Unión','Liborina','Maceo','Marinilla','Medellín',
  'Montebello','Murindó','Mutatá','Nechí','Necoclí','Olaya','El Peñol',
  'Peque','Pueblorrico','Puerto Berrío','Puerto Nare','Puerto Triunfo',
  'Remedios','El Retiro','Rionegro','Sabaneta','Salgar','San Andrés de Cuerquia',
  'San Carlos','San Francisco','San Jerónimo','San José de la Montaña',
  'San Juan de Urabá','San Luis','San Pedro','San Rafael','San Roque',
  'San Vicente','Santa Bárbara','Santa Fe de Antioquia','Santa Rosa',
  'Santo Domingo','El Santuario','Santuario','Segovia','Sonsón','Sopetrán',
  'Támesis','Tarazá','Tarso','Titiribí','Toledo','Turbo','Uramita','Urrao',
  'Valdivia','Valparaíso','Vegachí','Venecia','Vigía del Fuerte','Yalí',
  'Yarumal','Yolombó','Yondó','Zaragoza','Angélópolis',
  'San Antonio de Prado','Santa Elena','San Cristóbal','Altavista','Llanogrande',
  'Buga','Puerto Boyacá',
]

interface MunicipioOption { name: string; filename?: string }

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
  const [clasificacionGeneral, setClasificacionGeneral] = useState('')
  const [personalizarPorLab, setPersonalizarPorLab] = useState(false)
  const [clasificacionesPorLab, setClasificacionesPorLab] = useState<ClasificacionesPorLab>(DEFAULT_CLASIFICACIONES)
  const [newSoilType, setNewSoilType] = useState('')
  const [showCustomSoilInput, setShowCustomSoilInput] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Municipality autocomplete state
  const [munInput, setMunInput] = useState('')
  const [munOption, setMunOption] = useState<MunicipioOption | null>(null)
  const [munDropdownOpen, setMunDropdownOpen] = useState(false)
  const [munOptions, setMunOptions] = useState<MunicipioOption[]>(
    MUNICIPIOS_ESTATICOS.map((n) => ({ name: n }))
  )

  // Fetch from backend to enrich with filenames; fallback = static list
  useEffect(() => {
    getWordMunicipios().then((list) => {
      if (!list.length) return
      const backendMap = new Map(list.map((m) => [m.municipio.toLowerCase(), m.filename]))
      const merged: MunicipioOption[] = MUNICIPIOS_ESTATICOS.map((name) => ({
        name,
        filename: backendMap.get(name.toLowerCase()),
      }))
      list.forEach((m) => {
        const key = m.municipio.toLowerCase()
        if (!MUNICIPIOS_ESTATICOS.some((s) => s.toLowerCase() === key))
          merged.push({ name: m.municipio, filename: m.filename })
      })
      setMunOptions(merged.sort((a, b) => a.name.localeCompare(b.name, 'es')))
    })
  }, [])

  const munSuggestions = munInput.trim().length === 0
    ? []
    : munOptions
        .filter((m) => m.name.toLowerCase().includes(munInput.toLowerCase()))
        .slice(0, 20)

  // Restore form data from sessionStorage after mount (client-only, avoids hydration mismatch)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(FORM_STORAGE_KEY)
      if (!raw) return
      const d = JSON.parse(raw)
      if (d.proyectoUbicacion) setProyectoUbicacion(d.proyectoUbicacion)
      if (d.cliente) setCliente(d.cliente)
      if (d.fechaRegistro) setFechaRegistro(d.fechaRegistro)
      if (d.pisos !== undefined && d.pisos !== '') setPisos(d.pisos)
      if (Array.isArray(d.soilLayers) && d.soilLayers.length > 0) setSoilLayers(d.soilLayers)
      if (d.clasificacionGeneral) setClasificacionGeneral(d.clasificacionGeneral)
      if (d.personalizarPorLab !== undefined) setPersonalizarPorLab(d.personalizarPorLab)
      if (d.clasificacionesPorLab) setClasificacionesPorLab(d.clasificacionesPorLab)
    } catch {}
  }, [])

  // Save form data to sessionStorage on every change
  useEffect(() => {
    try {
      sessionStorage.setItem(FORM_STORAGE_KEY, JSON.stringify({
        proyectoUbicacion, cliente, fechaRegistro, pisos,
        soilLayers, clasificacionGeneral, personalizarPorLab, clasificacionesPorLab,
      }))
    } catch {}
  }, [proyectoUbicacion, cliente, fechaRegistro, pisos, soilLayers, clasificacionGeneral, personalizarPorLab, clasificacionesPorLab])

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

    if (!images || images.length === 0) {
      setErrorMessage('Debe seleccionar una carpeta de imágenes antes de generar el ZIP')
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
        clasificacion_suelo: personalizarPorLab ? undefined : (clasificacionGeneral || undefined),
        clasificaciones_por_lab: personalizarPorLab
          ? { '4': clasificacionesPorLab.lab1, '5': clasificacionesPorLab.lab2, '6': clasificacionesPorLab.lab3, '7': clasificacionesPorLab.lab4 }
          : undefined,
        // Municipality for the Word informe
        municipio_word: (munOption?.name || munInput.trim()) || undefined,
        word_template_filename: munOption?.filename || undefined,
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
      <div className='page-padding container-main'>
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

              {/* ── Municipio del informe Word — autocomplete ──────────────── */}
              <div className='border-t border-slate-100 pt-5 space-y-2'>
                <Label>Municipio del informe Word</Label>
                <p className='text-xs text-slate-500'>
                  Escribe el nombre del municipio. Si existe plantilla propia se usará automáticamente; si no, se usará la plantilla base.
                </p>

                <div className='relative'>
                  <Input
                    placeholder='Ej: Rionegro, El Retiro, Envigado...'
                    value={munInput}
                    autoComplete='off'
                    onChange={(e) => {
                      setMunInput(e.target.value)
                      setMunOption(null)
                      setMunDropdownOpen(true)
                    }}
                    onFocus={() => setMunDropdownOpen(true)}
                    onBlur={() => setTimeout(() => setMunDropdownOpen(false), 150)}
                    className='h-11 rounded-xl border-slate-200 bg-white/90 shadow-sm pr-9'
                  />
                  {munInput && (
                    <button
                      type='button'
                      onMouseDown={() => { setMunInput(''); setMunOption(null) }}
                      className='absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600'
                    >
                      <X className='h-4 w-4' />
                    </button>
                  )}

                  {munDropdownOpen && munSuggestions.length > 0 && (
                    <div className='absolute z-50 mt-1 w-full rounded-xl border border-slate-200 bg-white shadow-lg overflow-hidden'>
                      <div className='max-h-52 overflow-y-auto'>
                        {munSuggestions.map((m, i) => (
                          <button
                            key={i}
                            type='button'
                            onMouseDown={() => {
                              setMunInput(m.name)
                              setMunOption(m)
                              setMunDropdownOpen(false)
                            }}
                            className={`w-full text-left px-4 py-2.5 text-sm transition-colors flex items-center justify-between gap-2 ${
                              munOption?.name === m.name
                                ? 'bg-emerald-50 text-emerald-800 font-medium'
                                : 'text-slate-700 hover:bg-slate-50'
                            }`}
                          >
                            <span>{m.name}</span>
                            {m.filename && (
                              <span className='text-xs text-emerald-600 bg-emerald-50 border border-emerald-200 rounded-full px-2 py-0.5 whitespace-nowrap'>
                                plantilla disponible
                              </span>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {munOption?.filename && (
                  <p className='flex items-center gap-1.5 text-xs text-emerald-700 font-medium'>
                    <Check className='h-3.5 w-3.5' />
                    Se usará la plantilla Word de <strong>{munOption.name}</strong>
                  </p>
                )}
                {munInput.trim() && !munOption && (
                  <p className='text-xs text-slate-500'>
                    Municipio personalizado — se usará la plantilla base con el nombre &ldquo;{munInput.trim()}&rdquo;
                  </p>
                )}
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

          {/* Clasificación de suelo USCS */}
          <Card className='border-gray-200 shadow-lg shadow-slate-200/50 overflow-hidden'>
            <CardHeader className='border-b border-gray-200 bg-slate-50/80'>
              <CardTitle className='text-center text-lg'>Clasificación de suelo (Laboratorio)</CardTitle>
            </CardHeader>
            <CardContent className='p-6 sm:p-8 space-y-5'>
              {/* Clasificación general */}
              <div className='space-y-2'>
                <Label htmlFor='clasificacion-general'>Clasificación USCS (General)</Label>
                <p className='text-xs text-slate-500'>Se aplica a todos los laboratorios del informe.</p>
                <select
                  id='clasificacion-general'
                  value={clasificacionGeneral}
                  onChange={(e) => setClasificacionGeneral(e.target.value)}
                  className='h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm shadow-sm outline-none transition focus:border-blue-500'
                >
                  {USCS_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </div>

              {/* Toggle personalización */}
              <label className='flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 select-none'>
                <input
                  type='checkbox'
                  checked={personalizarPorLab}
                  onChange={(e) => setPersonalizarPorLab(e.target.checked)}
                  className='h-4 w-4 rounded accent-blue-600'
                />
                <span className='text-sm font-medium text-slate-700'>Personalizar clasificación por laboratorio</span>
              </label>

              {/* Selectores individuales */}
              {personalizarPorLab && (
                <div className='grid gap-3 sm:grid-cols-2'>
                  {(['lab1', 'lab2', 'lab3', 'lab4'] as const).map((key, idx) => (
                    <div key={key} className='space-y-1'>
                      <Label htmlFor={`clf-${key}`} className='text-xs'>
                        Laboratorio {idx + 1}{idx === 3 ? <span className='ml-1 text-slate-400'>(solo &gt;3 pisos)</span> : null}
                      </Label>
                      <select
                        id={`clf-${key}`}
                        value={clasificacionesPorLab[key]}
                        onChange={(e) =>
                          setClasificacionesPorLab((prev) => ({ ...prev, [key]: e.target.value }))
                        }
                        className='h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-xs shadow-sm outline-none transition focus:border-blue-500'
                      >
                        {USCS_OPTIONS.map((o) => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className='border-gray-200 shadow-lg shadow-slate-200/50 overflow-hidden'>
            <CardHeader className='border-b border-gray-200 bg-slate-50/80'>
              <CardTitle className='text-center text-lg'>Imágenes</CardTitle>
            </CardHeader>
            <CardContent className='p-6 sm:p-8'>
              <p className='text-sm text-slate-500 mb-4'>
                Selecciona una carpeta con las imágenes del sondeo. Se incluirán en la carpeta ZIP dentro de la carpeta <em>imagenes</em>.
                <span className='text-red-500 font-medium'> Obligatorio para generar el ZIP.</span>
              </p>

              <div className='flex flex-col gap-3'>
                {/* Input fixed at top-left so the browser never scrolls to it when focused */}
                <input
                  ref={fileInputRef}
                  type='file'
                  multiple
                  {...({ webkitdirectory: '', directory: '' } as any)}
                  onChange={(e) => {
                    const files = e.target.files
                    if (!files) return
                    setImages(Array.from(files))
                  }}
                  className='fixed left-0 top-0 h-px w-px opacity-0 pointer-events-none'
                  tabIndex={-1}
                />

                <button
                  type='button'
                  onClick={() => fileInputRef.current?.click()}
                  className='inline-flex w-fit cursor-pointer items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50'
                >
                  Seleccionar carpeta de imágenes
                </button>

                <p className={`text-sm ${images?.length ? 'text-green-600 font-medium' : 'text-red-500'}`}>
                  {images?.length ? `${images.length} imágenes seleccionadas` : 'Ninguna carpeta seleccionada — requerida para continuar'}
                </p>
              </div>
            </CardContent>
          </Card>

          <div className='flex flex-col items-center justify-center gap-3 sm:flex-row'>
            <Button
              variant='outline'
              onClick={() => {
                try { sessionStorage.removeItem(FORM_STORAGE_KEY) } catch {}
                setProyectoUbicacion('')
                setCliente('')
                setFechaRegistro('')
                setPisos('')
                setSoilLayers(DEFAULT_SOIL_LAYERS.map((layer) => ({ ...layer })))
                setClasificacionGeneral('')
                setPersonalizarPorLab(false)
                setClasificacionesPorLab(DEFAULT_CLASIFICACIONES)
                setImages(null)
                setDownloadUrl('')
                setErrorMessage('')
                setSuccessMessage('')
                setMunInput('')
                setMunOption(null)
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
