import curses
import socket
import time

from . import VERSION


class Tema:

    def __init__(self):
        n = curses.A_NORMAL
        self.rojo = self.sel = self.texto = self.blanco = self.tenue = self.barra = n
        if not curses.has_colors():
            self.sel = self.barra = curses.A_REVERSE
            return
        curses.start_color()
        try:
            curses.use_default_colors()
            fondo = -1
        except curses.error:
            fondo = curses.COLOR_BLACK
        gris = 8 if curses.COLORS >= 16 else curses.COLOR_WHITE
        curses.init_pair(1, curses.COLOR_RED, fondo)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, fondo)
        curses.init_pair(4, gris, fondo)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)
        self.rojo = curses.color_pair(1) | curses.A_BOLD
        self.sel = curses.color_pair(2) | curses.A_BOLD
        self.texto = curses.color_pair(3)
        self.blanco = curses.color_pair(3) | curses.A_BOLD
        self.tenue = curses.color_pair(4) | (curses.A_DIM if gris == curses.COLOR_WHITE else 0)
        self.barra = curses.color_pair(5)


def put(win, y, x, texto, attr=0):
    alto, ancho = win.getmaxyx()
    if y < 0 or y >= alto or x < 0 or x >= ancho:
        return
    limite = ancho - x - (1 if y == alto - 1 else 0)
    try:
        win.addstr(y, x, texto[:max(0, limite)], attr)
    except curses.error:
        pass


def cabecera(win, tema, titulo):
    _, ancho = win.getmaxyx()
    izquierda = f" NEON//OS v{VERSION} // {titulo}"
    derecha = f"{socket.gethostname()}  {time.strftime('%Y-%m-%d %H:%M:%S')} "
    put(win, 0, 0, " " * ancho, tema.barra)
    put(win, 0, 0, izquierda, tema.barra | curses.A_BOLD)
    put(win, 0, max(len(izquierda) + 2, ancho - len(derecha)), derecha, tema.barra)


def pie(win, tema, texto):
    alto, ancho = win.getmaxyx()
    put(win, alto - 1, 0, " " * ancho, tema.tenue)
    put(win, alto - 1, 1, texto, tema.tenue)


TECLAS_VOLVER = (ord("q"), ord("Q"), 27, curses.KEY_LEFT, curses.KEY_BACKSPACE, 127)


def visor(win, tema, titulo, lineas):
    lineas = [l.expandtabs() for l in lineas] or ["(sin datos)"]
    pos = 0
    win.timeout(1000)
    while True:
        alto, _ = win.getmaxyx()
        visibles = max(1, alto - 4)
        pos = max(0, min(pos, len(lineas) - visibles))
        win.erase()
        cabecera(win, tema, titulo)
        for i, linea in enumerate(lineas[pos:pos + visibles]):
            if linea.startswith("[!!]"):
                attr = tema.rojo
            elif linea.startswith("──"):
                attr = tema.blanco
            else:
                attr = tema.texto
            put(win, 2 + i, 2, linea, attr)
        fin = min(pos + visibles, len(lineas))
        pie(win, tema, f"flechas / RePág / AvPág: desplazar · Q: volver    [{pos + 1}-{fin} de {len(lineas)}]")
        win.refresh()
        k = win.getch()
        if k in TECLAS_VOLVER:
            return
        if k in (curses.KEY_DOWN, ord("j")):
            pos += 1
        elif k in (curses.KEY_UP, ord("k")):
            pos -= 1
        elif k in (curses.KEY_NPAGE, ord(" ")):
            pos += visibles
        elif k == curses.KEY_PPAGE:
            pos -= visibles
        elif k in (curses.KEY_HOME, ord("g")):
            pos = 0
        elif k in (curses.KEY_END, ord("G")):
            pos = len(lineas)


def aviso(win, tema, texto):
    alto, ancho = win.getmaxyx()
    put(win, alto // 2, max(0, (ancho - len(texto)) // 2), texto, tema.blanco)
    win.refresh()


def confirmar(win, tema, pregunta):
    alto, ancho = win.getmaxyx()
    w = min(ancho - 2, max(len(pregunta) + 6, 34))
    h = 7
    dlg = curses.newwin(h, w, max(0, (alto - h) // 2), max(0, (ancho - w) // 2))
    dlg.keypad(True)
    dlg.bkgd(" ", tema.texto)
    dlg.attron(tema.rojo)
    dlg.box()
    dlg.attroff(tema.rojo)
    put(dlg, 0, 2, " CONFIRMAR ", tema.sel)
    put(dlg, 2, 3, pregunta, tema.blanco)
    put(dlg, 4, 3, "[S] Sí      [N] No", tema.tenue)
    dlg.refresh()
    while True:
        k = dlg.getch()
        if k in (ord("s"), ord("S"), ord("y"), ord("Y")):
            return True
        if k in (ord("n"), ord("N"), ord("q"), ord("Q"), 27, 10, 13, curses.KEY_ENTER):
            return False


def fuera_de_curses(win, funcion):
    curses.def_prog_mode()
    curses.endwin()
    pausar = True
    try:
        pausar = funcion()
    except KeyboardInterrupt:
        pass
    if pausar:
        try:
            input("\nPulsá Enter para volver a NEON...")
        except (EOFError, KeyboardInterrupt):
            pass
    curses.reset_prog_mode()
    win.clear()
    win.refresh()
