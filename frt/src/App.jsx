import { useState, useEffect } from 'react'
import './App.css'

import PasoAPaso from './PasoAPaso'

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
    } catch {
      setError('No se pudo conectar con el servidor. ¿Está corriendo app.py?')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="contenedor">
      <header className="hero">
        <div className="hero-kicker">Proyecto de Teoría de la Computación</div>
        <h1>Analizador de expresiones regulares</h1>
        <p>Convierte una expresión en autómatas y recorre cada etapa de su construcción.</p>
      </header>

      <form className="formulario" onSubmit={manejarEnvio} aria-busy={cargando}>
        <div className="formulario-cabecera">
          <div>
            <span className="eyebrow">Entrada</span>
            <h2>Define el lenguaje que quieres analizar</h2>
          </div>
        </div>
        {listaExpresiones.length > 0 && (
          <label>
            <span>Ejemplos guardados</span>
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
          <span>Expresión regular <code>(r)</code></span>
          <input
            type="text"
            value={expresion}
            onChange={(e) => setExpresion(e.target.value)}
            placeholder="(a|b)*abb"
            required
          />
        </label>

        <label>
          <span>Cadena a reconocer <code>(w)</code></span>
          <input
            type="text"
            value={cadena}
            onChange={(e) => setCadena(e.target.value)}
            placeholder="aabbb"
          />
        </label>

        <button className="boton-principal" type="submit" disabled={cargando}>
          {cargando ? 'Construyendo...' : 'Analizar expresión'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {resultados && (
        <section className="resultados" aria-live="polite">
          <div className="seccion-heading">
            <div>
              <span className="eyebrow">Resultado de la simulación</span>
              <h2>¿La cadena pertenece al lenguaje?</h2>
            </div>
            <code className="cadena-resultada">w = {cadena || 'ε'}</code>
          </div>
          <div className="badges">
            <BadgeResultado nombre="AFN" aceptada={resultados.afn} />
            <BadgeResultado nombre="AFD" aceptada={resultados.afd} />
            <BadgeResultado nombre="AFD min (Particiones)" aceptada={resultados.afd_min} />
            <BadgeResultado nombre="AFD min · Myhill-Nerode" aceptada={resultados.afd_min_myhill} />
          </div>
        </section>
      )}

      {cargando && (
        <div className="estado-carga" role="status">
          <span className="spinner" aria-hidden="true" />
          Generando árbol y autómatas...
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