case $- in
    *i*) ;;
    *) return 0 ;;
esac

if [ -t 1 ] && [ ! -e "$HOME/.neon_no_banner" ] && command -v neon-banner >/dev/null 2>&1; then
    neon-banner
fi

if [ -t 0 ] && [ ! -e "$HOME/.neon_no_menu" ] && [ -z "${SSH_CONNECTION:-}" ] && command -v neon >/dev/null 2>&1; then
    case "$(tty 2>/dev/null)" in
        /dev/tty[0-9]*) neon ;;
    esac
fi
