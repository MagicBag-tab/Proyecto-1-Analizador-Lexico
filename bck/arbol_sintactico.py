from stack import Stack

class NodoSintactico:
    contador = 0

    def __init__(self, token, izquierdo=None, derecho=None):
        NodoSintactico.contador += 1
        self.id = NodoSintactico.contador
        self.token = token
        self.izquierdo = izquierdo
        self.derecho = derecho

    def es_hoja(self):
        return self.izquierdo is None and self.derecho is None

    def __repr__(self):
        return f"NodoSintactico(id={self.id}, token={self.token!r})"

class ArbolSintactico: 
    def __init__(self, raiz=None):
        self.raiz = raiz

    def esta_vacio(self):
        return self.raiz is None

    def preorden(self):
        resultado = []

        def recorrer(nodo):
            if nodo is None:
                return
            resultado.append(nodo.token)
            recorrer(nodo.izquierdo)
            recorrer(nodo.derecho)

        recorrer(self.raiz)
        return resultado

    def altura(self):
        def calcular(nodo):
            if nodo is None:
                return 0
            return 1 + max(calcular(nodo.izquierdo), calcular(nodo.derecho))

        return calcular(self.raiz)

    def __str__(self):
        return " ".join(self.preorden())

def construir_arbol_sintactico(postfix): 
    operadores_binarios = {"|", "."}
    operadores_unarios = {"*"}

    pila = Stack()

    for token in postfix:
        if token in operadores_unarios:
            if pila.size() < 1:
                raise ValueError(f"El operador unario '{token}' no tiene operando.")

            hijo = pila.pop()
            pila.push(NodoSintactico(token, izquierdo=hijo))

        elif token in operadores_binarios:
            if pila.size() < 2:
                raise ValueError(f"El operador binario '{token}' no tiene dos operandos.")

            derecho = pila.pop()
            izquierdo = pila.pop()

            pila.push(
                NodoSintactico(
                    token,
                    izquierdo=izquierdo,
                    derecho=derecho
                )
            )

        else:
            pila.push(NodoSintactico(token))

    if pila.size() != 1:
        raise ValueError("La expresión postfix no produce un único árbol sintáctico.")

    return ArbolSintactico(pila.pop())