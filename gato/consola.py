"""Utilidades de terminal: colores ANSI, limpiar pantalla y lectura de entrada."""

import os
import sys
from contextlib import contextmanager

USAR_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

_CODIGOS = {
    "negrita": "1",
    "rojo": "31",
    "verde": "32",
    "amarillo": "33",
    "azul": "34",
    "magenta": "35",
    "cian": "36",
    "gris": "90",
}


class Salir(Exception):
    """Se lanza cuando el usuario cierra la entrada (Ctrl+D) o pide salir."""


def color(texto, *estilos):
    if not USAR_COLOR or not estilos:
        return str(texto)
    codigos = ";".join(_CODIGOS[e] for e in estilos)
    return f"\033[{codigos}m{texto}\033[0m"


@contextmanager
def sin_color():
    """Desactiva los colores temporalmente (p. ej. para exportar a un .txt)."""
    global USAR_COLOR
    anterior = USAR_COLOR
    USAR_COLOR = False
    try:
        yield
    finally:
        USAR_COLOR = anterior


def limpiar():
    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")


def titulo(texto):
    linea = "═" * (len(texto) + 4)
    print(color(f"\n╔{linea}╗\n║  {texto}  ║\n╚{linea}╝", "negrita", "cian"))


def pedir(mensaje=""):
    try:
        return input(mensaje).strip()
    except EOFError:
        raise Salir from None


def pausa(mensaje="Presiona Enter para continuar..."):
    pedir(color(mensaje, "gris"))
