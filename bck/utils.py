OPERADORES = {"|", ".", "*", "+", "?"}

def tokenizar(expresion):
    tokens = []
    i = 0
    expresion = expresion.replace("∗", "*")

    while i < len(expresion):
        if expresion[i].isspace():
            i += 1
            continue

        caracter = expresion[i]

        if caracter == "\\":
            if i + 1 >= len(expresion):
                raise ValueError("Secuencia de escape incompleta.")

            tokens.append(expresion[i:i + 2])
            i += 2
            continue

        if caracter == "[":
            j = i + 1

            while j < len(expresion) and expresion[j] != "]":
                j += 1

            if j == len(expresion):
                raise ValueError("Clase de caracteres '[' sin cerrar.")

            tokens.append(expresion[i:j + 1])
            i = j + 1
            continue

        if caracter.isalnum() or caracter == "ε":
            tokens.append(caracter)
            i += 1
            continue

        tokens.append(caracter)
        i += 1

    return tokens

def es_operando(token):
    return (
        token not in OPERADORES
        and token not in {"(", ")"}
    )

def insertar_concatenacion(tokens):
    resultado = []

    for i in range(len(tokens)):
        actual = tokens[i]
        resultado.append(actual)

        if i == len(tokens) - 1:
            continue

        siguiente = tokens[i + 1]

        izquierda = (
            es_operando(actual)
            or actual in {")", "*", "+", "?"}
        )

        derecha = (
            es_operando(siguiente)
            or siguiente == "("
        )

        if izquierda and derecha:
            resultado.append(".")

    return resultado

def obtener_operando(tokens, indice):
    fin = indice - 1

    if fin < 0:
        return [], 0

    if tokens[fin] != ")":
        return [tokens[fin]], fin

    contador = 1
    inicio = fin - 1

    while inicio >= 0:

        if tokens[inicio] == ")":
            contador += 1

        elif tokens[inicio] == "(":
            contador -= 1

            if contador == 0:
                break

        inicio -= 1

    if contador != 0:
        raise ValueError("Paréntesis desbalanceados.")

    return tokens[inicio:fin + 1], inicio

def expandir_plus(tokens):
    resultado = []
    i = 0

    while i < len(tokens):

        if tokens[i] != "+":
            resultado.append(tokens[i])
            i += 1
            continue

        if not resultado:
            raise ValueError("Uso inválido del operador '+'.")

        operando, inicio = obtener_operando(resultado, len(resultado))
        resultado = resultado[:inicio]

        resultado.extend(operando)
        resultado.append(".")

        resultado.extend(operando)
        resultado.append("*")

        i += 1

    return resultado

def expandir_question(tokens):
    resultado = []
    i = 0

    while i < len(tokens):
        if tokens[i] != "?":
            resultado.append(tokens[i])
            i += 1
            continue

        if not resultado:
            raise ValueError("Uso inválido del operador '?'.")

        operando, inicio = obtener_operando(resultado, len(resultado))
        resultado = resultado[:inicio]

        resultado.extend([
            "(",
            "ε",
            "|"
        ])

        resultado.extend(operando)
        resultado.append(")")

        i += 1

    return resultado