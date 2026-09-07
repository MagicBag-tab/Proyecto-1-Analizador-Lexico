import React, { useState } from 'react';
import './PasoAPaso.css';

export default function PasoAPaso({ detalles, imagenes }) {
  const [paso, setPaso] = useState(0);

  const pasos = [
    {
      titulo: '1. Infix a Postfix (Shunting Yard)',
      contenido: () => (
        <div className="paso-card">
          <p>La expresión regular se transformó a notación postfija para facilitar la creación del árbol.</p>
          <div className="postfix-array">
            {detalles.postfix.map((tok, i) => (
              <span key={i} className="token">{tok}</span>
            ))}
          </div>
        </div>
      ),
    },
    {
      titulo: '2. Árbol Sintáctico',
      contenido: () => (
        <div className="paso-card">
          <p>Se construyó el árbol sintáctico a partir de la expresión postfija.</p>
          {imagenes.arbol && <img src={imagenes.arbol} alt="Árbol" className="img-paso" />}
        </div>
      ),
    },
    {
      titulo: '3. AFN (Construcción de Thompson)',
      contenido: () => (
        <div className="paso-card">
          <p>El AFN generado une pequeños autómatas usando transiciones "nobady" (ε).</p>
          {imagenes.afn && <img src={imagenes.afn} alt="AFN" className="img-paso" />}
        </div>
      ),
    },
    {
      titulo: '4. AFD (Subconjuntos)',
      contenido: () => (
        <div className="paso-card row-layout">
          <div className="tabla-container">
            <h4>Tabla de Transiciones</h4>
            <TablaAFD datos={detalles.tabla_afd} />
          </div>
          {imagenes.afd && <img src={imagenes.afd} alt="AFD" className="img-paso img-half" />}
        </div>
      ),
    },
    {
      titulo: '5. AFD Minimizado (Particiones)',
      contenido: () => (
        <div className="paso-card row-layout">
          <div className="tabla-container">
            <h4>Tabla de Transiciones</h4>
            <TablaAFD datos={detalles.tabla_afd_min} />
          </div>
          {imagenes.afd_min && <img src={imagenes.afd_min} alt="AFD Min" className="img-paso img-half" />}
        </div>
      ),
    },
    {
      titulo: '6. AFD Minimizado (Myhill-Nerode)',
      contenido: () => (
        <div className="paso-card row-layout">
          <div className="tabla-container">
            <h4>Tabla de Transiciones (Myhill)</h4>
            <TablaAFD datos={detalles.tabla_afd_min_myhill} />
          </div>
          {imagenes.afd_min_myhill && <img src={imagenes.afd_min_myhill} alt="AFD Min Myhill" className="img-paso img-half" />}
        </div>
      ),
    }];

  const avanzar = () => setPaso(p => Math.min(p + 1, pasos.length - 1));
  const retroceder = () => setPaso(p => Math.max(p - 1, 0));

  return (
    <div className="paso-a-paso">
      <div className="paso-header">
        <h3>Simulación</h3>
        <div className="controles">
          <button onClick={retroceder} disabled={paso === 0}>Anterior</button>
          <span className="indicador-paso">{paso + 1} / {pasos.length}</span>
          <button onClick={avanzar} disabled={paso === pasos.length - 1}>Siguiente</button>
        </div>
      </div>
      
      <div className="paso-content">
        <h3 className="paso-titulo">{pasos[paso].titulo}</h3>
        {pasos[paso].contenido()}
      </div>
    </div>
  );
}

function TablaAFD({ datos }) {
  if (!datos || !datos.filas) return null;
  return (
    <table className="tabla-estados">
      <thead>
        <tr>
          <th>Estado</th>
          {datos.alfabeto.map(s => <th key={s}>{s}</th>)}
        </tr>
      </thead>
      <tbody>
        {datos.filas.map((fila, i) => (
          <tr key={i} className={fila.aceptacion ? 'estado-aceptacion' : ''}>
            <td>{fila.estado}</td>
            {datos.alfabeto.map(s => (
              <td key={s}>{fila.transiciones[s]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
