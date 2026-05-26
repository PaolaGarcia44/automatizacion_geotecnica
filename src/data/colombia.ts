// colombia.ts
// Datos oficiales de Colombia - Departamentos y Municipios
// Fuente: DANE - Actualizado 2025
// Total: 32 Departamentos + Bogotá D.C. | 1,103 Municipios

import colombiaData from './colombia.json';

export interface MunicipalityOption {
  id: string;
  name: string;
}

export interface DepartmentOption {
  id: string;
  name: string;
  municipalities: MunicipalityOption[];
}

// Normaliza texto para generar IDs consistentes
function normalize(s: string): string {
  return s
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

// Construye la estructura de datos con IDs generados automáticamente
const DATA: DepartmentOption[] = (colombiaData as any[]).map((d) => {
  const deptName: string = d.departamento;
  const municipalities: string[] = Array.isArray(d.municipios) ? d.municipios : [];
  
  // Eliminar duplicados dentro del mismo departamento
  const uniqueMunicipalities = [...new Map(municipalities.map(m => [normalize(m), m])).values()];
  
  return {
    id: normalize(deptName),
    name: deptName,
    municipalities: uniqueMunicipalities.map((m) => ({ id: normalize(m), name: m })),
  };
});

/**
 * Obtiene la lista de todos los departamentos
 * @returns Array con id y nombre de cada departamento
 */
export function getDepartments(): { id: string; name: string }[] {
  return DATA.map((d) => ({ id: d.id, name: d.name }));
}

/**
 * Obtiene los municipios de un departamento específico
 * @param departamentoId - ID del departamento (normalizado o nombre original)
 * @returns Array de municipios con id y nombre
 */
export function getMunicipalitiesByDepartment(departamentoId: string): MunicipalityOption[] {
  const target = DATA.find(
    (d) => d.id === departamentoId || normalize(d.name) === normalize(departamentoId)
  );
  return target ? target.municipalities : [];
}

/**
 * Busca municipios por nombre en todo el país o en un departamento específico
 * @param query - Texto a buscar
 * @param departamentoId - (Opcional) ID del departamento para filtrar
 * @returns Array de municipios que coinciden con la búsqueda
 */
export function searchMunicipalities(query: string, departamentoId?: string): MunicipalityOption[] {
  const q = normalize(query || '');
  if (!q) return [];

  const results: MunicipalityOption[] = [];
  
  const departmentsToSearch = departamentoId
    ? DATA.filter((d) => d.id === departamentoId || normalize(d.name) === normalize(departamentoId))
    : DATA;

  for (const d of departmentsToSearch) {
    for (const m of d.municipalities) {
      if (m.id.includes(q) || normalize(m.name).includes(q)) {
        results.push(m);
      }
    }
  }

  return results;
}

/**
 * Obtiene el nombre del departamento al que pertenece un municipio
 * @param municipalityName - Nombre del municipio a buscar
 * @returns Nombre del departamento o null si no se encuentra
 */
export function getDepartmentByMunicipality(municipalityName: string): string | null {
  const normalizedSearch = normalize(municipalityName);
  
  for (const d of DATA) {
    const found = d.municipalities.find(
      (m) => m.id === normalizedSearch || normalize(m.name) === normalizedSearch
    );
    if (found) {
      return d.name;
    }
  }
  return null;
}

/**
 * Obtiene datos completos de un departamento por su ID o nombre
 * @param identifier - ID normalizado o nombre del departamento
 * @returns Departamento completo o undefined si no existe
 */
export function getDepartment(identifier: string): DepartmentOption | undefined {
  return DATA.find(
    (d) => d.id === identifier || normalize(d.name) === normalize(identifier)
  );
}

/**
 * Verifica si un municipio existe en un departamento específico
 * @param departamentoId - ID del departamento
 * @param municipalityName - Nombre del municipio
 * @returns boolean indicando si existe
 */
export function municipalityExists(departamentoId: string, municipalityName: string): boolean {
  const municipalities = getMunicipalitiesByDepartment(departamentoId);
  const normalizedSearch = normalize(municipalityName);
  return municipalities.some((m) => m.id === normalizedSearch || normalize(m.name) === normalizedSearch);
}

export default DATA;