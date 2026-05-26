'use client'

import { usePathname } from 'next/navigation'

interface HeaderProps {
  sidebarCollapsed?: boolean
}

export function Header({ sidebarCollapsed = false }: HeaderProps) {
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
    <header className='h-16 border-b border-secondary-200 bg-white shadow-sm'>
      <div className='flex h-full items-center justify-between px-6'>
        {/* Breadcrumb */}
        <div className='flex items-center gap-2'>
          <h2 className='text-lg font-semibold text-secondary-900'>
            {getBreadcrumb()}
          </h2>
        </div>
      </div>
    </header>
  )
}
