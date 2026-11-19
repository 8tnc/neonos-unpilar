import shutil

from .. import sysinfo


def run(win, tema):
    import curses
    from ..ui import cabecera, pie, put

    win.timeout(1000)
    previa = sysinfo.muestra_cpu()
    while True:
        actual = sysinfo.muestra_cpu()
        cpu = sysinfo.porcentaje_cpu(previa, actual)
        previa = actual
        mem = sysinfo.memoria()
        alto, ancho = win.getmaxyx()
        ancho_barra = max(10, min(40, ancho - 40))

        win.erase()
        cabecera(win, tema, "MONITOR")
        y = 2

        def fila(etiqueta, fraccion, detalle):
            nonlocal y
            put(win, y, 2, etiqueta.ljust(7), tema.tenue)
            if fraccion is None:
                put(win, y, 10, detalle, tema.texto)
            else:
                put(win, y, 10, sysinfo.barra(fraccion, ancho_barra), tema.rojo)
                put(win, y, 12 + ancho_barra, detalle, tema.blanco)
            y += 1

        fila("CPU", cpu / 100 if cpu is not None else None,
             f"{cpu:5.1f} %" if cpu is not None else "midiendo...")
        if mem:
            fila("MEMORIA", mem["usada"] / mem["total"], f"{mem['usada']} / {mem['total']} MiB")
            if mem["swap_total"]:
                fila("SWAP", mem["swap_usada"] / mem["swap_total"],
                     f"{mem['swap_usada']} / {mem['swap_total']} MiB")
            else:
                fila("SWAP", None, "sin swap")
        else:
            fila("MEMORIA", None, "no disponible (sin /proc/meminfo)")
        try:
            d = shutil.disk_usage("/")
            fila("DISCO /", d.used / d.total, f"{d.used / 2**30:.1f} / {d.total / 2**30:.1f} GiB")
        except OSError:
            fila("DISCO /", None, "no disponible")

        activo = sysinfo.segundos_activo()
        resumen = (f"CARGA {sysinfo.carga() or '?'}    "
                   f"ACTIVO {sysinfo.tiempo_activo(activo) if activo is not None else '?'}")
        put(win, y + 1, 2, resumen, tema.texto)

        y += 3
        put(win, y, 2, "── Procesos (ps, % CPU promedio de cada proceso) ──", tema.blanco)
        for i, linea in enumerate(sysinfo.proc_list(limite=max(0, alto - y - 3))):
            put(win, y + 1 + i, 2, linea, tema.rojo if linea.startswith("[!!]") else tema.texto)

        pie(win, tema, "Se actualiza cada segundo · Q: volver")
        win.refresh()
        if win.getch() in (ord("q"), ord("Q"), 27, curses.KEY_LEFT, curses.KEY_BACKSPACE, 127):
            return
