'use client'

import { useState, useCallback, useMemo } from 'react'
import { ChevronDown, Search } from 'lucide-react'
import { municipios } from '@/data/municipios'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface MunicipioAutocompleteProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export function MunicipioAutocomplete({
  value,
  onChange,
  placeholder = 'Selecciona un municipio...',
}: MunicipioAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  const filteredMunicipios = useMemo(() => {
    if (!searchTerm) return municipios
    return municipios.filter((m) =>
      m.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [searchTerm])

  const handleSelect = useCallback(
    (municipio: string) => {
      onChange(municipio)
      setIsOpen(false)
      setSearchTerm('')
    },
    [onChange]
  )

  return (
    <div className='relative'>
      <div className='relative'>
        <Input
          type='text'
          placeholder={placeholder}
          value={value || searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value)
            setIsOpen(true)
          }}
          onFocus={() => setIsOpen(true)}
          className='pr-10'
        />
        <Button
          variant='ghost'
          size='icon'
          className='absolute right-0 top-1/2 -translate-y-1/2'
          onClick={() => setIsOpen(!isOpen)}
        >
          <ChevronDown className='h-4 w-4 text-secondary-400' />
        </Button>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className='absolute top-full left-0 right-0 z-50 mt-2 max-h-60 rounded-md border border-secondary-200 bg-white shadow-md overflow-hidden'>
          {/* Search Box */}
          <div className='border-b border-secondary-200 p-2 sticky top-0 bg-white'>
            <div className='relative'>
              <Search className='absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400' />
              <Input
                type='text'
                placeholder='Buscar municipio...'
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className='pl-8'
                autoFocus
              />
            </div>
          </div>

          {/* Options */}
          <div className='max-h-52 overflow-y-auto'>
            {filteredMunicipios.length > 0 ? (
              filteredMunicipios.map((municipio) => (
                <button
                  key={municipio}
                  onClick={() => handleSelect(municipio)}
                  className={cn(
                    'w-full px-3 py-2 text-left text-sm transition-colors hover:bg-primary-50',
                    value === municipio
                      ? 'bg-primary-100 text-primary-700 font-medium'
                      : 'text-secondary-900'
                  )}
                >
                  {municipio}
                </button>
              ))
            ) : (
              <div className='px-3 py-8 text-center text-sm text-secondary-500'>
                No se encontraron municipios
              </div>
            )}
          </div>
        </div>
      )}

      {/* Backdrop to close */}
      {isOpen && (
        <div
          className='fixed inset-0 z-40'
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}
