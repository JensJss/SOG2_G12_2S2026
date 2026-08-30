import { useEffect, useState } from 'react'
import type { IconType } from 'react-icons'
import { FiBarChart2, FiLoader, FiSend } from 'react-icons/fi'

interface NavbarButtonProps {
  label: string
  icon: IconType
  onClick: () => void
  disabled?: boolean
  cargando?: boolean
}

function NavbarButton({ label, icon: Icon, onClick, disabled = false, cargando = false }: NavbarButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="group inline-flex cursor-pointer items-center gap-1.5 rounded-lg border-[1.5px] border-blue-500/50 px-4 py-1.5 font-mono text-[10px] font-medium tracking-wider text-primary-soft uppercase transition-all duration-300 hover:-translate-y-0.5 hover:border-accent hover:text-accent hover:shadow-[0_0_12px_#00d4ff] active:scale-90 active:shadow-[inset_0_0_10px_rgba(0,212,255,0.4)] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0 disabled:hover:border-blue-500/50 disabled:hover:text-primary-soft disabled:hover:shadow-none sm:gap-2 sm:px-6 sm:py-2 sm:text-xs"
    >
      {cargando ? (
        <FiLoader size={14} className="animate-spin" />
      ) : (
        <Icon size={14} className="transition-transform duration-300 group-hover:rotate-12 group-active:scale-125" />
      )}
      {label}
    </button>
  )
}

interface NavbarProps {
  onEnviar: () => void
  onGraficar: () => void
  deshabilitado?: boolean
}

export default function Navbar({ onEnviar, onGraficar, deshabilitado = false }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav
      className={`sticky top-4 z-50 mx-auto mt-4 flex w-[95%] max-w-[1280px] animate-fade-down items-center justify-between rounded-full border bg-surface/80 py-2.5 backdrop-blur-md transition-all duration-500 sm:top-8 sm:mt-8 sm:py-3 ${
        scrolled
          ? 'border-accent/70 shadow-[0_0_25px_rgba(0,212,255,0.35)]'
          : 'border-secondary-soft/30 shadow-[0_0_15px_rgba(0,103,126,0.2)] hover:border-accent hover:shadow-[0_0_12px_#00d4ff]'
      }`}
    >
      <h1 className="ml-3 cursor-default truncate text-lg font-bold tracking-tight text-primary-soft transition-all duration-300 hover:drop-shadow-[0_0_10px_rgba(0,212,255,0.8)] sm:ml-4 sm:text-2xl">
        Practica 1 - Grupo 12
      </h1>
      <div className="mr-3 flex shrink-0 items-center gap-2 sm:mr-4 sm:gap-4">
        <NavbarButton label="Graficar" icon={FiBarChart2} onClick={onGraficar} disabled={deshabilitado} cargando={deshabilitado} />
        <NavbarButton label="Enviar" icon={FiSend} onClick={onEnviar} disabled={deshabilitado} />
      </div>
    </nav>
  )
}
