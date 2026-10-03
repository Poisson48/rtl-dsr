#!/usr/bin/env python3
"""
Deploy RTL-SDR integration to Home Assistant.
Uses hassio.addon_stdin with core_ssh (Terminal & SSH add-on).
"""
import asyncio
import websockets
import json
import base64
import sys
import io
from pathlib import Path

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
ACTION = sys.argv[2] if len(sys.argv) > 2 else "deploy"

async def deploy():
    uri = "ws://homeassistant.local:8123/api/websocket"

    async with websockets.connect(uri) as websocket:
        # Wait for auth_required
        response = json.loads(await websocket.recv())
        print(f"1. Serveur: {response['type']}")

        # Send auth
        await websocket.send(json.dumps({"type": "auth", "access_token": TOKEN}))
        response = json.loads(await websocket.recv())
        print(f"2. Auth: {response['type']}")

        if response["type"] != "auth_ok":
            print("ERREUR: Authentification echouee")
            return False

        print("OK: Authentification reussie\n")

        msg_id = 1

        async def send_command(command, addon="core_ssh"):
            """Send a command to an add-on via hassio.addon_stdin."""
            nonlocal msg_id
            msg = {
                "id": msg_id,
                "type": "call_service",
                "domain": "hassio",
                "service": "addon_stdin",
                "service_data": {
                    "addon": addon,
                    "input": {"command": command}
                }
            }
            await websocket.send(json.dumps(msg))
            msg_id += 1
            response = json.loads(await websocket.recv())
            return response

        if ACTION == "deploy":
            print("Deploiement de l'integration RTL-SDR...")

            # Create directories
            print("\nCreation des dossiers...")
            result = await send_command("mkdir -p /config/custom_components/rtl_dsr/translations && mkdir -p /config/www/rtl_dsr && echo OK")
            print(f"  Resultat: {result.get('result', result)}")

            if not result.get('result', {}).get('success', False):
                print("ERREUR: Impossible de creer les dossiers")
                return False

            # Files to deploy
            files = [
                ("custom_components/rtl_dsr/manifest.json", "/config/custom_components/rtl_dsr/manifest.json"),
                ("custom_components/rtl_dsr/const.py", "/config/custom_components/rtl_dsr/const.py"),
                ("custom_components/rtl_dsr/config_flow.py", "/config/custom_components/rtl_dsr/config_flow.py"),
                ("custom_components/rtl_dsr/coordinator.py", "/config/custom_components/rtl_dsr/coordinator.py"),
                ("custom_components/rtl_dsr/model.py", "/config/custom_components/rtl_dsr/model.py"),
                ("custom_components/rtl_dsr/entity.py", "/config/custom_components/rtl_dsr/entity.py"),
                ("custom_components/rtl_dsr/__init__.py", "/config/custom_components/rtl_dsr/__init__.py"),
                ("custom_components/rtl_dsr/sensor.py", "/config/custom_components/rtl_dsr/sensor.py"),
                ("custom_components/rtl_dsr/binary_sensor.py", "/config/custom_components/rtl_dsr/binary_sensor.py"),
                ("custom_components/rtl_dsr/number.py", "/config/custom_components/rtl_dsr/number.py"),
                ("custom_components/rtl_dsr/select.py", "/config/custom_components/rtl_dsr/select.py"),
                ("custom_components/rtl_dsr/switch.py", "/config/custom_components/rtl_dsr/switch.py"),
                ("custom_components/rtl_dsr/button.py", "/config/custom_components/rtl_dsr/button.py"),
                ("custom_components/rtl_dsr/text.py", "/config/custom_components/rtl_dsr/text.py"),
                ("custom_components/rtl_dsr/services.py", "/config/custom_components/rtl_dsr/services.py"),
                ("custom_components/rtl_dsr/services.yaml", "/config/custom_components/rtl_dsr/services.yaml"),
                ("custom_components/rtl_dsr/strings.json", "/config/custom_components/rtl_dsr/strings.json"),
                ("custom_components/rtl_dsr/websocket_api.py", "/config/custom_components/rtl_dsr/websocket_api.py"),
                ("custom_components/rtl_dsr/translations/fr.json", "/config/custom_components/rtl_dsr/translations/fr.json"),
                ("panel/sdrplusplus/card.js", "/config/www/rtl_dsr/card.js"),
                ("panel/sdrplusplus/sdr-plus-plus-card.js", "/config/www/rtl_dsr/sdr-plus-plus-card.js"),
            ]

            print(f"\nDeploiement de {len(files)} fichiers...")
            success_count = 0
            for i, (local, remote) in enumerate(files, 1):
                content = Path(local).read_text(encoding="utf-8")
                b64 = base64.b64encode(content.encode()).decode()
                filename = Path(local).name

                print(f"  [{i}/{len(files)}] {filename}", end=" ")
                result = await send_command(f"echo '{b64}' | base64 -d > {remote} && echo OK")

                if result.get('result', {}).get('success', False):
                    print("✓")
                    success_count += 1
                else:
                    print("✗")
                    print(f"      Erreur: {result.get('result', {}).get('error', 'unknown')}")

            print(f"\n=== DEPLOIEMENT TERMINE: {success_count}/{len(files)} fichiers ===")

            if success_count == len(files):
                print("\nProchaines etapes :")
                print("  1. Redemarrez Home Assistant")
                print("  2. Ajoutez l'integration RTL-SDR")
                print("  3. Ajoutez la ressource Lovelace: /local/rtl_dsr/card.js")
                print("  4. Ajoutez une carte: type: custom:sdr-plus-plus-card")
                return True
            else:
                print(f"\nATTENTION: {len(files) - success_count} fichiers en echec")
                return False

        elif ACTION == "verify":
            print("Verification des fichiers...")
            result = await send_command("ls -la /config/custom_components/rtl_dsr/")
            print(f"\nFichiers deployes:\n{result.get('result', result)}")
            return True

        elif ACTION == "test_dongle":
            print("Test de detection du dongle RTL-SDR...")
            result = await send_command("lsusb | grep -iE 'realtek|rtl|283[28]' || echo 'Aucun dongle'")
            print(f"\nResultat lsusb:\n{result.get('result', result)}")
            return True

        elif ACTION == "restart":
            print("Redemarrage de Home Assistant...")
            msg = {
                "id": msg_id,
                "type": "call_service",
                "domain": "homeassistant",
                "service": "restart"
            }
            await websocket.send(json.dumps(msg))
            msg_id += 1
            response = json.loads(await websocket.recv())
            print(f"Redemarrage: {response.get('result', response)}")
            return True

if __name__ == "__main__":
    success = asyncio.run(deploy())
    sys.exit(0 if success else 1)
