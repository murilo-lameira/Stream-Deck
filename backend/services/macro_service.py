import os
import json
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional

from apps_config import launch_app_async
from audio_service import set_volume_level, toggle_mute, set_mic_mute_state
from managers.connection_manager import manager

logger = logging.getLogger("streamdeck.macro")

MACROS_PATH = os.path.join(os.path.dirname(__file__), "..", "macros_config.json")

def load_macros() -> Dict[str, Any]:
    """Carrega as macros configuradas no macros_config.json."""
    if not os.path.isfile(MACROS_PATH):
        return {}
    try:
        with open(MACROS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar macros_config.json: {e}")
        return {}

async def execute_macro(macro_name: str) -> Dict[str, Any]:
    """Executa uma macro sequencialmente de forma assíncrona."""
    macros = load_macros()
    if macro_name not in macros:
        return {"status": "error", "message": f"Macro '{macro_name}' não encontrada."}

    macro = macros[macro_name]
    steps = macro.get("steps", [])
    logger.info(f"Iniciando execução da macro '{macro_name}' ({len(steps)} passos).")

    results = []
    for idx, step in enumerate(steps):
        action = step.get("action")
        try:
            if action == "open":
                app = step.get("app")
                success = await launch_app_async(app)
                results.append({"step": idx, "action": action, "app": app, "success": success})
            elif action == "set_volume":
                level = step.get("level", 50)
                new_lvl, is_muted = set_volume_level(level)
                await manager.broadcast({
                    "type": "volume_state",
                    "level": new_lvl,
                    "muted": is_muted
                })
                results.append({"step": idx, "action": action, "level": new_lvl})
            elif action == "set_mic_mute":
                muted = step.get("muted", True)
                res = await asyncio.to_thread(set_mic_mute_state, muted)
                results.append({"step": idx, "action": action, "muted": res})
            elif action == "toggle_mute":
                new_lvl, is_muted = toggle_mute()
                await manager.broadcast({
                    "type": "volume_state",
                    "level": new_lvl,
                    "muted": is_muted
                })
                results.append({"step": idx, "action": action, "muted": is_muted})
            elif action == "call_webhook":
                url = step.get("url")
                payload = step.get("payload", {})
                success = await dispatch_webhook(url, payload)
                results.append({"step": idx, "action": action, "success": success})

            # Pequeno intervalo seguro entre passos da macro
            await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Erro no passo {idx} da macro '{macro_name}': {e}", exc_info=True)
            results.append({"step": idx, "action": action, "error": str(e)})

    return {"status": "success", "macro": macro_name, "results": results}

async def dispatch_webhook(url: str, payload: Optional[dict] = None) -> bool:
    """Despacha um webhook HTTP POST assíncrono para o n8n ou outro serviço de automação."""
    if not url:
        return False
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.post(url, json=payload or {})
            return resp.status_code in (200, 201, 202, 204)
    except Exception as e:
        logger.error(f"Falha ao disparar webhook para {url}: {e}")
        return False

