#!/usr/bin/env python3

#module by @vulndosclosure

import sys
import subprocess
import json
import socket
from datetime import datetime

def check_service(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def run_nmap_scan(target):
    print(f"[*] Scanning {target}...")
    
    try:
        nmap_check = subprocess.run(['which', 'nmap'], 
                                   capture_output=True, text=True)
        if nmap_check.returncode != 0:
            print("[-] Nmap not found. Install: apt-get install nmap")
            return None
    except:
        return None
    
    nmap_args = [
        'nmap', '-sS', '-sV', '--script',
        'banner,ssh-hostkey,ldap-rootdse,msrpc-enum,sip-enum-users,smb-os-discovery',
        '-p', '21,22,23,25,53,80,88,110,139,143,389,443,445,465,587,636,993,995,1723,3306,3389,5060,5061,5900,8080,8443',
        '-T4', '--open', target
    ]
    
    try:
        result = subprocess.run(nmap_args, capture_output=True, text=True, timeout=300)
        return result.stdout
    except subprocess.TimeoutExpired:
        print("[-] Scan timeout")
        return None
    except Exception as e:
        print(f"[-] Scan error: {e}")
        return None

def analyze_results(nmap_output):
    if not nmap_output:
        return {}
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "ids_detected": "not detected",
        "critical_services": {},
        "enterprise_services": {},
        "network_type": "standard"
    }
    
    if "filtered" in nmap_output.lower() and "1000" in nmap_output:
        results["ids_detected"] = "detected"
    
    critical_services = {
        "filebin.net": check_service("filebin.net", 443),
        "api.telegram.org": check_service("api.telegram.org", 443),
        "github.com": check_service("github.com", 443),
        "raw.githubusercontent.com": check_service("raw.githubusercontent.com", 443)
    }
    results["critical_services"] = critical_services
    
    enterprise_flags = {
        "LDAP": False,
        "Kerberos": False,
        "SIP": False,
        "Asterisk": False,
        "DropbearSSH": False,
        "SMB": False,
        "RDP": False,
        "MSRPC": False
    }
    
    nmap_lower = nmap_output.lower()
    
    if "ldap" in nmap_lower or "389" in nmap_output:
        enterprise_flags["LDAP"] = True
    if "kerberos" in nmap_lower or "88" in nmap_output:
        enterprise_flags["Kerberos"] = True
    if "sip" in nmap_lower or "5060" in nmap_output or "5061" in nmap_output:
        enterprise_flags["SIP"] = True
    if "asterisk" in nmap_lower:
        enterprise_flags["Asterisk"] = True
    if "dropbear" in nmap_lower:
        enterprise_flags["DropbearSSH"] = True
    if "smb" in nmap_lower or "microsoft-ds" in nmap_lower or "445" in nmap_output:
        enterprise_flags["SMB"] = True
    if "ms-wbt-server" in nmap_lower or "3389" in nmap_output:
        enterprise_flags["RDP"] = True
    if "msrpc" in nmap_lower or "135" in nmap_output:
        enterprise_flags["MSRPC"] = True
    
    results["enterprise_services"] = enterprise_flags
    
    enterprise_count = sum(1 for v in enterprise_flags.values() if v)
    if enterprise_count >= 3:
        results["network_type"] = "enterprise"
    elif enterprise_count >= 1:
        results["network_type"] = "mixed"
    
    return results

def print_results(results):
    print(f"\n{'='*50}")
    print("PROMETHEUS ENVIRONMENT SCAN")
    print(f"{'='*50}")
    
    print(f"\n[+] IDS/IPS: {results.get('ids_detected', 'unknown')}")
    
    print("\n[+] Critical Services:")
    for service, status in results.get('critical_services', {}).items():
        status_str = "✓ ONLINE" if status else "✗ OFFLINE"
        print(f"  {service:<25} {status_str}")
    
    print("\n[+] Enterprise Services Detected:")
    enterprise = results.get('enterprise_services', {})
    detected = [k for k, v in enterprise.items() if v]
    if detected:
        for service in detected:
            print(f"  • {service}")
    else:
        print("  None")
    
    print(f"\n[+] Network Type: {results.get('network_type', 'unknown')}")
    print(f"{'='*50}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nmap_env_discovery.py [target]")
        print("Example: python3 nmap_env_discovery.py 192.168.1.0/24")
        sys.exit(1)
    
    target = sys.argv[1]
    
    print("[*] Checking critical services...")
    
    nmap_output = run_nmap_scan(target)
    
    results = analyze_results(nmap_output)
    
    print_results(results)
    
    filename = f"scan_env_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Results saved to {filename}")

if __name__ == "__main__":
    main()
