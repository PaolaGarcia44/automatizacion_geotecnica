import { ReactNode } from 'react'
import { Card, CardContent } from '@/components/ui/card'

interface StatCardProps {
  title: string
  value: string | number
  icon: ReactNode
  description?: string
}

export function StatCard({ title, value, icon, description }: StatCardProps) {
  return (
    <Card className='border-secondary-200 hover:shadow-md transition-shadow'>
      <CardContent className='pt-6'>
        <div className='flex items-start justify-between'>
          <div>
            <p className='text-sm text-secondary-600 font-medium'>{title}</p>
            <p className='text-2xl font-bold text-secondary-900 mt-2'>{value}</p>
            {description && (
              <p className='text-xs text-secondary-500 mt-1'>{description}</p>
            )}
          </div>
          <div className='h-12 w-12 rounded-lg bg-primary-100 flex items-center justify-center text-primary-600'>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
