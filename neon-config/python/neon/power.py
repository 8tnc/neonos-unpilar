import subprocess

ACCIONES = {
    "reboot": ("Reiniciando", ["systemctl", "reboot"]),
    "poweroff": ("Apagando", ["systemctl", "poweroff"]),
}


def ejecutar(accion):
    texto, cmd = ACCIONES[accion]
    print(f"» {texto} el sistema...")
    try:
        if subprocess.run(cmd).returncode == 0:
            return True
        print("» systemd pide privilegios de administrador; se intentará con sudo.")
        return subprocess.run(["sudo"] + cmd).returncode == 0
    except FileNotFoundError as e:
        print(f"[!!] Dependencia ausente: {e.filename}")
        return False
