import { useState } from 'react'
import ChartSection from '../components/ChartSection'
import InputOutputSection from '../components/InputOutputSection'
import Navbar from '../components/Navbar'
import type { RespuestaAgente } from '../services/api'
import { consultarAgente, generarGrafico } from '../services/api'
import { formatearRespuesta } from '../services/formato'

export default function HomePage() {
  const [pregunta, setPregunta] = useState('')
  const [respuesta, setRespuesta] = useState('')
  const [cargando, setCargando] = useState(false)
  const [imagenGrafico, setImagenGrafico] = useState<string | null>(null)

  const ejecutar = async (accion: (texto: string) => Promise<RespuestaAgente>) => {
    const texto = pregunta.trim()
    if (!texto || cargando) return

    setCargando(true)
    try {
      const data = await accion(texto)
      setRespuesta(formatearRespuesta(data.respuesta))
      if (data.imagen) setImagenGrafico(data.imagen)
    } catch (error) {
      setRespuesta(
        error instanceof Error ? error.message : 'Ocurrió un error inesperado.',
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-base font-body text-content antialiased selection:bg-accent selection:text-base">
      <Navbar
        onGraficar={() => ejecutar(generarGrafico)}
        onEnviar={() => ejecutar(consultarAgente)}
        deshabilitado={cargando}
      />

      <main className="relative mx-auto flex w-full max-w-[1280px] flex-grow flex-col gap-8 px-6 py-8">
        <div
          className="pointer-events-none absolute inset-0 z-[-1] opacity-20"
          style={{
            backgroundImage:
              'radial-gradient(circle at 50% 0%, rgba(0, 212, 255, 0.15) 0%, transparent 50%)',
          }}
        />

        <div className="animate-fade-up [animation-delay:150ms]">
          <InputOutputSection
            pregunta={pregunta}
            onChangePregunta={setPregunta}
            respuesta={respuesta}
            cargando={cargando}
          />
        </div>

        <div className="animate-fade-up [animation-delay:300ms]">
          <ChartSection imagen={imagenGrafico} />
        </div>
      </main>
    </div>
  )
}
