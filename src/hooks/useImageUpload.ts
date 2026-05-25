'use client'

import { useState, useCallback } from 'react'

export interface UploadedImage {
  file: File
  preview: string
  id: string
}

export const useImageUpload = () => {
  const [images, setImages] = useState<UploadedImage[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const addImages = useCallback((files: File[]) => {
    setIsUploading(true)
    try {
      const newImages = files.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
        id: Math.random().toString(36).substr(2, 9),
      }))

      setImages((prev) => [...prev, ...newImages])
    } finally {
      setIsUploading(false)
    }
  }, [])

  const removeImage = useCallback((id: string) => {
    setImages((prev) => {
      const image = prev.find((img) => img.id === id)
      if (image) {
        URL.revokeObjectURL(image.preview)
      }
      return prev.filter((img) => img.id !== id)
    })
  }, [])

  const clearImages = useCallback(() => {
    images.forEach((image) => {
      URL.revokeObjectURL(image.preview)
    })
    setImages([])
  }, [images])

  const validateFiles = useCallback(
    (files: FileList | File[]): { valid: File[]; errors: string[] } => {
      const errors: string[] = []
      const validFiles: File[] = []
      const maxSize = 10 * 1024 * 1024 // 10MB
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/tiff']

      Array.from(files).forEach((file) => {
        if (file.size > maxSize) {
          errors.push(`${file.name} excede el tamaño máximo de 10MB`)
        } else if (!allowedTypes.includes(file.type)) {
          errors.push(`${file.name} tiene un formato no soportado`)
        } else {
          validFiles.push(file)
        }
      })

      return { valid: validFiles, errors }
    },
    []
  )

  return {
    images,
    isUploading,
    addImages,
    removeImage,
    clearImages,
    validateFiles,
  }
}
