from utils import tokenizar, expandir_plus, expandir_question, insertar_concatenacion
from shunting_yard import shunting_yard
from balanceador import balanceada
from arbol_sintactico import construir_arbol_sintactico
from visualizador import dibujar_arbol, dibujar_afn, dibujar_afd
from afn import construir_afn_thompson
from afd import construccion_subconjuntos

def procesar(expresion, numero=None, mostrar_arbol=True, mostrar_afn=True, mostrar_afd=True):
    print("=" * 80)
    print("Expresión regular:")
    print(expresion)

    if not balanceada(expresion):
        print("\nERROR: expresión no balanceada.")
        return None

    try:
        tokens = tokenizar(expresion)
        print("\nTokens:")
        print(tokens)

        tokens = expandir_plus(tokens)
        print("\nDespués de expandir +:")
        print(tokens)

        tokens = expandir_question(tokens)
        print("\nDespués de expandir ?:")
        print(tokens)

        tokens = insertar_concatenacion(tokens)
        print("\nDespués de insertar concatenación:")
        print(tokens)

        postfix = shunting_yard(tokens)
        print("\nPostfix:")
        print(" ".join(postfix))

        arbol = construir_arbol_sintactico(postfix)
        print("\nÁrbol sintáctico:")
        print("Preorden:", " -> ".join(arbol.preorden()))
        print("Altura:", arbol.altura())

        if mostrar_arbol:
            dibujar_arbol(arbol, expresion, numero=numero, mostrar=True, guardar=True)

        afn = construir_afn_thompson(arbol)

        print("\nAFN de Thompson:")
        print(f"Estado inicial: q{afn.inicial.id}")
        print(f"Estado de aceptación: q{afn.aceptacion.id}")
        print(f"Cantidad de estados: {len(afn.estados)}")

        if mostrar_afn:
            dibujar_afn(afn, expresion, numero=numero, mostrar=True, guardar=True)

        afd = construccion_subconjuntos(afn)

        print("\nAFD por construcción de subconjuntos:")
        print(f"Estado inicial: D{afd.inicial.id} = {afd.inicial.etiqueta_conjunto()}")
        print(f"Cantidad de estados: {len(afd.estados)}")
        print(f"Alfabeto: {', '.join(afd.alfabeto) if afd.alfabeto else '∅'}")
        print("Estados de aceptación:", ", ".join(
            f"D{estado.id} = {estado.etiqueta_conjunto()}"
            for estado in afd.estados_aceptacion
        ) or "ninguno")

        print("Transiciones del AFD:")
        for estado in afd.estados:
            for simbolo in afd.alfabeto:
                destino = estado.transiciones.get(simbolo)
                if destino is not None:
                    print(
                        f"  D{estado.id} --{simbolo}--> D{destino.id}"
                        f"   {destino.etiqueta_conjunto()}"
                    )

        if mostrar_afd:
            dibujar_afd(afd, expresion, numero=numero, mostrar=True, guardar=True)

        return {
            "expresion": expresion,
            "tokens": tokens,
            "postfix": postfix,
            "arbol": arbol,
            "afn": afn,
            "afd": afd,
        }

    except ValueError as e:
        print("\nERROR:", e)
        return None