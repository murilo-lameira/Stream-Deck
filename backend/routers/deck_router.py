import os
import asyncio
import hmac
import logging
from typing import Optional, Dict, Any, Callable, Coroutine
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Header, HTTPException, Depends, Response, Request
from pydantic import ValidationError

from managers.connection_manager import manager
from apps_config import APPS_MAP, launch_app_async
from audio_service import get_volume_state, set_volume_level, toggle_mute, toggle_mic_mute
from services.system_service import get_running_app_keys
from services.catalog_service import load_catalog, save_catalog
from services.macro_service import load_macros, execute_macro, dispatch_webhook
from services.media_service import get_current_art
from services.auth_service import get_auth_token, rotate_token, generate_pairing_url, is_valid_token
from services.network_service import get_local_ip
from schemas.deck_schemas import AuthPayload, DeckActionPayload, TriggerPayload

logger = logging.getLogger("streamdeck.router")
router = APIRouter()

# Mantém referência compatível inicializada dinamicamente
AUTH_TOKEN = get_auth_token()

def verify_bearer_token(authorization: Optional[str] = Header(None)) -> bool:
    """Verifica autenticação via Bearer token no cabeçalho Authorization."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabeçalho Authorization ausente."
        )
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not is_valid_token(parts[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer inválido ou não autorizado."
        )
    return True

@router.get("/api/v1/deck/pairing")
async def get_pairing_info(request: Request):
    """Retorna a URL e o token de pareamento para conexão de dispositivos clientes."""
    host = request.url.hostname or get_local_ip()
    port = request.url.port or int(os.getenv("PORT", 8000))
    token = get_auth_token()
    pairing_url = generate_pairing_url(host, port)
    return {
        "status": "success",
        "auth_token": token,
        "pairing_url": pairing_url,
        "host": host,
        "port": port
    }

@router.post("/api/v1/deck/pairing/rotate")
async def rotate_pairing_token(request: Request, authorized: bool = Depends(verify_bearer_token)):
    """Exige autenticação Bearer e realiza a rotação segura do token de autenticação."""
    new_token = rotate_token()
    host = request.url.hostname or get_local_ip()
    port = request.url.port or int(os.getenv("PORT", 8000))
    pairing_url = generate_pairing_url(host, port)
    return {
        "status": "success",
        "message": "Token de autenticação rotacionado com sucesso.",
        "auth_token": new_token,
        "pairing_url": pairing_url
    }

@router.get("/api/v1/deck/catalog")
async def get_deck_catalog():
    """Retorna o catálogo dinâmico de páginas e botões do Stream Deck."""
    return load_catalog()

@router.put("/api/v1/deck/catalog")
async def update_deck_catalog(data: dict, authorized: bool = Depends(verify_bearer_token)):
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

@router.get("/api/v1/deck/media/art")
async def get_media_art(
    v: Optional[str] = None,
    if_none_match: Optional[str] = Header(None)
):
    """
    Retorna a imagem binária da capa da mídia em reprodução com suporte a ETag e cache HTTP.
    Retorna 304 Not Modified quando o If-None-Match coincidir com o hash da imagem.
    """
    art_bytes, art_hash, mime_type = get_current_art()

    if not art_bytes or not art_hash:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma capa de mídia disponível no momento."
        )

    etag_header = f'"{art_hash}"'
    cache_headers = {
        "ETag": etag_header,
        "Cache-Control": "public, max-age=3600"
    }

    if if_none_match:
        client_tags = [
            tag.strip().lstrip("W/").strip('"')
            for tag in if_none_match.split(",")
        ]
        if art_hash in client_tags or "*" in client_tags:
            return Response(
                status_code=status.HTTP_304_NOT_MODIFIED,
                headers=cache_headers
            )

    return Response(
        content=art_bytes,
        media_type=mime_type,
        headers=cache_headers
    )

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
        new_lvl, is_muted = await asyncio.to_thread(set_volume_level, lvl)
        await manager.broadcast({"type": "volume_state", "level": new_lvl, "muted": is_muted})
        return {"status": "success", "action": "set_volume", "level": new_lvl, "muted": is_muted}

    elif action == "toggle_mute":
        new_lvl, is_muted = await asyncio.to_thread(toggle_mute)
        await manager.broadcast({"type": "volume_state", "level": new_lvl, "muted": is_muted})
        return {"status": "success", "action": "toggle_mute", "level": new_lvl, "muted": is_muted}

    elif action == "toggle_mic":
        is_muted = await asyncio.to_thread(toggle_mic_mute)
        return {"status": "success", "action": "toggle_mic", "mic_muted": is_muted}

    elif action == "run_macro" and payload.macro:
        result = await execute_macro(payload.macro)
        return result

    elif action == "call_webhook" and payload.url:
        success = await dispatch_webhook(payload.url, payload.payload)
        return {"status": "success" if success else "error", "action": "call_webhook", "url": payload.url}

    return {"status": "error", "message": f"Ação '{action}' desconhecida ou parâmetros insuficientes."}

# --- WebSocket Command Handlers (Command Handler Pattern - ARCH-03) ---

async def handle_open_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    app_name = command.app
    if app_name:
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
    else:
        await websocket.send_json({
            "type": "action_result",
            "status": "error",
            "message": "Identificador do aplicativo não especificado."
        })

async def handle_set_volume_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    level = command.level if command.level is not None else 50
    new_lvl, is_muted = await asyncio.to_thread(set_volume_level, level)
    await manager.broadcast({
        "type": "volume_state",
        "level": new_lvl,
        "muted": is_muted
    })

async def handle_toggle_mute_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    new_lvl, is_muted = await asyncio.to_thread(toggle_mute)
    await manager.broadcast({
        "type": "volume_state",
        "level": new_lvl,
        "muted": is_muted
    })

async def handle_toggle_mic_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    is_muted = await asyncio.to_thread(toggle_mic_mute)
    await websocket.send_json({
        "type": "mic_state",
        "mic_muted": is_muted
    })

async def handle_get_volume_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    lvl, is_muted = await asyncio.to_thread(get_volume_state)
    await websocket.send_json({
        "type": "volume_state",
        "level": lvl,
        "muted": is_muted
    })

async def handle_run_macro_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    if command.macro:
        res = await execute_macro(command.macro)
        await websocket.send_json({
            "type": "action_result",
            "status": res.get("status", "error"),
            "macro": command.macro,
            "message": f"Macro '{command.macro}' executada."
        })
    else:
        await websocket.send_json({
            "type": "action_result",
            "status": "error",
            "message": "Nome da macro não especificado."
        })

async def handle_call_webhook_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    if command.url:
        res = await dispatch_webhook(command.url)
        await websocket.send_json({
            "type": "action_result",
            "status": "success" if res else "error",
            "message": f"Webhook disparado: {command.url}"
        })
    else:
        await websocket.send_json({
            "type": "action_result",
            "status": "error",
            "message": "URL do webhook não especificada."
        })

async def handle_get_catalog_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    await websocket.send_json({
        "type": "catalog_updated",
        "catalog": load_catalog()
    })

async def handle_ping_action(websocket: WebSocket, command: DeckActionPayload) -> None:
    await websocket.send_json({"type": "pong"})

ACTION_HANDLERS: Dict[str, Callable[[WebSocket, DeckActionPayload], Coroutine[Any, Any, None]]] = {
    "open": handle_open_action,
    "set_volume": handle_set_volume_action,
    "toggle_mute": handle_toggle_mute_action,
    "toggle_mic": handle_toggle_mic_action,
    "get_volume": handle_get_volume_action,
    "run_macro": handle_run_macro_action,
    "call_webhook": handle_call_webhook_action,
    "get_catalog": handle_get_catalog_action,
    "ping": handle_ping_action,
}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "desconhecido"
    logger.info(f"Nova tentativa de conexao WebSocket recebida de {client_ip}")

    # Validação de Origin contra Cross-Site WebSocket Hijacking (CSWSH)
    origin = websocket.headers.get("origin")
    if origin:
        from urllib.parse import urlparse
        import ipaddress
        parsed = urlparse(origin)
        hostname = (parsed.hostname or "").lower()

        is_allowed = False
        allowed_exact_hosts = {"127.0.0.1", "localhost", "testserver", "streamdeck.local"}
        if hostname in allowed_exact_hosts:
            is_allowed = True
        else:
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback:
                    is_allowed = True
            except ValueError:
                pass

        if not is_allowed:
            logger.warning(f"Origem WebSocket não autorizada rejeitada: {origin} de {client_ip}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Origem não autorizada.")
            return

    # 1. Handshake de Seguranca Inicial com Pydantic e Timeout Estrito (5s)
    try:
        raw_auth = await asyncio.wait_for(websocket.receive_json(), timeout=5.0)
        auth_data = AuthPayload.model_validate(raw_auth)

        if not is_valid_token(auth_data.auth_token):
            logger.warning(f"Falha de autenticacao de {client_ip}. Fechando conexao (1008).")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Token de autenticacao invalido ou ausente."
            )
            return

        logger.info(f"Cliente {client_ip} autenticado com sucesso!")
        await manager.connect(websocket)

        vol_level, vol_muted = await asyncio.to_thread(get_volume_state)
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

    except asyncio.TimeoutError:
        logger.warning(f"Timeout no handshake WebSocket de {client_ip}. Fechando conexao.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Timeout no handshake de autenticacao.")
        return
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

            handler = ACTION_HANDLERS.get(action)
            if handler:
                await handler(websocket, command)
            else:
                logger.warning(f"Acao desconhecida recebida de {client_ip}: {action}")
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
