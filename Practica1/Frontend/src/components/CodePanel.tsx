import type { ReactNode } from 'react'

interface CodePanelProps {
  icon: ReactNode
  title: string
  placeholder: string
  readOnly?: boolean
  value?: string
  onChange?: (valor: string) => void
  cargando?: boolean
}

export default function CodePanel({
  icon,
  title,
  placeholder,
  readOnly = false,
  value,
  onChange,
  cargando = false,
}: CodePanelProps) {
  return (
    <div className="group relative flex h-[400px] flex-col gap-3 rounded-xl border border-blue-500/30 bg-base p-6 shadow-lg transition-all duration-500 hover:-translate-y-1 hover:border-accent/60 focus-within:border-accent/60 hover:shadow-[0_0_25px_rgba(0,212,255,0.2)] focus-within:shadow-[0_0_25px_rgba(0,212,255,0.2)]">
      <div className="absolute top-0 right-0 left-0 rounded-t-xl bg-accent opacity-0 shadow-[0_0_8px_#00d4ff] transition-opacity duration-300 group-hover:opacity-100 group-focus-within:opacity-100" style={{ height: '2px' }} />
      <header className="flex items-center gap-2 border-b border-blue-500/50 pb-2 uppercase transition-colors duration-300 group-hover:border-accent/50">
        <span className="text-accent transition-transform duration-300 group-hover:scale-125 group-focus-within:animate-spin-slow">{icon}</span>
        <h2 className="font-mono text-xs font-medium tracking-wider text-secondary-soft transition-colors duration-300 group-hover:text-primary-soft">
          {title}
        </h2>
        {cargando && (
          <span className="ml-auto flex items-center gap-1.5 font-mono text-[10px] text-accent">
            <span className="h-1.5 w-1.5 animate-blink rounded-full bg-accent" />
            Procesando...
          </span>
        )}
      </header>

      <textarea
        placeholder={placeholder}
        readOnly={readOnly}
        spellCheck={false}
        value={value}
        onChange={onChange ? (e) => onChange(e.target.value) : undefined}
        className={`w-full flex-grow resize-none rounded-lg border border-blue-500/30 bg-black/40 p-4 font-mono text-xs text-accent transition-all duration-300 outline-none placeholder:text-muted/40 focus:border-accent focus:bg-black/60 focus:shadow-[inset_0_0_12px_rgba(0,212,255,0.25),0_0_10px_rgba(0,212,255,0.3)] ${
          readOnly ? 'cursor-default opacity-80' : ''
        }`}
      />

      <div className="mx-auto h-1 w-24 shrink-0 rounded-full bg-gradient-to-r from-transparent via-accent/50 to-transparent" />
    </div>
  )
}
