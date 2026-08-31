from dataclasses import dataclass, field
from typing import Optional

EPSILON = "ε"

@dataclass
class Transicion:
    destino: "Estado"
    simbolo: str = EPSILON

@dataclass(eq=False)
class Estado:
    id: int
    transiciones: list[Transicion] = field(default_factory=list)
    es_aceptacion: bool = False

    def agregar_transicion(self, destino: "Estado", simbolo: str = EPSILON):
        self.transiciones.append(Transicion(destino, simbolo))

class AFN:
    def __init__(self, inicial: Estado, aceptacion: Estado, estados: list[Estado]):
        self.inicial = inicial
        self.aceptacion = aceptacion
        self.estados = estados

    def transiciones_epsilon(self, estados):
        """Calcula el cierre-ε de un conjunto de estados."""
        cierre = set(estados)
        pila = list(estados)

        while pila:
            estado = pila.pop()
            for transicion in estado.transiciones:
                if transicion.simbolo == EPSILON and transicion.destino not in cierre:
                    cierre.add(transicion.destino)
                    pila.append(transicion.destino)

        return cierre

    def mover(self, estados, simbolo):
        """Obtiene los estados alcanzables con un símbolo y luego aplica cierre-ε."""
        destinos = set()

        for estado in estados:
            for transicion in estado.transiciones:
                if transicion.simbolo == simbolo:
                    destinos.add(transicion.destino)

        return self.transiciones_epsilon(destinos)

    def simular(self, cadena):
        """
        Simula el AFN mediante conjuntos de estados.
        Devuelve (aceptada, traza), donde la traza contiene los estados
        activos después de cada paso.
        """
        actuales = self.transiciones_epsilon({self.inicial})
        traza = [("", sorted(estado.id for estado in actuales))]

        for simbolo in cadena:
            actuales = self.mover(actuales, simbolo)
            traza.append((simbolo, sorted(estado.id for estado in actuales)))

            if not actuales:
                for restante in cadena[len(traza) - 1:]:
                    traza.append((restante, []))
                break

        return self.aceptacion in actuales, traza

class ConstructorThompson:
    def __init__(self):
        self.siguiente_id = 0
        self.estados = []

    def nuevo_estado(self, es_aceptacion=False):
        estado = Estado(self.siguiente_id, es_aceptacion=es_aceptacion)
        self.siguiente_id += 1
        self.estados.append(estado)
        return estado

    def simbolo(self, token):
        inicio = self.nuevo_estado()
        fin = self.nuevo_estado()
        inicio.agregar_transicion(fin, EPSILON if token == EPSILON else token)
        return inicio, fin

    def concatenacion(self, izquierda, derecha):
        inicio_izq, fin_izq = izquierda
        inicio_der, fin_der = derecha
        fin_izq.agregar_transicion(inicio_der, EPSILON)
        return inicio_izq, fin_der

    def union(self, izquierda, derecha):
        inicio = self.nuevo_estado()
        fin = self.nuevo_estado()

        inicio_izq, fin_izq = izquierda
        inicio_der, fin_der = derecha

        inicio.agregar_transicion(inicio_izq, EPSILON)
        inicio.agregar_transicion(inicio_der, EPSILON)
        fin_izq.agregar_transicion(fin, EPSILON)
        fin_der.agregar_transicion(fin, EPSILON)

        return inicio, fin

    def estrella(self, operando):
        inicio = self.nuevo_estado()
        fin = self.nuevo_estado()

        inicio_op, fin_op = operando

        inicio.agregar_transicion(fin, EPSILON)
        inicio.agregar_transicion(inicio_op, EPSILON)
        fin_op.agregar_transicion(inicio_op, EPSILON)
        fin_op.agregar_transicion(fin, EPSILON)

        return inicio, fin

    def construir(self, arbol):
        if arbol is None or arbol.raiz is None:
            raise ValueError("No se puede construir un AFN a partir de un árbol vacío.")

        pila = []

        def recorrer(nodo):
            if nodo is None:
                return
            recorrer(nodo.izquierdo)
            recorrer(nodo.derecho)
            pila.append(nodo)

        recorrer(arbol.raiz)

        pila = []

        def construir_nodo(nodo):
            if nodo is None:
                raise ValueError("Nodo sintáctico inválido.")

            if nodo.token == "*":
                return self.estrella(construir_nodo(nodo.izquierdo))

            if nodo.token == ".":
                izquierda = construir_nodo(nodo.izquierdo)
                derecha = construir_nodo(nodo.derecho)
                return self.concatenacion(izquierda, derecha)

            if nodo.token == "|":
                izquierda = construir_nodo(nodo.izquierdo)
                derecha = construir_nodo(nodo.derecho)
                return self.union(izquierda, derecha)

            return self.simbolo(nodo.token)

        inicio, fin = construir_nodo(arbol.raiz)
        fin.es_aceptacion = True

        return AFN(inicio, fin, self.estados)

def construir_afn_thompson(arbol):
    return ConstructorThompson().construir(arbol)
