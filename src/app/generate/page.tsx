
'use client'

import { useState } from 'react'
import { useFormData } from '@/hooks/useFormData'
import { generateDocuments } from '@/services/documentService'
import type { DepartmentMunicipalityValue } from '@/components/forms/DepartmentMunicipalitySelector'
import DepartmentMunicipalitySelector from '@/components/forms/DepartmentMunicipalitySelector'
import {
  Building2,
  MapPin,
  Layers3,
  Check,
  AlertCircle,
} from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function GenerarPage() {
  const { formData, updateField, updateDepartmentMunicipality, resetForm, isFormValid, isSubmitting, setIsSubmitting } = useFormData()
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'1' | '2' | '3' | ''>('')
  const [perforaciones, setPerforaciones] = useState<
    Array<{ numero: number; profundidad: string; tipo_suelo: string; observaciones: string }>
  >([
    { numero: 1, profundidad: '', tipo_suelo: '', observaciones: '' },
    { numero: 2, profundidad: '', tipo_suelo: '', observaciones: '' },
    { numero: 3, profundidad: '', tipo_suelo: '', observaciones: '' },
  ])

  const categorias = {
    '1': {
      titulo: 'Categoría 1: Hasta 3 pisos',
      carga: '500 kN',
      minPerforaciones: 3,
      profundidad: '6 m',
    },
    '2': {
      titulo: 'Categoría 2: Hasta 10 pisos',
      carga: '4000 kN',
      minPerforaciones: 4,
      profundidad: '15 m',
    },
    '3': {
      titulo: 'Categoría 3: Más de 10 pisos',
      carga: '> 4000 kN',
      minPerforaciones: 4,
      profundidad: '25 m',
    },
  }

  const handlePerforacionChange = (index: number, field: string, value: string) => {
    setPerforaciones((prev) =>
      prev.map((perf, idx) => {
        if (idx === index) {
          return {
            ...perf,
            [field]: value,
          }
        }
        return perf
      })
    )
  }

  const handleSubmit = async () => {
    if (!isFormValid() || !selectedCategory) {
      setErrorMessage('Por favor complete todos los campos requeridos')
      return
    }

    setIsSubmitting(true)
    setErrorMessage('')

    try {
      const perfData = perforaciones
        .filter((p) => p.profundidad)
        .map((p) => ({
          numero: p.numero,
          profundidad: typeof p.profundidad === 'string' ? parseFloat(p.profundidad) : p.profundidad,
          tipo_suelo: p.tipo_suelo,
          observaciones: p.observaciones,
        }))

      const response = await generateDocuments({
        nombre_proyecto: formData.nombre_proyecto,
        municipio: formData.municipio_name,
        fecha_registro: formData.fecha_inicio,
        categoria: selectedCategory,
        campo_n: formData.campo_n,
        descripcion: formData.descripcion,
        perforaciones: perfData,
        imagenes: [],
      })

      if (response.success) {
        setSuccessMessage(
          `✅ Documentos generados exitosamente!\nID: ${response.project_id}`
        )
        setShowSuccessModal(true)
        resetForm()
        setSelectedCategory('')
      } else {
        setErrorMessage(`Error: ${response.message}`)
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : 'Error desconocido al generar documentos'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <MainLayout>
      <div className='page-padding container-main space-y-8'>
        {/* Header */}
        <div>
          <h1 className='text-3xl font-bold text-gray-900 mb-2'>Generar Automatización</h1>
          <p className='text-gray-600'>Completa el formulario para generar documentos Excel automáticamente</p>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <Card className='border-red-200 bg-red-50'>
            <CardContent className='pt-6 flex gap-3'>
              <AlertCircle className='h-5 w-5 text-red-600 flex-shrink-0 mt-0.5' />
              <p className='text-red-700'>{errorMessage}</p>
            </CardContent>
          </Card>
        )}

        {/* General Info Section */}
        <Card className='border-gray-200'>
          <CardHeader className='bg-gray-50 border-b border-gray-200'>
            <CardTitle className='flex items-center gap-2 text-lg'>
              <Building2 className='h-5 w-5 text-green-600' />
              Información General
            </CardTitle>
          </CardHeader>
          <CardContent className='pt-6 space-y-4'>
            <div>
              <Label htmlFor='nombre'>Nombre del Proyecto</Label>
              <Input
                id='nombre'
                placeholder='Ej: Estudio Geotécnico Centro Medellín'
                value={formData.nombre_proyecto}
                onChange={(e) => updateField('nombre_proyecto', e.target.value)}
                className='mt-2'
              />
            </div>

            <DepartmentMunicipalitySelector
              value={{
                departamento: formData.departamento,
                departamento_name: formData.departamento_name,
                municipio: formData.municipio,
                municipio_name: formData.municipio_name,
              }}
              onChange={(value: DepartmentMunicipalityValue) => updateDepartmentMunicipality(value)}
              label='Ubicación del Proyecto'
              placeholder='Selecciona departamento y municipio'
            />

            <div className='grid grid-cols-2 gap-4'>
              <div>
                <Label htmlFor='fecha-inicio'>Fecha Registro</Label>
                <Input
                  id='fecha-inicio'
                  type='date'
                  value={formData.fecha_inicio}
                  onChange={(e) => updateField('fecha_inicio', e.target.value)}
                  className='mt-2'
                />
              </div>
              <div>
                <Label htmlFor='fecha-final'>Fecha Final (auto +20 días)</Label>
                <Input
                  id='fecha-final'
                  type='date'
                  value={formData.fecha_final}
                  disabled
                  className='mt-2 opacity-70'
                />
              </div>
            </div>

            <div>
              <Label htmlFor='campo-n'>Campo N</Label>
              <Input
                id='campo-n'
                placeholder='Ej: Suelo tipo C'
                value={formData.campo_n}
                onChange={(e) => updateField('campo_n', e.target.value)}
                className='mt-2'
              />
            </div>

            <div>
              <Label htmlFor='descripcion'>Descripción</Label>
              <textarea
                id='descripcion'
                placeholder='Descripción del proyecto'
                value={formData.descripcion}
                onChange={(e) => updateField('descripcion', e.target.value)}
                className='w-full mt-2 px-3 py-2 border border-gray-200 rounded-md'
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* Category Selection */}
        <Card className='border-gray-200'>
          <CardHeader className='bg-gray-50 border-b border-gray-200'>
            <CardTitle className='flex items-center gap-2 text-lg'>
              <Layers3 className='h-5 w-5 text-green-600' />
              Categoría del Proyecto
            </CardTitle>
          </CardHeader>
          <CardContent className='pt-6'>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              {Object.entries(categorias).map(([key, cat]) => (
                <button
                  key={key}
                  onClick={() => setSelectedCategory(key as '1' | '2' | '3')}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    selectedCategory === key
                      ? 'border-green-600 bg-green-50'
                      : 'border-gray-200 bg-white hover:border-green-400'
                  }`}
                >
                  <h3 className='font-semibold text-gray-900'>{cat.titulo}</h3>
                  <p className='text-sm text-gray-600 mt-1'>Carga: {cat.carga}</p>
                  <div className='flex gap-2 mt-3 text-xs'>
                    <span className='px-2 py-1 bg-gray-100 rounded'>
                      {cat.minPerforaciones} perf.
                    </span>
                    <span className='px-2 py-1 bg-gray-100 rounded'>{cat.profundidad}</span>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Perforaciones */}
        <Card className='border-gray-200'>
          <CardHeader className='bg-gray-50 border-b border-gray-200'>
            <CardTitle className='flex items-center gap-2 text-lg'>
              <MapPin className='h-5 w-5 text-green-600' />
              Perforaciones
            </CardTitle>
          </CardHeader>
          <CardContent className='pt-6'>
            <div className='overflow-x-auto'>
              <table className='w-full text-sm'>
                <thead>
                  <tr className='border-b border-gray-200'>
                    <th className='text-left py-2 font-semibold text-gray-700'>Num</th>
                    <th className='text-left py-2 font-semibold text-gray-700'>Profundidad (m)</th>
                    <th className='text-left py-2 font-semibold text-gray-700'>Tipo Suelo</th>
                    <th className='text-left py-2 font-semibold text-gray-700'>Observaciones</th>
                  </tr>
                </thead>
                <tbody>
                  {perforaciones.map((perf, idx) => (
                    <tr key={idx} className='border-b border-gray-100 hover:bg-gray-50'>
                      <td className='py-3'>{perf.numero}</td>
                      <td className='py-3'>
                        <Input
                          type='number'
                          placeholder='6.0'
                          value={perf.profundidad}
                          onChange={(e) => handlePerforacionChange(idx, 'profundidad', e.target.value)}
                          className='w-24'
                        />
                      </td>
                      <td className='py-3'>
                        <Input
                          placeholder='Arena'
                          value={perf.tipo_suelo}
                          onChange={(e) => handlePerforacionChange(idx, 'tipo_suelo', e.target.value)}
                          className='w-32'
                        />
                      </td>
                      <td className='py-3'>
                        <Input
                          placeholder='SPT=30'
                          value={perf.observaciones}
                          onChange={(e) => handlePerforacionChange(idx, 'observaciones', e.target.value)}
                          className='w-40'
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Submit Button */}
        <div className='flex justify-end gap-4'>
          <Button
            variant='outline'
            onClick={() => {
              resetForm()
              setSelectedCategory('')
            }}
          >
            Limpiar
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !selectedCategory}
            className='gap-2'
          >
            {isSubmitting ? (
              <>
                <div className='animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full' />
                Generando...
              </>
            ) : (
              <>
                <Check className='h-4 w-4' />
                Generar Documentos
              </>
            )}
          </Button>
        </div>

        {/* Success Modal */}
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


