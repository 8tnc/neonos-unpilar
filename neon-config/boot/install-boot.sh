#!/usr/bin/env bash
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: hace falta ser root. Ejecutá: sudo bash $0" >&2
    exit 1
fi
if ! command -v update-grub >/dev/null 2>&1; then
    echo "ERROR: no se encontró update-grub. ¿Este sistema arranca con GRUB?" >&2
    exit 1
fi
if [ ! -r /usr/local/share/neon/assets/ascii/emblem-ascii.txt ]; then
    echo "ERROR: falta el emblema ASCII. Ejecutá primero: sudo bash install.sh" >&2
    exit 1
fi

echo "» Instalando configuración de GRUB"
install -d /etc/default/grub.d
install -m 644 "$SRC/grub-neon.cfg" /etc/default/grub.d/neon.cfg
install -m 755 "$SRC/06_neon" /etc/grub.d/06_neon

CS=/etc/default/console-setup
if ls /usr/share/consolefonts/*Terminus16.psf.gz >/dev/null 2>&1 && [ -w "$CS" ]; then
    echo "» Fuente de consola: Terminus 8x16"
    if [ ! -e "$CS.neon-backup" ]; then
        cp -a "$CS" "$CS.neon-backup"
        echo "» Respaldo: $CS.neon-backup"
    fi
    sed -i 's/^FONTFACE=.*/FONTFACE="Terminus"/; s/^FONTSIZE=.*/FONTSIZE="8x16"/' "$CS"
else
    echo "AVISO: no se encontró la fuente Terminus o $CS; se mantiene la fuente actual." >&2
fi

echo "» Regenerando /boot/grub/grub.cfg"
update-grub

echo
echo "Listo. Reiniciá con: sudo reboot"
echo "Si algo se ve mal: en el menú de GRUB pulsá 'e' para editar ese arranque, o entrá en"
echo "'Opciones avanzadas' > modo de recuperación. Para revertir: sudo bash boot/uninstall-boot.sh"
