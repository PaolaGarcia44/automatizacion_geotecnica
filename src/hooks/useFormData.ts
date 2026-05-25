'use client'

import { useState, useCallback } from 'react'
import type { FormData } from '@/data/formSchema'

const INITIAL_FORM_DATA: FormData = {
  nombre_proyecto: '',
  municipio: '',
  fecha_inicio: '',
  fecha_final: '',
  descripcion: '',
  campo_n: '',
  imagenes: [],
}

export const useFormData = () => {
  const [formData, setFormData] = useState<FormData>(INITIAL_FORM_DATA)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const updateField = useCallback(
    (field: keyof FormData, value: unknown) => {
      setFormData((prev) => {
        const updated = { ...prev, [field]: value }
        
        // Auto-calculate fecha_final if fecha_inicio changes
        if (field === 'fecha_inicio' && typeof value === 'string') {
          const startDate = new Date(value)
          const endDate = new Date(startDate)
          endDate.setDate(endDate.getDate() + 20)
          updated.fecha_final = endDate.toISOString().split('T')[0]
        }
        
        return updated
      })
    },
    []
  )

  const addImage = useCallback((file: File) => {
    setFormData((prev) => ({
      ...prev,
      imagenes: [...prev.imagenes, file],
    }))
  }, [])

  const removeImage = useCallback((index: number) => {
    setFormData((prev) => ({
      ...prev,
      imagenes: prev.imagenes.filter((_, i) => i !== index),
    }))
  }, [])

  const resetForm = useCallback(() => {
    setFormData(INITIAL_FORM_DATA)
  }, [])

  const isFormValid = useCallback((): boolean => {
    return (
      formData.nombre_proyecto.trim() !== '' &&
      formData.municipio.trim() !== '' &&
      formData.fecha_inicio !== '' &&
      formData.campo_n !== ''
    )
  }, [formData])

  return {
    formData,
    updateField,
    addImage,
    removeImage,
    resetForm,
    isFormValid,
    isSubmitting,
    setIsSubmitting,
  }
}
