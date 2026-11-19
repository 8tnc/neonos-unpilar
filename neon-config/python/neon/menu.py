import curses
import locale
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass

from . import manual, power, sysinfo
from .claude_code import abrir_claude
from .apps import calendario, monitor
from .ui import Tema, aviso, cabecera, confirmar, fuera_de_curses, pie, put, visor


@dataclass
class Item:
    etiqueta: str
    descripcion: str = ""
    tipo: str = "seccion"
    accion: object = None


def abrir_bash():
    shell = shutil.which("bash") or os.environ.get("SHELL") or "/bin/sh"
    print("» Saliendo a Bash. Escribí 'exit' para volver al menú NEON.\n")
    subprocess.run([shell])
    return False


def abrir_notas():
    editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano")
    if not shutil.which(editor[0]):
        print(f"[!!] No se encontró el editor '{editor[0]}'. Instalalo o definí la variable EDITOR.")
        return True
    subprocess.run(editor + [os.path.expanduser("~/notas.txt")])
    return False


def elementos():
    return [
        Item("SISTEMA"),
        Item("Diagnóstico del sistema", "Nodo, kernel, CPU, memoria, disco y tiempo activo.", "visor", sysinfo.sys_scan),
        Item("Estado de red", "Interfaces, direcciones, rutas y servidores DNS.", "visor", sysinfo.net_status),
        Item("Procesos", "Procesos ordenados por uso de CPU.", "visor", sysinfo.proc_list),
        Item("Registros del sistema", "Últimas 300 entradas del journal, las más recientes primero.", "visor", sysinfo.access_logs),
        Item("APLICACIONES"),
        Item("Calendario", "Calendario mensual navegable con el día de hoy resaltado.", "app", calendario.run),
        Item("Monitor en vivo", "CPU, memoria, swap, disco y procesos, actualizado cada segundo.", "app", monitor.run),
        Item("Notas", "Abre ~/notas.txt en tu editor ($EDITOR o nano).", "externo", abrir_notas),
        Item("TERMINAL"),
        Item("Abrir Bash", "Sale de NEON a una sesión Bash normal. Escribí 'exit' para volver.", "externo", abrir_bash),
        Item("Claude Code", "Asistente de programación en la terminal. Cada usuario lo instala e inicia sesión con su propia cuenta; si falta, muestra cómo instalarlo.", "externo", abrir_claude),
        Item("AYUDA"),
        Item("Manual de uso", "Cómo usar el menú, los comandos de neon y la lista de alias.", "visor", manual.lineas),
        Item("ENERGÍA"),
        Item("Reiniciar", "Reinicia el sistema (pide confirmación).", "energia", "reboot"),
        Item("Apagar", "Apaga el sistema (pide confirmación).", "energia", "poweroff"),
        Item("Salir de NEON", "Cierra el menú y vuelve a la consola.", "salir"),
    ]


def cargar_emblema():
    ruta = os.path.join(os.environ.get("NEON_HOME", "/usr/local/share/neon"), "assets", "ascii", "emblem.txt")
    try:
        with open(ruta, encoding="utf-8") as f:
            return f.read().splitlines()
    except OSError:
        return []


ANCHO_MENU = 34
ALTO_MINIMO, ANCHO_MINIMO = 22, 50


def dibujar(win, tema, items, actual, emblema):
    alto, ancho = win.getmaxyx()
    win.erase()
    if alto < ALTO_MINIMO or ancho < ANCHO_MINIMO:
        put(win, 0, 0, f"Terminal demasiado pequeña: mínimo {ANCHO_MINIMO}x{ALTO_MINIMO}.", tema.rojo)
        win.refresh()
        return
    cabecera(win, tema, "MENÚ PRINCIPAL")

    y, x = 2, 2
    for i, it in enumerate(items):
        if it.tipo == "seccion":
            if i:
                y += 1
            put(win, y, x, f"── {it.etiqueta} ".ljust(ANCHO_MENU, "─"), tema.rojo)
        elif i == actual:
            put(win, y, x, f" » {it.etiqueta}".ljust(ANCHO_MENU), tema.sel)
        else:
            put(win, y, x, f"   {it.etiqueta}", tema.texto)
        y += 1

    xd = x + ANCHO_MENU + 4
    descripcion = items[actual].descripcion
    if emblema and ancho - xd >= max(len(l) for l in emblema) + 1:
        for j, linea in enumerate(emblema):
            put(win, 2 + j, xd, linea, tema.rojo)
        yd = 3 + len(emblema)
        for j, linea in enumerate(textwrap.wrap(descripcion, max(10, ancho - xd - 2))[:alto - yd - 2]):
            put(win, yd + j, xd, linea, tema.blanco)
    else:
        put(win, alto - 3, x, descripcion, tema.blanco)

    pie(win, tema, "arriba/abajo: mover · ENTER: abrir · Q: salir")
    win.refresh()


def activar(win, tema, item):
    if item.tipo == "visor":
        aviso(win, tema, "Recopilando datos...")
        visor(win, tema, item.etiqueta.upper(), item.accion())
    elif item.tipo == "app":
        item.accion(win, tema)
    elif item.tipo == "externo":
        fuera_de_curses(win, item.accion)
    elif item.tipo == "energia":
        if confirmar(win, tema, f"¿{item.etiqueta} el sistema ahora?"):
            fuera_de_curses(win, lambda: not power.ejecutar(item.accion))


def preparar(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.keypad(True)


def bucle(stdscr):
    preparar(stdscr)
    tema = Tema()
    items = elementos()
    seleccionables = [i for i, it in enumerate(items) if it.tipo != "seccion"]
    emblema = cargar_emblema()
    pos = 0
    while True:
        stdscr.timeout(1000)
        dibujar(stdscr, tema, items, seleccionables[pos], emblema)
        k = stdscr.getch()
        if k in (curses.KEY_UP, ord("k")):
            pos = (pos - 1) % len(seleccionables)
        elif k in (curses.KEY_DOWN, ord("j"), 9):
            pos = (pos + 1) % len(seleccionables)
        elif k == curses.KEY_HOME:
            pos = 0
        elif k == curses.KEY_END:
            pos = len(seleccionables) - 1
        elif k in (10, 13, curses.KEY_ENTER, ord(" "), curses.KEY_RIGHT, ord("l")):
            item = items[seleccionables[pos]]
            if item.tipo == "salir":
                return
            activar(stdscr, tema, item)
        elif k in (ord("q"), ord("Q"), 27):
            return


def iniciar(funcion):
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("neon: esta función necesita una terminal interactiva. Usá 'neon help' para los comandos.", file=sys.stderr)
        return 1
    locale.setlocale(locale.LC_ALL, "")
    os.environ.setdefault("ESCDELAY", "25")
    try:
        curses.wrapper(funcion)
    except KeyboardInterrupt:
        pass
    return 0


def run_menu():
    return iniciar(bucle)


APPS = {"calendario": calendario.run, "monitor": monitor.run}


def run_app(nombre):
    app = APPS[nombre]

    def _app(stdscr):
        preparar(stdscr)
        app(stdscr, Tema())
    return iniciar(_app)
