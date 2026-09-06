from pathlib import Path
import sys
from procesador import procesar

BASE = Path(__file__).resolve().parent
ARCHIVO_EXPRESIONES = BASE / "expresiones.txt"

def obtener_cadena(expresion, argumento=None):
    if argumento is not None:
        return argumento

    respuesta = input(f"\nIngrese la cadena w para r = {expresion}: ")
    return respuesta

archivo = Path(sys.argv[1]) if len(sys.argv) > 1 else ARCHIVO_EXPRESIONES
if not archivo.is_absolute():
    archivo = BASE / archivo

if not archivo.exists():
    raise FileNotFoundError(f"No existe el archivo de expresiones: {archivo}")

print("Analizador léxico - Proyecto 1")
print("Procesamiento: infix -> postfix -> AFN Thompson -> AFD subconjuntos -> AFD minimizado.")
print(f"Archivo de entrada: {archivo}")

numero = 0

with archivo.open("r", encoding="utf-8") as entrada:
    for linea in entrada:
        linea = linea.strip()

        if not linea or linea.startswith("#"):
            continue

        partes = linea.split(";", 1)
        expresion = partes[0].strip()
        cadena = partes[1] if len(partes) == 2 else None

        if not expresion:
            continue

        numero += 1
        cadena = obtener_cadena(expresion, cadena)

        resultado = procesar(
            expresion,
            cadena=cadena,
            numero=numero,
            mostrar_arbol=False,
            mostrar_afn=True,
            mostrar_afd=True,
            mostrar_minimizado=True,
            simular=True,
        )

        if resultado is None:
            print(f"\nLa expresión {numero} no pudo procesarse.")

print("\nProcesamiento terminado.")