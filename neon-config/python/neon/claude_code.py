import os
import shutil
import subprocess

INSTRUCCIONES = [
    "[!!] Claude Code no está instalado en esta cuenta.",
    "",
    "Para instalarlo, salí del menú (Q) y ESCRIBÍ estos comandos en la terminal",
    "(sin sudo; queda en ~/.local/bin). Si falta curl: sudo apt install curl",
    "  curl -fsSL https://claude.ai/install.sh -o /tmp/claude-install.sh",
    "  less /tmp/claude-install.sh      # revisá el instalador",
    "  bash /tmp/claude-install.sh",
    "",
    "La primera vez que lo abras te pedirá iniciar sesión con TU cuenta:",
    "muestra un enlace para abrir en el navegador de otro equipo y pegar el código.",
    "Las credenciales quedan en tu directorio personal, nunca en el sistema.",
]


def ruta_claude():
    encontrado = shutil.which("claude")
    if encontrado:
        return encontrado
    local = os.path.expanduser("~/.local/bin/claude")
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return local
    return None


def abrir_claude():
    ruta = ruta_claude()
    if not ruta:
        print("\n".join(INSTRUCCIONES))
        return True
    print("» Abriendo Claude Code. Escribí /exit para volver al menú NEON.\n")
    subprocess.run([ruta])
    return False
