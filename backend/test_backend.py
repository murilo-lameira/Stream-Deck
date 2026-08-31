import asyncio
import websockets
import json
import subprocess
import time
import sys

async def run_tests():
    uri = "ws://localhost:8000/ws"
    
    print("--- Teste 1: Conexao com token invalido (esperado: 1008) ---")
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"auth_token": "TOKEN_ERRADO"}))
            response = await ws.recv()
            print("FALHA: Nao deveria ter recebido:", response)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"SUCESSO: Conexao fechada com codigo {e.code} (esperado 1008)")
        assert e.code == 1008, f"Esperava 1008, veio {e.code}"

    print("\n--- Teste 2: Conexao com token valido e handshake ---")
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"auth_token": "mi9_deck_secret_2026"}))
        auth_res = await ws.recv()
        print("Resposta do servidor:", auth_res)
        auth_data = json.loads(auth_res)
        assert auth_data.get("type") == "auth_success"
        print("SUCESSO: Autenticado com sucesso!")

        print("\n--- Teste 3: Envio de comando Fire-and-Forget (calc) ---")
        await ws.send(json.dumps({"action": "open", "app": "calc"}))
        action_res = await ws.recv()
        print("Resposta do comando:", action_res)
        action_data = json.loads(action_res)
        assert action_data.get("status") == "success"
        print("SUCESSO: Comando disparado com resposta imediata!")

if __name__ == "__main__":
    asyncio.run(run_tests())
