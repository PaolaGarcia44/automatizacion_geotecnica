export interface RecognizedPerforacion {
  numero: number
  profundidad: string
  tipo_suelo: string
  observaciones: string
}

function normalizeSpaces(value: string): string {
  return value.replace(/\s+/g, ' ').trim()
}

function sanitizeOcrLine(value: string): string {
  return value
    .replace(/[|¦]/g, ' ')
    .replace(/[—–−]/g, '-')
    .replace(/[_•·]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function isHeaderLine(line: string): boolean {
  const lower = line.toLowerCase()
  return (
    lower.includes('num') && lower.includes('profundidad') ||
    lower.includes('tipo suelo') ||
    lower.includes('observaciones')
  )
}

export function extractPerforacionesFromText(text: string): RecognizedPerforacion[] {
  const rows: RecognizedPerforacion[] = []
  const lines = text
    .split(/\r?\n/)
    .map(sanitizeOcrLine)
    .filter(Boolean)

  for (const line of lines) {
    if (isHeaderLine(line)) {
      continue
    }

    const rowMatch = line.match(/^(\d{1,2})\D+([0-9]+(?:[.,][0-9]+)?)(?:\D+(.+))?$/)
    if (!rowMatch) {
      continue
    }

    const numero = Number.parseInt(rowMatch[1], 10)
    const profundidad = rowMatch[2].replace(',', '.')
    const remainder = normalizeSpaces(rowMatch[3] || '')

    let tipo_suelo = remainder
    let observaciones = ''

    const sptMatch = remainder.match(/\bSPT\s*=?\s*\d.*$/i)
    if (sptMatch && typeof sptMatch.index === 'number') {
      tipo_suelo = normalizeSpaces(remainder.slice(0, sptMatch.index))
      observaciones = normalizeSpaces(remainder.slice(sptMatch.index))
    } else {
      const splitByTab = remainder.split(/\s{2,}/)
      if (splitByTab.length >= 2) {
        tipo_suelo = normalizeSpaces(splitByTab[0])
        observaciones = normalizeSpaces(splitByTab.slice(1).join(' '))
      } else if (!remainder) {
        tipo_suelo = ''
        observaciones = ''
      }
    }

    if (!tipo_suelo && !observaciones && line.length > 0) {
      const tail = normalizeSpaces(line.replace(/^\d{1,2}\D+([0-9]+(?:[.,][0-9]+)?)/, ''))
      if (tail) {
        tipo_suelo = tail
      }
    }

    rows.push({
      numero,
      profundidad,
      tipo_suelo,
      observaciones,
    })
  }

  const unique = new Map<number, RecognizedPerforacion>()
  for (const row of rows) {
    unique.set(row.numero, row)
  }

  return Array.from(unique.values()).sort((a, b) => a.numero - b.numero)
}
