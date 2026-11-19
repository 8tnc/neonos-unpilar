import os
import re

from . import VERSION

_ALIAS = re.compile(r"^alias\s+([\w.-]+)='(.*)'\s+#\s*(.+)$")


def ruta_alias():
    return os.path.join(os.environ.get("NEON_HOME", "/usr/local/share/neon"), "lib", "aliases.sh")


def parse_alias(texto):
    return [m.groups() for m in map(_ALIAS.match, texto.splitlines()) if m]


def leer_alias():
    try:
        with open(ruta_alias(), encoding="utf-8") as f:
            return parse_alias(f.read())
    except OSError:
        return []


def lineas():
    out = [
        f"── NEON//OS {VERSION} · MANUAL DE USO",
        "",
        "NEON//OS es una consola de texto basada en Debian, con estética cyberpunk.",
        "Todo se maneja con el teclado desde el menú principal o con comandos.",
        "",
        "── MENÚ PRINCIPAL",
        "  Se abre solo al iniciar sesión en la consola. También con: menu (o neon)",
        "  arriba/abajo o j/k   moverse entre opciones",
        "  Enter o derecha      abrir la opción elegida",
        "  Q o Esc              volver / salir del menú (queda la consola normal)",
        "",
        "── EN LOS VISORES Y APLICACIONES",
        "  arriba/abajo, RePág/AvPág   desplazarse",
        "  Calendario: izquierda/derecha = mes, arriba/abajo = año, T = hoy",
        "  Q                           volver al menú",
        "",
        "── COMANDOS DE neon",
        "  neon help        lista completa de comandos",
        "  neon sys.scan    diagnóstico      neon net.status   estado de red",
        "  neon proc.list   procesos         neon access.logs  registros",
        "  neon calendario  neon monitor     neon apagar       neon reiniciar",
        "",
        "── ALIAS DISPONIBLES",
    ]
    alias = leer_alias()
    if alias:
        out += [f"  {nombre:<12} {desc}" for nombre, _, desc in alias]
    else:
        out.append(f"[!!] No se encontró la lista de alias ({ruta_alias()}).")
    out += [
        "",
        "── PERSONALIZAR",
        "  touch ~/.neon_no_menu     no abrir el menú al iniciar sesión",
        "  touch ~/.neon_no_banner   no mostrar el banner",
        "  En GRUB, agregar neon.noboot a la línea del kernel omite la secuencia de arranque.",
        "",
        "── APAGAR",
        "  Desde el menú (sección ENERGÍA) o con los comandos apagar / reiniciar.",
        "  Siempre se pide confirmación antes de hacerlo.",
    ]
    return out
