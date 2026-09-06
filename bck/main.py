from pathlib import Path
import sys
from procesador import procesar

print("Para cada expresión se solicitará la cadena w que se desea reconocer.")
print("Cierre la ventana de cada árbol/AFN/AFD/AFD minimizado para continuar.\n")

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
            print("\nLa expresión no pudo procesarse.")
        else:
            print("\n--- Resumen ---")
            print(f"AFN            : {'sí' if resultado['aceptada'] else 'no'}")
            print(f"AFD            : {'sí' if resultado['aceptada_afd'] else 'no'}")
            print(f"AFD minimizado : {'sí' if resultado['aceptada_min'] else 'no'}")

print("\nProcesamiento terminado.")