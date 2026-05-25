'use client'

import { useState } from 'react'
import {
  Calendar,
  AlertCircle,
  Loader2,
  CheckCircle,
} from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { FormCard } from '@/components/forms/FormCard'
import { ImageDropzone } from '@/components/forms/ImageDropzone'
import { MunicipioAutocomplete } from '@/components/forms/MunicipioAutocomplete'
import { useFormData } from '@/hooks/useFormData'
import { technicalFieldOptions } from '@/data/formSchema'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

export default function GeneratePage() {
  const {
    formData,
    updateField,
    addImage,
    removeImage,
    resetForm,
    isFormValid,
    isSubmitting,
    setIsSubmitting,
  } = useFormData()

  const [showSuccess, setShowSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!isFormValid()) {
      return
    }

    setIsSubmitting(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000))

      console.log('Form submitted:', formData)
      setShowSuccess(true)

      // Reset after showing success
      setTimeout(() => {
        resetForm()
        setShowSuccess(false)
      }, 3000)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <MainLayout>
      <div className='page-padding container-main'>
        {/* Page Header */}
        <div className='mb-8'>
          <h1 className='text-3xl font-bold text-secondary-900 mb-2'>
            Generar Automatización
          </h1>
          <p className='text-secondary-600'>
            Completa el formulario para generar documentos geotécnicos
            automáticamente
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className='space-y-6 max-w-4xl'>
          {/* Section 1: Información General */}
          <FormCard
            title='Información General'
            description='Detalles básicos del proyecto'
          >
            <div className='space-y-6'>
              <div>
                <Label htmlFor='nombre_proyecto' className='text-base mb-2'>
                  Nombre del Proyecto *
                </Label>
                <Input
                  id='nombre_proyecto'
                  placeholder='Ej: Estudio Geotécnico - Medellín'
                  value={formData.nombre_proyecto}
                  onChange={(e) =>
                    updateField('nombre_proyecto', e.target.value)
                  }
                  disabled={isSubmitting}
                  required
                />
              </div>

              <div>
                <Label htmlFor='municipio' className='text-base mb-2'>
                  Municipio *
                </Label>
                <MunicipioAutocomplete
                  value={formData.municipio}
                  onChange={(value) => updateField('municipio', value)}
                />
              </div>

              <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div>
                  <Label htmlFor='fecha_inicio' className='text-base mb-2'>
                    Fecha de Inicio *
                  </Label>
                  <div className='relative'>
                    <Calendar className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400 pointer-events-none' />
                    <Input
                      id='fecha_inicio'
                      type='date'
                      value={formData.fecha_inicio}
                      onChange={(e) =>
                        updateField('fecha_inicio', e.target.value)
                      }
                      disabled={isSubmitting}
                      className='pl-10'
                      required
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor='fecha_final' className='text-base mb-2'>
                    Fecha Final (Auto-calculada)
                  </Label>
                  <div className='relative'>
                    <Calendar className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400 pointer-events-none' />
                    <Input
                      id='fecha_final'
                      type='date'
                      value={formData.fecha_final}
                      disabled
                      className='pl-10 bg-secondary-50'
                    />
                  </div>
                  <p className='text-xs text-secondary-500 mt-1'>
                    Se calcula automáticamente como 20 días después de la fecha
                    de inicio
                  </p>
                </div>
              </div>

              <div>
                <Label htmlFor='descripcion' className='text-base mb-2'>
                  Descripción (Opcional)
                </Label>
                <Textarea
                  id='descripcion'
                  placeholder='Descripción adicional del proyecto...'
                  value={formData.descripcion}
                  onChange={(e) => updateField('descripcion', e.target.value)}
                  disabled={isSubmitting}
                  rows={4}
                />
              </div>
            </div>
          </FormCard>

          <Separator />

          {/* Section 2: Información Técnica */}
          <FormCard
            title='Información Técnica'
            description='Especificaciones técnicas del proyecto'
          >
            <div className='space-y-4'>
              <div>
                <Label htmlFor='campo_n' className='text-base mb-2'>
                  Tipo de Estudio *
                </Label>
                <Select
                  value={formData.campo_n}
                  onValueChange={(value) => updateField('campo_n', value)}
                  disabled={isSubmitting}
                >
                  <SelectTrigger id='campo_n'>
                    <SelectValue placeholder='Selecciona un tipo de estudio' />
                  </SelectTrigger>
                  <SelectContent>
                    {technicalFieldOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </FormCard>

          <Separator />

          {/* Section 3: Carga de Imágenes */}
          <FormCard
            title='Carga de Imágenes'
            description='Sube las imágenes o documentos visuales del proyecto'
          >
            <ImageDropzone
              onImagesSelected={(files) => {
                files.forEach((file) => addImage(file))
              }}
              maxFiles={5}
              maxSizePerFile={10}
            />
          </FormCard>

          {/* Form Actions */}
          <div className='flex justify-end gap-3 pt-6 border-t border-secondary-200'>
            <Button
              type='button'
              variant='outline'
              onClick={resetForm}
              disabled={isSubmitting}
            >
              Limpiar
            </Button>
            <Button
              type='submit'
              disabled={!isFormValid() || isSubmitting}
              className='gap-2'
            >
              {isSubmitting ? (
                <>
                  <Loader2 className='h-4 w-4 animate-spin' />
                  Generando...
                </>
              ) : (
                'Generar Documentos'
              )}
            </Button>
          </div>
        </form>
      </div>

      {/* Success Dialog */}
      <Dialog open={showSuccess} onOpenChange={setShowSuccess}>
        <DialogContent>
          <DialogHeader>
            <div className='flex items-center gap-3 mb-2'>
              <CheckCircle className='h-6 w-6 text-green-600' />
              <DialogTitle>¡Éxito!</DialogTitle>
            </div>
            <DialogDescription>
              Los documentos se han generado correctamente. Pronto podrás
              descargarlos desde tu historial.
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </MainLayout>
  )
}
