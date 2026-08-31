from stack import Stack

class Balanceador:
    def __init__(self):
        self.apertura = {
            "(": ")",
            "[": "]",
            "{": "}"
        }

        self.cierre = {
            ")": "(",
            "]": "[",
            "}": "{"
        }

    def verificar(self, expresion):
        pila = Stack()

        print("\nExpresión:", expresion)

        i = 0

        while i < len(expresion):
            caracter = expresion[i]

            if caracter == "\\":
                if i + 1 < len(expresion):
                    siguiente = expresion[i + 1]

                    if siguiente in "()[]{}":
                        i += 2
                        continue

                    if siguiente in "ntr":
                        i += 2
                        continue

            if caracter in self.apertura:
                pila.push(caracter)
                print(f"'{caracter}' PUSH\tPila = {pila}")

            elif caracter in self.cierre:
                if pila.is_empty():
                    print(f"'{caracter}' ERROR (la pila está vacía)")
                    return False

                ultimo = pila.pop()
                print(f"'{caracter}' POP '{ultimo}'\tPila = {pila}")

                if ultimo != self.cierre[caracter]:
                    print("No coincide el símbolo de apertura.")
                    return False

            i += 1

        if pila.is_empty():
            print("Resultado: Expresión balanceada")
            return True

        else:
            print("Resultado: Quedaron símbolos sin cerrar, no se pudo balancear la expresión", pila)
            return False

def balanceada(expresion):
    balanceador = Balanceador()
    return balanceador.verificar(expresion)