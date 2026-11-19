[ -n "${BASH_VERSION:-}" ] || return 0
case $- in
    *i*) ;;
    *) return 0 ;;
esac

__neon_status() {
    local s=$?
    [ "$s" -ne 0 ] && printf '[ERR %d]' "$s"
    return 0
}

__neon_prompt() {
    local r='\[\e[1;31m\]' w='\[\e[1;37m\]' g='\[\e[90m\]' x='\[\e[0m\]'
    local sym='»'
    [ "$EUID" -eq 0 ] && sym='#'
    PS1="${r}┌─[${w}\u${g}@${w}\h${r}]─[${x}\w${r}]${x}\n${r}└─${w}\$(__neon_status)${r}${sym}${x} "
    PS2="${r}  »${x} "
}
__neon_prompt
unset -f __neon_prompt
