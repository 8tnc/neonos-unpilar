#!/usr/bin/env bash
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
SHARE=/usr/local/share/neon

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: hace falta ser root. Ejecutá: sudo $0" >&2
    exit 1
fi

for cmd in awk free ip hostname; do
    command -v "$cmd" >/dev/null 2>&1 || echo "AVISO: falta '$cmd'; el banner mostrará ese dato como desconocido." >&2
done
if ! python3 -c 'import curses' 2>/dev/null; then
    echo "AVISO: falta python3 (o su módulo curses); el menú 'neon' no funcionará. Instalalo con: sudo apt install python3" >&2
fi

echo "» Copiando archivos a $SHARE"
install -d "$SHARE/lib" "$SHARE/assets/ascii"
install -m 644 "$SRC"/lib/*.sh "$SHARE/lib/"
install -m 644 "$SRC"/assets/ascii/*.txt "$SHARE/assets/ascii/"
install -m 755 "$SRC/bin/neon-banner" /usr/local/bin/neon-banner
install -m 644 "$SRC/profile.d/neon.sh" /etc/profile.d/neon.sh
install -m 755 "$SRC/bin/neon-bootseq" /usr/local/bin/neon-bootseq

echo "» Instalando el menú neon"
rm -rf /usr/local/lib/neon/neon
install -d /usr/local/lib/neon
cp -r "$SRC/python/neon" /usr/local/lib/neon/
find /usr/local/lib/neon -name __pycache__ -prune -exec rm -rf {} +
chmod -R u=rwX,go=rX /usr/local/lib/neon
install -m 755 "$SRC/bin/neon" /usr/local/bin/neon

echo "» Registrando servicio de arranque neon-bootseq"
install -m 644 "$SRC/systemd/neon-bootseq.service" /etc/systemd/system/neon-bootseq.service
systemctl daemon-reload
systemctl enable neon-bootseq.service

backup() {
    if [ -e "$1" ] && [ ! -e "$1.neon-backup" ]; then
        cp -a "$1" "$1.neon-backup"
        echo "» Respaldo: $1.neon-backup"
    fi
}
backup /etc/issue
backup /etc/motd

echo "» Generando /etc/issue"
ESC=$'\033'
R="${ESC}[1;31m" W="${ESC}[1;37m" G="${ESC}[90m" X="${ESC}[0m"
sep="${R}──────────────────────────────────────${X}"
right=(
    "" ""
    "${W}A R A S A K A   C O R P O R A T I O N${X}"
    "${G}NEON//OS · consola corporativa${X}"
    "$sep"
    "${G}NODO    ${X} \\n"
    "${G}TERMINAL${X} \\l"
    "${G}KERNEL  ${X} \\r"
    "${G}FECHA   ${X} \\d \\t"
    "$sep"
)
mapfile -t left < "$SRC/assets/ascii/emblem.txt"
{
    printf '%s[H%s[2J\n' "$ESC" "$ESC"
    for i in "${!left[@]}"; do
        printf ' %s%s%s  %s\n' "$R" "${left[i]}" "$X" "${right[i]:-}"
    done
    printf '\n%s' "$R"
} > /etc/issue

echo "» Vaciando /etc/motd"
: > /etc/motd

INICIO="# >>> NEON//OS >>>"
FIN="# <<< NEON//OS <<<"
agregar_bloque() {
    [ -e "$1" ] || return 0
    if ! grep -qF "$INICIO" "$1"; then
        printf '
%s
%s
%s
' "$INICIO" "$2" "$FIN" >> "$1"
        echo "» Bloque NEON agregado a $1"
    fi
}

echo "» Activando alias en /etc/bash.bashrc"
agregar_bloque /etc/bash.bashrc "[ -r $SHARE/lib/aliases.sh ] && . $SHARE/lib/aliases.sh"

echo "» Activando el prompt NEON"
PROMPT_LINEA="[ -r $SHARE/lib/prompt.sh ] && . $SHARE/lib/prompt.sh"
agregar_bloque /etc/skel/.bashrc "$PROMPT_LINEA"
agregar_bloque /root/.bashrc "$PROMPT_LINEA"
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != root ]; then
    agregar_bloque "$(getent passwd "$SUDO_USER" | cut -d: -f6)/.bashrc" "$PROMPT_LINEA"
fi

echo
echo "Listo. Cerrá sesión y volvé a entrar para ver el banner, el menú, el prompt y los alias."
echo "Escribí 'manual' para ver el manual de uso."
