#!/usr/bin/env python3
"""
SSH diagnostic and fix script for Home Assistant RTL-SDR plugin.
"""
import paramiko
import sys
import time

# SSH connection details
HOST = "homeassistant.local"
PORT = 22222
USER = "leo"
PASSWORD = "1524XLH1524xlh"

def ssh_connect():
    """Create SSH connection."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
    return client

def run_command(client, command):
    """Run a command and return output."""
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    print("=== Diagnostic SSH Home Assistant ===")
    print()
    
    try:
        client = ssh_connect()
        print("✅ Connexion SSH réussie")
        print()
        
        # 1. Check files
        print("1. Vérification des fichiers dans /config/custom_components/rtl_dsr/")
        output, error = run_command(client, "ls -la /config/custom_components/rtl_dsr/")
        print(output)
        if error:
            print(f"Erreur: {error}")
        print()
        
        # 2. Check www directory
        print("2. Vérification de /config/www/rtl_dsr/")
        output, error = run_command(client, "ls -la /config/www/rtl_dsr/")
        print(output)
        if error:
            print(f"Erreur: {error}")
        print()
        
        # 3. Check logs
        print("3. Vérification des logs d'erreur")
        output, error = run_command(client, "tail -50 /config/home-assistant.log | grep -i rtl")
        print(output)
        if error:
            print(f"Erreur: {error}")
        print()
        
        # 4. Test panel.js
        print("4. Test de panel.js")
        output, error = run_command(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:8123/local/rtl_dsr/panel.js")
        print(f"Status HTTP: {output}")
        print()
        
        client.close()
        print("✅ Diagnostic terminé")
        
    except Exception as e:
        print(f"❌ Erreur SSH: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
