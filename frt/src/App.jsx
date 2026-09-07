import { useState, useEffect } from 'react'
import './App.css'

import PasoAPaso from './PasoAPaso'

const ETIQUETAS_IMAGENES = {
  arbol: 'Árbol sintáctico',
  afn: 'AFN (Thompson)',
  afd: 'AFD (Subconjuntos)',
  afd_min: 'AFD minimizado (Particiones)',
  afd_min_myhill: 'AFD minimizado (Myhill-Nerode)',
}

function BadgeResultado({ nombre, aceptada }) {
  return (
    <div className={`badge ${aceptada ? 'badge-si' : 'badge-no'}`}>
      <span className="badge-nombre">{nombre}</span>
      <span className="badge-valor">{aceptada ? 'sí' : 'no'}</span>
    </div>
  )
}

function App() {
  const [expresion, setExpresion] = useState('(a|b)*abb')
  const [cadena, setCadena] = useState('aabbb')
  const [listaExpresiones, setListaExpresiones] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)
  const [consola, setConsola] = useState('')
  const [imagenes, setImagenes] = useState(null)
  const [resultados, setResultados] = useState(null)
  const [detalles, setDetalles] = useState(null)

  useEffect(() => {
    fetch('/api/expresiones')
      .then(res => res.json())
      .then(data => setListaExpresiones(data))
      .catch(err => console.error('Error cargando expresiones', err))
  }, [])

  const manejarEnvio = async (evento) => {
    evento.preventDefault()
    setCargando(true)
    setError(null)
    setImagenes(null)
    setResultados(null)
    setConsola('')

    try {
      const respuesta = await fetch('/api/procesar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expresion, cadena }),
      })

      const datos = await respuesta.json()

      if (!respuesta.ok) {
        setError(datos.error || 'Error desconocido')
        setConsola(datos.consola || '')
        return
      }

      setConsola(datos.consola)
      setImagenes(datos.imagenes)
      setResultados(datos.resultados)
      setDetalles(datos.detalles)
    } catch (err) {
      setError('No se pudo conectar con el servidor. ¿Está corriendo app.py?')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="contenedor">
      <h1>Analizador Léxico — Expresiones Regulares</h1>

      <form className="formulario" onSubmit={manejarEnvio}>
        {listaExpresiones.length > 0 && (
          <label>
            Seleccionar de expresiones.txt
            <select className="input-select" onChange={(e) => {
              if(e.target.value === "") return;
              const sel = listaExpresiones[e.target.value];
              setExpresion(sel.expresion);
              setCadena(sel.cadena || '');
            }}>
              <option value="">-- Elige una expresión --</option>
              {listaExpresiones.map((item, i) => (
                <option key={i} value={i}>{item.expresion} {item.cadena ? `(w=${item.cadena})` : ''}</option>
              ))}
            </select>
          </label>
        )}

        <label>
          Expresión regular (r)
          <input
            type="text"
            value={expresion}
            onChange={(e) => setExpresion(e.target.value)}
            placeholder="(a|b)*abb"
            required
          />
        </label>

        <label>
          Cadena a reconocer (w)
          <input
            type="text"
            value={cadena}
            onChange={(e) => setCadena(e.target.value)}
            placeholder="aabbb"
          />
        </label>

        <button type="submit" disabled={cargando}>
          {cargando ? 'Procesando...' : 'Procesar'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {resultados && (
        <div className="badges">
          <BadgeResultado nombre="AFN" aceptada={resultados.afn} />
          <BadgeResultado nombre="AFD" aceptada={resultados.afd} />
          <BadgeResultado nombre="AFD min (Particiones)" aceptada={resultados.afd_min} />
          <BadgeResultado nombre="AFD min (Myhill-Nerode)" aceptada={resultados.afd_min_myhill} />
        </div>
      )}

      {imagenes && detalles && (
        <PasoAPaso detalles={detalles} imagenes={imagenes} />
      )}

      {consola && (
        <div className="consola-wrapper">
          <h3>Salida de consola</h3>
          <pre className="consola">{consola}</pre>
        </div>
      )}
    </div>
  )
}

export default App