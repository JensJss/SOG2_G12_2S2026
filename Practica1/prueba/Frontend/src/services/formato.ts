const REGEX_EMOJI = /\p{Extended_Pictographic}\uFE0F?/gu

/** Quita énfasis Markdown (negritas, cursivas con asteriscos, código inline). */
function limpiarEnfasis(texto: string): string {
  return texto
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`(.+?)`/g, '$1')
}

/** Convierte una tabla Markdown en columnas de texto plano alineadas (fuente monoespaciada). */
function convertirTabla(filas: string[]): string[] {
  const celdas = filas
    .map((fila) =>
      fila
        .split('|')
        .slice(1, -1)
        .map((celda) => limpiarEnfasis(celda.trim())),
    )
    .filter(
      (fila) =>
        fila.length > 0 && !fila.every((celda) => /^:?-{2,}:?$/.test(celda) || celda === ''),
    )

  if (celdas.length === 0) return []

  const anchos = celdas[0].map((_, col) =>
    Math.max(...celdas.map((fila) => fila[col]?.length ?? 0)),
  )

  const [cabecera, ...datos] = celdas
  const anchoTotal =
    anchos.reduce((acum, ancho) => acum + ancho, 0) + (anchos.length - 1) * 3

  return [
    cabecera.map((celda, col) => celda.padEnd(anchos[col])).join('   ').trimEnd(),
    '-'.repeat(anchoTotal),
    ...datos.map((fila) =>
      fila.map((celda, col) => (celda ?? '').padEnd(anchos[col])).join('   ').trimEnd(),
    ),
    '',
  ]
}

/**
 * Normaliza la respuesta del agente a texto plano legible:
 * sin emojis, sin almohadillas (#), sin asteriscos y con tablas alineadas.
 */
export function formatearRespuesta(texto: string): string {
  const lineas = texto.replace(/\r\n/g, '\n').split('\n')
  const salida: string[] = []
  let indice = 0

  while (indice < lineas.length) {
    let linea = lineas[indice].replace(REGEX_EMOJI, '').replace(/[ \t]+$/, '')

    // Tablas Markdown: se procesan como bloque completo
    if (/^\s*\|/.test(linea)) {
      const bloque: string[] = []
      while (indice < lineas.length && /^\s*\|/.test(lineas[indice])) {
        bloque.push(lineas[indice])
        indice += 1
      }
      salida.push(...convertirTabla(bloque))
      continue
    }

    // Separadores horizontales ---
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(linea)) {
      indice += 1
      continue
    }

    // Encabezados # -> MAYUSCULAS:
    linea = linea.replace(/^\s*#{1,6}\s+(.*)$/, (_m, titulo: string) => `${titulo.trim().toUpperCase()}:`)

    // Viñetas - / * -> • (antes de quitar énfasis, para no romper itálicas)
    linea = linea.replace(/^(\s*)[-*]\s+/, '$1\u2022 ')

    linea = limpiarEnfasis(linea)

    salida.push(linea)
    indice += 1
  }

  return salida.join('\n').replace(/\n{3,}/g, '\n\n').trim()
}
