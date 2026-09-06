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

    return jsonify({
        "consola": consola,
        "imagenes": imagenes,
        "resultados": {
            "afn": resultado["aceptada"],
            "afd": resultado["aceptada_afd"],
            "afd_min": resultado["aceptada_min"],
        },
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)