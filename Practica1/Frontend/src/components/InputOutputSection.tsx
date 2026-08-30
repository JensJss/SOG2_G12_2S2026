import { FiCode, FiTerminal } from 'react-icons/fi'
import CodePanel from './CodePanel'

interface InputOutputSectionProps {
  pregunta: string
  onChangePregunta: (valor: string) => void
  respuesta: string
  cargando: boolean
}

export default function InputOutputSection({
  pregunta,
  onChangePregunta,
  respuesta,
  cargando,
}: InputOutputSectionProps) {
  return (
    <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <CodePanel
        icon={<FiTerminal size={18} />}
        title="Entrada"
        placeholder="// Escribe tu consulta o pide una gráfica..."
        value={pregunta}
        onChange={onChangePregunta}
      />
      <CodePanel
        icon={<FiCode size={18} />}
        title="Respuesta"
        placeholder="// La justificación del análisis se mostrará aquí..."
        value={cargando ? 'Analizando los datos, espera un momento...' : respuesta}
        readOnly
        cargando={cargando}
      />
    </section>
  )
}
