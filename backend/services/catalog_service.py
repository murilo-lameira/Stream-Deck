import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("streamdeck.catalog")

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "deck_catalog.json")

DEFAULT_CATALOG: Dict[str, Any] = {
    "version": "2.0.0",
    "pages": [
        {
            "id": "page_apps",
            "name": "Principais",
            "type": "grid",
            "items": [
                { "id": "vscode",   "name": "VS Code",    "icon": "vscode",   "color": "#007ACC" },
                { "id": "discord",  "name": "Discord",    "icon": "discord",  "color": "#5865F2" },
                { "id": "whatsapp", "name": "WhatsApp",   "icon": "whatsapp", "color": "#25D366" },
                { "id": "chrome",   "name": "Chrome",     "icon": "chrome",   "color": "#EA4335" },
                { "id": "spotify",  "name": "Spotify",    "icon": "spotify",  "color": "#1DB954" },
                { "id": "gemini",   "name": "Gemini",     "icon": "gemini",   "color": "#8E24AA" },
                { "id": "youtube",  "name": "YouTube",    "icon": "youtube",  "color": "#FF0000" },
                { "id": "obsidian", "name": "Obsidian",   "icon": "obsidian", "color": "#7c3aed" }
            ]
        },
        {
            "id": "page_media",
            "name": "Mídia & Volume",
            "type": "media",
            "items": [
                { "id": "sys_media_prev",      "name": "Anterior",    "icon": "media-prev",  "color": "#10b981" },
                { "id": "sys_media_playpause", "name": "Play/Pause",  "icon": "media-play",  "color": "#10b981" },
                { "id": "sys_media_next",      "name": "Próxima",     "icon": "media-next",  "color": "#10b981" },
                { "id": "sys_vol_mute",        "name": "Mutar",       "icon": "vol-mute",    "color": "#ef4444" },
                { "id": "sys_mic_mute",        "name": "Microfone",   "icon": "mic",         "color": "#f59e0b" },
                { "id": "shutdown_pc",         "name": "Desligar PC", "icon": "power",       "color": "#ff4444" }
            ]
        },
        {
            "id": "page_tools",
            "name": "Ferramentas & Jogos",
            "type": "grid",
            "items": [
                { "id": "obs",     "name": "OBS Studio",  "icon": "obs",               "color": "#ffffff" },
                { "id": "github",  "name": "GitHub",      "icon": "github",            "color": "#ffffff" },
                { "id": "ghub",    "name": "G HUB",       "icon": "logitech",          "color": "#00B8FC" },
                { "id": "vms",     "name": "VMS Câmeras", "icon": "vms",               "color": "#00d2ff" },
                { "id": "checkup", "name": "CheckUP",     "icon": "checkup",           "color": "#8C4FFF" },
                { "id": "lol",     "name": "League",      "icon": "league-of-legends", "color": "#D4AF37" },
                { "id": "steam",   "name": "Steam",       "icon": "steam",             "color": "#66c0f4" },
                { "id": "blitz",   "name": "Blitz",       "icon": "blitz",             "color": "#ED1F34" }
            ]
        }
    ]
}

def load_catalog() -> Dict[str, Any]:
    """Carrega o catálogo do arquivo JSON ou retorna a configuração padrão."""
    if not os.path.isfile(CATALOG_PATH):
        logger.info("Catálogo não encontrado em disco, inicializando com configuração padrão.")
        save_catalog(DEFAULT_CATALOG)
        return DEFAULT_CATALOG

    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "pages" in data and isinstance(data["pages"], list):
                return data
            logger.warning("Estrutura do catálogo inválida, usando padrão.")
            return DEFAULT_CATALOG
    except Exception as e:
        logger.error(f"Erro ao ler deck_catalog.json: {e}", exc_info=True)
        return DEFAULT_CATALOG

def save_catalog(catalog_data: Dict[str, Any]) -> bool:
    """Salva a estrutura do catálogo em disco de forma segura."""
    try:
        temp_path = f"{CATALOG_PATH}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
        
        # Substitui atomicamente
        if os.path.exists(CATALOG_PATH):
            os.replace(temp_path, CATALOG_PATH)
        else:
            os.rename(temp_path, CATALOG_PATH)
        logger.info("Catálogo atualizado com sucesso em disco.")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar deck_catalog.json: {e}", exc_info=True)
        return False

