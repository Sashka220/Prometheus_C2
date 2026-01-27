#!/usr/bin/env python3
# create_cert.py

import subprocess
import os

print("[*] Generating self-signed SSL certificate...")

# Создаем директорию для сертификатов, если её нет
os.makedirs("cert", exist_ok=True)

# Генерируем приватный ключ и сертификат одной командой openssl
command = [
    "openssl", "req", "-x509", "-newkey", "rsa:4096",
    "-keyout", "cert/server.key",
    "-out", "cert/server.crt",
    "-days", "365",
    "-nodes",
    "-subj", "/C=RU/ST=RU/L=Moscow/O=crypto.app.alexander.selinuxov/CN=VulndisclosenterpriseTEAM"
]

try:
    subprocess.run(command, check=True, capture_output=True)
    print("[+] Certificate generated successfully!")
    print(f"   Key:  cert/server.key")
    print(f"   Cert: cert/server.crt")
    print("[!] IMPORTANT: Your browser will warn about self-signed certificate.")
except subprocess.CalledProcessError as e:
    print(f"[-] Error generating certificate: {e.stderr.decode()}")
except FileNotFoundError:
    print("[-] OpenSSL not found. Please install openssl package.")
