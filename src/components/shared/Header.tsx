'use client'

import { usePathname } from 'next/navigation'
import { User, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/button'

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

        {/* User Menu */}
        <div className='flex items-center gap-3'>
          <Button variant='ghost' size='icon' className='relative'>
            <User className='h-5 w-5 text-secondary-600' />
          </Button>
          <div className='h-8 w-px bg-secondary-200' />
          <Button variant='ghost' size='sm' className='gap-2'>
            <LogOut className='h-4 w-4' />
            <span className='hidden sm:inline text-sm'>Logout</span>
          </Button>
        </div>
      </div>
    </header>
  )
}
