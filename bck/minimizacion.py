from dataclasses import dataclass, field
from afd import AFD, EstadoAFD

@dataclass(eq=False)
class EstadoAFDMin:
    id: int
    estados_afd: frozenset[EstadoAFD]
    es_aceptacion: bool = False
    transiciones: dict[str, "EstadoAFDMin"] = field(default_factory=dict)

    def agregar_transicion(self, simbolo: str, destino: "EstadoAFDMin"):
        self.transiciones[simbolo] = destino

    def etiqueta_conjunto(self) -> str:
        if not self.estados_afd:
            return "∅"
        ids = sorted(e.id for e in self.estados_afd)
        return "{" + ", ".join(f"D{i}" for i in ids) + "}"

class AFDMinimizado:
    def __init__(self, inicial, estados, alfabeto):
        self.inicial = inicial
        self.estados = estados
        self.alfabeto = tuple(sorted(alfabeto))

    @property
    def estados_aceptacion(self):
        return [e for e in self.estados if e.es_aceptacion]

    def transicion(self, estado, simbolo):
        return estado.transiciones.get(simbolo)

def minimizar_afd(afd: AFD) -> AFDMinimizado:
    if afd is None or afd.inicial is None:
        raise ValueError("No se puede minimizar un AFD vacío.")

    estados = set(afd.estados)
    alfabeto = tuple(sorted(afd.alfabeto))

    if not estados:
        raise ValueError("El AFD no contiene estados.")

    finales = frozenset(e for e in estados if e.es_aceptacion)
    no_finales = frozenset(estados - set(finales))

    particiones = [p for p in (finales, no_finales) if p]
    pendientes = list(particiones)

    while pendientes:
        actual = pendientes.pop()
        for simbolo in alfabeto:
            preimagen = frozenset(
                estado for estado in estados
                if afd.transicion(estado, simbolo) in actual
            )

            nuevas = []
            for grupo in particiones:
                inter = grupo & preimagen
                diff = grupo - preimagen
                if inter and diff:
                    nuevas.extend((frozenset(inter), frozenset(diff)))
                    if grupo in pendientes:
                        pendientes.remove(grupo)
                        pendientes.extend((frozenset(inter), frozenset(diff)))
                    else:
                        menores = inter if len(inter) <= len(diff) else diff
                        pendientes.append(frozenset(menores))
                else:
                    nuevas.append(grupo)
            particiones = nuevas

    particiones.sort(key=lambda p: min(e.id for e in p))
    grupo_por_estado = {}
    for i, grupo in enumerate(particiones):
        for estado in grupo:
            grupo_por_estado[estado] = i

    estados_min = [
        EstadoAFDMin(
            id=i,
            estados_afd=frozenset(grupo),
            es_aceptacion=any(e.es_aceptacion for e in grupo),
        )
        for i, grupo in enumerate(particiones)
    ]

    for i, grupo in enumerate(particiones):
        representante = min(grupo, key=lambda e: e.id)
        for simbolo in alfabeto:
            destino = afd.transicion(representante, simbolo)
            if destino is None:
                continue
            estados_min[i].agregar_transicion(
                simbolo, estados_min[grupo_por_estado[destino]]
            )

    return AFDMinimizado(
        inicial=estados_min[grupo_por_estado[afd.inicial]],
        estados=estados_min,
        alfabeto=alfabeto,
    )

minimizar = minimizar_afd