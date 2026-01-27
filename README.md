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
