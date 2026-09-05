import os
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from managers.connection_manager import manager
from apps_config import APPS_MAP, launch_app_async
from audio_service import get_volume_state, set_volume_level, toggle_mute
from services.system_service import get_running_app_keys

logger = logging.getLogger("streamdeck.router")
router = APIRouter()

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "mi9_deck_secret_2026")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "desconhecido"
    logger.info(f"Nova tentativa de conexao WebSocket recebida de {client_ip}")

    # 1. Handshake de Seguranca Inicial
    try:
        auth_payload = await websocket.receive_json()
        token_recebido = auth_payload.get("auth_token")

        if token_recebido != AUTH_TOKEN:
            logger.warning(f"Falha de autenticacao de {client_ip}. Fechando conexao (1008).")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Token de autenticacao invalido ou ausente."
            )
            return

        logger.info(f"Cliente {client_ip} autenticado com sucesso!")
        await manager.connect(websocket)

        vol_level, vol_muted = get_volume_state()
        running_apps = await get_running_app_keys()

        await websocket.send_json({
            "type": "auth_success",
            "message": "Autenticado com sucesso no Stream Deck.",
            "available_apps": list(APPS_MAP.keys()),
            "running_apps": running_apps,
            "volume": {
                "level": vol_level,
                "muted": vol_muted
            }
        })

    except WebSocketDisconnect:
        logger.info(f"Cliente {client_ip} desconectou antes do handshake.")
        return
    except Exception as e:
        logger.error(f"Erro durante o handshake de {client_ip}: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Erro no handshake.")
        return

    # 2. Loop de Processamento de Comandos
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            app_name = data.get("app")

            logger.info(f"Comando recebido de {client_ip}: action={action}, payload={data}")

            if action == "open" and app_name:
                # Execucao nao-bloqueante em thread dedicada
                success = await launch_app_async(app_name)
                if success:
                    await websocket.send_json({
                        "type": "action_result",
                        "status": "success",
                        "app": app_name,
                        "message": f"Aplicativo '{app_name}' disparado com sucesso."
                    })
                    # Atualiza o status dos aplicativos rodando logo apos abrir
                    running_apps = await get_running_app_keys()
                    await manager.broadcast({
                        "type": "running_apps_update",
                        "running_apps": running_apps
                    })
                else:
                    await websocket.send_json({
                        "type": "action_result",
                        "status": "error",
                        "app": app_name,
                        "message": f"Falha ao disparar aplicativo '{app_name}'. Verifique o mapeamento."
                    })
            elif action == "set_volume":
                level = data.get("level", 50)
                new_lvl, is_muted = set_volume_level(level)
                await manager.broadcast({
                    "type": "volume_state",
                    "level": new_lvl,
                    "muted": is_muted
                })
            elif action == "toggle_mute":
                new_lvl, is_muted = toggle_mute()
                await manager.broadcast({
                    "type": "volume_state",
                    "level": new_lvl,
                    "muted": is_muted
                })
            elif action == "get_volume":
                lvl, is_muted = get_volume_state()
                await websocket.send_json({
                    "type": "volume_state",
                    "level": lvl,
                    "muted": is_muted
                })
            elif action == "ping":
                # Heartbeat de alta velocidade
                await websocket.send_json({"type": "pong"})
            else:
                logger.warning(f"Acao desconhecida recebida: {data}")
                await websocket.send_json({
                    "type": "action_result",
                    "status": "error",
                    "message": "Acao nao suportada."
                })

    except WebSocketDisconnect:
        logger.info(f"Cliente {client_ip} desconectado.")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Erro na conexao com {client_ip}: {e}", exc_info=True)
        manager.disconnect(websocket)
