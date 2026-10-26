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
| `gato/consola.py` | Colores ANSI, limpiar pantalla, leer entrada. |
| `tests/test_minimax.py` | Pruebas (17). Ejecutar: `python3 -m unittest discover`. |

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
3. **Si no**, decidir si es MAX o MIN, y poner `mejor` en ±INF.
4. **Por cada jugada legal**: crear el tablero hijo, **llamarse recursivamente** pasando los
   `alfa`/`beta` actuales, y con el valor `v` que vuelve:
   - MAX: si `v > mejor` → actualizar `mejor` y `mejor_mov`; si `mejor > alfa` → `alfa = mejor`.
   - MIN: si `v < mejor` → actualizar; si `mejor < beta` → `beta = mejor`.
   - **Si `ctx.poda and alfa >= beta` → podar** (sección 5) y salir del bucle.
5. **Cierre**: guardar en el nodo `valor`, `elegido`, `alfa`, `beta`, `sub`, y devolver `mejor`.

Sin poda, el paso 4 nunca hace `break`, y se recorre el árbol entero: eso es Minimax puro.

### 4.5 Eventos del `callback`

Solo si hay `callback` (la animación). Cada evento se emite con `(nombre, nodo, valor, alfa, beta)`:

| Evento | Cuándo se emite |
|---|---|
| `entrar` | Al llegar a un nodo (antes de mirar a sus hijos) |
| `hoja` | Al evaluar un terminal (justo después de `entrar`) |
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
