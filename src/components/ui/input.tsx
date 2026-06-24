import * as React from 'react'

import { cn } from '@/lib/utils'

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={cn(
        'flex h-10 w-full rounded-md border border-secondary-200 bg-white px-3 py-2 text-sm text-secondary-900 placeholder:text-secondary-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:border-transparent disabled:cursor-not-allowed disabled:bg-secondary-50 disabled:text-secondary-400 transition-colors dark:border-secondary-600 dark:bg-secondary-700 dark:text-secondary-100 dark:placeholder:text-secondary-500 dark:disabled:bg-secondary-800 dark:focus:ring-offset-secondary-800',
        className
      )}
      ref={ref}
      {...props}
    />
  )
)
Input.displayName = 'Input'

export { Input }
