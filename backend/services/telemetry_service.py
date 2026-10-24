import asyncio
import logging
from managers.connection_manager import manager
from services.media_service import start_media_thread, fetch_media_info, set_current_art
from services.system_service import get_running_app_keys, get_system_metrics
from audio_service import get_mic_mute_state

logger = logging.getLogger("streamdeck.telemetry")

async def system_telemetry_loop():
    """Tarefa em segundo plano que monitora mídia, microfone, processos ativos e métricas do PC."""
    start_media_thread()
    
    last_title = None
    last_artist = None
    last_source_app = None
    last_is_playing = None
    last_mic_mute = None
    last_art_hash = None
    last_running_apps = None
    last_metrics = None
    last_conn_count = 0
    ticks = 0

    while True:
        try:
            current_conns = len(manager.active_connections)
            ticks += 1

            media_info = await fetch_media_info()
            title = media_info.get("title", "")
            artist = media_info.get("artist", "")
            source_app = media_info.get("source_app", "")
            is_playing = media_info.get("is_playing", False)
            raw_thumbnail = media_info.get("raw_thumbnail")

            # Armazena os bytes brutos no media_service e obtém hash e has_thumbnail
            art_hash, has_thumbnail = set_current_art(raw_thumbnail)
            thumbnail_url = f"/api/v1/deck/media/art?v={art_hash}" if has_thumbnail and art_hash else ""

            mic_muted = await asyncio.to_thread(get_mic_mute_state)

            # Verifica aplicativos ativos e métricas a cada ~2 segundos (evita I/O excessivo)
            if ticks % 2 == 0 or last_running_apps is None:
                running_apps = await get_running_app_keys()
                current_metrics = await get_system_metrics()
            else:
                running_apps = last_running_apps
                current_metrics = last_metrics or {"cpu": 0, "ram": 0}

            # Se houve mudanca de estado ou novo cliente conectado
            if (title != last_title or artist != last_artist or
                source_app != last_source_app or is_playing != last_is_playing or
                mic_muted != last_mic_mute or art_hash != last_art_hash or
                running_apps != last_running_apps or
                current_metrics != last_metrics or
                current_conns > last_conn_count):

                last_title = title
                last_artist = artist
                last_source_app = source_app
                last_is_playing = is_playing
                last_mic_mute = mic_muted
                last_art_hash = art_hash
                last_running_apps = running_apps
                last_metrics = current_metrics
                last_conn_count = current_conns

                if current_conns > 0:
                    await manager.broadcast({
                        "type": "system_status",
                        "now_playing": {
                            "title": title,
                            "artist": artist,
                            "source_app": source_app,
                            "is_playing": is_playing,
                            "has_thumbnail": has_thumbnail,
                            "thumbnail_url": thumbnail_url
                        },
                        "mic_muted": mic_muted,
                        "running_apps": running_apps,
                        "system_metrics": current_metrics
                    })

        except Exception as e:
            logger.error(f"Erro na telemetria de sistema: {e}", exc_info=True)

        await asyncio.sleep(1)

