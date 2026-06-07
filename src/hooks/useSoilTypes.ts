'use client'

import { useEffect, useState } from 'react'

const STORAGE_KEY = 'custom-soil-types'

const DEFAULT_SOIL_TYPES = [
  'Capa vegetal con raíces y material orgánico',
  'Capa vegetal húmeda con presencia de raíces finas',
  'Material orgánico color negro de consistencia blanda',
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
  'Limo arenoso color gris amarillento',
  'Limo arenoso húmedo de baja plasticidad',
  'Limo arcilloso color café claro',
  'Limo orgánico húmedo color negro',
  'Limo fino saturado de color gris oscuro',
  'Grava arenosa con cantos rodados pequeños',
  'Grava limosa de compacidad media',
  'Grava fina mezclada con arena amarilla',
  'Material granular húmedo y compacto',
  'Material aluvial compuesto por arena y grava',
  'Material de relleno heterogéneo con fragmentos pétreos',
  'Material de relleno con presencia de escombros',
  'Suelo residual de roca meteorizada',
  'Suelo residual arenoso de origen ígneo',
  'Suelo residual arcilloso color naranja',
  'Suelo residual con fragmentos de cuarzo',
  'Suelo residual parcialmente meteorizado',
  'Roca meteorizada color café amarillento',
  'Roca fracturada parcialmente meteorizada',
  'Roca alterada con presencia de humedad',
  'Ceniza volcánica mezclada con arena fina',
  'Arena fina con presencia de ceniza volcánica',
  'Material residual arcilloso de color rojizo',
  'Arena limosa compacta de color amarillo oscuro',
  'Arcilla con presencia de óxidos de hierro',
  'Suelo limo arenoso de baja plasticidad',
  'Arena arcillosa medianamente compacta',
  'Material granular con humedad natural moderada',
  'Arcilla húmeda con fragmentos meteorizados',
  'Arena fina beige con grava dispersa',
  'Arcilla café amarillenta de consistencia rígida',
  'Material limo arcilloso parcialmente saturado',
  'Suelo residual compacto con gravas finas',
]

export function useSoilTypes() {
  const [soilTypes, setSoilTypes] = useState<string[]>(DEFAULT_SOIL_TYPES)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const customTypes = JSON.parse(stored) as string[]
        // Merge default types with custom types (remove duplicates)
        const merged = Array.from(new Set([...DEFAULT_SOIL_TYPES, ...customTypes]))
        setSoilTypes(merged)
      }
    } catch (error) {
      console.error('Error loading soil types from localStorage:', error)
    }
    setIsLoaded(true)
  }, [])

  // Add new custom soil type
  const addSoilType = (type: string) => {
    const trimmed = type.trim()
    if (!trimmed) return

    const updated = Array.from(new Set([...soilTypes, trimmed]))
    setSoilTypes(updated)

    // Get custom types only (excluding defaults)
    const customTypes = updated.filter((t) => !DEFAULT_SOIL_TYPES.includes(t))
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(customTypes))
    } catch (error) {
      console.error('Error saving soil types to localStorage:', error)
    }
  }

  // Remove custom soil type
  const removeSoilType = (type: string) => {
    if (DEFAULT_SOIL_TYPES.includes(type)) {
      console.warn('Cannot remove default soil type:', type)
      return
    }

    const updated = soilTypes.filter((t) => t !== type)
    setSoilTypes(updated)

    // Update localStorage
    const customTypes = updated.filter((t) => !DEFAULT_SOIL_TYPES.includes(t))
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(customTypes))
    } catch (error) {
      console.error('Error updating soil types in localStorage:', error)
    }
  }

  return {
    soilTypes,
    addSoilType,
    removeSoilType,
    isLoaded,
  }
}
