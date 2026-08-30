const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface RespuestaAgente {
  respuesta: string
  imagen: string | null
}

interface PeticionConsulta {
  pregunta: string
}

interface PeticionGrafico {
  peticion: string
}

async function manejarError(res: Response): Promise<never> {
  let detalle = `Error ${res.status}`
  try {
    const cuerpo = await res.json()
    if (typeof cuerpo.detail === 'string') detalle = cuerpo.detail
  } catch {
    // respuesta sin cuerpo JSON, se conserva el código de estado
  }
  throw new Error(detalle)
}

/** Envía una pregunta al agente y devuelve su justificación y el gráfico generado (si aplica). */
export async function consultarAgente(pregunta: string): Promise<RespuestaAgente> {
  const cuerpo: PeticionConsulta = { pregunta }
  let res: Response
  try {
    res = await fetch(`${API_URL}/api/consultar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cuerpo),
    })
  } catch {
    throw new Error(
      'No se pudo conectar con el servidor. Verifica que esté ejecutándose en ' + API_URL,
    )
  }
  if (!res.ok) await manejarError(res)
  return (await res.json()) as RespuestaAgente
}

/** Genera una gráfica con el módulo de Graficación del backend según la petición. */
export async function generarGrafico(peticion: string): Promise<RespuestaAgente> {
  const cuerpo: PeticionGrafico = { peticion }
  let res: Response
  try {
    res = await fetch(`${API_URL}/api/graficar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cuerpo),
    })
  } catch {
    throw new Error(
      'No se pudo conectar con el servidor. Verifica que esté ejecutándose en ' + API_URL,
    )
  }
  if (!res.ok) await manejarError(res)
  return (await res.json()) as RespuestaAgente
}

/** Devuelve los nombres de los gráficos PNG generados por el agente. */
export async function listarGraficos(): Promise<string[]> {
  const res = await fetch(`${API_URL}/api/graficos`)
  if (!res.ok) await manejarError(res)
  const data = (await res.json()) as { graficos: string[] }
  return data.graficos
}

/** Construye la URL pública de un gráfico generado. */
export function urlGrafico(nombre: string): string {
  return `${API_URL}/api/graficos/${encodeURIComponent(nombre)}`
}
