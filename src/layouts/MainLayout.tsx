'use client'

import { ReactNode } from 'react'
import { Sidebar } from '@/components/shared/Sidebar'
import { Header } from '@/components/shared/Header'
import { useSidebar } from '@/hooks/useSidebar'
import { cn } from '@/lib/utils'

interface MainLayoutProps {
  children: ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  const { isCollapsed, isMounted } = useSidebar()

  if (!isMounted) {
    return null
  }

  return (
    <div className='flex h-screen bg-secondary-50'>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div
        className={cn(
          'flex flex-1 flex-col min-h-0 transition-all duration-300 ease-in-out',
          isCollapsed ? 'ml-20' : 'ml-64'
        )}
      >
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className='flex-1 min-h-0 overflow-y-auto'>
          {children}
        </main>
      </div>
    </div>
  )
}
