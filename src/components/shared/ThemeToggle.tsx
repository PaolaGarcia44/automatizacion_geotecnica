'use client'

import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { Button } from '@/components/ui/button'

export function ThemeToggle() {
  const { isDark, isMounted, toggle } = useTheme()

  if (!isMounted) return null

  return (
    <Button
      variant='ghost'
      size='icon'
      onClick={toggle}
      title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      className='text-secondary-600 hover:text-secondary-900 dark:text-secondary-400 dark:hover:text-secondary-100'
    >
      {isDark ? <Sun className='h-4 w-4' /> : <Moon className='h-4 w-4' />}
    </Button>
  )
}
