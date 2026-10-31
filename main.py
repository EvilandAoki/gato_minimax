#!/usr/bin/env python3
"""Gato (tres en línea) con Minimax: menú principal."""

from gato.animacion import menu_animacion
from gato.consola import Salir, color, pedir, titulo
from gato.estadisticas import comparar, mostrar_estadisticas
from gato.juego import jugar
from gato.solitario import menu_movil

MENU = """
  Gato contra la máquina (Minimax con poda alfa-beta)
    1. Jugar contra la máquina (y ver su razonamiento)
    2. Animación paso a paso del algoritmo
    3. Estadísticas del árbol completo del gato
    4. Comparar Minimax vs. poda alfa-beta

  Gato en movimiento (un agente: DFS, BFS, costo uniforme, A*)
    5. Resolver un caso y comparar algoritmos

    6. Salir
"""


def main():
    """Bucle del menú: cada opción llama a una función de otro módulo (ver `acciones`)."""
    acciones = {"1": jugar, "2": menu_animacion, "3": mostrar_estadisticas, "4": comparar,
                "5": menu_movil}
    titulo("GATO + MINIMAX")
    try:
        while True:
            print(MENU)
            opcion = pedir("Elige una opción: ")
            if opcion == "6":
                break
            accion = acciones.get(opcion)
            if accion is None:
                print(color("Opción no válida.", "rojo"))
                continue
            accion()
            pedir(color("\nEnter para volver al menú...", "gris"))
    except (Salir, KeyboardInterrupt):
        print()
    print("¡Hasta luego!")


if __name__ == "__main__":
    main()
