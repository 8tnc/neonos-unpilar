import getpass
import os
import platform
import shutil
import socket
import subprocess
import time


def run(cmd, timeout=5):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return [f"[!!] Dependencia ausente: no se encontró '{cmd[0]}'."]
    except PermissionError:
        return [f"[!!] Permiso denegado al ejecutar '{cmd[0]}'."]
    except subprocess.TimeoutExpired:
        return [f"[!!] '{cmd[0]}' no respondió en {timeout} s."]
    lineas = p.stdout.splitlines()
    error = p.stderr.strip()
    if p.returncode != 0:
        lineas.append(f"[!!] {cmd[0]} falló: {error or f'código de salida {p.returncode}'}")
    elif error:
        lineas += [f"  {linea}" for linea in error.splitlines()]
    return lineas


def leer(ruta):
    try:
        with open(ruta, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def tiempo_activo(segundos):
    s = int(segundos)
    return f"{s // 86400}d {s % 86400 // 3600}h {s % 3600 // 60}m"


def barra(fraccion, ancho):
    n = round(max(0.0, min(1.0, fraccion)) * ancho)
    return "█" * n + "░" * (ancho - n)


def tabla(filas):
    ancho = max(len(e) for e, _ in filas)
    return [f"{e.ljust(ancho)}  {v}" for e, v in filas]


def parse_os_release(texto):
    for linea in texto.splitlines():
        if linea.startswith("PRETTY_NAME="):
            return linea.split("=", 1)[1].strip().strip('"')
    return None


def parse_meminfo(texto):
    datos = {}
    for linea in texto.splitlines():
        partes = linea.split()
        if len(partes) >= 2 and partes[0].endswith(":") and partes[1].isdigit():
            datos[partes[0][:-1]] = int(partes[1])
    return datos


def parse_cpu(texto):
    for linea in texto.splitlines():
        if linea.startswith("cpu "):
            v = [int(x) for x in linea.split()[1:9]]
            inactivo = v[3] + (v[4] if len(v) > 4 else 0)
            total = sum(v)
            return total - inactivo, total
    return None


def porcentaje_cpu(antes, despues):
    if not antes or not despues or despues[1] <= antes[1]:
        return None
    return 100.0 * (despues[0] - antes[0]) / (despues[1] - antes[1])


def muestra_cpu():
    texto = leer("/proc/stat")
    return parse_cpu(texto) if texto else None


def memoria():
    texto = leer("/proc/meminfo")
    if not texto:
        return None
    m = parse_meminfo(texto)
    if "MemTotal" not in m:
        return None
    disponible = m.get("MemAvailable", m.get("MemFree", 0))
    return {
        "total": m["MemTotal"] // 1024,
        "usada": (m["MemTotal"] - disponible) // 1024,
        "swap_total": m.get("SwapTotal", 0) // 1024,
        "swap_usada": (m.get("SwapTotal", 0) - m.get("SwapFree", 0)) // 1024,
    }


def segundos_activo():
    texto = leer("/proc/uptime")
    return float(texto.split()[0]) if texto else None


def carga():
    texto = leer("/proc/loadavg")
    return " ".join(texto.split()[:3]) if texto else None


def modelo_cpu():
    texto = leer("/proc/cpuinfo") or ""
    for linea in texto.splitlines():
        if linea.startswith("model name"):
            return linea.split(":", 1)[1].strip()
    return platform.processor() or None


def nombre_sistema():
    texto = leer("/etc/os-release")
    return (parse_os_release(texto) if texto else None) or platform.system()


def sys_scan():
    mem = memoria()
    activo = segundos_activo()
    try:
        disco = shutil.disk_usage("/")
        disco_txt = f"{disco.used / 2**30:.1f} GiB usados de {disco.total / 2**30:.1f} GiB"
    except OSError:
        disco_txt = "desconocido"
    filas = [
        ("NODO", socket.gethostname()),
        ("USUARIO", getpass.getuser()),
        ("SISTEMA", nombre_sistema()),
        ("KERNEL", platform.release()),
        ("ARQUITECTURA", platform.machine()),
        ("CPU", modelo_cpu() or "desconocida"),
        ("NÚCLEOS", str(os.cpu_count() or "desconocido")),
        ("CARGA", carga() or "desconocida"),
        ("ACTIVO", tiempo_activo(activo) if activo is not None else "desconocido"),
        ("MEMORIA", f"{mem['usada']} MiB usados de {mem['total']} MiB" if mem else "desconocida"),
        ("DISCO /", disco_txt),
        ("FECHA", time.strftime("%Y-%m-%d %H:%M:%S")),
    ]
    return tabla(filas)


def net_status():
    lineas = ["── Interfaces ──"] + run(["ip", "-brief", "address"])
    lineas += ["", "── Rutas ──"] + run(["ip", "route"])
    dns = [l.split()[1] for l in (leer("/etc/resolv.conf") or "").splitlines()
           if l.startswith("nameserver") and len(l.split()) > 1]
    lineas += ["", "── DNS ──"] + (dns or ["sin servidores DNS configurados"])
    return lineas


def proc_list(limite=60):
    return run(["ps", "-eo", "pid,user,%cpu,%mem,comm", "--sort=-%cpu"])[:limite]


def access_logs():
    return run(["journalctl", "-r", "-n", "300", "--no-pager", "-o", "short-iso"], timeout=15)
