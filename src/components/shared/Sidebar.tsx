'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  ClipboardList,
  Menu,
  ChevronLeft,
  Sun,
  Moon,
} from 'lucide-react'
import { useSidebar } from '@/hooks/useSidebar'
import { useTheme } from '@/hooks/useTheme'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

const navItems = [
  {
    title: 'Generar',
    href: '/generate',
    icon: ClipboardList,
    description: 'Generar Automatización',
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, isMobile, toggle } = useSidebar()
  const { isDark, isMounted, setTheme } = useTheme()

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen border-r border-secondary-200 bg-white dark:border-secondary-700 dark:bg-secondary-800 transition-all duration-300 ease-in-out',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Header */}
      <div className='flex h-16 items-center justify-between border-b border-secondary-200 dark:border-secondary-700 px-4'>
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
      <nav className='space-y-2 p-4 pb-28'>
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'group relative flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:bg-primary-50 dark:hover:bg-primary-900/20',
                isActive
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                  : 'text-secondary-600 hover:text-secondary-900 dark:text-secondary-400 dark:hover:text-secondary-100'
              )}
            >
              <Icon className='h-5 w-5 shrink-0' />
              {!isCollapsed && (
                <div className='flex flex-col overflow-hidden'>
                  <span className='text-sm font-medium'>{item.title}</span>
                  <span className='text-xs text-secondary-500 dark:text-secondary-500 truncate'>
                    {item.description}
                  </span>
                </div>
              )}

              {isCollapsed && (
                <div className='absolute left-full ml-2 whitespace-nowrap rounded-md bg-secondary-900 px-2 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100'>
                  {item.title}
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Footer — Opciones */}
      <div className='absolute bottom-0 left-0 right-0 border-t border-secondary-200 dark:border-secondary-700 bg-white dark:bg-secondary-800 p-4'>
        {isCollapsed ? (
          isMounted && (
            <button
              onClick={() => setTheme(!isDark)}
              title={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
              className='flex items-center justify-center w-8 h-8 rounded-lg text-secondary-500 dark:text-secondary-400 hover:bg-secondary-100 dark:hover:bg-secondary-700 mx-auto transition-colors'
            >
              {isDark ? <Sun className='h-4 w-4' /> : <Moon className='h-4 w-4' />}
            </button>
          )
        ) : (
          <div className='space-y-3'>
            <p className='text-xs text-secondary-500 dark:text-secondary-400'>
              v1.0.0 — AutoGeo
            </p>
            {isMounted && (
              <div>
                <p className='text-xs font-medium text-secondary-400 dark:text-secondary-500 mb-1.5'>
                  Apariencia
                </p>
                <div className='flex rounded-lg border border-secondary-200 dark:border-secondary-600 bg-secondary-50 dark:bg-secondary-900 p-0.5 gap-0.5'>
                  <button
                    onClick={() => setTheme(false)}
                    className={cn(
                      'flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-all',
                      !isDark
                        ? 'bg-white shadow-sm text-secondary-900'
                        : 'text-secondary-400 hover:text-secondary-600 dark:hover:text-secondary-300'
                    )}
                  >
                    <Sun className='h-3 w-3' />
                    Claro
                  </button>
                  <button
                    onClick={() => setTheme(true)}
                    className={cn(
                      'flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium transition-all',
                      isDark
                        ? 'bg-secondary-700 shadow-sm text-secondary-100'
                        : 'text-secondary-400 hover:text-secondary-600'
                    )}
                  >
                    <Moon className='h-3 w-3' />
                    Oscuro
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}
