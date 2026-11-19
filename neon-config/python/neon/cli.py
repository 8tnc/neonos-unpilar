import sys

from . import VERSION, manual, power, sysinfo

COMANDOS = {
    "sys.scan": (sysinfo.sys_scan, "información básica del sistema"),
    "net.status": (sysinfo.net_status, "interfaces de red, rutas y DNS"),
    "proc.list": (sysinfo.proc_list, "procesos ordenados por uso de CPU"),
    "access.logs": (sysinfo.access_logs, "últimos registros del sistema"),
    "manual": (manual.lineas, "manual de uso de NEON//OS"),
}
APPS = {
    "calendario": "calendario mensual interactivo",
    "monitor": "monitor de recursos en vivo",
}
ENERGIA = {
    "apagar": ("poweroff", "apaga el equipo"),
    "reiniciar": ("reboot", "reinicia el equipo"),
}


def ayuda():
    lineas = [f"NEON//OS {VERSION}", "", "Uso: neon [comando]", "",
              "  (sin comando)  abre el menú interactivo"]
    lineas += [f"  {nombre:<13}  {desc}" for nombre, (_, desc) in COMANDOS.items()]
    lineas += [f"  {nombre:<13}  {desc}" for nombre, desc in APPS.items()]
    lineas += [f"  {nombre:<13}  {desc} (pide confirmación)" for nombre, (_, desc) in ENERGIA.items()]
    lineas += ["  help           muestra esta ayuda", "  --version      muestra la versión"]
    return "\n".join(lineas)


def energia(nombre):
    accion, _ = ENERGIA[nombre]
    if not sys.stdin.isatty():
        print(f"neon: '{nombre}' necesita una terminal para confirmar.", file=sys.stderr)
        return 1
    try:
        respuesta = input(f"¿{nombre.capitalize()} el equipo ahora? [s/N] ")
    except (EOFError, KeyboardInterrupt):
        respuesta = ""
    if respuesta.strip().lower() not in ("s", "si", "sí"):
        print("Cancelado.")
        return 0
    return 0 if power.ejecutar(accion) else 1


def _curses(nombre_funcion, *args):
    try:
        from . import menu
    except ImportError as e:
        print(f"neon: esta función necesita el módulo curses de Python ({e}).", file=sys.stderr)
        return 1
    return getattr(menu, nombre_funcion)(*args)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] == "menu":
        return _curses("run_menu")
    cmd = args[0]
    if cmd in ("help", "-h", "--help"):
        print(ayuda())
        return 0
    if cmd in ("--version", "-V"):
        print(f"NEON//OS {VERSION}")
        return 0
    if cmd not in COMANDOS and cmd not in APPS and cmd not in ENERGIA:
        print(f"neon: comando desconocido '{cmd}'. Usá 'neon help'.", file=sys.stderr)
        return 2
    if len(args) > 1:
        print(f"neon: '{cmd}' no acepta argumentos.", file=sys.stderr)
        return 2
    if cmd in APPS:
        return _curses("run_app", cmd)
    if cmd in ENERGIA:
        return energia(cmd)
    for linea in COMANDOS[cmd][0]():
        print(linea)
    return 0
