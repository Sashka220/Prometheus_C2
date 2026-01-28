# Prometheus C2

Minimal red team framework for authorized security operations. Lightweight, modular, and designed for physical access scenarios.

Written in Python and Bash, using LoTL PowerShell stagers and shells.

---

## Core Features

### Compact and Efficient
- **Total unpacked size:** <150KB
- **Minimal dependencies,** pure Python/Bash
- **Low memory footprint,** stealth execution

### Telegram C2
- Real-time command execution via Telegram bots
- Encrypted communication through Telegram API
- Session persistence and auto-reconnect
- Error handling with detailed tracebacks

### AV Evasion
- Chimera obfuscator integration
- AMSI bypass techniques
- String and variable substitution
- Stream encryption via chimera

### Web Interface
- HTTPS with self-signed certificates
- Payload generator with Filebin integration
- Ducky script auto-updater
- REST API for automation

### Modular Architecture
- Standalone module system
- Plug-and-play reconnaissance scripts
- Custom module support
- Network discovery tools

---

## Quick Start

### Installation
```bash
git clone https://github.com/Sashka220/Prometheus_C2.git
cd Prometheus_C2
chmod +x pmtgener prm
python3 -m pip install flask requests
```
### Usage & troubleshooting 

## pmtgener – Payload Generator

Usage:
pmtgener is the main payload generator script. It supports multiple payload types with configurable encryption levels and options.

Help Command Display:
Run:
./pmtgener -h

Options Explained:
| Option | Description |
|--------|-------------|
| -h, --help | Show this help message and exit |
| -V, --version | Show version and exit |
| -v, --verbose | Enable verbosity during generation |
| -t, --type TYPE | Payload type (required). Available types: better_tg, standart, advanced, tg_shell |
| -EL, --encrypt-level (0-5) | Encryption level for chimera (default: 5) |
| --output FILE | Output filename (default: based on type) |
| --token TOKEN | HTTP token for telegram bot (for better_tg and tg_shell) |
| --id ID | Telegram user ID for bot access control (for better_tg and tg_shell) |
| --ip IP | Your local IP in wifi network (for standart and advanced) |
| --port PORT | Port for shell to connect (for standart and advanced) |

Examples:
pmtgener -t better_tg --token 123:ABC --id 456789
pmtgener -t standart --ip 192.168.1.100 --port 4444
pmtgener -t advanced --ip 10.0.0.5 --port 9001 -EL 4 -v

---

## server.py – Web Server

Usage:
server.py is the main web server for the Prometheus C2 web interface and API.

Help Command Display:
Run:
python server.py -h

Options Explained:
| Option | Description |
|--------|-------------|
| -h, --help | Show this help message and exit |
| --port PORT | Port to run on (default: 8443) |
| --host HOST | Host to bind to (default: 0.0.0.0) |
| --no-ssl | Run without SSL (not recommended) |

Example:
python server.py --port 9443 --host 127.0.0.1

---

## setup_web.py – Web Server Setup

Usage:
setup_web.py prepares the environment for running the web server, checking dependencies and creating necessary directories.

Run:
python setup_web.py

What it does:
- Checks Python dependencies
- Creates required directories (templates/, uploads/, cert/)
- Verifies essential files (pmtgener, chimera.sh, etc.)
- Checks for existing SSL certificates

After setup, start the server with:
python web_server.py

---

## prm – Prometheus C2 CLI

Usage:
prm is the command-line interface for managing and operating the Prometheus C2 framework interactively.

Help Command Display:
Type help in the CLI:
prm> help

Commands:
| Command | Description |
|---------|-------------|
| help | Show help |
| exit/quit | Exit CLI |
| clear | Clear screen |
| set GATEWAY [ip] | Set gateway IP |
| set INTERFACE [iface] | Set network interface |
| recon --all | Network discovery |
| recon -m [module] | Run recon module |
| configure --payload [type] [target_ip] | Configure payload |
| generate | Generate payload via pmtgener |
| web | Start web interface |
| modules | List available modules |
| scan [ip/range] | Scan target |
| status | Show system status |

Flags:
| Flag | Description |
|------|-------------|
| -h, --help | Show help |
| -m, --module [name] | Run module |
| --list | List modules |
| -iface [interface] | Set interface |
| -I [on/off] | Interactive mode |
| -v, --version | Show version |

Example usage in CLI:
prm> set INTERFACE eth0
prm> recon --all
prm> generate
prm> status
```
```
### troubleshooting 

## cannot open web panel?
try to use 443 port when running server.py 
```
python server.py --port 443
```
## payloads don't upload to filebin?
try to:
use a VPN 
restart network manager
