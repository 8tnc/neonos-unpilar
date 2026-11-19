[ -n "${BASH_VERSION:-}" ] || return 0
case $- in
    *i*) ;;
    *) return 0 ;;
esac

alias menu='neon'                               # abre el menú principal de NEON//OS
alias manual='neon manual'                      # muestra el manual de uso
alias ayuda='neon help'                         # lista los comandos de neon
alias escanear='neon sys.scan'                  # diagnóstico del sistema
alias red='neon net.status'                     # interfaces, rutas y DNS
alias procesos='neon proc.list'                 # procesos ordenados por uso de CPU
alias registros='neon access.logs'              # últimos registros del sistema
alias calendario='neon calendario'              # calendario mensual interactivo
alias monitor='neon monitor'                    # monitor de recursos en vivo
alias notas='${EDITOR:-nano} ~/notas.txt'       # abre el archivo de notas personal
alias banner='neon-banner'                      # vuelve a mostrar el banner de bienvenida
alias secuencia='neon-bootseq'                  # repite la secuencia de arranque
alias apagar='neon apagar'                      # apaga el equipo (pide confirmación)
alias reiniciar='neon reiniciar'                # reinicia el equipo (pide confirmación)
alias limpiar='clear'                           # limpia la pantalla
alias actualizar='sudo apt update && sudo apt upgrade'   # actualiza el sistema
alias ll='ls -lh --color=auto'                  # lista detallada
alias la='ls -lAh --color=auto'                 # lista detallada con archivos ocultos
