"""Minimax y poda alfa-beta sobre el gato.

Las dos variantes comparten una única función recursiva (_evaluar); la poda se activa con
un parámetro. Un `callback` opcional recibe cada evento del recorrido (lo usa la animación).

Utilidad (desde el punto de vista de la IA, que es MAX):
    gana la IA     ->  10 - profundidad   (mientras antes gane, mejor)
    gana el rival  ->  profundidad - 10   (mientras más tarde pierda, mejor)
    empate         ->  0

Quién llama a quién:
    juego.py / animacion.py / estadisticas.py
        -> minimax() o alfabeta()      (API pública, solo cambia el flag `poda`)
            -> _buscar()               (prepara el contexto y la raíz)
                -> _evaluar()          (recursión: aquí vive todo el algoritmo)
                    -> utilidad()      (solo en hojas)
"""

from typing import NamedTuple

from .arbol import Nodo
from .tablero import (aplicar, esta_lleno, ganador, movimientos_validos, oponente,
                      turno as turno_de)

# Infinito: valor inicial de alfa (-INF) y beta (+INF). Cualquier utilidad real (-10..10)
# lo supera, así que la primera hoja que se evalúe siempre "mejora" a alfa o beta.
INF = float("inf")


class Resultado(NamedTuple):
    """Lo que devuelven minimax() y alfabeta(). Es una tupla con nombres."""
    mejor_mov: int | None
    valor: int
    nodos: int            # nodos evaluados (sin contar ramas podadas)
    raiz: Nodo | None     # árbol de búsqueda (None si construir_arbol=False)


class _Ctx:
    """Contexto de UNA búsqueda: configuración fija + contador de nodos.

    Se crea una sola vez en _buscar() y se pasa tal cual (misma instancia) a todas las
    llamadas recursivas de _evaluar(). Así no hay que arrastrar 4 parámetros constantes
    en cada llamada, y `nodos` es un contador compartido por toda la recursión
    (los enteros normales no se pueden "compartir" entre llamadas; un atributo sí).
    `__slots__` solo ahorra memoria/tiempo de acceso; no cambia la lógica.
    """
    __slots__ = ("construir", "prof_arbol", "poda", "callback", "nodos")

    def __init__(self, construir, prof_arbol, poda, callback):
        self.construir = construir    # ¿guardar los nodos en un árbol de objetos Nodo?
        self.prof_arbol = prof_arbol  # profundidad máxima hasta la que se guardan nodos
        self.poda = poda              # True = alfa-beta, False = minimax puro
        self.callback = callback      # función a avisar en cada evento (o None)
        self.nodos = 0                # cuántos nodos se han evaluado hasta ahora


def utilidad(gana, jugador_ia, profundidad):
    """Valor de un estado terminal. `gana` es 'X', 'O' o None (empate).

    Se llama desde _evaluar() solo cuando el tablero ya terminó. Restar la profundidad
    hace que la IA prefiera ganar rápido y perder lo más tarde posible.
    """
    if gana is None:
        return 0
    return 10 - profundidad if gana == jugador_ia else profundidad - 10


def _evaluar(t, ia, jugador, prof, alfa, beta, nodo, ctx):
    """Corazón del algoritmo. Devuelve el valor minimax del tablero `t`.

    Parámetros:
        t        tablero actual (tupla de 9 celdas)
        ia       ficha de la IA; es MAX durante TODA la búsqueda (no cambia al recursar)
        jugador  ficha a la que le toca mover en `t` (alterna X/O en cada nivel)
        prof     profundidad: jugadas hechas desde la raíz (raíz = 0)
        alfa     mejor valor que MAX ya tiene asegurado en el camino hacia la raíz
        beta     mejor valor que MIN ya tiene asegurado en el camino hacia la raíz
        nodo     objeto Nodo donde anotar los resultados (None si no se guarda el árbol)
        ctx      el _Ctx compartido (flag de poda, contador, callback...)

    Se llama: una vez desde _buscar() (raíz) y una vez por cada jugada legal desde sí misma.
    """
    ctx.nodos += 1              # este nodo cuenta como evaluado
    inicio = ctx.nodos          # para saber luego cuántos nodos tuvo SU subárbol
    cb = ctx.callback
    gana = ganador(t)

    # --- Caso base: estado terminal (alguien ganó o no quedan casillas) ---
    if gana or esta_lleno(t):
        v = utilidad(gana, ia, prof)
        if nodo is not None:
            nodo.tipo, nodo.valor, nodo.sub = "HOJA", v, 1
            if cb:
                cb("entrar", nodo, alfa=alfa, beta=beta)
                cb("hoja", nodo, valor=v, alfa=alfa, beta=beta)
        return v

    # --- Nodo interno: ¿maximiza (turno de la IA) o minimiza (turno del rival)? ---
    maximiza = jugador == ia
    if nodo is not None:
        nodo.tipo = "MAX" if maximiza else "MIN"
        if cb:
            cb("entrar", nodo, alfa=alfa, beta=beta)

    # `mejor` es el valor provisional de este nodo. MAX arranca en -inf (cualquier hijo lo
    # mejora) y MIN en +inf. `mejor_mov` recuerda qué jugada produjo ese valor.
    mejor = -INF if maximiza else INF
    mejor_mov = None
    movs = movimientos_validos(t)
    # ¿Este nivel se guarda en el árbol? (si no, la búsqueda sigue igual, solo sin Nodo)
    guardar = ctx.construir and prof + 1 <= ctx.prof_arbol

    for i, m in enumerate(movs):
        t_hijo = aplicar(t, m, jugador)     # tablero nuevo; el original no se modifica
        hijo = None
        if guardar and nodo is not None:
            hijo = Nodo(t_hijo, m, oponente(jugador), prof + 1)
            nodo.hijos.append(hijo)
        # Recursión: baja un nivel, cambia el turno y PASA alfa/beta actuales al hijo.
        v = _evaluar(t_hijo, ia, oponente(jugador), prof + 1, alfa, beta, hijo, ctx)

        # Al volver, actualizamos el mejor valor y el límite correspondiente:
        if maximiza:
            if v > mejor:
                mejor, mejor_mov = v, m
            if mejor > alfa:        # MAX sube su piso garantizado
                alfa = mejor
        else:
            if v < mejor:
                mejor, mejor_mov = v, m
            if mejor < beta:        # MIN baja su techo garantizado
                beta = mejor

        # PODA: si alfa >= beta, el padre ya tiene una alternativa igual o mejor en otra
        # rama, así que jamás elegiría este nodo. Los hermanos que faltan no pueden cambiar
        # el resultado y se descartan sin evaluarlos (por eso `ctx.nodos` crece menos).
        if ctx.poda and alfa >= beta:
            if guardar and nodo is not None:
                # Se registran como nodos "PODA" solo para poder dibujarlos (✂).
                for resto in movs[i + 1:]:
                    nodo.hijos.append(Nodo(aplicar(t, resto, jugador), resto,
                                           oponente(jugador), prof + 1, tipo="PODA",
                                           podado=True, alfa=alfa, beta=beta))
                if cb:
                    cb("poda", nodo, valor=mejor, alfa=alfa, beta=beta)
            break

    # --- Cierre: anotar el resultado en el nodo y devolverlo al padre ---
    if nodo is not None:
        nodo.valor, nodo.elegido = mejor, mejor_mov
        nodo.alfa, nodo.beta = (alfa, beta) if ctx.poda else (None, None)
        nodo.sub = ctx.nodos - inicio + 1   # nodos contados mientras estuvimos dentro
        if cb:
            cb("subir", nodo, valor=mejor, alfa=alfa, beta=beta)
    return mejor


def _buscar(tablero, jugador_ia, poda, construir_arbol, callback, prof_arbol):
    """Prepara la búsqueda y lanza _evaluar() sobre la raíz. Lo usan minimax y alfabeta."""
    ia = jugador_ia or turno_de(tablero)    # por defecto MAX = a quien le toca mover
    ctx = _Ctx(construir_arbol, prof_arbol if prof_arbol is not None else 99, poda, callback)
    # La raíz siempre existe (guarda la jugada elegida); sus hijos solo si construir_arbol.
    raiz = Nodo(tablero, None, turno_de(tablero), 0)
    # Arranque: alfa = -inf, beta = +inf ("todavía no sé nada, todo me sirve").
    valor = _evaluar(tablero, ia, turno_de(tablero), 0, -INF, INF, raiz, ctx)
    return Resultado(raiz.elegido, valor, ctx.nodos, raiz if construir_arbol else None)


def minimax(tablero, jugador_ia=None, construir_arbol=True, callback=None, prof_arbol=None):
    """Minimax puro. `jugador_ia` es quien mueve en la raíz (MAX); por defecto, el del turno.

    prof_arbol limita hasta qué profundidad se *guardan* nodos (la búsqueda sigue completa).
    Lo llaman: juego._explicar_ia, animacion._grabar, estadisticas.comparar.
    """
    return _buscar(tablero, jugador_ia, False, construir_arbol, callback, prof_arbol)


def alfabeta(tablero, jugador_ia=None, construir_arbol=True, callback=None, prof_arbol=None):
    """Minimax con poda alfa-beta: misma jugada, menos nodos.

    Lo llaman: juego._explicar_ia (solo para comparar nodos), animacion._grabar y
    estadisticas.comparar.
    """
    return _buscar(tablero, jugador_ia, True, construir_arbol, callback, prof_arbol)


def valores_por_movimiento(tablero, jugador_ia=None):
    """Valor Minimax exacto de cada jugada posible de la raíz: {posición: valor}.

    Se evalúa cada jugada por separado y SIN poda (con poda, los valores de las jugadas
    no óptimas serían solo cotas, no valores exactos). Lo usa estadisticas.mostrar_estadisticas.
    """
    ia = jugador_ia or turno_de(tablero)
    jugador = turno_de(tablero)
    valores = {}
    for m in movimientos_validos(tablero):
        ctx = _Ctx(False, 99, False, None)
        valores[m] = _evaluar(aplicar(tablero, m, jugador), ia, oponente(jugador), 1,
                              -INF, INF, None, ctx)
    return valores
