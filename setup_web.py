#!/usr/bin/env python3
# setup_web.py

import os
import sys
import subprocess

def check_dependencies():
    """Проверяет необходимые зависимости"""
    print("[*] Checking Python dependencies...")
    
    required_modules = ['flask', 'requests']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"[-] Missing Python modules: {', '.join(missing)}")
        print("[*] Installing with pip...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("[+] Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("[-] Failed to install dependencies. Please install manually:")
            print(f"    pip install {' '.join(missing)}")
            sys.exit(1)
    else:
        print("[+] All Python dependencies are satisfied.")

def setup_directories():
    """Создает необходимые директории"""
    directories = ['templates', 'uploads', 'cert']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"[+] Created directory: {directory}/")

def check_openssl():
    """Проверяет наличие OpenSSL"""
    try:
        subprocess.run(['openssl', 'version'], capture_output=True, check=True)
        print("[+] OpenSSL is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] OpenSSL not found. SSL certificate generation will fail.")
        print("[*] Install OpenSSL: sudo apt-get install openssl (Debian/Ubuntu)")
        return False

def main():
    print("=" * 50)
    print("Prometheus C2 - Web Server Setup")
    print("=" * 50)
    
    # Проверяем зависимости
    check_dependencies()
    
    # Создаем директории
    setup_directories()
    
    # Проверяем OpenSSL
    has_openssl = check_openssl()
    
    # Проверяем существование основных файлов
    print("\n[*] Checking essential files...")
    essential_files = ['pmtgener', 'chimera.sh', 'stealth_loader.txt', 'main_loader.txt']
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"[+] Found: {file}")
        else:
            print(f"[-] Missing: {file}")
    
    # Генерируем SSL сертификат если нужно
    if has_openssl:
        cert_files = ['cert/server.crt', 'cert/server.key']
        if all(os.path.exists(f) for f in cert_files):
            print("[+] SSL certificates already exist")
        else:
            print("\n[*] Generating SSL certificates...")
            try:
                from create_cert import generate_cert
                generate_cert()
            except ImportError:
                print("[-] Could not generate certificates automatically")
                print("[*] Run manually: python create_cert.py")
    
    print("\n" + "=" * 50)
    print("[+] Setup completed!")
    print("\nTo start the web server:")
    print("  1. Make sure pmtgener is executable: chmod +x pmtgener chimera.sh")
    print("  2. Run: python web_server.py")
    print("  3. Open: https://localhost in your browser")
    print("  4. Accept the self-signed certificate warning")
    print("\nDefault API endpoint: https://localhost:443/api/quick_generate")
    print("=" * 50)

if __name__ == '__main__':
    main()
