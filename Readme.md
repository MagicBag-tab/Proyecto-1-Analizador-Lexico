# Proyecto 1: Analizador Léxico

Aplicación web para analizar expresiones regulares y construir los autómatas
correspondientes. El sistema muestra el proceso completo:

1. Conversión de infix a postfix mediante Shunting Yard.
2. Construcción del árbol sintáctico.
3. Construcción del AFN mediante Thompson.
4. Conversión del AFN a AFD mediante subconjuntos.
5. Minimización del AFD por particiones.
6. Minimización del AFD mediante Myhill-Nerode.
7. Simulación de una cadena sobre los autómatas generados.

## Estructura

- `bck/`: API Flask y algoritmos de análisis, construcción, minimización y simulación.
- `frt/`: interfaz web React con Vite.
- `afn/`, `afd/` y `afd_minimizado/`: archivos generados y resultados visuales.
- `docker-compose.yml`: configuración para ejecutar backend y frontend juntos.

## Ejecución con Docker

Desde la raíz del proyecto:

```bash
docker compose up --build
```

Después, abre [http://localhost:5173](http://localhost:5173). La API queda
disponible en [http://localhost:5000](http://localhost:5000).

Para detener los servicios:

```bash
docker compose down
```

## Ejecución manual

### Backend

Requiere Python 3.12 o compatible:

```bash
cd bck
pip install -r requirements.txt
python main.py
```

El backend se ejecuta en `http://localhost:5000`.

### Frontend

En otra terminal, desde la raíz del proyecto:

```bash
cd frt
npm install
npm run dev
```

La interfaz se ejecuta en `http://localhost:5173` y redirige las peticiones
`/api` al backend local.

## Comandos del frontend

Desde `frt/`:

```bash
npm run dev      # servidor de desarrollo
npm run build    # compilación de producción
npm run preview  # vista previa de la compilación
npm run lint     # revisión de código
```

## Uso

1. Introduce una expresión regular, por ejemplo `(a|b)*abb`.
2. Introduce la cadena que quieres reconocer, por ejemplo `aabbb`.
3. Pulsa **Analizar expresión**.
4. Consulta la aceptación en cada autómata y avanza por las etapas de la construcción.