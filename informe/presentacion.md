# Guion de la presentación (máx. 15 min, 12 diapositivas)

Reparto sugerido entre 3 integrantes (A, B, C). **Todos deben poder responder por cualquier algoritmo.**
Grabar un video de respaldo de la demostración.

| # | Diapositiva | Tiempo | Quién | Contenido |
|---|---|---|---|---|
| 1 | Título + qué hace la app | 0:30 | A | Gato con dos modos: Gato en movimiento (un agente) y Gato contra la máquina |
| 2 | Modelado del problema | 1:30 | A | Estado (`frozenset` de X), acciones, transición, meta (línea), costos 2/3; utilidad del modo adversario. Dibujo de un tablero |
| 3 | Demo en vivo | 4:00 | B | `python3 main.py` → opción 5: caso 2 con BFS y UCS (14 contra 10), luego A\*; opción 1 con profundidad 3 y la comparación con y sin poda |
| 4 | DFS y BFS | 2:00 | B | Pila contra cola (diagrama de 4.2 y 4.3); DFS: costo 170 con 75 pasos; BFS: mínimo de pasos |
| 5 | Costo uniforme | 1:00 | C | Cola de prioridad por g; por qué la meta se prueba al sacar; BFS ≠ UCS |
| 6 | A\* y su heurística | 2:00 | C | h1 (asignación a la mejor línea), ejemplo numérico, admisible y consistente en una línea cada una |
| 7 | Por qué A\* expande menos | (incl. en 6) | C | Tabla: UCS 8.060 contra A\* 475 (5×5); mencionar que h1 es más lenta por nodo |
| 8 | Minimax | 1:00 | A | Cómo decide la máquina; utilidad; función de evaluación y profundidad límite |
| 9 | Poda alfa-beta | 1:00 | A | α/β, ejemplo `XOX/.O./.X.`: 61 contra 29 nodos; vacío: 549.946 contra 20.866 |
| 10 | Comparación | 1:30 | B | Tabla/gráfica de nodos, tiempo, memoria y costo por algoritmo y caso |
| 11 | Conclusiones | 0:30 | C | 3 aprendizajes y limitaciones |
| 12 | Preguntas | — | todos | Hasta 5 min |

Total ≈ 14:30 (diapositivas 6 y 7 comparten los 2:00 y la 3 es la más larga).

## Preguntas probables
- ¿Por qué UCS prueba la meta al sacar y BFS al generar? (UCS: al generar solo se conoce un camino, no el más barato.)
- ¿Por qué h1 es admisible? ¿y consistente? (ver informe 6a)
- ¿Qué pasa con alfa-beta si se cambia el orden de las jugadas? (misma jugada, distinta cantidad de nodos podados)
- ¿Por qué `|evaluacion| < 1`? (para que nunca valga más que ganar de verdad)
- ¿Por qué DFS necesita `explorados`? (mover una ficha y devolverla crea ciclos)
- ¿Por qué esto no es un laberinto? (la meta es un patrón de varias fichas, no una casilla)
