#!/usr/bin/env python3
"""
WebSocket API script to execute shell commands on Home Assistant.
"""
import asyncio
import websockets
import json
import sys

TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""
COMMAND = sys.argv[2] if len(sys.argv) > 2 else "ls -la /config/"

async def execute_command():
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

        # Execute command via hassio.addon_stdin
        msg = {
            "id": 1,
            "type": "call_service",
            "domain": "hassio",
            "service": "addon_stdin",
            "service_data": {
                "addon": "core_ssh",
                "input": {"command": COMMAND}
            }
        }
        await websocket.send(json.dumps(msg))
        response = json.loads(await websocket.recv())
        print(f"Resultat: {json.dumps(response, indent=2)}")
        return True

if __name__ == "__main__":
    success = asyncio.run(execute_command())
    sys.exit(0 if success else 1)
