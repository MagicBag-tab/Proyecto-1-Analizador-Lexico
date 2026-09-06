from afn import AFN, Estado, EPSILON

def simular_afn(afn: AFN, cadena: str, mostrar=True) -> bool:
    if afn is None or afn.inicial is None:
        raise ValueError("No se puede simular un AFN vacío.")

    actuales = afn.transiciones_epsilon({afn.inicial})
    if mostrar:
        print(f"\nSimulación AFN para w = {cadena!r}")
        print("Inicio:", _ids(actuales))

    for simbolo in cadena:
        actuales = afn.mover(actuales, simbolo)
        if mostrar:
            print(f"  con {simbolo!r} -> {_ids(actuales)}")

        if not actuales:
            break

    aceptada = afn.aceptacion in actuales
    if mostrar:
        print("Resultado AFN:", "sí" if aceptada else "no")
    return aceptada

def simular_afd(afd, cadena: str, mostrar=True, nombre="AFD") -> bool:
    if afd is None or afd.inicial is None:
        raise ValueError("No se puede simular un AFD vacío.")

    actual = afd.inicial
    if mostrar:
        print(f"\nSimulación {nombre} para w = {cadena!r}")
        print(f"Inicio: {actual.etiqueta_conjunto()}")

    for simbolo in cadena:
        destino = afd.transicion(actual, simbolo)
        if mostrar:
            if destino is None:
                print(f"  con {simbolo!r} -> ∅")
            else:
                print(f"  con {simbolo!r} -> {destino.etiqueta_conjunto()}")
        if destino is None:
            actual = None
            break
        actual = destino

    aceptada = actual is not None and actual.es_aceptacion
    if mostrar:
        print(f"Resultado {nombre}:", "sí" if aceptada else "no")
    return aceptada

def _ids(estados):
    return "{" + ", ".join(f"q{e.id}" for e in sorted(estados, key=lambda x: x.id)) + "}"