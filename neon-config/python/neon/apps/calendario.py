import calendar
import datetime

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
DIAS_CORTOS = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]


def cuadricula(anio, mes):
    return calendar.Calendar(firstweekday=0).monthdayscalendar(anio, mes)


def mover_mes(anio, mes, delta):
    m = mes - 1 + delta
    anio = max(1, min(9999, anio + m // 12))
    return anio, m % 12 + 1


def fecha_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def run(win, tema):
    import curses
    from ..ui import cabecera, pie, put

    hoy = datetime.date.today()
    anio, mes = hoy.year, hoy.month
    win.timeout(1000)
    celda = 5
    while True:
        hoy = datetime.date.today()
        alto, ancho = win.getmaxyx()
        win.erase()
        cabecera(win, tema, "CALENDARIO")
        ancho_grid = 7 * celda
        x0 = max(2, (ancho - ancho_grid) // 2)
        y = 3
        titulo = f"{MESES[mes - 1].upper()} {anio}"
        put(win, y, x0 + (ancho_grid - len(titulo)) // 2, titulo, tema.blanco)
        put(win, y + 1, x0, "─" * ancho_grid, tema.rojo)
        for i, d in enumerate(DIAS_CORTOS):
            put(win, y + 2, x0 + i * celda, d.rjust(3), tema.rojo if i >= 5 else tema.tenue)
        for f, semana in enumerate(cuadricula(anio, mes)):
            for i, dia in enumerate(semana):
                if not dia:
                    continue
                if (anio, mes, dia) == (hoy.year, hoy.month, hoy.day):
                    attr = tema.sel
                elif i >= 5:
                    attr = tema.rojo
                else:
                    attr = tema.texto
                put(win, y + 3 + f, x0 + i * celda, f"{dia:>3}", attr)
        y += 10
        linea1 = f"Hoy: {fecha_larga(hoy)}"
        linea2 = f"Semana {hoy.isocalendar()[1]} · día {hoy.timetuple().tm_yday} del año"
        put(win, y, max(2, (ancho - len(linea1)) // 2), linea1, tema.blanco)
        put(win, y + 1, max(2, (ancho - len(linea2)) // 2), linea2, tema.tenue)
        pie(win, tema, "izq/der: mes · arriba/abajo: año · T: hoy · Q: volver")
        win.refresh()

        k = win.getch()
        if k in (ord("q"), ord("Q"), 27, curses.KEY_BACKSPACE, 127):
            return
        if k in (curses.KEY_LEFT, ord("h")):
            anio, mes = mover_mes(anio, mes, -1)
        elif k in (curses.KEY_RIGHT, ord("l")):
            anio, mes = mover_mes(anio, mes, 1)
        elif k in (curses.KEY_UP, ord("k")):
            anio, mes = mover_mes(anio, mes, -12)
        elif k in (curses.KEY_DOWN, ord("j")):
            anio, mes = mover_mes(anio, mes, 12)
        elif k in (ord("t"), ord("T")):
            anio, mes = hoy.year, hoy.month
