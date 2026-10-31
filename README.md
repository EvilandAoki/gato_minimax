# Gato (3 en línea): algoritmos de búsqueda (Proyecto 1, IA)

**Integrantes:** _(completar: nombre y código de cada integrante, máximo 3)_
**Curso / docente:** _(completar)_

Todo el proyecto gira alrededor del gato y cubre los cinco algoritmos pedidos:

| Modo | Problema | Algoritmos |
|---|---|---|
| **Gato en movimiento** (un agente) | Mover fichas X por el tablero hasta formar una línea, con costos distintos | DFS, BFS, costo uniforme, A\* (heurística propia) |
| **Gato contra la máquina** (adversario) | Juego normal de gato, dos jugadores por turnos | Minimax con poda alfa-beta, profundidad límite y función de evaluación |

## Requisitos y ejecución

Solo Python 3.12 o superior y la biblioteca estándar (no hay que instalar nada).

```bash
python3 main.py                  # menú principal
python3 -m unittest              # pruebas (36, ≈ 12 s)
python3 -m gato.experimentos     # tablas de resultados del informe (Markdown)
```

Documentación: `DOCUMENTACION.md` (implementación línea por línea de Minimax y alfa-beta, y de la
búsqueda) y `informe/` (borrador del informe y guion de la presentación).

**Herramientas de apoyo declaradas:** se usó Claude Code (asistente de IA de Anthropic) para
ayudar a escribir y documentar el código. _(Ajustar a lo que realmente use el grupo.)_

La primera parte del proyecto: un juego de gato en la terminal contra una máquina que
decide con el algoritmo **Minimax**, y que **muestra su razonamiento modelándolo como un árbol de
juego**. Incluye además la **poda alfa-beta** para comparar cuánto trabajo se ahorra.

## Contenido del menú

| Opción | Qué hace |
|---|---|
| 1. Jugar | Partida contra la máquina. Tras cada jugada suya muestra cuántos nodos evaluó, el valor Minimax de cada casilla, y permite ver el árbol (`a`), exportarlo a `.txt` (`e`) o animarlo (`p`). |
| 2. Animación | Recorre paso a paso el árbol de una posición pequeña: cómo se baja a las hojas y cómo los valores *suben* hasta la raíz. Con o sin poda. |
| 3. Estadísticas | Enumera el árbol **completo** del gato: nodos por nivel, partidas posibles, victorias/empates. |
| 4. Comparar | Minimax vs. alfa-beta en varias posiciones, y el árbol podado con sus ramas descartadas (`✂`). |
| 5. Gato en movimiento | Elegir un caso y DFS / BFS / costo uniforme / A\*; muestra solución, costo, pasos, nodos expandidos, memoria y tiempo; compara los 4 algoritmos y las heurísticas de A\*. |

---

## 1. Juegos como árboles

El gato es un juego **de suma cero, por turnos, de información perfecta y determinista**: lo que gana
un jugador lo pierde el otro, ambos ven todo el tablero y no hay azar. Un juego así se modela con un
**árbol de juego**:

- **Nodo** = una posición del tablero.
- **Arista** = una jugada legal.
- **Raíz** = la posición actual.
- **Hojas** = posiciones terminales (alguien ganó o el tablero se llenó).
- Los niveles se **alternan** entre los dos jugadores.

```
                     raíz (mueve X)
              ┌──────────┼──────────┐
           X en 1      X en 2      X en 3 …      9 hijos
         ┌─────┼─────┐
      O en 2  O en 3 …                           8 hijos cada uno
```

Etiquetamos a la máquina como **MAX** (quiere maximizar su puntaje) y a su rival como **MIN**
(quiere minimizarlo, porque lo que es bueno para MIN es malo para MAX).

## 2. Función de utilidad

Solo las hojas tienen un valor "real". Se mide desde el punto de vista de la máquina:

| Hoja | Utilidad |
|---|---|
| Gana la máquina | `+10 − profundidad` |
| Gana el rival | `profundidad − 10` |
| Empate | `0` |

Restar la profundidad hace que la máquina **prefiera ganar rápido y perder tarde**: ganar en la
jugada 3 vale `+7`, ganar en la 5 vale `+5`. Sin ese detalle, la máquina vería igual de buenas todas
las victorias y podría "jugar con su comida" en lugar de cerrar la partida.

## 3. El algoritmo Minimax

Idea: **suponer que el rival siempre juega lo mejor posible** y propagar los valores de las hojas
hacia la raíz.

- En un nodo **MAX** (le toca a la máquina) el valor es el **máximo** de los valores de sus hijos.
- En un nodo **MIN** (le toca al rival) el valor es el **mínimo** de los valores de sus hijos.
- La jugada elegida en la raíz es la que lleva al hijo con el mejor valor.

```text
función MINIMAX(estado, turno, profundidad):
    si estado es terminal:
        devolver UTILIDAD(estado, profundidad)

    si turno es MAX:
        mejor ← −∞
        para cada jugada m legal en estado:
            mejor ← max(mejor, MINIMAX(aplicar(estado, m), MIN, profundidad + 1))
        devolver mejor
    sino:                                   # turno de MIN
        mejor ← +∞
        para cada jugada m legal en estado:
            mejor ← min(mejor, MINIMAX(aplicar(estado, m), MAX, profundidad + 1))
        devolver mejor
```

Es una **búsqueda en profundidad**: baja hasta una hoja, y al regresar cada nodo calcula su valor.
En el código es una única función recursiva, `_evaluar` en [`gato/minimax.py`](gato/minimax.py).

### Ejemplo resuelto (salida real del programa)

Posición `X O X / O X O / · · ·` con 3 casillas libres, le toca a **X** (la máquina, MAX):

```
[MAX(X)]  raíz  v=+9  X O X | O X O | · · ·
├── [HOJA]  mov=7  v=+9  X O X | O X O | X · ·  gana X
├── [MIN(O)]  mov=8  v=+7  X O X | O X O | · X ·
│   ├── [MAX(X)]  mov=7  v=+7  X O X | O X O | O X ·
│   │   └── [HOJA]  mov=9  v=+7  X O X | O X O | O X X  gana X
│   └── [MAX(X)]  mov=9  v=+7  X O X | O X O | · X O
│       └── [HOJA]  mov=7  v=+7  X O X | O X O | X X O  gana X
└── [HOJA]  mov=9  v=+9  X O X | O X O | · · X  gana X
```

Cómo se lee:

1. Jugar en **7** o en **9** gana de inmediato (profundidad 1) → utilidad `10 − 1 = +9`.
2. Jugar en **8** no gana al instante; el rival responde y X gana después (profundidad 3) →
   `10 − 3 = +7`. Los dos hijos de ese nodo valen `+7`; MIN elige el mínimo, que también es `+7`.
3. La raíz es MAX: `max(+9, +7, +9) = +9`. Hay empate entre 7 y 9; se elige la **primera** (la 7),
   así el programa es determinista.

## 4. ¿Qué tan grande es el árbol del gato?

Medido con la opción 3 del menú (recorriendo el árbol completo desde el tablero vacío):

| Profundidad | Mueve | Nodos | Hojas |
|---:|:--:|---:|---:|
| 0 | X | 1 | 0 |
| 1 | O | 9 | 0 |
| 2 | X | 72 | 0 |
| 3 | O | 504 | 0 |
| 4 | X | 3.024 | 0 |
| 5 | O | 15.120 | 1.440 |
| 6 | X | 54.720 | 5.328 |
| 7 | O | 148.176 | 47.952 |
| 8 | X | 200.448 | 72.576 |
| 9 | — | 127.872 | 127.872 |
| **Total** | | **549.946** | **255.168** |

- **255.168 partidas posibles**: 131.184 ganan las X, 77.904 ganan las O y 46.080 empatan.
- La cota ingenua `9! = 362.880` no se alcanza porque muchas partidas terminan antes de llenar el tablero.
- Hay solo **5.478 posiciones distintas**: el árbol tiene muchas repeticiones (se llega a la misma
  posición por distinto orden de jugadas). Minimax no lo aprovecha; una tabla de transposición sí podría.
- El valor Minimax de **cada una de las 9 primeras jugadas es 0**: con juego perfecto de ambos lados
  el gato **siempre termina en empate**.

Complejidad general: con factor de ramificación `b` y profundidad máxima `m`, Minimax visita
`O(b^m)` nodos. Aquí `b ≤ 9` y `m = 9`, lo que es pequeño; en ajedrez (`b ≈ 35`, `m ≈ 80`) sería
imposible sin podas y heurísticas.

## 5. Poda alfa-beta

Minimax evalúa ramas que **no pueden cambiar la decisión**. Alfa-beta lleva dos cotas:

- **α**: el mejor valor que MAX ya tiene asegurado en el camino hacia la raíz.
- **β**: el mejor valor (el más bajo) que MIN ya tiene asegurado.

Si en algún nodo ocurre **β ≤ α**, las ramas restantes de ese nodo se descartan: quien esté
arriba ya tiene una alternativa al menos igual de buena y nunca dejaría llegar a esa rama.

```text
función ALFABETA(estado, turno, α, β):
    si estado es terminal: devolver UTILIDAD(...)
    si turno es MAX:
        mejor ← −∞
        para cada jugada m:
            mejor ← max(mejor, ALFABETA(hijo, MIN, α, β))
            α ← max(α, mejor)
            si α ≥ β: romper           # poda: MIN nunca permitiría llegar aquí
        devolver mejor
    sino: (simétrico con min y β)
```

Ejemplo real (posición `X O X / · O · / · X ·`, le toca a O). Las ramas `✂` ni siquiera se evaluaron:

```
├── [MIN(X)]  mov=6  v=0  X O X | · O O | · X ·  α=0 β=0
│   ├── [MAX(O)]  mov=4  v=0  X O X | X O O | · X ·  α=0 β=+∞
│   │   ├── [MIN(X)]  mov=7  v=0 ...
│   │   └── [MIN(X)]  mov=9  v=-6 ...
│   ├── ✂ mov=7  podado  (β=0 ≤ α=0)
│   └── ✂ mov=9  podado  (β=0 ≤ α=0)
```

La raíz (MAX) ya tenía `α = 0` por una rama anterior. Aquí el primer hijo de este nodo MIN vale 0,
así que `β = 0`. MIN nunca ofrecerá más de 0, y MAX ya tiene 0 asegurado: las jugadas 7 y 9 no
pueden mejorar el resultado, por lo que se descartan.

### Resultados medidos (opción 4 del menú)

| Posición | Minimax | Alfa-beta | Ahorro | Misma jugada |
|---|---:|---:|---:|:--:|
| Tablero vacío (mueve X) | 549.946 | 20.866 | 96,2 % | sí |
| X en esquina (mueve O) | 59.705 | 2.788 | 95,3 % | sí |
| X centro, O esquina (mueve X) | 6.812 | 832 | 87,8 % | sí |
| Ejemplo A (4 libres) | 61 | 29 | 52,5 % | sí |
| Ejemplo C (5 libres) | 238 | 93 | 60,9 % | sí |
| Ejemplo B (3 libres) | 8 | 6 | 25,0 % | sí |

Desde el tablero vacío, Minimax tarda ≈ 1 s en Python y alfa-beta ≈ 0,05 s, con **exactamente** la
misma jugada y el mismo valor. La poda no es una aproximación: solo omite lo irrelevante. Su
rendimiento depende del orden en que se exploran las jugadas (aquí, orden de casilla 1 a 9, sin
heurística, por lo que el ahorro podría ser aún mayor con un mejor orden).

## 6. ¿Por qué la máquina nunca pierde?

(Con la profundidad por defecto, hasta el final de la partida; con una profundidad límite baja la
máquina sí puede perder, porque no ve toda la partida.) Porque Minimax supone un rival perfecto. Como el valor de la raíz del gato es 0, la máquina
siempre puede asegurar al menos el empate, y en cuanto el rival se equivoca, el árbol le muestra
una rama con valor positivo y la toma. Las pruebas lo verifican **exhaustivamente**: prueban todas
las jugadas posibles del humano, jugando la máquina como X y como O, y ninguna partida la derrota.

## 7. Estructura del proyecto

```
main.py                 menú principal
gato/
  tablero.py            reglas: tablero (tupla de 9), turnos, ganador, dibujo
  arbol.py              clase Nodo + dibujo del árbol en ASCII + exportación a .txt
  minimax.py            Minimax y alfa-beta (una sola función recursiva con poda opcional)
  animacion.py          reproduce la búsqueda paso a paso (usa los eventos del algoritmo)
  estadisticas.py       enumeración del árbol completo y comparación Minimax vs. alfa-beta
  juego.py              partida humano vs. máquina (con profundidad límite configurable)
  movil.py              problema "Gato en movimiento": estados, acciones, costos, meta, heurísticas
  busqueda.py           DFS, BFS, costo uniforme y A* (genéricos) + medición de tiempo y memoria
  solitario.py          interfaz de consola del Gato en movimiento
  experimentos.py       genera las tablas del informe
  consola.py            colores ANSI, entrada, pantalla
tests/test_minimax.py   23 pruebas de Minimax, alfa-beta y profundidad límite
tests/test_busqueda.py  13 pruebas de DFS/BFS/UCS/A* y de las heurísticas
arboles/                árboles exportados desde el juego (se crea al exportar)
```

Detalles de implementación que conviene saber:

- **X siempre empieza**; el turno se deduce contando fichas. Si juegas con O, la máquina abre.
- La animación no duplica la lógica: el algoritmo acepta un `callback` que recibe los eventos
  (`entrar`, `hoja`, `subir`, `poda`) y la animación solo los reproduce sobre el árbol ya construido.
- Cuando la máquina abre en un tablero vacío, el árbol tiene 549.946 nodos: se evalúa completo,
  pero solo se **guardan** los primeros 3 niveles (`prof_arbol`), por eso en ese caso no se puede
  exportar el árbol completo. Con 8 o menos casillas libres (≈ 60 mil nodos o menos) el árbol se guarda entero.
- Los árboles exportados con `e` quedan en `arboles/arbol_<timestamp>.txt`.

## 8. Gato en movimiento (DFS, BFS, costo uniforme y A\*)

Tablero N×N con **k fichas X móviles** y algunas **O fijas** (obstáculos). Cada jugada mueve una X
a una casilla vecina libre (8 direcciones). **Meta:** que las k fichas X formen una línea (fila,
columna o diagonal). No es un laberinto: la meta es un patrón de varias fichas, no una casilla.

| Elemento | Definición |
|---|---|
| Estado | `frozenset` con las casillas ocupadas por X (las O y N son fijas por caso) |
| Acciones | `(origen, destino)`: una X a una casilla vecina sin X ni O |
| Costo | paso recto = 2, paso en diagonal = 3 |
| Meta | las X ocupan exactamente una línea de k casillas sin O |

Los casos de prueba están en `gato/movil.py` (`CASOS`). El caso 2 está elegido para que **BFS (menos
pasos) y UCS (menor costo) den soluciones distintas**.

**Frontera de cada algoritmo** (`gato/busqueda.py`): DFS pila, BFS cola, UCS y A\* cola de
prioridad (`heapq`). Todos descartan estados repetidos con un conjunto de explorados.

**Heurística propia de A\*** (`ProblemaMovil.heuristica`): para cada línea posible se asignan las
fichas a sus casillas del modo más barato (distancia con costos 2 y 3, ignorando que las fichas
se estorben) y se toma la mejor línea. Es admisible y consistente; la prueba está en
`DOCUMENTACION.md` y las pruebas la verifican en **todos** los estados de los casos pequeños. También
hay una heurística más simple (`heuristica_simple`) para compararlas.

## 9. Profundidad límite y función de evaluación (Minimax)

Al jugar se puede fijar una **profundidad límite** (1-9). Al llegar a ella el nodo no se expande
(se marca `CORTE` en el árbol) y se valora con `minimax.evaluacion()`:

- línea abierta con solo fichas de la IA: +1 (una ficha) o +10 (dos); del rival: −1 o −10;
- +1 si la IA tiene el centro; el total se divide entre 100.

Así la evaluación siempre queda en (−1, 1) y nunca supera una victoria o derrota real
(que valen al menos 1 en valor absoluto). La poda alfa-beta funciona igual con el límite y da la
misma jugada que Minimax en cada profundidad (hay pruebas para esto). `python3 -m gato.experimentos`
muestra los nodos con y sin poda para varias profundidades.
