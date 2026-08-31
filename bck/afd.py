from dataclasses import dataclass, field
from collections import deque
from typing import FrozenSet, Iterable
from afn import AFN, Estado, EPSILON

@dataclass(eq=False)
class EstadoAFD:
    id: int
    conjunto_afn: FrozenSet[Estado]
    es_aceptacion: bool = False
    transiciones: dict[str, "EstadoAFD"] = field(default_factory=dict)

    def agregar_transicion(self, simbolo: str, destino: "EstadoAFD"):
        self.transiciones[simbolo] = destino

    def etiqueta_conjunto(self) -> str:
        if not self.conjunto_afn:
            return "∅"
        ids = sorted(estado.id for estado in self.conjunto_afn)
        return "{" + ", ".join(f"q{i}" for i in ids) + "}"

class AFD:
    def __init__(
        self,
        inicial: EstadoAFD,
        estados: list[EstadoAFD],
        alfabeto: Iterable[str],
        subconjuntos: dict[FrozenSet[Estado], EstadoAFD],
    ):
        self.inicial = inicial
        self.estados = estados
        self.alfabeto = tuple(sorted(alfabeto))
        self.subconjuntos = subconjuntos

    @property
    def estados_aceptacion(self) -> list[EstadoAFD]:
        return [estado for estado in self.estados if estado.es_aceptacion]

    def transicion(self, estado: EstadoAFD, simbolo: str):
        return estado.transiciones.get(simbolo)

    def simular(self, cadena: str):
        actual = self.inicial
        traza = [("", actual)]

        for simbolo in cadena:
            siguiente = actual.transiciones.get(simbolo)

            if siguiente is None:
                traza.append((simbolo, None))
                return False, traza

            actual = siguiente
            traza.append((simbolo, actual))

        return actual.es_aceptacion, traza


def _alfabeto_afn(afn: AFN) -> set[str]:
    return {
        transicion.simbolo
        for estado in afn.estados
        for transicion in estado.transiciones
        if transicion.simbolo != EPSILON
    }

def _mover_sin_cierre(afn: AFN, estados: FrozenSet[Estado], simbolo: str):
    destinos = set()

    for estado in estados:
        for transicion in estado.transiciones:
            if transicion.simbolo == simbolo:
                destinos.add(transicion.destino)

    return destinos

def construccion_subconjuntos(afn: AFN) -> AFD:
    if afn is None or afn.inicial is None:
        raise ValueError("No se puede construir un AFD a partir de un AFN vacío.")

    alfabeto = _alfabeto_afn(afn)
    inicial_conjunto = frozenset(afn.transiciones_epsilon({afn.inicial}))

    def es_aceptacion(conjunto: FrozenSet[Estado]) -> bool:
        return afn.aceptacion in conjunto

    conjuntos: dict[FrozenSet[Estado], EstadoAFD] = {}
    estados: list[EstadoAFD] = []
    pendientes = deque()

    estado_inicial = EstadoAFD(
        id=0,
        conjunto_afn=inicial_conjunto,
        es_aceptacion=es_aceptacion(inicial_conjunto),
    )
    conjuntos[inicial_conjunto] = estado_inicial
    estados.append(estado_inicial)
    pendientes.append(inicial_conjunto)

    siguiente_id = 1

    while pendientes:
        conjunto_actual = pendientes.popleft()
        estado_actual = conjuntos[conjunto_actual]

        for simbolo in sorted(alfabeto):
            destinos = _mover_sin_cierre(afn, conjunto_actual, simbolo)
            cierre = frozenset(afn.transiciones_epsilon(destinos))

            if cierre not in conjuntos:
                nuevo_estado = EstadoAFD(
                    id=siguiente_id,
                    conjunto_afn=cierre,
                    es_aceptacion=es_aceptacion(cierre),
                )
                siguiente_id += 1
                conjuntos[cierre] = nuevo_estado
                estados.append(nuevo_estado)
                pendientes.append(cierre)

            estado_actual.agregar_transicion(simbolo, conjuntos[cierre])

    return AFD(
        inicial=estado_inicial,
        estados=estados,
        alfabeto=alfabeto,
        subconjuntos=conjuntos,
    )

construir_afd_subconjuntos = construccion_subconjuntos
