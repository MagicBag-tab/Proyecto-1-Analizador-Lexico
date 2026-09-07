# Estte es para la API, no para la ejecución desde consola. Para eso está main.py
import base64
import contextlib
import io
import itertools
import os
import traceback

import matplotlib
matplotlib.use("Agg")  # IMPORTANTE: debe ir antes de importar procesador
                        # (que importa visualizador -> pyplot). Evita que
                        # el servidor intente abrir ventanas gráficas.

from flask import Flask, jsonify, request
from flask_cors import CORS

from procesador import procesar

app = Flask(__name__)
CORS(app)  # respaldo por si el frontend no usa el proxy de Vite

# Contador simple para no pisar las imágenes de peticiones anteriores mientras el servidor sigue corriendo.
contador_numero = itertools.count(1)


def _imagen_a_base64(carpeta, prefijo, numero):
    nombre = f"{prefijo}_{numero}.png" if numero is not None else f"{prefijo}.png"
    ruta = os.path.join(carpeta, nombre)

    if not os.path.exists(ruta):
        return None

    with open(ruta, "rb") as archivo:
        contenido = archivo.read()

    return "data:image/png;base64," + base64.b64encode(contenido).decode("utf-8")


@app.route("/api/expresiones", methods=["GET"])
def obtener_expresiones():
    try:
        if not os.path.exists("expresiones.txt"):
            return jsonify([])
        
        lista = []
        with open("expresiones.txt", "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"): continue
                
                if ";" in linea:
                    exp, cad = linea.split(";", 1)
                    lista.append({"expresion": exp.strip(), "cadena": cad.strip()})
                else:
                    lista.append({"expresion": linea, "cadena": ""})
        return jsonify(lista)
    except Exception as e:
        return jsonify([])


@app.route("/api/procesar", methods=["POST"])
def procesar_endpoint():
    datos = request.get_json(force=True) or {}

    expresion = (datos.get("expresion") or "").strip()
    cadena = datos.get("cadena", "")

    if not expresion:
        return jsonify({"error": "Debe indicar una expresión regular."}), 400

    numero = next(contador_numero)
    buffer_consola = io.StringIO()

    try:
        with contextlib.redirect_stdout(buffer_consola):
            resultado = procesar(
                expresion,
                cadena=cadena,
                numero=numero,
                mostrar_arbol=True,
                mostrar_afn=True,
                mostrar_graficos=False,  # nunca abrir ventanas en el servidor
            )
    except Exception:
        return jsonify({
            "error": "Ocurrió un error inesperado al procesar la expresión.",
            "detalle": traceback.format_exc(),
            "consola": buffer_consola.getvalue(),
        }), 500

    consola = buffer_consola.getvalue()

    if resultado is None:
        return jsonify({
            "error": "La expresión no pudo procesarse (revisa balanceo o sintaxis).",
            "consola": consola,
        }), 400

    imagenes = {
        "arbol": _imagen_a_base64("arboles", "arbol", numero),
        "afn": _imagen_a_base64("afn", "afn", numero),
        "afd": _imagen_a_base64("afd", "afd", numero),
        "afd_min": _imagen_a_base64("afd_min", "afd_min", numero),
    }

    def extraer_tabla(afd_obj, prefijo="D"):
        if not afd_obj or not hasattr(afd_obj, 'estados'): return None
        alfabeto = afd_obj.alfabeto if hasattr(afd_obj, 'alfabeto') else []
        filas = []
        for estado in afd_obj.estados:
            fila = {
                "estado": f"{prefijo}{estado.id}",
                "aceptacion": estado.es_aceptacion,
                "transiciones": {}
            }
            for sim in alfabeto:
                dest = estado.transiciones.get(sim) if hasattr(estado, 'transiciones') else afd_obj.transicion(estado, sim)
                fila["transiciones"][sim] = f"{prefijo}{dest.id}" if dest else "-"
            filas.append(fila)
        return {"alfabeto": list(alfabeto), "filas": filas}

    detalles = {
        "postfix": resultado["postfix"],
        "traza_afn": [{"simbolo": t[0], "estados": t[1]} for t in resultado["traza"]],
        "tabla_afd": extraer_tabla(resultado["afd"], "D"),
        "tabla_afd_min": extraer_tabla(resultado["afd_min"], "M"),
    }

    return jsonify({
        "consola": consola,
        "imagenes": imagenes,
        "resultados": {
            "afn": resultado["aceptada"],
            "afd": resultado["aceptada_afd"],
            "afd_min": resultado["aceptada_min"],
        },
        "detalles": detalles
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)