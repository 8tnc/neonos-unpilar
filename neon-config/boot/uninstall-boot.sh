#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: hace falta ser root. Ejecutá: sudo bash $0" >&2
    exit 1
fi

rm -f /etc/default/grub.d/neon.cfg /etc/grub.d/06_neon

CS=/etc/default/console-setup
if [ -e "$CS.neon-backup" ]; then
    mv "$CS.neon-backup" "$CS"
    echo "» Restaurado $CS"
fi

update-grub
echo "Arranque de Debian restaurado. Reiniciá para verlo."
