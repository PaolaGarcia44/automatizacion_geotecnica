import { ReactNode } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

interface FormCardProps {
  title: string
  description?: string
  children: ReactNode
}

export function FormCard({ title, description, children }: FormCardProps) {
  return (
    <Card className='border-secondary-200'>
      <CardHeader>
        <CardTitle className='text-lg'>{title}</CardTitle>
        {description && (
          <CardDescription className='text-secondary-600'>
            {description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}
