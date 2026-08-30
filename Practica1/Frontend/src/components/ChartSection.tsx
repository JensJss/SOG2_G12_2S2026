import { useState } from 'react'
import { FiBarChart2, FiImage } from 'react-icons/fi'
import { urlGrafico } from '../services/api'

interface Bar {
  label: string
  value: number
}

const BARS: Bar[] = [
  { label: 'Var 1', value: 45 },
  { label: 'Var 2', value: 85 },
  { label: 'Var 3', value: 30 },
  { label: 'Var 4', value: 60 },
  { label: 'Var 5', value: 95 },
  { label: 'Var 6', value: 20 },
  { label: 'Var 7', value: 75 },
]

interface ChartSectionProps {
  imagen: string | null
}

export default function ChartSection({ imagen }: ChartSectionProps) {
  const [imagenCargada, setImagenCargada] = useState<string | null>(null)
  const cargada = imagen !== null && imagenCargada === imagen

  return (
    <section className="group/chart relative flex flex-col gap-6 rounded-xl border border-blue-500/30 bg-base p-6 shadow-lg transition-all duration-500 hover:border-accent/60 hover:shadow-[0_0_25px_rgba(0,212,255,0.2)]">
      <div className="absolute top-0 right-0 left-0 rounded-t-xl bg-accent opacity-0 shadow-[0_0_8px_#00d4ff] transition-opacity duration-300 group-hover/chart:opacity-100" style={{ height: '2px' }} />
      <header className="flex items-center justify-between border-b border-blue-500/50 pb-2 uppercase transition-colors duration-300 group-hover/chart:border-accent/50">
        <div className="flex items-center gap-2">
          <FiBarChart2 size={18} className="text-accent transition-transform duration-300 group-hover/chart:scale-125" />
          <h2 className="font-mono text-xs font-medium tracking-wider text-secondary-soft">
            Visualización
          </h2>
        </div>
        <div className="flex gap-2">
          <div className={`h-2 w-2 rounded-full transition-colors duration-300 ${imagen ? 'animate-blink bg-accent' : 'bg-accent shadow-[0_0_8px_#00d4ff]'}`} />
          <div className="h-2 w-2 rounded-full bg-secondary-soft/30 transition-colors duration-300 group-hover/chart:bg-secondary-soft/60" />
          <div className="h-2 w-2 rounded-full bg-secondary-soft/30 transition-colors duration-300 group-hover/chart:bg-secondary-soft/60" />
        </div>
      </header>

      {imagen ? (
        <div className="flex min-h-[300px] items-center justify-center rounded-lg border border-blue-500/20 bg-black/40 p-4 animate-fade-up">
          {!cargada && (
            <span className="absolute flex items-center gap-2 font-mono text-xs text-muted">
              <FiImage size={16} className="animate-pulse" />
              Cargando gráfico...
            </span>
          )}
          <img
            key={imagen}
            src={urlGrafico(imagen)}
            alt={imagen}
            onLoad={() => setImagenCargada(imagen)}
            className={`max-h-[420px] w-auto max-w-full rounded-md shadow-[0_0_20px_rgba(0,212,255,0.15)] transition-all duration-700 ${cargada ? 'scale-100 opacity-100 blur-0' : 'scale-95 opacity-0 blur-sm'}`}
          />
        </div>
      ) : (
        <>
          <div className="relative flex h-[300px] w-full items-end justify-around gap-2 border-b border-l border-secondary-soft/20 px-4 pt-8 pb-4">
            <span className="absolute bottom-4 left-[-20px] font-mono text-[10px] text-muted">0</span>
            <span className="absolute top-1/2 left-[-25px] font-mono text-[10px] text-muted">50</span>
            <span className="absolute top-4 left-[-30px] font-mono text-[10px] text-muted">100</span>

            {BARS.map(({ label, value }, index) => (
              <div
                key={label}
                className="group relative w-full max-w-[40px] origin-bottom cursor-pointer animate-bar-grow"
                style={{ height: `${value}%`, animationDelay: `${400 + index * 90}ms` }}
              >
                <div className="h-full w-full rounded-t-sm bg-gradient-to-t from-accent/25 to-secondary-soft/20 transition-all duration-300 group-hover:from-accent/60 group-hover:to-accent/50 group-hover:shadow-[0_-5px_20px_rgba(0,212,255,0.4)] group-active:scale-y-95" />
                <span className="absolute -top-6 left-1/2 -translate-x-1/2 font-mono text-[10px] text-accent opacity-0 transition-all duration-300 group-hover:-top-7 group-hover:opacity-100">
                  {value}
                </span>
                <span className="sr-only">{label}</span>
              </div>
            ))}
          </div>

          <div className="mt-2 flex justify-around px-4 font-mono text-[10px] tracking-wider text-muted uppercase">
            {BARS.map(({ label }) => (
              <span key={label}>{label}</span>
            ))}
          </div>
        </>
      )}
    </section>
  )
}
