#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: hace falta ser root. Ejecutá: sudo $0" >&2
    exit 1
fi

if [ -e /etc/systemd/system/neon-bootseq.service ]; then
    systemctl disable neon-bootseq.service
    rm -f /etc/systemd/system/neon-bootseq.service
    systemctl daemon-reload
fi

rm -f /usr/local/bin/neon-banner /usr/local/bin/neon-bootseq /usr/local/bin/neon /etc/profile.d/neon.sh
rm -rf /usr/local/share/neon /usr/local/lib/neon

for f in /etc/issue /etc/motd; do
    if [ -e "$f.neon-backup" ]; then
        mv "$f.neon-backup" "$f"
        echo "» Restaurado $f"
    fi
done

quitar_bloque() {
    if [ -e "$1" ] && grep -qF "# >>> NEON//OS >>>" "$1"; then
        sed -i '/^# >>> NEON\/\/OS >>>$/,/^# <<< NEON\/\/OS <<<$/d' "$1"
        echo "» Bloque NEON quitado de $1"
    fi
}
quitar_bloque /etc/bash.bashrc
quitar_bloque /etc/skel/.bashrc
quitar_bloque /root/.bashrc
getent passwd | while IFS=: read -r _ _ uid _ _ home _; do
    [ "$uid" -ge 1000 ] && [ "$uid" -lt 60000 ] && quitar_bloque "$home/.bashrc"
done

echo "NEON//OS desinstalado."
