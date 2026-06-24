'use client'

import { usePathname } from 'next/navigation'

export function Header() {
  const pathname = usePathname()

  const getBreadcrumb = () => {
    const segments: Record<string, string> = {
      '/generate': 'Generar Automatización',
      '/history': 'Historial',
      '/ai': 'Asistente IA',
    }
    return segments[pathname] || 'Dashboard'
  }

  return (
    <header className='h-16 border-b border-secondary-200 bg-white shadow-sm dark:border-secondary-700 dark:bg-secondary-800 dark:shadow-none'>
      <div className='flex h-full items-center px-6'>
        <h2 className='text-lg font-semibold text-secondary-900 dark:text-secondary-100'>
          {getBreadcrumb()}
        </h2>
      </div>
    </header>
  )
}
