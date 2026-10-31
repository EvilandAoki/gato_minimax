# Explicación completa del proyecto y verificación de que cumple el enunciado

Este documento responde dos preguntas:

1. **¿Cuál es la idea y cómo funciona, en detalle?** (secciones 1 a 8)
2. **¿Cómo se comprueba que cumple lo que pide `proyecto_1_2026.pdf`?** (secciones 2, 9 y 10)

Todo número que aparece aquí salió de ejecutar el código del repositorio (los comandos para repetirlo
están en la sección 11). Lo que no se pudo comprobar, o lo que es una limitación, está dicho
explícitamente en la sección 10.

---

## 1. La idea en una página

El enunciado pide **una sola aplicación** que resuelva problemas con cinco algoritmos programados por
el grupo: DFS, BFS, costo uniforme (UCS), A\* con heurística propia y Minimax con poda alfa-beta. Prohíbe
el laberinto y exige que Minimax tenga un escenario de dos jugadores.

La idea del proyecto es **usar el juego del gato para todo**, con dos modos que comparten tablero y
filosofía:

| Modo | Agentes | Problema | Algoritmos |
|---|---|---|---|
| **Gato contra la máquina** | 2 (por turnos) | Jugar gato normal: colocar fichas hasta alinear tres | Minimax con poda alfa-beta, profundidad límite y función de evaluación |
| **Gato en movimiento** | 1 | Un tablero ya tiene fichas X y obstáculos O; se *mueven* las X hasta formar una línea | DFS, BFS, UCS, A\* con heurística propia |

¿Por qué hacen falta dos modos? Porque Minimax necesita un rival que responda, y DFS, BFS, UCS y A\*
necesitan un problema de **un solo agente** con **costos distintos** (UCS y A\* no tienen sentido si
todo cuesta igual). El gato normal no cumple eso; por eso se inventó la variante donde las fichas
se mueven. El enunciado lo permite expresamente: *"Si el problema principal es de un solo agente, la
aplicación puede tener un segundo modo de juego adversario"*, y viceversa en la lista de ideas
válidas ("Combinaciones").

**¿Por qué no es un laberinto?** En un laberinto se busca el camino de *un* agente hasta *una casilla*.
Aquí el estado son varias fichas a la vez y la meta no es una casilla sino un *patrón* (cualquier línea
de fichas). Aun así es un riesgo de interpretación; ver sección 10.

---

## 2. Matriz de cumplimiento del enunciado

Cada requisito del PDF, dónde está resuelto y cómo se verifica.

### 2.1 Requisitos técnicos

| Requisito del PDF | Dónde se cumple | Verificación |
|---|---|---|
| DFS: encontrar una solución, reportar camino y nodos expandidos | `busqueda.dfs` | `test_todos_encuentran_solucion_valida` repite el camino jugada por jugada y comprueba que termina en la meta |
| BFS: solución con menor número de pasos | `busqueda.bfs` | `test_bfs_menos_pasos_ucs_menos_costo` |
| UCS: costos no todos iguales, menor costo total | `busqueda.ucs` + costos 2 y 3 en `movil.costo` | `test_ucs_y_astar_dan_el_costo_optimo` compara contra un Dijkstra independiente escrito en el test |
| A\*: heurística propia, explicada y analizada (admisibilidad y consistencia) | `ProblemaMovil.heuristica` (h1) y `heuristica_simple` (h2) | `test_admisible_y_consistente` la comprueba por fuerza bruta en todos los estados alcanzables de los casos 1 a 3; la demostración está en la sección 6 |
| Minimax con poda alfa-beta, jugador humano o IA, función de evaluación y profundidad límite | `minimax._evaluar`, `evaluacion`, parámetro `prof_max` | `test_alfabeta_igual_que_minimax_en_cada_profundidad`, `test_evaluacion_nunca_supera_una_victoria` |
| Algoritmos programados por el grupo, sin librerías que los resuelvan | Solo biblioteca estándar (`heapq`, `collections.deque`, `tracemalloc`); no hay dependencias externas | Revisar los imports de `gato/busqueda.py` y `gato/minimax.py` |

### 2.2 Restricciones y condiciones de la aplicación

| Requisito del PDF | Cómo se cumple |
|---|---|
| No se permite laberinto | El problema de un agente es de patrón multificha, no de camino a una casilla (secciones 1 y 10) |
| Minimax requiere dos jugadores con turnos | Gato normal: humano contra máquina |
| Permitir elegir qué algoritmo ejecutar | Menú principal opción 5: DFS / BFS / UCS / A\* / comparar los 4 / comparar heurísticas |
| Mostrar solución, nodos expandidos, profundidad o costo, tiempo | `solitario.ejecutar_algoritmo` imprime jugadas, costo, pasos, expandidos, generados, memoria y milisegundos |
| Minimax: nodos evaluados **con y sin poda** | `juego._explicar_ia` los muestra en cada jugada de la máquina; la opción 4 y `experimentos.tabla_minimax` los comparan en varias posiciones y profundidades |
| Python preferible; consola clara aceptable | Python 3.12, consola con colores ANSI |
| Ejecutar según el README sin modificaciones | `README.md`: `python3 main.py`, sin instalar nada |

### 2.3 Entregables

| Entregable | Estado |
|---|---|
| Código fuente + README con requisitos, instalación, ejecución e integrantes | Hecho; los **integrantes** están como marcador por completar |
| Informe PDF (estructura de 11 secciones) | Borrador completo en `informe/informe.md`; falta pasarlo a PDF y completar los marcadores |
| Presentación PDF (≤ 15 min) | Guion de 12 diapositivas en `informe/presentacion.md`; faltan las diapositivas en sí |
| Declarar fuentes y herramientas de IA | Declarado en README e informe; el grupo debe ajustarlo a su uso real |

### 2.4 Rúbrica de aplicación y código (40 puntos)

| Criterio (puntos) | Lo que pide el nivel "Excelente" | Evidencia en el proyecto |
|---|---|---|
| DFS y BFS (8) | Funcionan en todos los casos, controlan repetidos, reportan camino y métricas | Los 4 casos se resuelven; `explorados` / `vistos`; `ResultadoBusqueda` con camino y métricas |
| Costo uniforme (6) | Costos distintos, cola de prioridad, siempre menor costo | Costos 2 y 3; `heapq`; test contra Dijkstra independiente |
| A\* con heurística propia (8) | Admisible, bien implementada, expande menos nodos que UCS | h1 admisible; test `test_astar_expande_menos_que_ucs` en los 4 casos |
| Minimax con poda (10) | Poda correcta, evaluación sólida, juega competitivo, muestra nodos con y sin poda | Poda verificada contra Minimax en cada profundidad; evaluación acotada; contadores con y sin poda |
| Funcionalidad e interfaz (5) | Elegir algoritmo, mostrar solución y métricas sin errores | Menú y tabla comparativa; ver límites en la sección 10 |
| Calidad del código y README (3) | Modular, comentado, README completo y ejecutable | Módulos separados, docstrings, README y esta documentación |

### 2.5 Rúbrica del informe (35) y presentación (25)

El borrador `informe/informe.md` sigue el orden exacto del PDF (portada, introducción, formulación,
arquitectura con diagramas de flujo, algoritmos, heurísticas, evidencias, análisis comparativo,
conclusiones, referencias, anexos). Lo que **no se puede entregar sin el grupo**: capturas de pantalla,
portada, referencias definitivas, la elección razonada de la profundidad límite y las conclusiones
propias. La presentación necesita las diapositivas y que **todos** los integrantes conozcan **todos**
los algoritmos (el PDF lo exige explícitamente); `informe/presentacion.md` trae preguntas probables.

---

## 3. Arquitectura del código

```
main.py                         menú principal
gato/
  tablero.py      reglas del gato normal (tupla de 9 celdas, turnos, ganador, dibujo)
  minimax.py      Minimax + alfa-beta + evaluacion (una sola función recursiva, _evaluar)
  arbol.py        clase Nodo, dibujo ASCII del árbol, exportación a .txt
  juego.py        partida humano contra máquina
  animacion.py    reproducción paso a paso del algoritmo
  estadisticas.py conteo del árbol completo y comparación Minimax contra alfa-beta
  movil.py        problema "Gato en movimiento": estado, acciones, costos, meta, heurísticas
  busqueda.py     DFS, BFS, UCS, A* + medir() (tiempo y memoria)
  solitario.py    interfaz de consola del Gato en movimiento
  experimentos.py tablas del informe
  consola.py      colores ANSI, entrada
tests/            45 pruebas (36 anteriores + 9 de torneo)
informe/          borrador de informe, guion de presentación, resultados medidos
```

**Idea de diseño importante:** `busqueda.py` es *genérico*. No sabe nada del gato. Cualquier problema
que ofrezca `estado_inicial`, `acciones(s)`, `resultado(s, a)`, `costo(s, a)`, `es_meta(s)` y
`heuristica(s)` se puede resolver con los cuatro algoritmos. Eso es justamente lo que pide la
formulación como espacio de estados del enunciado (estado inicial, acciones, transición, prueba de meta
y costo de camino), y separa el *problema* de los *algoritmos*.

Flujo general de la aplicación:

```
Usuario ─► main.py ─┬─ 5 ─► solitario.menu_movil ─► elegir caso ─► busqueda.medir(algoritmo)
                    │                                              └► problema.acciones / resultado / costo / es_meta / heuristica
                    │                                   ◄─ ResultadoBusqueda ◄─┘ ─► imprimir solución y métricas
                    └─ 1 ─► juego.jugar ─► (turno humano: _pedir_jugada)
                                           (turno máquina: minimax y alfabeta con prof_max ─► nodos con y sin poda)
```

---

## 4. Gato en movimiento: el problema de un agente, en detalle

### 4.1 Reglas

- Tablero de N×N (3, 4 o 5). Hay **k fichas X móviles** y algunas **O fijas** (obstáculos que nunca se mueven).
- Una **jugada** mueve una X a una casilla **vecina** (8 direcciones, un solo paso) que esté libre (sin X ni O).
- **Meta:** que las k fichas X ocupen exactamente las k casillas de una línea (fila, columna o diagonal de
  k casillas seguidas) que no contenga ninguna O.
- **Costo:** mover en línea recta cuesta **2**; mover en diagonal cuesta **3**.

¿Por qué 2 y 3? Con costos iguales, BFS y UCS serían el mismo algoritmo. Con 2 y 3 el camino con menos
pasos puede ser más caro que uno con más pasos... en teoría. En este tablero, para una sola ficha sin
estorbos, el camino con menos pasos también es el más barato (la diagonal 3 es menor que dos pasos rectos 4).
La diferencia real aparece por los **obstáculos y las fichas que se estorban**, y por eso el caso 2 se
buscó expresamente: hay empates en número de pasos (5) y BFS elige uno más caro. Ver sección 5.3.

### 4.2 Modelado como espacio de estados (lo que pide la sección 3 del informe)

| Elemento | Definición | Código |
|---|---|---|
| **Estado** | `frozenset` con los índices (0 a N²−1) de las casillas con X | tipo del estado en `movil.py` |
| **Estado inicial** | El de cada caso de prueba | `ProblemaMovil.estado_inicial` |
| **Acciones** | `(origen, destino)` para cada X y cada vecino libre | `acciones(estado)` |
| **Transición** | `(estado − {origen}) ∪ {destino}` | `resultado(estado, accion)` |
| **Prueba de meta** | `estado in self.lineas` | `es_meta(estado)` |
| **Costo** | 2 recto, 3 diagonal | `costo(estado, accion)` |

**Por qué `frozenset` y no una lista o tupla de 9 celdas.** (a) Es hashable, así que se puede guardar en
los conjuntos `explorados` / `vistos` que evitan repetir estados. (b) Es inmutable: aplicar una jugada
crea un estado nuevo y no se corrompe el del padre. (c) Las fichas X son indistinguibles: el conjunto
{1, 5} es el mismo estado sin importar cuál ficha está en cuál casilla. Una tupla ordenada duplicaría
estados equivalentes. Las O y el tamaño N **no están en el estado** porque nunca cambian.

**Tamaño del espacio de estados.** Como máximo C(casillas libres, k) estados:

| Caso | Tablero | Fichas | Casillas sin O | Estados como máximo | Líneas válidas |
|---|---|---|---|---:|---:|
| 1 | 3×3 | 3 | 7 | C(7,3) = 35 | 2 |
| 2 | 4×4 | 4 | 14 | C(14,4) = 1.001 | 5 |
| 3 | 4×4 | 4 | 14 | C(14,4) = 1.001 | 5 |
| 4 | 5×5 | 4 | 24 | C(24,4) = 10.626 | 20 |

(Alcanzables pueden ser menos si los obstáculos separan regiones.) Son espacios finitos y pequeños: por
eso todos los algoritmos terminan, y por eso se pueden comprobar por fuerza bruta.

**Casos de prueba** (`X` ficha móvil, `O` obstáculo, `.` libre):

```
Caso 1 (3×3)         Caso 2 (4×4, BFS≠UCS)   Caso 3 (4×4 esquinas)    Caso 4 (5×5)
X . X                . . . .                 X . . X                  X . . . X
. O .                X O . X                 . O . .                  . . . . .
X . O                . X O .                 . . O .                  . . O . .
                     . . X .                 X . . X                  . . . . .
                                                                      X . . . X
```

### 4.3 La función `distancia` (base de la heurística)

`distancia(a, b, n) = 3·min(dr, dc) + 2·|dr − dc|`, donde `dr` y `dc` son las diferencias de fila y de columna.
Es el costo exacto de llevar **una** ficha de `a` a `b` si el tablero estuviera vacío: se usan todas las diagonales
posibles (3 cada una, más baratas que dos pasos rectos que costarían 4) y se completa con pasos rectos (2).

Ejemplos (tablero 3×3, casillas numeradas desde 0): `d(0,1) = 2` (un paso recto), `d(0,4) = 3` (una diagonal),
`d(0,5) = 3 + 2 = 5` (diagonal y recto), `d(0,8) = 6` (dos diagonales). Los cuatro están en `test_distancia_octil`.

---

## 5. Los algoritmos de búsqueda, en detalle

### 5.1 Esqueleto común

Todos mantienen:

- **Frontera:** nodos descubiertos que aún no se han expandido.
- **Explorados:** estados ya expandidos. Es **imprescindible**: en este problema mover una ficha y devolverla
  crea ciclos; sin explorados, DFS no terminaría nunca.
- **Nodo** (`NodoBusqueda`): `estado`, `padre`, `accion`, `g` (costo acumulado) y `prof` (pasos). Para recuperar
  la solución se sigue la cadena de `padre` hasta la raíz (`camino()`).

Lo único que distingue un algoritmo de otro es **qué estructura de datos es la frontera**, porque decide
qué nodo sale primero:

| Algoritmo | Estructura | Sale primero | Función |
|---|---|---|---|
| DFS | pila (`list`, LIFO) | el último que entró: baja por una rama hasta el fondo | `dfs` |
| BFS | cola (`deque`, FIFO) | el primero que entró: avanza nivel por nivel | `bfs` |
| UCS | cola de prioridad (`heapq`) por `g` | el de menor costo acumulado | `ucs` → `_mejor_primero` |
| A\* | cola de prioridad por `g + h` | el de menor costo estimado total | `astar` → `_mejor_primero` |

**Convención de métricas** (importante para comparar con justicia):
`expandidos` = nodos a los que se les generaron sucesores (el nodo meta **no** se cuenta);
`generados` = nodos creados, incluidos los repetidos que se descartan;
`max_memoria` = máximo de |frontera| + |explorados| en algún instante;
`pico_bytes` = pico de memoria de Python (`tracemalloc`);
`tiempo_ms` = milisegundos de reloj.

### 5.2 DFS (`dfs`)

1. Se apila el nodo inicial. Mientras haya nodos: se saca el **último**; si su estado ya está explorado se ignora;
   si no, se marca explorado y se expande.
2. Para cada acción se crea el hijo; si ya está explorado se descarta; si es meta, se termina; si no, se apila.
3. Los hijos se apilan **al revés** (`reversed`) para que la primera jugada de la lista sea la primera en explorarse.
   Esto hace el recorrido determinista y reproducible.

**Qué se espera ver:** soluciones **largas y caras**, porque DFS se compromete con una rama y la sigue hasta que
se agota, sin importarle si hay un atajo. Resultado medido: en el caso 2, DFS halla una solución de **75 pasos y costo
170**, frente a 5 pasos y costo 10 del óptimo. Es correcto según el enunciado (*"encontrar una solución"*), y es
justamente lo que se explica en la presentación sobre en qué se diferencian las soluciones.

**Propiedades:** completo aquí porque el espacio es finito y se controlan repetidos; **no óptimo**.

### 5.3 BFS (`bfs`)

1. Cola FIFO; `vistos` guarda todo lo que ya se encoló (frontera + explorados) para no encolar un estado dos veces.
2. Se saca el **primero**, se expande y para cada hijo nuevo se **prueba la meta al generarlo** (en BFS es seguro:
   el primer hijo meta que aparezca está en el nivel más superficial posible).

**Garantía:** menor **número de pasos**. **No** garantiza menor **costo**. Evidencia real, caso 2:

| Algoritmo | Jugadas (costo de cada una) | Pasos | Costo total |
|---|---|---:|---:|
| BFS | 5→2 (3), 2→7 (3), 8→4 (2), 10→13 (3), 15→10 (3) | 5 | **14** |
| UCS | 5→9 (2), 8→12 (2), 9→13 (2), 10→14 (2), 12→16 (2) | 5 | **10** |

Las dos hallan una solución de 5 pasos (el mínimo posible). BFS se queda con la primera que encuentra, que
usa cuatro diagonales (cada una cuesta 3) y un solo paso recto; UCS encuentra la de cinco pasos rectos (cada uno cuesta 2).
Esto demuestra con datos que **minimizar pasos no es minimizar costo**, que es lo que la rúbrica de UCS quiere ver.
`test_caso_donde_bfs_y_ucs_difieren` fija este resultado (14 contra 10, mismos pasos).

### 5.4 UCS y A\* (`_mejor_primero`)

Comparten el mismo código; solo cambia la función `prioridad`:

```python
ucs   → prioridad = n.g
astar → prioridad = n.g + h(n.estado)
```

Pasos:

1. `frontera` es un `heapq` de tuplas `(prioridad, contador, nodo)`. El `contador` desempata prioridades iguales
   porque `NodoBusqueda` no se puede comparar con `<`.
2. Se saca el nodo de **menor prioridad**. Si su estado ya está en `explorados`, es una **entrada obsoleta** y se ignora.
3. **La meta se prueba al SACAR el nodo, no al generarlo.** Razón: al generar un nodo meta solo se conoce *un*
   camino hacia ella, que puede no ser el más barato. Al sacarla de la cola de prioridad, ninguno de los caminos
   pendientes puede ser mejor (con `h` admisible), así que es óptima.
4. Si no es meta, se marca explorado y se generan hijos. `mejor_g[estado]` guarda el menor costo conocido; un hijo
   solo se encola si **mejora** ese costo (`h.g < mejor_g`). Si aparece un camino más barato a un estado ya
   encolado, se encola otra vez; la entrada vieja quedará obsoleta y se ignora al sacarla.

**Por qué entradas obsoletas y no "actualizar la prioridad":** `heapq` no permite modificar un elemento ya insertado;
la técnica estándar es insertar de nuevo e ignorar las viejas.

**Propiedades:** UCS es completo y óptimo (los costos son ≥ 2 > 0). A\* es óptimo si `h` es **admisible**; si además
es **consistente**, nunca hay que reabrir un estado ya explorado (por eso basta con `explorados`).

### 5.5 Traza real de A\* (caso 1)

Tablero inicial (X en 1, 3 y 7; O en 5 y 9):

```
 X │ 2 │ X
───┼───┼───
 4 │ O │ 6
───┼───┼───
 X │ 8 │ O
```

La heurística da `h = 5` en el estado inicial. Orden en que A\* saca nodos (medido):

| Se saca | X en | g | h | f = g + h | Comentario |
|---|---|---:|---:|---:|---|
| 1.º | 1, 3, 7 | 0 | 5 | 5 | Estado inicial |
| 2.º | 1, 2, 7 | 2 | 3 | 5 | La ficha 3 se movió a 2 (recto, cuesta 2) |
| 3.º | 1, 3, 4 | 2 | 3 | 5 | La ficha 7 se movió a 4 (recto, cuesta 2) |
| 4.º | 1, 4, 7 | 5 | 0 | 5 | **META** (columna izquierda): ficha 2 → 4 en diagonal, +3 |

Dos cosas se ven con claridad: (1) `f` **nunca baja** y se mantiene en 5 durante toda la búsqueda, que es la
firma de una heurística consistente y exacta aquí; (2) A\* solo **expandió 3 nodos** frente a 19 de UCS
(`test_astar_expande_menos_que_ucs` lo exige en los 4 casos). La solución es `3→2, 2→4`, costo `2 + 3 = 5`.

---

## 6. La heurística de A\*: definición, ejemplo y demostración

### 6.1 Definición (h1)

```
h1(s) = mínimo, sobre las líneas válidas L, de
          mínimo, sobre las formas de asignar cada ficha a una casilla distinta de L, de
            suma de distancia(ficha, casilla)
```

Como k ≤ 4, las asignaciones se prueban todas con `itertools.permutations` (como máximo 4! = 24 por línea).

**Intuición:** "el costo mínimo de reorganizar las fichas en una línea si nada estorbara". Es una **relajación del
problema**: se ignoran los obstáculos intermedios y las colisiones entre fichas. Toda heurística admisible
razonable nace así.

### 6.2 Ejemplo calculado (caso 1)

Líneas válidas (sin O): fila superior (1, 2, 3) y columna izquierda (1, 4, 7). Fichas en 1, 3 y 7.

- **Fila superior:** las fichas 1 y 3 ya están en la línea. La ficha 7 debe llegar a la casilla 2:
  `d(7, 2) = 3·min(2,1) + 2·|2−1| = 3 + 2 = 5`. Total 5.
- **Columna izquierda:** las fichas 1 y 7 ya están. La ficha 3 debe llegar a la casilla 4:
  `d(3, 4) = 3·min(1,2) + 2·|1−2| = 3 + 2 = 5`. Total 5.
- `h1 = min(5, 5) = 5`, y el costo óptimo real también es 5. La heurística es exacta en este estado.

### 6.3 Admisibilidad: nunca sobreestima

1. `distancia(a, b)` es el costo exacto de una ficha en un tablero vacío; las condiciones reales (obstáculos y otras
   fichas) solo pueden **encarecer** o impedir caminos, nunca abaratarlos.
2. Cualquier solución termina con las X ocupando alguna línea válida y cada ficha en una casilla distinta de ella;
   su costo es al menos el de **alguna** asignación, que es ≥ el mínimo sobre todas.
3. Por tanto `h1(s) ≤ costo real hasta la meta`.

### 6.4 Consistencia: `h(s) ≤ c(s, a) + h(s')`

1. Una jugada mueve **una** ficha de `p` a `q` con costo `c`, y `c = distancia(p, q)` (recto 2, diagonal 3; coincide con
   la fórmula octil para un paso).
2. La distancia es una **métrica** (cumple la desigualdad triangular): para cualquier casilla `x`,
   `distancia(q, x) ≥ distancia(p, x) − c`.
3. Fijada una asignación, la suma en `s'` baja como máximo `c` respecto a la de `s`; al tomar el mínimo sobre
   asignaciones y líneas la desigualdad se conserva.
4. Conclusión: `h1(s) ≤ c + h1(s')`.

### 6.5 Verificación empírica

`test_admisible_y_consistente` hace lo siguiente en los casos 1, 2 y 3: enumera **todos** los estados alcanzables,
calcula el costo exacto hasta la meta con un Dijkstra multifuente (las jugadas son reversibles y cuestan lo mismo en
ambos sentidos, así que basta partir de todas las metas a la vez) y comprueba para h1 **y** h2 que `h(s) ≤ costo real`
en cada estado y que `h(s) ≤ c + h(s')` en cada arista. Pasa. Además `test_h1_domina_a_h2` comprueba que h1 ≥ h2 en cada estado
muestreado (por eso h1 es "más informada").

### 6.6 La segunda heurística (h2) y la comparación

`h2(s) = 2 × (casillas de la mejor línea que todavía no tienen X)`. Cada jugada llena como mucho una casilla y cuesta
al menos 2, así que es admisible y consistente, pero ignora las distancias. Resultados medidos (nodos expandidos):

| Caso | UCS (h = 0) | A\* con h2 | A\* con h1 |
|---|---:|---:|---:|
| 1 (3×3) | 19 | 7 | 3 |
| 2 (4×4) | 684 | 155 | 24 |
| 3 (4×4) | 480 | 158 | 15 |
| 4 (5×5) | 8.060 | 4.176 | 475 |

Más información en la heurística, menos nodos. Pero hay un **costo oculto**: h1 prueba permutaciones en cada nodo.
En el caso 4 el tiempo medido fue ≈ 1.100 ms con h1 contra ≈ 130 ms de UCS, a pesar de expandir 17 veces menos nodos.
"Menos nodos expandidos" no implica "menos tiempo"; esto es un buen punto de discusión para el informe.

---

## 7. Minimax con poda alfa-beta, en detalle

### 7.1 MAX, MIN y utilidad

La IA es **MAX** durante toda la búsqueda (variable `ia`); el rival es **MIN**. Quién mueve en cada nodo lo dice
`jugador`, que alterna con `oponente()`. Si `jugador == ia`, el nodo maximiza; si no, minimiza.

La utilidad solo existe en las hojas (partida terminada): `10 − profundidad` si gana la IA, `profundidad − 10` si
gana el rival, `0` si empata. Restar la profundidad hace que la IA prefiera ganar pronto y perder tarde.

### 7.2 El contexto `ctx` y las variables de `_evaluar`

`_evaluar(t, ia, jugador, prof, alfa, beta, nodo, ctx)` es la **única** función recursiva; Minimax y alfa-beta
son la misma función con `ctx.poda` en `False` o `True`.

| Variable | Qué es | ¿Cambia al recursar? |
|---|---|---|
| `t` | tablero actual | sí (jugada aplicada) |
| `ia` | ficha de MAX | **no** |
| `jugador` | a quién le toca | sí (alterna) |
| `prof` | jugadas desde la raíz | sí (`+1`) |
| `alfa` | piso que MAX ya tiene asegurado | se **hereda** y puede subir |
| `beta` | techo que MIN ya tiene asegurado | se **hereda** y puede bajar |
| `nodo` | objeto `Nodo` donde anotar resultados (o `None`) | sí |
| `ctx` | contexto compartido | **no**, misma instancia |
| `mejor` | valor provisional del nodo (±infinito al inicio) | local |
| `mejor_mov` | jugada que produjo `mejor` | local |
| `maximiza` | `jugador == ia` | local |

`ctx` (`_Ctx`) es un objeto creado **una sola vez** en `_buscar()` y compartido por toda la recursión:

| Campo | Para qué |
|---|---|
| `poda` | **El único interruptor** entre Minimax (`False`) y alfa-beta (`True`) |
| `prof_max` | Profundidad límite; al llegarse se llama a `evaluacion()` (99 = sin límite) |
| `construir` y `prof_arbol` | Si se guardan objetos `Nodo`, y hasta qué profundidad (el árbol completo desde el tablero vacío tiene 549.946 nodos) |
| `callback` | Función a avisar en cada evento (la animación lo usa) |
| `nodos` | **Contador mutable** de nodos evaluados |

`nodos` está en un objeto y no es un parámetro entero porque un entero pasado por parámetro se copia; un atributo de
un objeto compartido no, así que `ctx.nodos += 1` en cualquier nivel de la recursión lo ve toda la búsqueda.

### 7.3 Cómo funciona alfa-beta

Cada nodo recibe `alfa` y `beta` heredados del camino hasta la raíz:

- `alfa` = lo mejor que **MAX** ya puede asegurarse (piso). Solo sube.
- `beta` = lo mejor que **MIN** ya puede asegurarse (techo). Solo baja.

Después de evaluar cada hijo, el nodo actualiza su `mejor` y su límite (MAX sube `alfa`, MIN baja `beta`). Si
`alfa ≥ beta`, la ventana quedó vacía: el nodo de arriba ya tiene una alternativa igual o mejor y **nunca elegirá
llegar aquí**, así que los hermanos que faltan no pueden cambiar el resultado y se descartan sin evaluar (`break`).
Los hermanos descartados se guardan como nodos `PODA` solo para dibujarlos con `✂`; no cuentan en `nodos`.

Detalle: la poda usa `≥` (no `>`), por lo que también corta empates. Y el valor que devuelve un nodo cortado es
solo una **cota**, no su valor exacto; por eso `valores_por_movimiento` (que necesita valores exactos) calcula
**sin** poda.

### 7.4 Profundidad límite y función de evaluación

El gato es tan pequeño que Minimax llega siempre al final, pero el enunciado exige una profundidad límite y una
función de evaluación. Con `prof_max=d`, al llegar a profundidad `d` el nodo **no se expande**: se marca `CORTE` y su
valor es `evaluacion(t, ia)`.

`evaluacion` recorre las 8 líneas ganadoras:

| Línea | Aporte |
|---|---|
| solo fichas de la IA: una / dos | +1 / +10 |
| solo fichas del rival: una / dos | −1 / −10 |
| fichas de ambos (nadie puede completarla) | 0 |
| centro de la IA | +1 |

y divide el total entre 100. **Por qué dividir:** una victoria real vale `10 − profundidad`, como mínimo 1 (profundidad 9).
Si la estimación pudiera valer más que eso, la IA preferiría una posición que "parece buena" a ganar de verdad.
El total está entre −80 y +81, así que `|evaluacion| < 1` siempre. `test_evaluacion_nunca_supera_una_victoria` lo verifica
en **todas** las posiciones no terminales alcanzables, para X y para O.

**Ejemplo calculado a mano** (verificado con el árbol de la sección 7.5): tablero `X O X | O X · | · · O`, evalúa la IA = X.

- Fila 3 (`· · O`): solo O, una ficha → −1.
- Diagonal `(2, 4, 6)` = `X X ·`: solo X, dos fichas → +10.
- Las demás líneas están mezcladas → 0.
- Centro de X → +1.
- Total 10 → 10 / 100 = **+0,10**. El árbol impreso por el programa muestra exactamente `v=+0.10`.

### 7.5 Árbol real con corte y poda (posición `XO./.X./..O`, mueve X, profundidad límite 2)

```
[MAX(X)]  raíz  v=+0.02  X O · | · X · | · · O  α=+0.02 β=+∞
├── [MIN(O)]  mov=3  v=-0.08  ...  α=-∞ β=-0.08
│   ├── [CORTE]  mov=4  v=+0.10   evaluación heurística
│   ├── [CORTE]  mov=6  v=+0.11
│   ├── [CORTE]  mov=7  v=-0.08          ← el mínimo: sube al padre
│   └── [CORTE]  mov=8  v=+0.03
├── [MIN(O)]  mov=4  v=+0.00  ...  α=-0.08 β=+0.00     (4 hijos CORTE evaluados)
├── [MIN(O)]  mov=6  v=+0.01  ...  α=+0.00 β=+0.01     (4 hijos CORTE evaluados)
├── [MIN(O)]  mov=7  v=+0.02  ...  α=+0.01 β=+0.02     (4 hijos CORTE evaluados)  ← el mejor: la raíz sube a +0.02
└── [MIN(O)]  mov=8  v=-0.07  ...  α=+0.02 β=-0.07
    ├── [CORTE]  mov=3  v=-0.07
    ├── ✂ mov=4  podado  (β=-0.07 ≤ α=+0.02)
    ├── ✂ mov=6  podado
    └── ✂ mov=7  podado
```

Se lee así: cada nodo MIN (jugada de O) elige el mínimo de sus hijos `CORTE`. La raíz (MAX) elige el máximo entre sus cinco
hijos: +0,02, en la casilla 7. En el último nodo MIN, tras evaluar el primer hijo (−0,07) se tiene `β = −0,07`, y como la raíz
ya asegura `α = +0,02`, resulta `β ≤ α`: no importa lo que valgan los otros tres hijos, la raíz no elegirá esa rama. Se podan.
Resultado medido: **26 nodos** con Minimax y **23** con alfa-beta, misma jugada (7) y mismo valor.

### 7.6 Ahorro de la poda (medido)

Desde el tablero vacío (mueve X), nodos evaluados:

| Profundidad límite | Minimax | Alfa-beta | Ahorro |
|---:|---:|---:|---:|
| 2 | 82 | 36 | 56,1 % |
| 3 | 586 | 174 | 70,3 % |
| 4 | 3.610 | 630 | 82,5 % |
| 5 | 18.730 | 2.873 | 84,7 % |
| 6 | 73.450 | 4.743 | 93,5 % |
| 9 (sin límite) | 549.946 | 20.866 | **96,2 %** |

El ahorro **crece con la profundidad**: cuanto más grande el árbol, más ramas hay que descartar. Con profundidad 1
no hay poda posible (10 contra 10). En todas las filas Minimax y alfa-beta dan la **misma jugada y el mismo valor**
(el script `experimentos.py` lo comprueba con un `assert`). Las jugadas se prueban en orden numérico, sin ordenarlas;
ordenar mejor las jugadas podaría aún más.

---

## 8. Verificación: qué prueba cada test

Hay **45 pruebas** (`python3 -m unittest`), todas pasan (las 9 últimas, de `tests/test_torneo.py`, se describen en la sección 13). Resumen de lo que garantiza cada grupo:

| Grupo | Qué demuestra |
|---|---|
| Tablero (3) | Las 8 líneas, empate sin ganador, turno deducido y aplicar jugada |
| Árbol completo (2) | 549.946 nodos y nodos por nivel conocidos |
| Minimax (6) | Gato perfecto = empate; gana de inmediato; bloquea; prefiere ganar rápido; árbol guardado consistente |
| Alfa-beta (3) | Misma jugada y valor que Minimax en posiciones de comparación y en **todas** las posiciones con ≤ 6 casillas libres |
| IA como X y como O (3) | La máquina nunca pierde contra ninguna jugada humana posible, jugando como X y como O |
| Profundidad límite (6) | `\|evaluacion\| < 1` en todas las posiciones; `prof_max=None` equivale a 9; alfa-beta igual a Minimax en cada profundidad; cortes marcados como `CORTE`; bloquea con profundidad 2 |
| Problema móvil (3) | Distancia octil correcta; acciones no pisan fichas ni obstáculos; meta exige línea sin O |
| Algoritmos (7) | Todos devuelven caminos válidos y repetibles; BFS mínimo en pasos; UCS y A\* mínimo en costo **comparado con Dijkstra independiente**; A\* expande menos que UCS; caso BFS≠UCS fijo; caso sin solución; estado inicial ya meta |
| Heurística (3) | Admisible y consistente (h1 y h2); vale 0 en la meta; h1 ≥ h2 |

**Lo que NO está probado automáticamente** (ver sección 10): la admisibilidad de h1 en el caso 4 (5×5) se argumenta
pero no se enumera por fuerza bruta; los tiempos no se prueban (dependen de la máquina); la interfaz de consola se
probó a mano, no con tests.

---

## 9. Resultados comparativos medidos

Mismos casos, los cuatro algoritmos (tiempos en la máquina de desarrollo, cambian en otra):

| Caso | Alg. | Costo | Pasos | Expandidos | Generados | Memoria máx. (nodos) | Pico (KB) | ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 (3×3) | DFS | 9 | 4 | 4 | 24 | 16 | 7 | 0,1 |
| | BFS | 5 | 2 | 4 | 21 | 15 | 6 | 0,0 |
| | UCS | 5 | 2 | 19 | 118 | 35 | 14 | 0,1 |
| | A\* | 5 | 2 | 3 | 18 | 14 | 6 | 0,2 |
| 2 (4×4) | DFS | 170 | 75 | 75 | 890 | 661 | 204 | 0,8 |
| | BFS | **14** | 5 | 511 | 6.476 | 871 | 262 | 5,0 |
| | UCS | 10 | 5 | 684 | 8.541 | 946 | 322 | 7,5 |
| | A\* | 10 | 5 | 24 | 281 | 143 | 49 | 14,4 |
| 3 (4×4) | DFS | 197 | 87 | 87 | 1.021 | 742 | 232 | 0,9 |
| | BFS | 10 | 4 | 77 | 938 | 274 | 88 | 0,8 |
| | UCS | 10 | 4 | 480 | 5.930 | 871 | 319 | 5,3 |
| | A\* | 10 | 4 | 15 | 190 | 130 | 43 | 12,8 |
| 4 (5×5) | DFS | 354 | 154 | 154 | 2.431 | 1.773 | 553 | 2,3 |
| | BFS | 17 | 7 | 3.421 | 63.922 | 6.501 | 2.421 | 47,5 |
| | UCS | 17 | 7 | 8.060 | 151.232 | 10.286 | 3.917 | 127,5 |
| | A\* | 17 | 7 | 475 | 9.084 | 3.099 | 1.261 | 1.127,4 |

**Lecturas que se pueden defender en la sustentación:**

1. **DFS expande poco pero la solución es pésima** (costo 170 a 354 contra 10 a 17 óptimos): es rápido porque se compromete sin comparar.
2. **BFS** da el mínimo de pasos; en el caso 2 su costo (14) es peor que el de UCS (10) con los mismos pasos.
3. **UCS** da siempre el costo mínimo, pero expande mucho: no sabe hacia dónde está la meta.
4. **A\*** da el mismo costo que UCS expandiendo entre 6 y 32 veces menos nodos (caso 1: 19 a 3; caso 3: 480 a 15), pero su tiempo
   de reloj puede ser mayor por el costo de calcular la heurística (caso 4).
5. **Memoria:** crece con los nodos que se mantienen a la vez; UCS usa más que A\*, y BFS más que DFS en los casos grandes.

---

## 10. Limitaciones y puntos honestos

Para que el grupo no se sorprenda en la sustentación:

1. **Riesgo de interpretación de "no laberinto".** Mover fichas por una cuadrícula puede parecerle al docente cercano
   a un laberinto. Argumentos: la meta es un patrón multificha, no una casilla; el estado es un conjunto de fichas. **Conviene
   confirmarlo con el docente.** El plan alternativo (gato deslizante tipo 8-puzzle) no está implementado.
2. **La heurística h1 es lenta.** Reduce nodos pero encarece cada uno. Se podría memoizar por estado o evitar probar
   todas las permutaciones (asignación húngara); no se hizo.
3. **Admisibilidad de h1 en el caso 4:** demostrada por argumento y verificada en casos 1 a 3, no enumerada en el 5×5.
4. **Los tiempos dependen de la máquina.** Los números absolutos de las tablas son de una ejecución; las comparaciones
   relativas (nodos, ahorro de la poda) son estables porque no dependen del reloj.
5. **La memoria** se mide de dos maneras (nodos en memoria a la vez y pico de `tracemalloc`); la segunda excluye
   lo que ya estuviera reservado antes de empezar la medición.
6. **Interfaz:** consola clara, sin interfaz gráfica (el enunciado la valora pero no la exige). La consola se probó a mano.
7. **Profundidad límite elegida:** el grupo debe decidirla y justificarla en el informe (sección 6c). El juego deja
   elegirla entre 1 y 9; no se hizo un estudio de "con cuál juega mejor".
8. **Poda y orden de jugadas:** se prueban en orden numérico; no hay ordenamiento heurístico de jugadas.
9. **Entregables que no se pueden generar automáticamente:** capturas, PDF del informe, diapositivas, video de respaldo,
   zip con el nombre pedido, nombres de los integrantes, referencias definitivas y la declaración exacta de herramientas de IA.
10. **Fecha y medio de entrega:** el enunciado dice "pendiente por definir".

---

## 11. Cómo repetir cada verificación

```bash
python3 -m unittest                      # las 45 pruebas
python3 -m unittest tests.test_busqueda  # solo búsqueda y heurísticas
python3 -m gato.experimentos             # todas las tablas de nodos, tiempo y memoria
python3 main.py                          # menú: 1 jugar · 4 comparar poda · 5 gato en movimiento
```

Recorrido sugerido para la demostración (≈ 4 min):

1. Opción 5 → caso 2 → **BFS** → ver costo 14; repetir con **UCS** → costo 10 con los mismos pasos.
2. Opción 5 → caso 4 → "Comparar los 4" → ver cómo A\* expande muchísimos menos nodos que UCS.
3. Opción 5 → caso 4 → "Comparar heurísticas" → h1 contra h2 contra UCS.
4. Opción 1 → jugar con profundidad 3 → ver nodos con y sin poda y el valor de cada casilla; entrar a `[a]` para ver los nodos `CORTE`.
5. Opción 4 → responder `s` para ver el árbol podado con `✂`.

## 12. Glosario rápido

| Término | Significado en este proyecto |
|---|---|
| Estado | Posición de las fichas X (`frozenset`) en el modo móvil; tablero de 9 celdas en el modo adversario |
| Frontera | Nodos descubiertos aún no expandidos (pila, cola o heap según el algoritmo) |
| Explorados | Estados ya expandidos; evitan ciclos |
| `g` | Costo acumulado desde el estado inicial |
| `h` | Heurística: estimación del costo restante hasta la meta |
| `f = g + h` | Prioridad de A\* |
| Admisible | `h` nunca sobreestima el costo real |
| Consistente | `h(s) ≤ c + h(s')` para toda jugada |
| MAX / MIN | Jugador que maximiza (la IA) / minimiza (el rival) la utilidad |
| `alfa` / `beta` | Piso de MAX / techo de MIN, heredados en el árbol |
| Poda | Descartar hermanos cuando `alfa ≥ beta` |
| `CORTE` | Nodo donde la búsqueda se detiene por profundidad límite y se estima con `evaluacion` |
| `ctx` | Contexto compartido de una búsqueda Minimax (poda, `prof_max`, callback, contador de nodos) |

---

## 13. Competencias entre algoritmos (torneo y competencia de búsqueda)

El torneo enfrenta 7 jugadores de máquina todos contra todos: un aleatorio (referencia),
alfa-beta con profundidad 1, 2, 3 y completa (9), y dos con una evaluación alternativa "posicional"
(centro +3, esquinas +1) a profundidad 2 y 3. Minimax y alfa-beta **no** compiten entre sí: dan la misma
jugada, solo empatarían; por eso todos usan alfa-beta y lo que compite es la profundidad y la evaluación.

Para que no se repita la misma partida (los jugadores son deterministas) cada pareja juega 10
**aperturas aleatorias de 2 jugadas**, y cada apertura se juega **dos veces, con cada jugador como X**.
Victoria = 1 punto, empate = 0,5. Los resultados salen de `python3 -m gato.experimentos` con semilla 1
(reproducibles):

| # | Jugador | Ganadas | Empatadas | Perdidas | % de puntos |
|---:|---|---:|---:|---:|---:|
| 1 | Prof 9 (completo) | 48 | 52 | 20 | 61,7 % |
| 2 | Prof 3 posicional | 53 | 40 | 27 | 60,8 % |
| 3 | Prof 3 | 53 | 39 | 28 | 60,4 % |
| 4 | Prof 2 | 45 | 46 | 29 | 56,7 % |
| 5 | Prof 1 | 41 | 49 | 30 | 54,6 % |
| 6 | Prof 2 posicional | 32 | 55 | 33 | 49,6 % |
| 7 | Aleatorio | 2 | 11 | 107 | 6,2 % |

**Cómo leerlo (con honestidad):**
- El **aleatorio queda último con claridad** (6 %): lo único que se afirma con seguridad.
- La profundidad completa queda primera, pero **por poco** frente a profundidad 3 (61,7 % contra 60,4 %). Con 120 partidas por jugador
  esa diferencia está dentro del ruido; más aperturas o más semillas la afinarían. Lo que sí se ve es una tendencia: más profundidad, más puntos.
- **El jugador perfecto pierde partidas (20).** No es un error: las 2 primeras jugadas son aleatorias y no las juega nadie, así que a veces
  dejan a su color en una posición ya perdida. Como cada apertura se juega con ambos colores, el efecto es parejo.
- A profundidad 2 la evaluación **por líneas** (56,7 %) supera a la **posicional** (49,6 %); a profundidad 3 son casi iguales
  (60,4 % contra 60,8 %). La evaluación importa más cuanto menos se ve del árbol.

### Competencia de búsqueda
Aquí "ganar" depende de qué se mida, así que se puntúa cada criterio por caso (el mejor recibe 4 puntos, el peor 0;
los empates comparten puntos) y se suman con pesos: **costo de la solución ×3**, nodos expandidos ×1, memoria ×1, tiempo ×1.
Se pesa más el costo porque una solución rápida pero 20 veces más cara no es mejor. Competidores: DFS, BFS, UCS, A\* con h1 y A\* con h2.

| Competidor | costo (×3) | expandidos | memoria | tiempo | Total (máx. 96) |
|---|---:|---:|---:|---:|---:|
| A\* (h1) | 16 | 15 | 15 | 0 | **78** |
| BFS | 13 | 9 | 9 | 13 | 70 |
| A\* (h2) | 16 | 5 | 7 | 9 | 69 |
| UCS | 16 | 0 | 0 | 4 | 52 |
| DFS | 0 | 12 | 9 | 14 | 35 |

Campeón con estos pesos: **A\* (h1)**. Pero **no es el mejor en todo** y el resultado depende de los pesos:
UCS, A\* (h1) y A\* (h2) empatan en costo (todos óptimos); A\* (h1) gana en nodos y memoria; **DFS gana en tiempo**
(y es último en costo); y A\* (h1) saca **0 puntos en tiempo** (su heurística es cara de calcular). Si el tiempo pesara mucho,
BFS o A\* (h2) pasarían adelante. Es una buena demostración de que la elección del algoritmo es un compromiso.

**Código:** `gato/torneo.py` (`torneo_gato`, `competencia_busqueda`, `menu_torneo`). `minimax()` y `alfabeta()` aceptan el
parámetro `evaluador` (por defecto `evaluacion`) para poder enfrentar evaluaciones distintas. Pruebas: `tests/test_torneo.py`.
