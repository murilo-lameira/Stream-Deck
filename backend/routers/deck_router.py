import os
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Header, HTTPException, Depends
from pydantic import ValidationError

from managers.connection_manager import manager
from apps_config import APPS_MAP, launch_app_async
from audio_service import get_volume_state, set_volume_level, toggle_mute, toggle_mic_mute
from services.system_service import get_running_app_keys
from services.catalog_service import load_catalog, save_catalog
from services.macro_service import load_macros, execute_macro, dispatch_webhook
from schemas.deck_schemas import AuthPayload, DeckActionPayload, TriggerPayload

logger = logging.getLogger("streamdeck.router")
router = APIRouter()

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "mi9_deck_secret_2026")

def verify_bearer_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verifica autenticação via Bearer token no cabeçalho Authorization."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabeçalho Authorization ausente."
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or parts[1] != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer inválido ou não autorizado."
        )
    return True

@router.get("/api/v1/deck/catalog")
async def get_deck_catalog():
    """Retorna o catálogo dinâmico de páginas e botões do Stream Deck."""
    return load_catalog()

@router.put("/api/v1/deck/catalog")
async def update_deck_catalog(data: dict):
    """Atualiza o catálogo de botões e faz broadcast em tempo real para os dispositivos conectados."""
    if not isinstance(data, dict) or "pages" not in data:
        return {"status": "error", "message": "Estrutura de catálogo inválida. Campo 'pages' é obrigatório."}

    success = save_catalog(data)
    if success:
        await manager.broadcast({
            "type": "catalog_updated",
            "catalog": data
        })
        return {"status": "success", "catalog": data}
    return {"status": "error", "message": "Falha ao persistir catálogo."}

@router.get("/api/v1/deck/macros")
async def get_macros():
    """Retorna o catálogo de macros disponíveis no backend."""
    return load_macros()

@router.post("/api/trigger")
async def trigger_external_action(payload: TriggerPayload, authorized: bool = Depends(verify_bearer_token)):
    """
    Endpoint REST para gatilhos remotos (Alexa, n8n, automações externas).
    Protegido por Bearer Token.
    """
    action = payload.action.lower()
    logger.info(f"Gatilho externo REST recebido: action={action}, payload={payload.model_dump()}")

    if action == "open" and payload.app:
        success = await launch_app_async(payload.app)
        running_apps = await get_running_app_keys()
        await manager.broadcast({"type": "running_apps_update", "running_apps": running_apps})
        return {"status": "success" if success else "error", "action": "open", "app": payload.app}

    elif action == "set_volume":
        lvl = payload.level if payload.level is not None else 50
        new_lvl, is_muted = set_volume_level(lvl)
        await manager.broadcast({"type": "volume_state", "level": new_lvl, "muted": is_muted})
        return {"status": "success", "action": "set_volume", "level": new_lvl, "muted": is_muted}

    elif action == "toggle_mute":
        new_lvl, is_muted = toggle_mute()
        await manager.broadcast({"type": "volume_state", "level": new_lvl, "muted": is_muted})
        return {"status": "success", "action": "toggle_mute", "level": new_lvl, "muted": is_muted}

    elif action == "toggle_mic":
        is_muted = toggle_mic_mute()
        return {"status": "success", "action": "toggle_mic", "mic_muted": is_muted}

    elif action == "run_macro" and payload.macro:
        result = await execute_macro(payload.macro)
        return result

    elif action == "call_webhook" and payload.url:
        success = await dispatch_webhook(payload.url, payload.payload)
        return {"status": "success" if success else "error", "action": "call_webhook", "url": payload.url}

    return {"status": "error", "message": f"Ação '{action}' desconhecida ou parâmetros insuficientes."}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "desconhecido"
    logger.info(f"Nova tentativa de conexao WebSocket recebida de {client_ip}")

    # 1. Handshake de Seguranca Inicial com Pydantic
    try:
        raw_auth = await websocket.receive_json()
        auth_data = AuthPayload.model_validate(raw_auth)

        if auth_data.auth_token != AUTH_TOKEN:
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
        catalog = load_catalog()

        await websocket.send_json({
            "type": "auth_success",
            "message": "Autenticado com sucesso no Stream Deck.",
            "available_apps": list(APPS_MAP.keys()),
            "running_apps": running_apps,
            "catalog": catalog,
            "volume": {
                "level": vol_level,
                "muted": vol_muted
            }
        })

    except ValidationError as ve:
        logger.warning(f"Formato de autenticacao invalido de {client_ip}: {ve}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Payload de autenticacao malformado.")
        return
    except WebSocketDisconnect:
        logger.info(f"Cliente {client_ip} desconectou antes do handshake.")
        return
    except Exception as e:
        logger.error(f"Erro durante o handshake de {client_ip}: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Erro no handshake.")
        return

    # 2. Loop de Processamento de Comandos Validados
    try:
        while True:
            raw_data = await websocket.receive_json()

            try:
                command = DeckActionPayload.model_validate(raw_data)
            except ValidationError as ve:
                logger.warning(f"Comando malformado recebido de {client_ip}: {ve}")
                await websocket.send_json({
                    "type": "action_result",
                    "status": "error",
                    "message": "Comando invalido ou campos ausentes."
                })
                continue

            action = command.action
            app_name = command.app

            logger.info(f"Comando recebido de {client_ip}: action={action}, app={app_name}")

            if action == "open" and app_name:
                success = await launch_app_async(app_name)
                if success:
                    await websocket.send_json({
                        "type": "action_result",
                        "status": "success",
                        "app": app_name,
                        "message": f"Aplicativo '{app_name}' disparado com sucesso."
                    })
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
                level = command.level if command.level is not None else 50
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
            elif action == "run_macro" and command.macro:
                res = await execute_macro(command.macro)
                await websocket.send_json({
                    "type": "action_result",
                    "status": res.get("status", "error"),
                    "macro": command.macro,
                    "message": f"Macro '{command.macro}' executada."
                })
            elif action == "call_webhook" and command.url:
                res = await dispatch_webhook(command.url)
                await websocket.send_json({
                    "type": "action_result",
                    "status": "success" if res else "error",
                    "message": f"Webhook disparado: {command.url}"
                })
            elif action == "get_catalog":
                await websocket.send_json({
                    "type": "catalog_updated",
                    "catalog": load_catalog()
                })
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                logger.warning(f"Acao desconhecida recebida: {action}")
                await websocket.send_json({
                    "type": "action_result",
                    "status": "error",
                    "message": f"Acao '{action}' nao suportada."
                })

    except WebSocketDisconnect:
        logger.info(f"Cliente {client_ip} desconectado.")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Erro na conexao com {client_ip}: {e}", exc_info=True)
        manager.disconnect(websocket)
