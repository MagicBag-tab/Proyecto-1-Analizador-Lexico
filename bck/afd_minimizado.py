from dataclasses import dataclass, field
from typing import FrozenSet, List, Optional
from afd import AFD, EstadoAFD


@dataclass(eq=False)
class EstadoAFDMin:
    id: int
    estados_originales: FrozenSet[EstadoAFD]
    es_aceptacion: bool = False
    transiciones: dict[str, "EstadoAFDMin"] = field(default_factory=dict)

    def agregar_transicion(self, simbolo: str, destino: "EstadoAFDMin"):
        self.transiciones[simbolo] = destino

    def etiqueta_conjunto(self) -> str:
        if not self.estados_originales:
            return "∅"
        ids = sorted(estado.id for estado in self.estados_originales)
        return "{" + ", ".join(f"D{i}" for i in ids) + "}"


class AFDMinimizado:
    def __init__(
        self,
        inicial: EstadoAFDMin,
        estados: List[EstadoAFDMin],
        alfabeto,
    ):
        self.inicial = inicial
        self.estados = estados
        self.alfabeto = tuple(sorted(alfabeto))

    @property
    def estados_aceptacion(self) -> List[EstadoAFDMin]:
        return [estado for estado in self.estados if estado.es_aceptacion]

    def transicion(self, estado: EstadoAFDMin, simbolo: str):
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


def _particion_inicial(afd: AFD):
    """Divide los estados en dos grupos: terminales y no terminales."""
    no_terminales = frozenset(
        estado for estado in afd.estados if not estado.es_aceptacion
    )
    terminales = frozenset(
        estado for estado in afd.estados if estado.es_aceptacion
    )

    particion = []
    if no_terminales:
        particion.append(no_terminales)
    if terminales:
        particion.append(terminales)

    return particion


def _grupo_de(estado: Optional[EstadoAFD], particion) -> Optional[int]:
    """Devuelve el índice del grupo al que pertenece un estado.
    Si el estado es None (no hay transición), se trata como un
    grupo especial 'muerto' que también es consistente entre estados."""
    if estado is None:
        return None

    for indice, grupo in enumerate(particion):
        if estado in grupo:
            return indice

    return None


def _refinar(particion, afd: AFD):
    """Genera una nueva partición separando estados que ya no se comportan
    igual (no van al mismo subconjunto con los mismos símbolos)."""
    nueva_particion = []

    for grupo in particion:
        subgrupos = {}

        for estado in grupo:
            firma = tuple(
                _grupo_de(afd.transicion(estado, simbolo), particion)
                for simbolo in afd.alfabeto
            )
            subgrupos.setdefault(firma, set()).add(estado)

        for subgrupo in subgrupos.values():
            nueva_particion.append(frozenset(subgrupo))

    return nueva_particion


def minimizar_afd(afd: AFD) -> AFDMinimizado:
    """
    Minimiza un AFD mediante el algoritmo de partición de estados
    equivalentes:

    1. Se separan los estados en terminales / no terminales.
    2. Se refina la partición mientras existan estados de un mismo
       grupo que, con algún símbolo, terminen en subconjuntos distintos.
    3. Cuando la partición deja de cambiar, cada grupo final se convierte
       en un único estado del AFD minimizado.
    """
    if afd is None or afd.inicial is None:
        raise ValueError("No se puede minimizar un AFD vacío.")

    particion = _particion_inicial(afd)

    while True:
        nueva_particion = _refinar(particion, afd)

        if set(nueva_particion) == set(particion):
            particion = nueva_particion
            break

        particion = nueva_particion

    # Orden estable: el grupo que contiene al estado con menor id va primero.
    particion_final = sorted(particion, key=lambda grupo: min(e.id for e in grupo))

    estado_a_grupo = {}
    for indice, grupo in enumerate(particion_final):
        for estado in grupo:
            estado_a_grupo[estado] = indice

    estados_min = [
        EstadoAFDMin(
            id=indice,
            estados_originales=grupo,
            es_aceptacion=any(estado.es_aceptacion for estado in grupo),
        )
        for indice, grupo in enumerate(particion_final)
    ]

    for indice, grupo in enumerate(particion_final):
        representante = next(iter(grupo))
        estado_min = estados_min[indice]

        for simbolo in afd.alfabeto:
            destino = afd.transicion(representante, simbolo)

            if destino is not None:
                grupo_destino = estado_a_grupo[destino]
                estado_min.agregar_transicion(simbolo, estados_min[grupo_destino])

    inicial_min = estados_min[estado_a_grupo[afd.inicial]]

    return AFDMinimizado(
        inicial=inicial_min,
        estados=estados_min,
        alfabeto=afd.alfabeto,
    )