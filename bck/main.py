from procesador import procesar

print("Para cada expresión se solicitará la cadena w que se desea reconocer.")
print("Cierre la ventana de cada árbol/AFN/AFD/AFD minimizado para continuar.\n")

numero = 0

with open("expresiones.txt", "r", encoding="utf-8") as archivo:
    for linea in archivo:
        linea = linea.strip()

        if not linea or linea.startswith("#"):
            continue

        numero += 1

        if ";" in linea:
            expresion, cadena = linea.split(";", 1)
            expresion = expresion.strip()
            cadena = cadena.strip()
            print(f"\nExpresión {numero}: {expresion}")
            print(f"Cadena tomada del archivo: {cadena!r}")
        else:
            expresion = linea
            cadena = input(
                f"\nIngrese la cadena w para la expresión {numero} "
                f"({expresion}): "
            )

        resultado = procesar(
            expresion,
            cadena=cadena,
            numero=numero,
            mostrar_arbol=True,
            mostrar_afn=True,
            mostrar_graficos=True
        )

        if resultado is None:
            print("\nLa expresión no pudo procesarse.")
        else:
            print("\n--- Resumen ---")
            print(f"AFN            : {'sí' if resultado['aceptada'] else 'no'}")
            print(f"AFD            : {'sí' if resultado['aceptada_afd'] else 'no'}")
            print(f"AFD minimizado : {'sí' if resultado['aceptada_min'] else 'no'}")

print("\nProcesamiento terminado.")