#!/usr/bin/env python3
"""
Fix all bugs in the RTL-SDR plugin.
"""
import paramiko
import sys

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
    print("=== Correction des bugs ===")
    print()
    
    try:
        client = ssh_connect()
        print("✅ Connexion SSH réussie")
        print()
        
        # 1. Create www directory if it doesn't exist
        print("1. Création du dossier /config/www/rtl_dsr/")
        output, error = run_command(client, "mkdir -p /config/www/rtl_dsr")
        print("✅ Dossier créé")
        print()
        
        # 2. Copy panel.js
        print("2. Copie de panel.js")
        # We'll use SFTP to copy the file
        sftp = client.open_sftp()
        sftp.put("panel/sdrplusplus/panel.js", "/config/www/rtl_dsr/panel.js")
        sftp.close()
        print("✅ panel.js copié")
        print()
        
        # 3. Verify
        print("3. Vérification")
        output, error = run_command(client, "ls -la /config/www/rtl_dsr/")
        print(output)
        print()
        
        # 4. Restart HA
        print("4. Redémarrage de Home Assistant")
        output, error = run_command(client, "ha core restart")
        print("✅ Redémarrage lancé")
        print()
        
        client.close()
        print("✅ Corrections terminées")
        
    except Exception as e:
        print(f"❌ Erreur SSH: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
