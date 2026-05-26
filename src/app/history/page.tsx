'use client'

import { useState } from 'react'
import {
  Download,
  Eye,
  FileText,
  TrendingUp,
  Search,
  Filter,
} from 'lucide-react'
import { MainLayout } from '@/layouts/MainLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { StatCard } from '@/components/history/StatCard'

// Sample data for the table
const sampleProjects = [
  {
    id: 1,
    nombre: 'Estudio Geotécnico - Centro',
    municipio: 'Medellín',
    fecha: '2024-05-20',
    descargas: 12,
    estado: 'Completado',
  },
  {
    id: 2,
    nombre: 'Análisis de Cimentaciones',
    municipio: 'Envigado',
    fecha: '2024-05-18',
    descargas: 8,
    estado: 'Completado',
  },
  {
    id: 3,
    nombre: 'Estabilidad de Taludes - Occidente',
    municipio: 'Bello',
    fecha: '2024-05-15',
    descargas: 15,
    estado: 'Completado',
  },
  {
    id: 4,
    nombre: 'Exploración Geotécnica Profunda',
    municipio: 'Rionegro',
    fecha: '2024-05-12',
    descargas: 5,
    estado: 'Completado',
  },
  {
    id: 5,
    nombre: 'Proyecto de Drenaje e Impermeabilización',
    municipio: 'La Ceja',
    fecha: '2024-05-10',
    descargas: 10,
    estado: 'Completado',
  },
  {
    id: 6,
    nombre: 'Geotecnia Ambiental - Sitio A',
    municipio: 'Sabaneta',
    fecha: '2024-05-08',
    descargas: 7,
    estado: 'Completado',
  },
  {
    id: 7,
    nombre: 'Mecánica de Suelos Avanzada',
    municipio: 'Medellín',
    fecha: '2024-05-05',
    descargas: 20,
    estado: 'Completado',
  },
  {
    id: 8,
    nombre: 'Estudio Preliminar de Factibilidad',
    municipio: 'Copacabana',
    fecha: '2024-05-01',
    descargas: 6,
    estado: 'Completado',
  },
]

export default function HistoryPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [municipioFilter, setMunicipioFilter] = useState('')

  // Filter projects
  const filteredProjects = sampleProjects.filter((project) => {
    const matchesSearch = project.nombre
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
    const matchesMunicipio = municipioFilter === 'all' || !municipioFilter || project.municipio === municipioFilter

    return matchesSearch && matchesMunicipio
  })

  // Calculate statistics
  const totalProjects = sampleProjects.length
  const thisMonthProjects = sampleProjects.filter((p) => {
    const projectDate = new Date(p.fecha)
    const now = new Date()
    return (
      projectDate.getMonth() === now.getMonth() &&
      projectDate.getFullYear() === now.getFullYear()
    )
  }).length
  const totalDescargas = sampleProjects.reduce((sum, p) => sum + p.descargas, 0)

  return (
    <MainLayout>
      <div className='page-padding container-main space-y-8'>
        {/* Page Header */}
        <div>
          <h1 className='text-3xl font-bold text-secondary-900 mb-2'>
            Historial de Proyectos
          </h1>
          <p className='text-secondary-600'>
            Consulta y descarga todos tus proyectos generados
          </p>
        </div>

        {/* Statistics */}
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
          <StatCard
            title='Total de Proyectos'
            value={totalProjects}
            icon={<FileText className='h-6 w-6' />}
            description='Proyectos generados'
          />
          <StatCard
            title='Este Mes'
            value={thisMonthProjects}
            icon={<TrendingUp className='h-6 w-6' />}
            description='Proyectos en mayo'
          />
          <StatCard
            title='Descargas'
            value={totalDescargas}
            icon={<Download className='h-6 w-6' />}
            description='Total de descargas'
          />
        </div>

        {/* Filters */}
        <Card className='border-secondary-200'>
          <CardContent className='pt-6'>
            <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
              {/* Search */}
              <div>
                <Label htmlFor='search' className='text-sm mb-2'>
                  Buscar Proyecto
                </Label>
                <div className='relative'>
                  <Search className='absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400' />
                  <Input
                    id='search'
                    placeholder='Ej: Medellín, Cimentaciones...'
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className='pl-10'
                  />
                </div>
              </div>

              {/* Filter by Municipio */}
              <div>
                <Label htmlFor='municipio' className='text-sm mb-2 flex items-center gap-2'>
                  <Filter className='h-4 w-4' />
                  Filtrar por Municipio
                </Label>
                <Select value={municipioFilter} onValueChange={setMunicipioFilter}>
                  <SelectTrigger id='municipio'>
                    <SelectValue placeholder='Todos los municipios' />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='all'>Todos los municipios</SelectItem>
                    {Array.from(new Set(sampleProjects.map((p) => p.municipio))).map(
                      (municipio) => (
                        <SelectItem key={municipio} value={municipio}>
                          {municipio}
                        </SelectItem>
                      )
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card className='border-secondary-200 overflow-hidden'>
          <CardHeader className='bg-secondary-50 border-b border-secondary-200'>
            <CardTitle className='text-lg'>
              {filteredProjects.length} Proyectos
            </CardTitle>
          </CardHeader>
          <CardContent className='p-0'>
            {filteredProjects.length > 0 ? (
              <div className='overflow-x-auto'>
                <table className='w-full'>
                  <thead className='border-b border-secondary-200 bg-secondary-50'>
                    <tr className='text-sm font-semibold text-secondary-700'>
                      <th className='px-6 py-3 text-left'>Proyecto</th>
                      <th className='px-6 py-3 text-left'>Municipio</th>
                      <th className='px-6 py-3 text-left'>Fecha</th>
                      <th className='px-6 py-3 text-right'>Acciones</th>
                    </tr>
                  </thead>
                  <tbody className='divide-y divide-secondary-200'>
                    {filteredProjects.map((project) => (
                      <tr
                        key={project.id}
                        className='hover:bg-secondary-50 transition-colors'
                      >
                        <td className='px-6 py-4'>
                          <div>
                            <p className='font-medium text-secondary-900'>
                              {project.nombre}
                            </p>
                            <p className='text-xs text-secondary-500'>
                              ID: {String(project.id).padStart(4, '0')}
                            </p>
                          </div>
                        </td>
                        <td className='px-6 py-4 text-sm text-secondary-600'>
                          {project.municipio}
                        </td>
                        <td className='px-6 py-4 text-sm text-secondary-600'>
                          {new Date(project.fecha).toLocaleDateString('es-CO')}
                        </td>
                        <td className='px-6 py-4'>
                          <div className='flex justify-end gap-2'>
                            <Button
                              variant='ghost'
                              size='sm'
                              className='gap-1 text-secondary-600 hover:text-secondary-900'
                            >
                              <Eye className='h-4 w-4' />
                              <span className='hidden sm:inline'>Ver</span>
                            </Button>
                            <Button
                              variant='ghost'
                              size='sm'
                              className='gap-1 text-primary-600 hover:text-primary-700'
                            >
                              <Download className='h-4 w-4' />
                              <span className='hidden sm:inline'>
                                Descargar
                              </span>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className='flex flex-col items-center justify-center py-12 text-center'>
                <FileText className='h-12 w-12 text-secondary-300 mb-4' />
                <p className='text-secondary-600 font-medium'>
                  No se encontraron proyectos
                </p>
                <p className='text-sm text-secondary-500 mt-1'>
                  Ajusta los filtros o{' '}
                  <a
                    href='/generate'
                    className='text-primary-600 hover:underline'
                  >
                    crea un nuevo proyecto
                  </a>
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}
