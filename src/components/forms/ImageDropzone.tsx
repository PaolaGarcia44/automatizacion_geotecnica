'use client'

import { useState, useCallback } from 'react'
import { Upload, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ImageDropzoneProps {
  onImagesSelected?: (files: File[]) => void
  onImagesChange?: (files: File[]) => void
  maxFiles?: number
  maxSizePerFile?: number // in MB
}

export function ImageDropzone({
  onImagesSelected,
  onImagesChange,
  maxFiles = 5,
  maxSizePerFile = 10,
}: ImageDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [previews, setPreviews] = useState<
    Array<{ file: File; preview: string; id: string }>
  >([])
  const [errors, setErrors] = useState<string[]>([])

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files) return

      const newErrors: string[] = []
      const validFiles: File[] = []
      const newPreviews = [...previews]

      Array.from(files).forEach((file) => {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          newErrors.push(`${file.name} no es una imagen válida`)
          return
        }

        // Validate file size
        if (file.size > maxSizePerFile * 1024 * 1024) {
          newErrors.push(
            `${file.name} excede el tamaño máximo de ${maxSizePerFile}MB`
          )
          return
        }

        // Check max files
        if (newPreviews.length + validFiles.length >= maxFiles) {
          newErrors.push(`Máximo ${maxFiles} imágenes permitidas`)
          return
        }

        validFiles.push(file)

        // Create preview
        const preview = URL.createObjectURL(file)
        newPreviews.push({
          file,
          preview,
          id: Math.random().toString(36).substr(2, 9),
        })
      })

      setPreviews(newPreviews)
      setErrors(newErrors)
      onImagesSelected?.(validFiles)
      onImagesChange?.(newPreviews.map((item) => item.file))
    },
    [onImagesSelected, onImagesChange, maxFiles, maxSizePerFile, previews]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)
      handleFiles(e.dataTransfer.files)
    },
    [handleFiles]
  )

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files)
    },
    [handleFiles]
  )

  const removeImage = useCallback((id: string) => {
    setPreviews((prev) => {
      const image = prev.find((img) => img.id === id)
      if (image) {
        URL.revokeObjectURL(image.preview)
      }
      const next = prev.filter((img) => img.id !== id)
      onImagesChange?.(next.map((item) => item.file))
      return next
    })
  }, [onImagesChange])

  return (
    <div className='space-y-4'>
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          'relative rounded-lg border-2 border-dashed transition-all p-8',
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-secondary-200 bg-secondary-50 hover:border-secondary-300'
        )}
      >
        <input
          type='file'
          multiple
          {...({ webkitdirectory: '', directory: '' } as any)}
          accept='image/*'
          onChange={handleInputChange}
          className='hidden'
          id='image-input'
        />

        <label
          htmlFor='image-input'
          className='flex flex-col items-center justify-center gap-3 cursor-pointer'
        >
          <Upload className='h-8 w-8 text-secondary-400' />
          <div className='text-center'>
            <p className='text-sm font-medium text-secondary-900'>
              Arrastra una carpeta aquí o haz clic para seleccionarla
            </p>
            <p className='text-xs text-secondary-500 mt-1'>
              Máximo {maxFiles} imágenes, {maxSizePerFile}MB cada una
            </p>
          </div>
        </label>
      </div>

      {/* Errors */}
      {errors.length > 0 && (
        <div className='rounded-md bg-red-50 p-3 border border-red-200'>
          {errors.map((error, i) => (
            <p key={i} className='text-xs text-red-700'>
              • {error}
            </p>
          ))}
        </div>
      )}

      {/* Preview Grid */}
      {previews.length > 0 && (
        <div>
          <h3 className='text-sm font-medium text-secondary-900 mb-3'>
            Imágenes cargadas ({previews.length}/{maxFiles})
          </h3>
          <div className='grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4'>
            {previews.map((item) => (
              <div key={item.id} className='relative group'>
                <div className='relative w-full aspect-square rounded-lg overflow-hidden bg-secondary-100'>
                  <img
                    src={item.preview}
                    alt='Preview'
                    className='w-full h-full object-cover'
                  />
                  <Button
                    variant='destructive'
                    size='icon'
                    onClick={() => removeImage(item.id)}
                    className='absolute top-1 right-1 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity'
                  >
                    <X className='h-3 w-3' />
                  </Button>
                </div>
                <p className='text-xs text-secondary-600 mt-1 truncate'>
                  {item.file.name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
