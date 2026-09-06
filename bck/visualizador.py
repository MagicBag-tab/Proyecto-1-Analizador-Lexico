from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
from arbol_sintactico import NodoSintactico
from afn import EPSILON, AFN

def _agregar_nodos(grafo, nodo, profundidad=0, posiciones=None, hojas=None):
    if posiciones is None:
        posiciones = {}

    if hojas is None:
        hojas = [0]

    if nodo is None:
        return posiciones, hojas

    grafo.add_node(nodo.id, label=nodo.token, profundidad=profundidad)

    hijos = [hijo for hijo in (nodo.izquierdo, nodo.derecho) if hijo is not None]

    for hijo in hijos:
        grafo.add_edge(nodo.id, hijo.id)
        _agregar_nodos(
            grafo,
            hijo,
            profundidad + 1,
            posiciones,
            hojas
        )

    if nodo.es_hoja():
        posiciones[nodo.id] = (hojas[0], -profundidad)
        hojas[0] += 1

    else:
        coordenadas_hijos = [
            posiciones[hijo.id]
            for hijo in hijos
            if hijo.id in posiciones
        ]
        if coordenadas_hijos:
            x = sum(punto[0] for punto in coordenadas_hijos) / len(coordenadas_hijos)
            posiciones[nodo.id] = (x, -profundidad)

    return posiciones, hojas

def dibujar_arbol(arbol, expresion, numero=None, mostrar=True, guardar=True):
    if arbol is None or arbol.raiz is None:
        raise ValueError("No se puede dibujar un árbol vacío.")

    grafo = nx.DiGraph()
    posiciones, _ = _agregar_nodos(grafo, arbol.raiz)

    etiquetas = nx.get_node_attributes(grafo, "label")

    ancho = max(10, len(grafo.nodes) * 0.8)
    alto = max(5, arbol.altura() * 1.3)

    figura, eje = plt.subplots(figsize=(ancho, alto))

    nx.draw_networkx_edges(
        grafo,
        posiciones,
        ax=eje,
        arrows=False,
        width=1.5
    )

    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        ax=eje,
        node_size=1700,
        node_color="white",
        edgecolors="black",
        linewidths=1.5
    )

    nx.draw_networkx_labels(
        grafo,
        posiciones,
        labels=etiquetas,
        ax=eje,
        font_size=11
    )

    titulo = "Árbol sintáctico"

    if numero is not None:
        titulo += f" - Expresión {numero}"

    eje.set_title(titulo)
    eje.axis("off")
    figura.tight_layout()

    if guardar:
        carpeta = Path("arboles")
        carpeta.mkdir(exist_ok=True)

        nombre = f"arbol_{numero}.png" if numero is not None else "arbol.png"
        ruta = carpeta / nombre
        figura.savefig(ruta, dpi=160, bbox_inches="tight")
        print(f"\nÁrbol guardado en: {ruta}")

    if mostrar:
        plt.show()

    else:
        plt.close(figura)

    return figura

def dibujar_afn(afn: AFN, expresion, numero=None, mostrar=True, guardar=True):
    if afn is None:
        raise ValueError("No se puede dibujar un AFN vacío.")

    grafo = nx.DiGraph()
    posiciones = {}
    niveles = {}
    visitados = set()
    cola = [(afn.inicial, 0)]

    while cola:
        estado, nivel = cola.pop(0)

        if estado.id in visitados:
            continue

        visitados.add(estado.id)
        niveles.setdefault(nivel, []).append(estado)

        for transicion in estado.transiciones:
            if transicion.destino.id not in visitados:
                cola.append((transicion.destino, nivel + 1))

    for estado in afn.estados:
        if estado.id not in visitados:
            niveles.setdefault(max(niveles, default=0) + 1, []).append(estado)

    for nivel, estados in niveles.items():
        estados.sort(key=lambda estado: estado.id)
        desplazamiento = (len(estados) - 1) / 2

        for indice, estado in enumerate(estados):
            posiciones[estado.id] = (indice - desplazamiento, -nivel)

    for estado in afn.estados:
        grafo.add_node(
            estado.id,
            label=f"q{estado.id}",
            aceptacion=estado.es_aceptacion
        )

    etiquetas_transiciones = {}

    for estado in afn.estados:
        for transicion in estado.transiciones:
            clave = (estado.id, transicion.destino.id)
            etiquetas_transiciones.setdefault(clave, []).append(transicion.simbolo)

    for (origen, destino), simbolos in etiquetas_transiciones.items():
        grafo.add_edge(
            origen,
            destino,
            label=", ".join(dict.fromkeys(simbolos))
        )

    figura, eje = plt.subplots(
        figsize=(max(12, len(afn.estados) * 0.65), max(7, len(niveles) * 1.8))
    )

    estados_normales = [
        estado.id for estado in afn.estados
        if not estado.es_aceptacion
    ]
    estados_aceptacion = [
        estado.id for estado in afn.estados
        if estado.es_aceptacion
    ]

    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        nodelist=estados_normales,
        node_size=1500,
        node_color="white",
        edgecolors="black",
        linewidths=1.5,
        ax=eje
    )

    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        nodelist=estados_aceptacion,
        node_size=1800,
        node_color="white",
        edgecolors="black",
        linewidths=2.5,
        node_shape="o",
        ax=eje
    )

    for estado_id in estados_aceptacion:
        x, y = posiciones[estado_id]
        circulo = plt.Circle(
            (x, y),
            0.12,
            fill=False,
            linewidth=1.5,
            transform=eje.transData
        )
        eje.add_patch(circulo)

    nx.draw_networkx_edges(
        grafo,
        posiciones,
        ax=eje,
        arrows=True,
        arrowsize=18,
        connectionstyle="arc3,rad=0.08",
        width=1.4
    )

    etiquetas = {
        estado.id: f"q{estado.id}"
        for estado in afn.estados
    }

    nx.draw_networkx_labels(
        grafo,
        posiciones,
        labels=etiquetas,
        ax=eje,
        font_size=10
    )

    etiquetas_aristas = nx.get_edge_attributes(grafo, "label")

    nx.draw_networkx_edge_labels(
        grafo,
        posiciones,
        edge_labels=etiquetas_aristas,
        ax=eje,
        font_size=9,
        label_pos=0.5
    )

    x, y = posiciones[afn.inicial.id]

    eje.annotate(
        "",
        xy=(x - 0.45, y),
        xytext=(x - 1.15, y),
        arrowprops=dict(arrowstyle="->", linewidth=1.5)
    )

    titulo = "AFN de Thompson"

    if numero is not None:
        titulo += f" - Expresión {numero}"

    eje.set_title(f"{titulo}\nr = {expresion}", fontsize=12)
    eje.axis("off")
    figura.tight_layout()

    if guardar:
        carpeta = Path("afn")
        carpeta.mkdir(exist_ok=True)

        nombre = f"afn_{numero}.png" if numero is not None else "afn.png"
        ruta = carpeta / nombre
        figura.savefig(ruta, dpi=160, bbox_inches="tight")
        print(f"AFN guardado en: {ruta}")

    if mostrar:
        plt.show()

    else:
        plt.close(figura)

    return figura

def dibujar_afd(afd, expresion, numero=None, mostrar=True, guardar=True):
    if afd is None or afd.inicial is None:
        raise ValueError("No se puede dibujar un AFD vacío.")

    grafo = nx.DiGraph()
    posiciones = {}
    estados = list(afd.estados)
    cantidad = len(estados)

    for indice, estado in enumerate(estados):
        posiciones[estado.id] = (indice, 0)

    for estado in estados:
        grafo.add_node(
            estado.id,
            label=f"D{estado.id}\n{estado.etiqueta_conjunto()}",
            aceptacion=estado.es_aceptacion,
        )

    etiquetas_transiciones = {}

    for estado in estados:
        for simbolo, destino in estado.transiciones.items():
            clave = (estado.id, destino.id)
            etiquetas_transiciones.setdefault(clave, []).append(simbolo)

    for (origen, destino), simbolos in etiquetas_transiciones.items():
        grafo.add_edge(
            origen,
            destino,
            label=", ".join(dict.fromkeys(simbolos)),
        )

    ancho = max(14, cantidad * 2.4)
    figura, eje = plt.subplots(figsize=(ancho, 7))
    normales = [estado.id for estado in estados if not estado.es_aceptacion]
    aceptacion = [estado.id for estado in estados if estado.es_aceptacion]

    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        nodelist=normales,
        node_size=2300,
        node_color="white",
        edgecolors="black",
        linewidths=1.5,
        ax=eje,
    )

    nx.draw_networkx_nodes(
        grafo,
        posiciones,
        nodelist=aceptacion,
        node_size=2500,
        node_color="white",
        edgecolors="black",
        linewidths=2.5,
        node_shape="o",
        ax=eje,
    )

    for estado_id in aceptacion:
        x, y = posiciones[estado_id]
        circulo = plt.Circle(
            (x, y),
            0.15,
            fill=False,
            linewidth=1.5,
            transform=eje.transData,
        )
        eje.add_patch(circulo)

    nx.draw_networkx_edges(
        grafo,
        posiciones,
        ax=eje,
        arrows=True,
        arrowsize=18,
        connectionstyle="arc3,rad=0.10",
        width=1.4,
    )

    etiquetas = nx.get_node_attributes(grafo, "label")
    nx.draw_networkx_labels(
        grafo,
        posiciones,
        labels=etiquetas,
        ax=eje,
        font_size=9,
    )

    etiquetas_aristas = nx.get_edge_attributes(grafo, "label")
    nx.draw_networkx_edge_labels(
        grafo,
        posiciones,
        edge_labels=etiquetas_aristas,
        ax=eje,
        font_size=9,
        label_pos=0.5,
    )

    x, y = posiciones[afd.inicial.id]
    eje.annotate(
        "",
        xy=(x - 0.35, y),
        xytext=(x - 1.15, y),
        arrowprops=dict(arrowstyle="->", linewidth=1.5),
    )

    titulo = "AFD - Construcción de Subconjuntos"

    if numero is not None:
        titulo += f" - Expresión {numero}"

    eje.set_title(f"{titulo}\nr = {expresion}", fontsize=12,)
    eje.axis("off")
    figura.tight_layout()

    if guardar:
        carpeta = Path("afd")
        carpeta.mkdir(exist_ok=True)

        nombre = f"afd_{numero}.png" if numero is not None else "afd.png"
        ruta = carpeta / nombre
        figura.savefig(ruta, dpi=160, bbox_inches="tight")
        print(f"AFD guardado en: {ruta}")

    if mostrar:
        plt.show()
    else:
        plt.close(figura)

    return figura

def dibujar_afd_minimizado(afd, expresion, numero=None, mostrar=True, guardar=True):
    """Dibuja el AFD resultante de la minimización."""
    if afd is None or afd.inicial is None:
        raise ValueError("No se puede dibujar un AFD minimizado vacío.")

    grafo = nx.DiGraph()
    posiciones = {}
    estados = list(afd.estados)

    for indice, estado in enumerate(estados):
        posiciones[estado.id] = (indice, 0)

    for estado in estados:
        grafo.add_node(
            estado.id,
            label=f"M{estado.id}\n{estado.etiqueta_conjunto()}",
            aceptacion=estado.es_aceptacion,
        )

    etiquetas_transiciones = {}
    for estado in estados:
        for simbolo, destino in estado.transiciones.items():
            clave = (estado.id, destino.id)
            etiquetas_transiciones.setdefault(clave, []).append(simbolo)

    for (origen, destino), simbolos in etiquetas_transiciones.items():
        grafo.add_edge(
            origen,
            destino,
            label=", ".join(dict.fromkeys(simbolos)),
        )

    figura, eje = plt.subplots(figsize=(max(14, len(estados) * 2.4), 7))
    normales = [e.id for e in estados if not e.es_aceptacion]
    finales = [e.id for e in estados if e.es_aceptacion]

    nx.draw_networkx_nodes(
        grafo, posiciones, nodelist=normales, node_size=2300,
        node_color="white", edgecolors="black", linewidths=1.5, ax=eje
    )
    nx.draw_networkx_nodes(
        grafo, posiciones, nodelist=finales, node_size=2500,
        node_color="white", edgecolors="black", linewidths=2.5, ax=eje
    )

    for estado_id in finales:
        x, y = posiciones[estado_id]
        eje.add_patch(plt.Circle(
            (x, y), 0.15, fill=False, linewidth=1.5, transform=eje.transData
        ))

    nx.draw_networkx_edges(
        grafo, posiciones, ax=eje, arrows=True, arrowsize=18,
        connectionstyle="arc3,rad=0.10", width=1.4
    )
    nx.draw_networkx_labels(
        grafo, posiciones,
        labels=nx.get_node_attributes(grafo, "label"),
        ax=eje, font_size=9
    )
    nx.draw_networkx_edge_labels(
        grafo, posiciones,
        edge_labels=nx.get_edge_attributes(grafo, "label"),
        ax=eje, font_size=9, label_pos=0.5
    )

    x, y = posiciones[afd.inicial.id]
    eje.annotate(
        "", xy=(x - 0.35, y), xytext=(x - 1.15, y),
        arrowprops=dict(arrowstyle="->", linewidth=1.5)
    )

    titulo = "AFD Minimizado"
    if numero is not None:
        titulo += f" - Expresión {numero}"
    eje.set_title(f"{titulo}\nr = {expresion}", fontsize=12)
    eje.axis("off")
    figura.tight_layout()

    if guardar:
        carpeta = Path("afd_minimizado")
        carpeta.mkdir(exist_ok=True)
        nombre = f"afd_minimizado_{numero}.png" if numero is not None else "afd_minimizado.png"
        ruta = carpeta / nombre
        figura.savefig(ruta, dpi=160, bbox_inches="tight")
        print(f"AFD minimizado guardado en: {ruta}")

    if mostrar:
        plt.show()
    else:
        plt.close(figura)

    return figura