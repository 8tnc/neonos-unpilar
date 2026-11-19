# NEON//OS

Distribución de consola basada en **Debian 13 (trixie)**, sin entorno gráfico y con estética cyberpunk. Reemplaza la experiencia de texto estándar de Debian por una identidad visual propia y suma un menú interactivo en español con herramientas de sistema y aplicaciones.

**Versión:** 0.1.0

## Características

- **Arranque personalizado:** GRUB con colores propios, intro con el emblema en ASCII y arranque silencioso del kernel.
- **Secuencia de arranque** en `tty1` con comprobaciones reales del sistema (raíz, memoria, red, DNS y servicios fallidos). Cualquier tecla la saltea.
- **Pantalla de login** (`/etc/issue`) con el emblema y datos del equipo; el texto `login:` aparece en rojo.
- **Banner de bienvenida** con nodo, usuario, sistema, kernel, tiempo activo, memoria, IP y fecha.
- **Prompt** de dos líneas que muestra el código de error del último comando.
- **Paleta de colores y fuente Terminus** en la consola.
- **Menú interactivo `neon`** (Python + curses) que se abre al iniciar sesión en la consola local.
- **18 alias** en español para las tareas más comunes.

## Requisitos

- Debian 13 instalado sin entorno gráfico.
- `python3` (incluye el módulo `curses`).
- Un usuario con permisos de `sudo`.

```bash
sudo apt install python3
```

## Instalación

```bash
git clone https://github.com/8tnc/neonos-unpilar.git
cd neonos-unpilar/neon-config
sudo bash install.sh
sudo bash boot/install-boot.sh
sudo reboot
```

- `install.sh` instala la identidad visual, el menú, los alias, el prompt y el servicio de arranque.
- `boot/install-boot.sh` configura GRUB, los parámetros del kernel y la fuente de la consola.

Los dos son independientes y se pueden revertir por separado.

## Uso

### Menú principal

Se abre automáticamente al iniciar sesión en la consola local (no por SSH). También se abre con `menu` o `neon`.

| Sección | Opción | Descripción |
|---|---|---|
| Sistema | Diagnóstico del sistema | Nodo, kernel, CPU, memoria, disco y tiempo activo |
| | Estado de red | Interfaces, direcciones, rutas y servidores DNS |
| | Procesos | Procesos ordenados por uso de CPU |
| | Registros del sistema | Últimas 300 entradas del journal |
| Aplicaciones | Calendario | Calendario mensual navegable, con el día actual resaltado |
| | Monitor en vivo | CPU, memoria, swap, disco y procesos, actualizado cada segundo |
| | Notas | Abre `~/notas.txt` con el editor del usuario (`nano` por defecto) |
| Terminal | Abrir Bash | Sale a una sesión Bash; con `exit` se vuelve al menú |
| | Claude Code | Abre Claude Code si el usuario lo instaló en su cuenta; si no, muestra cómo instalarlo |
| Ayuda | Manual de uso | Teclas, comandos y lista de alias |
| Energía | Reiniciar / Apagar | Con confirmación previa |

**Teclas:**

| Tecla | Acción |
|---|---|
| `↑` `↓` o `j` `k` | Moverse por el menú |
| `Enter` o `→` | Abrir la opción |
| `Q` o `Esc` | Volver o salir del menú |
| `←` `→` / `↑` `↓` / `T` (en el calendario) | Mes / año / volver a hoy |

### Comandos

```
neon                abre el menú interactivo
neon sys.scan       información básica del sistema
neon net.status     interfaces de red, rutas y DNS
neon proc.list      procesos ordenados por uso de CPU
neon access.logs    últimos registros del sistema
neon manual         manual de uso
neon calendario     calendario interactivo
neon monitor        monitor de recursos en vivo
neon apagar         apaga el equipo (pide confirmación)
neon reiniciar      reinicia el equipo (pide confirmación)
neon help           lista de comandos
neon --version      versión instalada
```

### Alias

| Alias | Comando | Descripción |
|---|---|---|
| `menu` | `neon` | Abre el menú principal |
| `manual` | `neon manual` | Muestra el manual de uso |
| `ayuda` | `neon help` | Lista los comandos de neon |
| `escanear` | `neon sys.scan` | Diagnóstico del sistema |
| `red` | `neon net.status` | Interfaces, rutas y DNS |
| `procesos` | `neon proc.list` | Procesos ordenados por uso de CPU |
| `registros` | `neon access.logs` | Últimos registros del sistema |
| `calendario` | `neon calendario` | Calendario mensual interactivo |
| `monitor` | `neon monitor` | Monitor de recursos en vivo |
| `notas` | `${EDITOR:-nano} ~/notas.txt` | Abre el archivo de notas personal |
| `banner` | `neon-banner` | Vuelve a mostrar el banner de bienvenida |
| `secuencia` | `neon-bootseq` | Repite la secuencia de arranque |
| `apagar` | `neon apagar` | Apaga el equipo, con confirmación |
| `reiniciar` | `neon reiniciar` | Reinicia el equipo, con confirmación |
| `limpiar` | `clear` | Limpia la pantalla |
| `actualizar` | `sudo apt update && sudo apt upgrade` | Actualiza el sistema |
| `ll` | `ls -lh --color=auto` | Lista detallada |
| `la` | `ls -lAh --color=auto` | Lista detallada con archivos ocultos |

## Estructura del repositorio

```
neon-config/
├── install.sh                  instalación de la identidad visual y el menú
├── uninstall.sh                desinstalación
├── bin/
│   ├── neon                    punto de entrada del menú y los comandos
│   ├── neon-banner             banner de bienvenida
│   └── neon-bootseq            secuencia de arranque
├── lib/
│   ├── theme.sh                paleta de colores
│   ├── prompt.sh               prompt de Bash
│   └── aliases.sh              alias
├── profile.d/neon.sh           banner y menú al iniciar sesión
├── systemd/
│   └── neon-bootseq.service    servicio de la secuencia de arranque
├── boot/
│   ├── grub-neon.cfg           configuración de GRUB y del kernel
│   ├── 06_neon                 colores e intro de GRUB
│   ├── install-boot.sh
│   └── uninstall-boot.sh
├── assets/ascii/
│   ├── emblem.txt              emblema (Unicode, para la consola)
│   └── emblem-ascii.txt        emblema (ASCII, para GRUB)
└── python/neon/                paquete del menú
    ├── cli.py                  comandos
    ├── menu.py                 menú principal
    ├── ui.py                   componentes de la interfaz
    ├── sysinfo.py              lectura de datos del sistema
    ├── power.py                apagado y reinicio
    ├── manual.py               manual de uso
    ├── claude_code.py          lanzador de Claude Code
    └── apps/
        ├── calendario.py
        └── monitor.py
```

## Archivos que modifica en el sistema

| Ruta | Cambio | Script |
|---|---|---|
| `/usr/local/share/neon/` | Tema, prompt, alias y arte ASCII | `install.sh` |
| `/usr/local/lib/neon/` | Paquete Python del menú | `install.sh` |
| `/usr/local/bin/neon`, `neon-banner`, `neon-bootseq` | Ejecutables | `install.sh` |
| `/etc/profile.d/neon.sh` | Muestra el banner y abre el menú al iniciar sesión | `install.sh` |
| `/etc/systemd/system/neon-bootseq.service` | Servicio de la secuencia de arranque | `install.sh` |
| `/etc/issue` | Pantalla previa al login (respaldo en `/etc/issue.neon-backup`) | `install.sh` |
| `/etc/motd` | Se vacía (respaldo en `/etc/motd.neon-backup`) | `install.sh` |
| `/etc/bash.bashrc` | Bloque que carga los alias | `install.sh` |
| `~/.bashrc`, `/root/.bashrc`, `/etc/skel/.bashrc` | Bloque que carga el prompt | `install.sh` |
| `/etc/default/grub.d/neon.cfg` | Menú, tiempo de espera y parámetros del kernel | `boot/install-boot.sh` |
| `/etc/grub.d/06_neon` | Colores e intro de GRUB | `boot/install-boot.sh` |
| `/etc/default/console-setup` | Fuente Terminus (respaldo en `console-setup.neon-backup`) | `boot/install-boot.sh` |

Los bloques agregados a archivos existentes quedan entre las líneas `# >>> NEON//OS >>>` y `# <<< NEON//OS <<<`, para poder quitarlos sin tocar el resto del archivo.

## Personalización

| Acción | Cómo |
|---|---|
| No abrir el menú al iniciar sesión | `touch ~/.neon_no_menu` |
| No mostrar el banner | `touch ~/.neon_no_banner` |
| Omitir la secuencia de arranque | Agregar `neon.noboot` a la línea del kernel en GRUB (tecla `e`) |

## Desinstalación

```bash
cd neonos-unpilar/neon-config
sudo bash boot/uninstall-boot.sh
sudo bash uninstall.sh
```

Restaura los archivos originales desde sus respaldos y quita los bloques agregados.
