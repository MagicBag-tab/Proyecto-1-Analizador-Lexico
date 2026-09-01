from procesador import procesar

print("Procesamiento de expresiones regulares")
print("Se construirán el árbol sintáctico, el AFN de Thompson y el AFD por subconjuntos.")
print("No se realizan simulaciones de cadenas en esta etapa.\n")

numero = 0

with open("expresiones.txt", "r", encoding="utf-8") as archivo:
    for linea in archivo:
        linea = linea.strip()

        if not linea or linea.startswith("#"):
            continue
        
        expresion = linea.split(";", 1)[0].strip()
        if not expresion:
            continue

        numero += 1
        print(f"\nExpresión {numero}: {expresion}")

        resultado = procesar(
            expresion,
            numero=numero,
            mostrar_arbol=True,
            mostrar_afn=True,
            mostrar_afd=True,
        )

        if resultado is None:
            print("\nLa expresión no pudo procesarse.")

print("\nProcesamiento terminado.")