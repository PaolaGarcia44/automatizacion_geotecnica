'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  ClipboardList,
  Clock,
  Menu,
  ChevronLeft,
} from 'lucide-react'
import { useSidebar } from '@/hooks/useSidebar'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

const navItems = [
  {
    title: 'Generar',
    href: '/generate',
    icon: ClipboardList,
    description: 'Generar Automatización',
  },
  // {
  //   title: 'Historial',
  //   href: '/history',
  //   icon: Clock,
  //   description: 'Historial de Proyectos',
  // },
  // {
  //   title: 'IA',
  //   href: '/ai',
  //   icon: Zap,
  //   description: 'Asistente IA',
  // },
]

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, isMobile, toggle } = useSidebar()

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen border-r border-secondary-200 bg-white transition-all duration-300 ease-in-out',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Header */}
      <div className='flex h-16 items-center justify-between border-b border-secondary-200 px-4'>
        {!isCollapsed && (
          <h1 className='font-bold text-lg text-primary-600 truncate'>
            AutoGeo
          </h1>
        )}
        {!isMobile && (
          <Button
            variant='ghost'
            size='icon'
            onClick={toggle}
            className='ml-auto'
          >
            {isCollapsed ? (
              <ChevronLeft className='h-4 w-4' />
            ) : (
              <Menu className='h-4 w-4' />
            )}
          </Button>
        )}
        {isMobile && isCollapsed && (
          <Button
            variant='ghost'
            size='icon'
            onClick={toggle}
          >
            <Menu className='h-4 w-4' />
          </Button>
        )}
      </div>

      {/* Navigation */}
      <nav className='space-y-2 p-4'>
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'group relative flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:bg-primary-50',
                isActive
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-secondary-600 hover:text-secondary-900'
              )}
            >
              <Icon className='h-5 w-5 shrink-0' />
              {!isCollapsed && (
                <div className='flex flex-col overflow-hidden'>
                  <span className='text-sm font-medium'>{item.title}</span>
                  <span className='text-xs text-secondary-500 truncate'>
                    {item.description}
                  </span>
                </div>
              )}

              {/* Tooltip for collapsed state */}
              {isCollapsed && (
                <div className='absolute left-full ml-2 whitespace-nowrap rounded-md bg-secondary-900 px-2 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100'>
                  {item.title}
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className='absolute bottom-0 left-0 right-0 border-t border-secondary-200 bg-gradient-to-t from-secondary-50 to-transparent p-4'>
        {!isCollapsed && (
          <p className='text-xs text-secondary-500'>
            v1.0.0 — AutoGeo
          </p>
        )}
      </div>
    </aside>
  )
}
