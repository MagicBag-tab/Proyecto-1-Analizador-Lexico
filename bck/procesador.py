from utils import tokenizar, expandir_plus, expandir_question, insertar_concatenacion
from shunting_yard import shunting_yard
from balanceador import balanceada
from arbol_sintactico import construir_arbol_sintactico
from visualizador import dibujar_arbol, dibujar_afn, dibujar_afd, dibujar_afd_minimizado
from afn import construir_afn_thompson
from afd import construccion_subconjuntos
from minimizacion import minimizar_afd
from simulacion import simular_afn, simular_afd

def procesar(
    expresion,
    cadena=None,
    numero=None,
    mostrar_arbol=False,
    mostrar_afn=True,
    mostrar_afd=True,
    mostrar_minimizado=True,
    simular=True,
):
    if not expresion or not expresion.strip():
        raise ValueError("La expresión regular está vacía.")

    print("=" * 80)
    print("Expresión regular:", expresion)

    if not balanceada(expresion):
        print("\nERROR: expresión no balanceada.")
        return None

    try:
        tokens_originales = tokenizar(expresion)
        if not tokens_originales:
            raise ValueError("La expresión regular no contiene tokens.")

        tokens = expandir_plus(tokens_originales)
        tokens = expandir_question(tokens)
        tokens = insertar_concatenacion(tokens)

        postfix = shunting_yard(tokens)
        arbol = construir_arbol_sintactico(postfix)
        afn = construir_afn_thompson(arbol)
        afd = construccion_subconjuntos(afn)
        afd_min = minimizar_afd(afd)

        print("\nPostfix:", " ".join(postfix))
        print(f"AFN: {len(afn.estados)} estados")
        print(f"AFD por subconjuntos: {len(afd.estados)} estados")
        print(f"AFD minimizado: {len(afd_min.estados)} estados")
        print("Alfabeto:", ", ".join(afd.alfabeto) if afd.alfabeto else "∅")

        if mostrar_arbol:
            dibujar_arbol(arbol, expresion, numero=numero, mostrar=False, guardar=True)
        if mostrar_afn:
            dibujar_afn(afn, expresion, numero=numero, mostrar=False, guardar=True)
        if mostrar_afd:
            dibujar_afd(afd, expresion, numero=numero, mostrar=False, guardar=True)
        if mostrar_minimizado:
            dibujar_afd_minimizado(afd_min, expresion, numero=numero, mostrar=False, guardar=True)

        resultados = None
        if simular and cadena is not None:
            afn_ok = simular_afn(afn, cadena, mostrar=True)
            afd_ok = simular_afd(afd, cadena, mostrar=True, nombre="AFD por subconjuntos")
            min_ok = simular_afd(afd_min, cadena, mostrar=True, nombre="AFD minimizado")
            resultados = {
                "afn": afn_ok,
                "afd": afd_ok,
                "afd_minimizado": min_ok,
            }

        return {
            "expresion": expresion,
            "cadena": cadena,
            "tokens": tokens_originales,
            "postfix": postfix,
            "arbol": arbol,
            "afn": afn,
            "afd": afd,
            "afd_minimizado": afd_min,
            "resultados": resultados,
        }

    except (ValueError, IndexError) as e:
        print("\nERROR:", e)
        return None