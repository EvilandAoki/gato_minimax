"""Minimax y poda alfa-beta sobre el gato.

Las dos variantes comparten una única función recursiva (_evaluar); la poda se activa con
un parámetro. Un `callback` opcional recibe cada evento del recorrido (lo usa la animación).

Utilidad (desde el punto de vista de la IA, que es MAX):
    gana la IA     ->  10 - profundidad   (mientras antes gane, mejor)
    gana el rival  ->  profundidad - 10   (mientras más tarde pierda, mejor)
    empate         ->  0
"""

from typing import NamedTuple

from .arbol import Nodo
from .tablero import (aplicar, esta_lleno, ganador, movimientos_validos, oponente,
                      turno as turno_de)

INF = float("inf")


class Resultado(NamedTuple):
    mejor_mov: int | None
    valor: int
    nodos: int            # nodos evaluados (sin contar ramas podadas)
    raiz: Nodo | None     # árbol de búsqueda (None si construir_arbol=False)


class _Ctx:
    __slots__ = ("construir", "prof_arbol", "poda", "callback", "nodos")

    def __init__(self, construir, prof_arbol, poda, callback):
        self.construir = construir
        self.prof_arbol = prof_arbol
        self.poda = poda
        self.callback = callback
        self.nodos = 0


def utilidad(gana, jugador_ia, profundidad):
    if gana is None:
        return 0
    return 10 - profundidad if gana == jugador_ia else profundidad - 10


def _evaluar(t, ia, jugador, prof, alfa, beta, nodo, ctx):
    ctx.nodos += 1
    inicio = ctx.nodos
    cb = ctx.callback
    gana = ganador(t)

    if gana or esta_lleno(t):
        v = utilidad(gana, ia, prof)
        if nodo is not None:
            nodo.tipo, nodo.valor, nodo.sub = "HOJA", v, 1
            if cb:
                cb("entrar", nodo, alfa=alfa, beta=beta)
                cb("hoja", nodo, valor=v, alfa=alfa, beta=beta)
        return v

    maximiza = jugador == ia
    if nodo is not None:
        nodo.tipo = "MAX" if maximiza else "MIN"
        if cb:
            cb("entrar", nodo, alfa=alfa, beta=beta)

    mejor = -INF if maximiza else INF
    mejor_mov = None
    movs = movimientos_validos(t)
    guardar = ctx.construir and prof + 1 <= ctx.prof_arbol

    for i, m in enumerate(movs):
        t_hijo = aplicar(t, m, jugador)
        hijo = None
        if guardar and nodo is not None:
            hijo = Nodo(t_hijo, m, oponente(jugador), prof + 1)
            nodo.hijos.append(hijo)
        v = _evaluar(t_hijo, ia, oponente(jugador), prof + 1, alfa, beta, hijo, ctx)

        if maximiza:
            if v > mejor:
                mejor, mejor_mov = v, m
            if mejor > alfa:
                alfa = mejor
        else:
            if v < mejor:
                mejor, mejor_mov = v, m
            if mejor < beta:
                beta = mejor

        if ctx.poda and alfa >= beta:
            if guardar and nodo is not None:
                for resto in movs[i + 1:]:
                    nodo.hijos.append(Nodo(aplicar(t, resto, jugador), resto,
                                           oponente(jugador), prof + 1, tipo="PODA",
                                           podado=True, alfa=alfa, beta=beta))
                if cb:
                    cb("poda", nodo, valor=mejor, alfa=alfa, beta=beta)
            break

    if nodo is not None:
        nodo.valor, nodo.elegido = mejor, mejor_mov
        nodo.alfa, nodo.beta = (alfa, beta) if ctx.poda else (None, None)
        nodo.sub = ctx.nodos - inicio + 1
        if cb:
            cb("subir", nodo, valor=mejor, alfa=alfa, beta=beta)
    return mejor


def _buscar(tablero, jugador_ia, poda, construir_arbol, callback, prof_arbol):
    ia = jugador_ia or turno_de(tablero)
    ctx = _Ctx(construir_arbol, prof_arbol if prof_arbol is not None else 99, poda, callback)
    # La raíz siempre existe (guarda la jugada elegida); sus hijos solo si construir_arbol.
    raiz = Nodo(tablero, None, turno_de(tablero), 0)
    valor = _evaluar(tablero, ia, turno_de(tablero), 0, -INF, INF, raiz, ctx)
    return Resultado(raiz.elegido, valor, ctx.nodos, raiz if construir_arbol else None)


def minimax(tablero, jugador_ia=None, construir_arbol=True, callback=None, prof_arbol=None):
    """Minimax puro. `jugador_ia` es quien mueve en la raíz (MAX); por defecto, el del turno.

    prof_arbol limita hasta qué profundidad se *guardan* nodos (la búsqueda sigue completa).
    """
    return _buscar(tablero, jugador_ia, False, construir_arbol, callback, prof_arbol)


def alfabeta(tablero, jugador_ia=None, construir_arbol=True, callback=None, prof_arbol=None):
    """Minimax con poda alfa-beta: misma jugada, menos nodos."""
    return _buscar(tablero, jugador_ia, True, construir_arbol, callback, prof_arbol)


def valores_por_movimiento(tablero, jugador_ia=None):
    """Valor Minimax exacto de cada jugada posible de la raíz: {posición: valor}."""
    ia = jugador_ia or turno_de(tablero)
    jugador = turno_de(tablero)
    valores = {}
    for m in movimientos_validos(tablero):
        ctx = _Ctx(False, 99, False, None)
        valores[m] = _evaluar(aplicar(tablero, m, jugador), ia, oponente(jugador), 1,
                              -INF, INF, None, ctx)
    return valores
