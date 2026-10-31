# Documentación técnica: Gato con Minimax y poda alfa-beta

El `README.md` explica la teoría (árboles de juego, utilidad, Minimax). Este documento explica
**cómo está implementado**: qué hace cada archivo, quién llama a quién, y sobre todo las
variables de `minimax.py`, el objeto `ctx` y cómo funciona la poda alfa-beta sobre el árbol.

---

## 1. Mapa del proyecto

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Menú principal. Cada opción llama a una función de otro módulo. |
| `gato/tablero.py` | Reglas del juego: representación del tablero, jugadas legales, ganador, dibujo. |
| `gato/minimax.py` | **El algoritmo.** Minimax y alfa-beta comparten una sola función recursiva. |
| `gato/arbol.py` | La clase `Nodo` (un nodo del árbol de búsqueda) y el dibujo ASCII del árbol. |
| `gato/juego.py` | Partida humano vs. máquina (opción 1). |
| `gato/animacion.py` | Reproducción paso a paso de la búsqueda (opción 2). |
| `gato/estadisticas.py` | Conteo del árbol completo (opción 3) y comparación Minimax vs. alfa-beta (opción 4). |
| `gato/movil.py` | Problema "Gato en movimiento" (un agente): estado, acciones, costos, meta y heurísticas (sección 9). |
| `gato/busqueda.py` | DFS, BFS, costo uniforme y A\*, genéricos sobre cualquier problema (sección 10). |
| `gato/solitario.py` | Interfaz de consola del Gato en movimiento (opción 5). |
| `gato/experimentos.py` | Genera las tablas del informe: `python3 -m gato.experimentos`. |
| `gato/consola.py` | Colores ANSI, limpiar pantalla, leer entrada. |
| `tests/` | 36 pruebas (`test_minimax.py` 23, `test_busqueda.py` 13). Ejecutar: `python3 -m unittest`. |

### Quién llama a quién

```
main.main()
 ├─ 1 → juego.jugar()
 │        ├─ _pedir_jugada()                 (turno humano)
 │        └─ _explicar_ia()                  (turno máquina)
 │              ├─ minimax(construir_arbol=True)     ← decide la jugada
 │              └─ alfabeta(construir_arbol=False)   ← solo para comparar nodos
 │        └─ _menu_razonamiento() → imprimir_arbol / exportar_arbol / animar
 ├─ 2 → animacion.menu_animacion() → animar() → _grabar() → minimax|alfabeta(callback=cb)
 ├─ 3 → estadisticas.mostrar_estadisticas() → enumerar_arbol_completo(), valores_por_movimiento()
 └─ 4 → estadisticas.comparar() → minimax() y alfabeta() sobre varias posiciones

minimax() / alfabeta()  →  _buscar()  →  _evaluar()  (recursiva)  →  utilidad()
```

---

## 2. El tablero (`tablero.py`)

- El tablero es una **tupla de 9 strings**: `'X'`, `'O'` o `' '` (`VACIO`).
  Índices 0-8, pero las **posiciones** que ve el usuario son 1-9:

  ```
  1 | 2 | 3
  4 | 5 | 6
  7 | 8 | 9
  ```
- Es **inmutable**: `aplicar(tablero, pos, jugador)` devuelve un tablero *nuevo*. Por eso en
  la recursión no hay que "deshacer" la jugada al volver al padre.
- `turno(tablero)` no guarda de quién es el turno: lo **deduce** contando fichas (si hay igual
  cantidad de X y O, mueve X).
- `LINEAS_GANADORAS` son las 8 tríos de índices; `ganador()` las revisa todas.

| Función | Qué hace | Quién la llama |
|---|---|---|
| `tablero_vacio()` | 9 celdas libres | `juego.jugar`, `estadisticas` |
| `desde_texto("XOX/.O./.X.")` | Crea un tablero desde texto | ejemplos y tests |
| `movimientos_validos(t)` | Lista de posiciones libres = **los hijos del nodo** | `_evaluar` |
| `aplicar(t, pos, j)` | Tablero resultante de jugar | `_evaluar` |
| `oponente(j)` | El otro jugador | `_evaluar` (alterna el turno) |
| `ganador(t)` | `'X'`, `'O'` o `None` | `_evaluar` (¿es terminal?) |
| `esta_lleno(t)` | ¿Sin casillas libres? | `_evaluar` |
| `dibujar`, `dibujar_mini` | Texto del tablero (grande / una línea) | juego, árbol |

---

## 3. Las dos ideas clave antes de leer el código

### 3.1 MAX y MIN
La IA es **siempre MAX** (quiere la utilidad más alta); el rival es **MIN** (quiere la más baja).
En `_evaluar`, el parámetro `ia` fija quién es MAX durante toda la búsqueda, y el parámetro
`jugador` dice a quién le toca en *ese* nodo. Si `jugador == ia` el nodo maximiza; si no, minimiza.

### 3.2 Utilidad
Solo se calcula en las hojas (partida terminada), en `utilidad(gana, ia, profundidad)`:

| Situación | Valor |
|---|---|
| Gana la IA | `10 - profundidad` |
| Gana el rival | `profundidad - 10` |
| Empate | `0` |

Restar la profundidad hace que la IA prefiera **ganar pronto** y **perder tarde**.
Desde el tablero vacío una victoria ocurre como pronto en la profundidad 5, así que los
valores van de −5 a +5; en posiciones avanzadas la profundidad es menor y salen valores
como ±6 o ±7 (como en el ejemplo de la sección 5.4).

---

## 4. `minimax.py` en detalle

### 4.1 Estructuras

**`INF = float("inf")`** — el infinito. `alfa` empieza en `-INF` y `beta` en `+INF`; también
`mejor` empieza en `-INF` (MAX) o `+INF` (MIN) para que cualquier hijo lo mejore.

**`Resultado`** (NamedTuple) — lo que devuelven `minimax()` y `alfabeta()`:

| Campo | Significado |
|---|---|
| `mejor_mov` | Posición 1-9 de la mejor jugada para la IA |
| `valor` | Valor minimax de la raíz (0 = empate forzado) |
| `nodos` | Cuántos nodos se **evaluaron** (las ramas podadas no cuentan) |
| `raiz` | El árbol (`Nodo`), o `None` si `construir_arbol=False` |

### 4.2 `ctx` — el contexto (`_Ctx`)

`ctx` es **un objeto único que se crea en `_buscar()` y se pasa, la misma instancia, a todas
las llamadas recursivas** de `_evaluar`. Tiene dos tipos de campos:

| Campo | Tipo | Para qué sirve |
|---|---|---|
| `construir` | config | ¿Se guardan objetos `Nodo`? (`False` = búsqueda "ligera", solo cuenta nodos) |
| `prof_arbol` | config | Hasta qué profundidad se guardan nodos (99 = todos). Con el tablero vacío el juego usa 3 porque el árbol completo tiene 549.946 nodos |
| `poda` | config | **`True` = alfa-beta, `False` = Minimax puro.** Es el *único* interruptor entre los dos algoritmos |
| `callback` | config | Función que se avisa en cada evento (la animación la usa para grabar la búsqueda) |
| `prof_max` | config | Profundidad límite de la búsqueda (99 = sin límite). Al llegar se usa `evaluacion()` (sección 8) |
| `nodos` | **estado mutable** | Contador global de nodos evaluados |

¿Por qué un objeto y no variables sueltas? Dos razones:

1. Evita pasar 4 parámetros constantes en cada llamada recursiva.
2. **`nodos` debe ser compartido por toda la recursión.** Un entero pasado por parámetro se
   copia; un atributo de un objeto compartido no. Así `ctx.nodos += 1` en una llamada profunda
   se ve en todas las demás.

### 4.3 Parámetros de `_evaluar(t, ia, jugador, prof, alfa, beta, nodo, ctx)`

| Parámetro | Qué es | ¿Cambia al recursar? |
|---|---|---|
| `t` | Tablero actual | Sí: `aplicar(t, m, jugador)` |
| `ia` | Ficha de la IA (= MAX) | **No**, es constante |
| `jugador` | A quién le toca en `t` | Sí: `oponente(jugador)` |
| `prof` | Jugadas desde la raíz (raíz = 0) | Sí: `prof + 1` |
| `alfa` | Piso que MAX ya tiene asegurado | Se **hereda** y puede subir |
| `beta` | Techo que MIN ya tiene asegurado | Se **hereda** y puede bajar |
| `nodo` | `Nodo` donde anotar el resultado (o `None`) | Sí: uno nuevo por hijo |
| `ctx` | Contexto compartido | **No**, misma instancia |

Variables locales importantes:

| Variable | Significado |
|---|---|
| `inicio` | Valor de `ctx.nodos` al entrar. Al salir, `ctx.nodos - inicio + 1` = tamaño del subárbol (`nodo.sub`) |
| `maximiza` | `jugador == ia`; decide si este nodo es MAX o MIN |
| `mejor` | Valor provisional del nodo: parte de `-INF` (MAX) o `+INF` (MIN) y se va mejorando con cada hijo |
| `mejor_mov` | La jugada que produjo `mejor`; termina siendo `nodo.elegido` |
| `movs` | Jugadas legales (los hijos) |
| `guardar` | ¿Se crea `Nodo` para los hijos? (`construir` y dentro de `prof_arbol`) |
| `v` | Valor que devolvió el hijo recién evaluado |

### 4.4 Flujo de `_evaluar`

1. **Contar** el nodo (`ctx.nodos += 1`).
2. **¿Terminal?** (alguien ganó o tablero lleno) → calcular `utilidad`, marcar el nodo `HOJA`, devolver.
3. **¿Profundidad límite?** (`prof >= ctx.prof_max`) → valorar con `evaluacion()`, marcar el nodo `CORTE`, devolver.
   Con `prof_max=None` este paso nunca se activa.
4. **Si no**, decidir si es MAX o MIN, y poner `mejor` en ±INF.
5. **Por cada jugada legal**: crear el tablero hijo, **llamarse recursivamente** pasando los
   `alfa`/`beta` actuales, y con el valor `v` que vuelve:
   - MAX: si `v > mejor` → actualizar `mejor` y `mejor_mov`; si `mejor > alfa` → `alfa = mejor`.
   - MIN: si `v < mejor` → actualizar; si `mejor < beta` → `beta = mejor`.
   - **Si `ctx.poda and alfa >= beta` → podar** (sección 5) y salir del bucle.
6. **Cierre**: guardar en el nodo `valor`, `elegido`, `alfa`, `beta`, `sub`, y devolver `mejor`.

Sin poda, el paso 5 nunca hace `break`, y se recorre el árbol entero: eso es Minimax puro.

### 4.5 Eventos del `callback`

Solo si hay `callback` (la animación). Cada evento se emite con `(nombre, nodo, valor, alfa, beta)`:

| Evento | Cuándo se emite |
|---|---|
| `entrar` | Al llegar a un nodo (antes de mirar a sus hijos) |
| `hoja` | Al evaluar un terminal (justo después de `entrar`) |
| `corte` | Al llegar a la profundidad límite (justo después de `entrar`) |
| `poda` | Cuando `alfa >= beta` corta el bucle |
| `subir` | Al terminar un nodo interno y devolver su valor al padre |

`animacion._grabar` ejecuta la búsqueda completa *de una vez* guardando los eventos, y
`animar` los reproduce uno por uno. No se calcula nada en vivo.

---

## 5. Poda alfa-beta

### 5.1 Idea
Mientras recorremos el árbol, cada nodo recibe dos cotas **heredadas del camino hasta la raíz**:

- **`alfa`** = lo mejor que MAX puede asegurarse ya (el *piso*). Solo sube.
- **`beta`** = lo mejor que MIN puede asegurarse ya (el *techo*). Solo baja.

El nodo actual solo importa si su valor cae **dentro de (alfa, beta)**. Si en algún momento
`alfa >= beta`, la ventana quedó vacía: quien está arriba ya tiene una alternativa igual o
mejor, nunca elegirá llegar aquí, y **los hermanos restantes no pueden cambiar el resultado**.
Se descartan sin evaluarlos. Garantía: misma jugada y mismo valor en la raíz que Minimax.

### 5.2 Cómo se hereda
```python
v = _evaluar(t_hijo, ia, oponente(jugador), prof + 1, alfa, beta, hijo, ctx)
```
El hijo recibe el `alfa`/`beta` **actuales** del padre (que pudieron mejorar por hermanos ya
evaluados). Lo que el hijo modifique es local a él: al volver, el padre no copia sus
`alfa`/`beta`; solo usa el **valor devuelto** `v` para actualizar los suyos.

### 5.3 Qué pasa al podar (en el código)
```python
if ctx.poda and alfa >= beta:
    # registrar los hermanos restantes como Nodo(tipo="PODA", podado=True) -> se dibujan con ✂
    break   # no se evalúan: ctx.nodos no crece por ellos
```
Los nodos `PODA` existen **solo para dibujar** (`✂`). No se evalúan ni cuentan en `nodos`
(`arbol.contar_nodos` los ignora con `if raiz.podado`).

### 5.4 Recorrido real (opción 4 → ejemplo A: `XOX/.O./.X.`, mueve O)

Minimax evalúa **61** nodos, alfa-beta **29**; ambos eligen la casilla **4** con valor 0.
Fragmento del árbol (`α`/`β` al terminar cada nodo):

```
[MAX(O)]  raíz  v=0        α=0  β=+∞
├── [MIN(X)]  mov=4  v=0   α=-∞ β=0
│   ├── [MAX(O)]  mov=6  v=0   α=0 β=+∞
│   │   ├── [MIN(X)]  mov=7  v=-6  α=-∞ β=-6   └─ HOJA gana X
│   │   └── [MIN(X)]  mov=9  v=0   α=-6 β=0    └─ HOJA empate
│   ├── [MAX(O)]  mov=7  v=+7  α=+7 β=0
│   │   ├── HOJA mov=6 v=+7  gana O
│   │   └── ✂ mov=9  podado  (β=0 ≤ α=+7)
│   └── ...
├── [MIN(X)]  mov=6  v=0   α=0  β=0
│   ├── [MAX(O)]  mov=4  v=0 ...
│   ├── ✂ mov=7  podado  (β=0 ≤ α=0)
│   └── ✂ mov=9  podado  (β=0 ≤ α=0)
```

**Paso a paso (rama `mov=4`):**

1. Raíz: `α=-∞, β=+∞`. Baja a `mov=4` (MIN), que hereda `(-∞, +∞)`.
2. `mov=4` baja a `mov=6` (MAX), hereda `(-∞, +∞)`. Su primer hijo `mov=7` es MIN y llega a una
   hoja donde gana X (`-6`) → ese MIN pone `β=-6` y devuelve `-6`.
3. `mov=6` (MAX) recibe `-6`: `mejor=-6`, **`α=-6`**. Su segundo hijo (`mov=9`) hereda `(α=-6, β=+∞)`,
   llega a empate (`0`), devuelve `0`. `mov=6` queda con `mejor=0`, `α=0`, y devuelve `0`.
4. `mov=4` (MIN) recibe `0`: `mejor=0`, **`β=0`**. Ahora MIN ya puede asegurar 0 o menos.
5. Su siguiente hijo `mov=7` (MAX) hereda `(α=-∞, β=0)`. Su primera jugada gana para O: `+7`.
   MAX sube `α=+7`. Como **`α=7 ≥ β=0`** → **poda**: `mov=9` no se evalúa.
   *Razón:* a MIN (padre) ya le basta con 0; este nodo vale al menos 7, que MIN jamás elegiría,
   así que da igual cuánto valga exactamente.
6. En la raíz, `mov=4` dio 0 → `α=0`. Los demás hijos de la raíz heredan `α=0`; en cuanto un MIN
   consigue `β=0` (`α ≥ β` con `0 ≥ 0`) se poda el resto (`mov=6`, `mov=7`, `mov=9` de la raíz).

**Nota:** el valor devuelto por un nodo cortado (como el `+7` de arriba) es solo una **cota**,
no su valor exacto. Es correcto para el algoritmo, pero por eso `valores_por_movimiento`
(que necesita valores exactos de cada jugada) se calcula **sin poda**.

**Nota 2:** la poda usa `>=` (no `>`), así que también corta empates. Por eso en la raíz se queda
la **primera** jugada con el mejor valor: las siguientes con el mismo valor no la reemplazan
(`v > mejor` es estricto).

### 5.5 Por qué ahorra tanto
La poda funciona mejor cuando se prueban primero las buenas jugadas. Aquí las jugadas se
prueban en orden numérico (sin ordenar), y aun así el ahorro es grande (la opción 4 del menú
lo mide en distintas posiciones; con el tablero vacío pasa de 549.946 a 20.866 nodos, un 96 % menos).

---

## 6. El árbol: `arbol.py`

### `Nodo` (dataclass)

| Campo | Significado |
|---|---|
| `tablero` | Posición de este nodo |
| `movimiento` | Jugada que llevó aquí (`None` en la raíz) |
| `turno` | Quién mueve en este nodo |
| `profundidad` | Jugadas desde la raíz |
| `tipo` | `MAX`, `MIN`, `HOJA` (terminal) o `PODA` (no evaluado) |
| `valor` | Valor que este nodo sube a su padre |
| `hijos` | Lista de `Nodo` (incluye los `PODA`) |
| `elegido` | Jugada hija con el mejor valor (en la raíz = la jugada de la máquina) |
| `podado` | `True` si fue descartado por alfa-beta |
| `alfa`, `beta` | Cotas finales del nodo (`None` sin poda) |
| `sub` | Nodos evaluados en su subárbol (para resumir ramas con "… N nodos más") |

La raíz **siempre** se crea (guarda `elegido`, que es la jugada de la IA), aunque
`construir_arbol=False`; en ese caso `_buscar` devuelve `raiz=None` en el `Resultado` y los
hijos no se guardan.

### Dibujo
`imprimir_arbol(raiz, prof_max, solo_mejor, visible, valores, actual, mostrar_ab)` es
recursiva (`rec`) y dibuja con `├──` / `└──`. Los parámetros opcionales sirven a la animación:
`visible` (ids de nodos ya descubiertos), `valores` (valores ya calculados), `actual`
(el nodo marcado con ▶). `exportar_arbol` vuelca todo el árbol a un `.txt` sin colores.

---

## 7. Resumen de estados de un nodo durante la búsqueda

```
entrar ──► (¿terminal?) ──sí──► hoja ──► devuelve utilidad
              │ no
              ▼
      por cada hijo: _evaluar(hijo, alfa, beta)  ──► actualiza mejor / alfa / beta
              │                                         │
              │                       (poda activa y alfa ≥ beta) ──► poda ──► break
              ▼
           subir ──► devuelve `mejor` al padre
```

---

## 8. Profundidad límite y función de evaluación

El gato es tan pequeño que Minimax llega siempre al final de la partida. En juegos grandes eso es
imposible, así que se **corta la búsqueda a una profundidad `prof_max`** y se *estima* el valor del
tablero con una función de evaluación. Se activa con `minimax(t, prof_max=d)` o `alfabeta(t, prof_max=d)`
(el juego lo pregunta al empezar). `prof_max=None` = sin límite, como antes.

`evaluacion(t, ia)` (en `minimax.py`) recorre las 8 `LINEAS_GANADORAS` y suma:

| Línea | Aporte |
|---|---|
| solo fichas de la IA: una / dos | +1 / +10 |
| solo fichas del rival: una / dos | −1 / −10 |
| fichas de ambos (nadie puede completarla) | 0 |
| casilla central de la IA | +1 |

El total (entre −80 y +81) se divide entre 100. **Por qué:** una victoria real vale `10 - prof` (al
menos 1 en la profundidad 9); si la estimación pudiera valer más, la IA preferiría una posición "que
parece buena" a ganar de verdad. Con `|evaluacion| < 1` las victorias y derrotas siempre dominan (hay
una prueba que lo verifica en todas las posiciones alcanzables). La poda alfa-beta no cambia: los
nodos `CORTE` son hojas con un valor decimal. Con límite baja la calidad de juego (la máquina puede
perder), con límite 9 vuelve a ser perfecta.

---

## 9. Gato en movimiento (`movil.py`): el problema de un agente

Formulación como espacio de estados (`ProblemaMovil`, interfaz que usa `busqueda.py`):

| Elemento | Definición | Dónde |
|---|---|---|
| Estado | `frozenset` de las casillas (0..N²−1) con X. Las O y N son fijas por caso; un `frozenset` es hashable (sirve para `explorados`) e inmutable | `estado_inicial` |
| Acciones | `(origen, destino)`: una X a una casilla vecina (8 direcciones) sin X ni O | `acciones(s)` |
| Transición | `(s − {origen}) ∪ {destino}` | `resultado(s, a)` |
| Costo | recto = 2, diagonal = 3 (si todo costara igual, BFS = UCS) | `costo(s, a)` |
| Meta | las X ocupan exactamente una línea de k casillas sin O | `es_meta(s)` |

Las líneas válidas (`lineas`) se calculan una vez: todas las ventanas de k casillas seguidas en filas,
columnas y diagonales que no contengan una O. Los casos de prueba (`CASOS`) son 4: 3×3, dos de 4×4 y
5×5. El caso 2 se encontró buscando uno donde BFS y UCS difieren (mismo número de pasos, 14 contra 10
de costo). El problema **no es un laberinto**: la meta no es una casilla sino un patrón de varias
fichas que se mueven a la vez.

### Heurística h1 (la que usa A\*)
`h1(s) = mín sobre las líneas válidas L de [ mín sobre las asignaciones ficha→casilla de L de Σ d(ficha, casilla) ]`,
con `d(a, b) = 3·mín(dx, dy) + 2·|dx − dy|` (distancia octil: todas las diagonales posibles a 3 y el
resto en recto a 2). Como k ≤ 4, las asignaciones se prueban todas (k! ≤ 24).

Ejemplo (caso 1, `X.X/.O./X.O`, X en 1, 3 y 7): la única línea libre de O es la columna izquierda
(1, 4, 7) y la fila superior (1, 2, 3). Para la fila superior las fichas ya ocupan 1 y 3 y la de 7 debe
llegar a 2: `d(7, 2) = 3·1 + 2·1 = 5`. Para la columna izquierda la ficha de 3 debe llegar a 4:
`d(3, 4) = 3·1 + 2·1 = 5`. Entonces `h1 = 5`, y el costo óptimo real es 5.

- **Admisible** (nunca sobreestima): `d` es el costo exacto de mover una ficha en un tablero vacío.
  Las fichas reales además se estorban y no pueden compartir casilla, lo que solo puede *subir* el costo.
  Además, la meta exige que las X ocupen una línea, así que la mejor asignación a alguna línea es una
  cota inferior de cualquier solución.
- **Consistente** (`h(s) ≤ c + h(s')` para toda jugada): una jugada mueve una sola ficha, con costo
  `c = d(origen, destino)` (2 recto, 3 diagonal, coincide con la distancia octil de un paso). Por la
  desigualdad triangular, `d(destino, q) ≥ d(origen, q) − c` para cualquier casilla `q`, así que para
  *cada* asignación la suma baja como mucho `c` en `s'`; al tomar el mínimo sobre asignaciones y
  líneas se conserva la desigualdad.
- Las pruebas (`tests/test_busqueda.py`) lo verifican por fuerza bruta en todos los estados alcanzables
  de los casos 1-3, comparando con el costo exacto a la meta.

### Heurística h2 (más débil, para comparar)
`h2(s) = 2 × (casillas de la mejor línea que aún no tienen X)`. También es admisible (cada jugada llena
a lo más una casilla y cuesta ≥ 2) y consistente, pero ignora las distancias. En el caso 5×5 A\* con h1
expande 475 nodos, con h2 4.176 y UCS 8.060. Pero h1 es más cara de calcular (probar permutaciones): en
tiempo real A\* con h1 tarda más en el caso grande (≈ 1,1 s contra 0,13 s de UCS), aunque expande 17
veces menos nodos. Es un buen punto de discusión para el informe: menos nodos no siempre significa menos tiempo.

---

## 10. Búsqueda: DFS, BFS, UCS y A\* (`busqueda.py`)

Los cuatro comparten el esqueleto (frontera + `explorados`); cambia la frontera:

| Algoritmo | Frontera | Sale primero | Prueba de meta | Garantía |
|---|---|---|---|---|
| `dfs` | pila (`list`, LIFO) | el último que entró | al generar | solo encuentra *una* solución |
| `bfs` | cola (`deque`, FIFO) | el primero que entró | al generar | menos pasos |
| `ucs` | cola de prioridad (`heapq`) por `g` | menor costo acumulado | al sacar | menor costo |
| `astar` | cola de prioridad por `g + h` | menor `g + h` estimado | al sacar | menor costo si `h` es admisible |

UCS y A\* comparten `_mejor_primero(problema, nombre, prioridad)`; solo cambia la función `prioridad`
(`g` o `g + h`). Detalles que conviene saber:

- **`NodoBusqueda`**: `estado`, `padre`, `accion`, `g` (costo acumulado) y `prof` (pasos). `camino()`
  sigue los `padre` hasta la raíz.
- **Estados repetidos**: `explorados` (DFS, UCS, A\*) o `vistos` (BFS, que marca al encolar). Sin esto
  DFS no termina en un grafo con ciclos (mover una ficha y volverla).
- **UCS/A\* y entradas obsoletas**: `heapq` no permite cambiar la prioridad de un elemento. Si se halla
  un camino más barato a un estado ya encolado, se encola otra vez y la entrada vieja se ignora al
  sacarla (`if nodo.estado in explorados: continue`). `mejor_g` evita encolar caminos peores.
- **Desempate**: la tupla del heap lleva un contador, porque `NodoBusqueda` no se puede comparar.
- **Por qué la meta se prueba al sacar (UCS/A\*)**: al generarla solo se sabe *un* camino; al sacarla se
  sabe que ninguno pendiente es más barato. BFS y DFS pueden probarla al generar.
- **Métricas** (`ResultadoBusqueda`): `expandidos` (nodos a los que se les generaron sucesores; la meta
  no cuenta), `generados`, `max_memoria` (máximo de |frontera| + |explorados|), `pico_bytes` (pico de
  memoria de Python con `tracemalloc`), `tiempo_ms`.
- **`medir()`** ejecuta el algoritmo dos veces: una para el tiempo y otra con `tracemalloc` para la
  memoria (`tracemalloc` ralentiza mucho y falsearía el tiempo).

### Propiedades (para el informe)
`b` = factor de ramificación, `d` = profundidad de la solución más superficial, `m` = profundidad máxima.
En este problema el espacio es finito y se controlan repetidos, así que todos son completos.

| | Completo | Óptimo | Tiempo | Espacio |
|---|---|---|---|---|
| DFS | sí (con `explorados`, espacio finito) | no | O(b^m) | O(b·m) en árbol; con `explorados` crece con los estados vistos |
| BFS | sí | en pasos (no en costo) | O(b^d) | O(b^d) |
| UCS | sí (costos ≥ 2 > 0) | sí (en costo) | O(b^(1+C\*/ε)) | ídem |
| A\* | sí | sí con h admisible (y consistente: no reabre estados) | depende de h; exponencial en el peor caso | O(b^d), guarda todos los nodos |

### Quién llama a quién (búsqueda)
```
main.main() → 5 → solitario.menu_movil()
   ├─ _elegir_caso()  (movil.CASOS)
   ├─ ejecutar_algoritmo() → busqueda.medir(dfs|bfs|ucs|astar) → problema.acciones/resultado/costo/es_meta/heuristica
   ├─ comparar_algoritmos()   (tabla de los 4)
   └─ comparar_heuristicas()  (UCS vs A* con h2 vs A* con h1)
```
