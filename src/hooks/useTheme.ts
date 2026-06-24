'use client'

import { useState, useCallback, useEffect } from 'react'

// Acceso tipado a la API de Electron expuesta por preload.js
declare global {
  interface Window {
    electronAPI?: {
      isElectron?: boolean
      onThemeSet?: (cb: (theme: string) => void) => void
      notifyThemeChanged?: (theme: string) => void
    }
  }
}

function applyThemeToDom(dark: boolean) {
  if (dark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

export const useTheme = () => {
  const [isDark, setIsDark] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)

    // Default: modo claro a menos que haya preferencia guardada
    const stored = localStorage.getItem('theme')
    const dark = stored === 'dark'
    setIsDark(dark)
    applyThemeToDom(dark)

    // Escuchar cambios de tema desde el menú nativo de Electron
    window.electronAPI?.onThemeSet?.((theme) => {
      const isDarkTheme = theme === 'dark'
      setIsDark(isDarkTheme)
      localStorage.setItem('theme', theme)
      applyThemeToDom(isDarkTheme)
    })
  }, [])

  const setTheme = useCallback((dark: boolean) => {
    const theme = dark ? 'dark' : 'light'
    setIsDark(dark)
    localStorage.setItem('theme', theme)
    applyThemeToDom(dark)
    // Notificar al proceso principal para actualizar el checkmark del menú
    window.electronAPI?.notifyThemeChanged?.(theme)
  }, [])

  const toggle = useCallback(() => {
    setIsDark((prev) => {
      const next = !prev
      const theme = next ? 'dark' : 'light'
      localStorage.setItem('theme', theme)
      applyThemeToDom(next)
      window.electronAPI?.notifyThemeChanged?.(theme)
      return next
    })
  }, [])

  return { isDark, isMounted, toggle, setTheme }
}
