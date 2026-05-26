'use client'

import { useState, useMemo } from 'react'
import { getDepartments, getMunicipalitiesByDepartment, searchMunicipalities } from '@/data/colombia'
import { ChevronDown, Search, MapPin } from 'lucide-react'

export interface DepartmentMunicipalityValue {
  departamento: string
  departamento_name: string
  municipio: string
  municipio_name: string
}

interface DepartmentMunicipalityProps {
  value: DepartmentMunicipalityValue
  onChange: (value: DepartmentMunicipalityValue) => void
  label?: string
  placeholder?: string
}

export const DepartmentMunicipalitySelector: React.FC<DepartmentMunicipalityProps> = ({
  value,
  onChange,
  label = 'Ubicación Geográfica',
  placeholder = 'Selecciona departamento y municipio',
}) => {
  const [departmentOpen, setDepartmentOpen] = useState(false)
  const [municipalityOpen, setMunicipalityOpen] = useState(false)
  const [municipalitySearch, setMunicipalitySearch] = useState('')

  const departments = useMemo(() => getDepartments(), [])

  const municipalities = useMemo(
    () => getMunicipalitiesByDepartment(value.departamento),
    [value.departamento]
  )

  const filteredMunicipalities = useMemo(() => {
    if (!municipalitySearch) return municipalities
    return searchMunicipalities(municipalitySearch, value.departamento)
  }, [municipalities, municipalitySearch, value.departamento])

  const handleDepartmentSelect = (deptId: string, deptName: string) => {
    onChange({
      departamento: deptId,
      departamento_name: deptName,
      municipio: '',
      municipio_name: '',
    })
    setDepartmentOpen(false)
    setMunicipalitySearch('')
  }

  const handleMunicipalitySelect = (munId: string, munName: string) => {
    onChange({
      ...value,
      municipio: munId,
      municipio_name: munName,
    })
    setMunicipalityOpen(false)
    setMunicipalitySearch('')
  }

  const selectedDept = departments.find((d) => d.id === value.departamento)
  const selectedMun = municipalities.find((m) => m.id === value.municipio)

  return (
    <div className='space-y-4'>
      {label && (
        <div className='flex items-center gap-2'>
          <MapPin className='w-4 h-4 text-green-600' />
          <label className='text-sm font-medium text-gray-700'>{label}</label>
        </div>
      )}

      <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
        {/* Departamento Selector */}
        <div className='relative'>
          <button
            onClick={() => setDepartmentOpen(!departmentOpen)}
            className={`w-full px-4 py-2 border rounded-lg text-left flex items-center justify-between transition-all ${
              departmentOpen
                ? 'border-green-500 bg-green-50 ring-2 ring-green-200'
                : 'border-gray-200 bg-white hover:border-green-400'
            }`}
          >
            <span className={selectedDept ? 'text-gray-900' : 'text-gray-500'}>
              {selectedDept?.name || 'Selecciona departamento'}
            </span>
            <ChevronDown className={`w-4 h-4 transition-transform ${departmentOpen ? 'rotate-180' : ''}`} />
          </button>

          {departmentOpen && (
            <div className='absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto'>
              {departments.map((dept) => (
                <button
                  key={dept.id}
                  onClick={() => handleDepartmentSelect(dept.id, dept.name)}
                  className={`w-full px-4 py-2 text-left text-sm transition-colors ${
                    value.departamento === dept.id
                      ? 'bg-green-100 text-green-900 font-medium'
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  {dept.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Municipio Selector */}
        <div className='relative'>
          <div className='relative'>
            <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400' />
            <input
              type='text'
              placeholder={selectedDept ? 'Busca municipio...' : 'Selecciona departamento primero'}
              value={municipalitySearch}
              onChange={(e) => {
                setMunicipalitySearch(e.target.value)
                if (!municipalityOpen && value.departamento) {
                  setMunicipalityOpen(true)
                }
              }}
              onFocus={() => value.departamento && setMunicipalityOpen(true)}
              disabled={!value.departamento}
              className={`w-full pl-9 pr-4 py-2 border rounded-lg text-sm transition-all ${
                value.departamento
                  ? 'border-gray-200 bg-white focus:border-green-500 focus:ring-2 focus:ring-green-200'
                  : 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
              }`}
            />
          </div>

          {municipalityOpen && value.departamento && (
            <div className='absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-64 overflow-y-auto'>
              {filteredMunicipalities.length > 0 ? (
                filteredMunicipalities.map((mun) => (
                  <button
                    key={mun.id}
                    onClick={() => handleMunicipalitySelect(mun.id, mun.name)}
                    className={`w-full px-4 py-2 text-left text-sm transition-colors ${
                      value.municipio === mun.id
                        ? 'bg-green-100 text-green-900 font-medium'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    {mun.name}
                  </button>
                ))
              ) : (
                <div className='px-4 py-3 text-center text-sm text-gray-500'>
                  No hay municipios que coincidan
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Selected Display */}
      {value.departamento && value.municipio && (
        <div className='p-3 bg-green-50 border border-green-200 rounded-lg'>
          <p className='text-sm text-green-900'>
            <span className='font-medium'>{value.municipio_name}</span>
            <span className='text-green-700 mx-1'>-</span>
            <span className='text-green-700'>{value.departamento_name}</span>
          </p>
        </div>
      )}
    </div>
  )
}

export default DepartmentMunicipalitySelector
