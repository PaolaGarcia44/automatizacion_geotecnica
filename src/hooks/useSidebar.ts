'use client'

import { useState, useCallback, useEffect } from 'react'

export const useSidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  // Initialize from localStorage
  useEffect(() => {
    setIsMounted(true)
    const stored = localStorage.getItem('sidebar-collapsed')
    if (stored !== null) {
      setIsCollapsed(JSON.parse(stored))
    }

    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  const toggle = useCallback(() => {
    setIsCollapsed((prev) => {
      const newValue = !prev
      localStorage.setItem('sidebar-collapsed', JSON.stringify(newValue))
      return newValue
    })
  }, [])

  const collapse = useCallback(() => {
    setIsCollapsed(true)
    localStorage.setItem('sidebar-collapsed', JSON.stringify(true))
  }, [])

  const expand = useCallback(() => {
    setIsCollapsed(false)
    localStorage.setItem('sidebar-collapsed', JSON.stringify(false))
  }, [])

  return {
    isCollapsed,
    isMobile,
    isMounted,
    toggle,
    collapse,
    expand,
  }
}
