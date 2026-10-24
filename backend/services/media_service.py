import asyncio
import hashlib
import logging
import threading
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("streamdeck.media")

# Cache em memória para os bytes brutos da capa de álbum atual
_current_art_bytes: Optional[bytes] = None
_current_art_hash: Optional[str] = None
_current_art_mime: str = "image/jpeg"
_art_lock = threading.Lock()

def get_image_mime_type(data: bytes) -> str:
    """Detecta o MIME type a partir dos magic bytes da imagem."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    elif data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
        return "image/gif"
    elif data.startswith(b"RIFF") and len(data) > 12 and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"

def set_current_art(data: Optional[bytes]) -> Tuple[Optional[str], bool]:
    """
    Armazena os bytes brutos da capa no cache em memória e calcula hash MD5 e MIME type.
    Retorna (hash_md5, has_thumbnail).
    """
    global _current_art_bytes, _current_art_hash, _current_art_mime
    with _art_lock:
        if not data:
            _current_art_bytes = None
            _current_art_hash = None
            _current_art_mime = "image/jpeg"
            return None, False

        # Se idêntico ao cache atual, evita recalcular MD5
        if _current_art_bytes is not None and _current_art_bytes == data:
            return _current_art_hash, True

        mime = get_image_mime_type(data)
        art_hash = hashlib.md5(data).hexdigest()
        _current_art_bytes = data
        _current_art_hash = art_hash
        _current_art_mime = mime
        return art_hash, True

def get_current_art() -> Tuple[Optional[bytes], Optional[str], str]:
    """
    Retorna uma tupla (bytes, hash_md5, mime_type) da capa atual em memória.
    """
    with _art_lock:
        return _current_art_bytes, _current_art_hash, _current_art_mime

def clear_media_art() -> None:
    """Limpa o cache de capa de mídia em memória."""
    set_current_art(None)


try:
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus
    from winrt.windows.storage.streams import Buffer, DataReader
except ImportError:
    MediaManager = None
    PlaybackStatus = None
    Buffer = None
    DataReader = None

# Thread dedicada para leitura de mídia via winrt (evita conflito de contexto COM)
_media_thread_loop: asyncio.AbstractEventLoop | None = None
_media_thread_ready = threading.Event()

def _media_thread_func():
    """Thread dedicada que mantém seu próprio event loop para chamadas winrt."""
    global _media_thread_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _media_thread_loop = loop
    _media_thread_ready.set()
    loop.run_forever()

def start_media_thread():
    global _media_thread_ready
    if not _media_thread_ready.is_set():
        t = threading.Thread(target=_media_thread_func, daemon=True, name="winrt-media-thread")
        t.start()
        _media_thread_ready.wait(timeout=5)

async def fetch_media_info() -> Dict[str, Any]:
    """Submete a coroutine de leitura de mídia ao loop da thread dedicada."""
    result = {"title": "", "artist": "", "source_app": "", "is_playing": False, "raw_thumbnail": None}
    
    if not _media_thread_loop or not MediaManager:
        return result

    async def _do():
        try:
            mgr = await MediaManager.request_async()
            session = None
            
            # Prioridade 1: sessão com status PLAYING
            all_sessions = mgr.get_sessions()
            for s in all_sessions:
                try:
                    pb = s.get_playback_info()
                    if pb and pb.playback_status == PlaybackStatus.PLAYING:
                        session = s
                        break
                except Exception as e:
                    logger.debug("WinRT media property extraction failure: %s", e)

            # Prioridade 2: sessão atual do Windows
            if not session:
                session = mgr.get_current_session()

            if not session:
                return result

            # Título e Artista
            try:
                info = await asyncio.wait_for(session.try_get_media_properties_async(), timeout=3.0)
                if info:
                    result["title"] = info.title or ""
                    result["artist"] = info.artist or ""
                    # Thumbnail
                    if info.thumbnail and Buffer and DataReader:
                        try:
                            stream = await asyncio.wait_for(info.thumbnail.open_read_async(), timeout=3.0)
                            buf = Buffer(stream.size)
                            await asyncio.wait_for(stream.read_async(buf, stream.size, 0), timeout=3.0)
                            reader = DataReader.from_buffer(buf)
                            b = bytearray(stream.size)
                            reader.read_bytes(b)
                            result["raw_thumbnail"] = bytes(b)
                        except Exception as e:
                            logger.debug("WinRT media property extraction failure: %s", e)
            except Exception as e:
                logger.debug("WinRT media property extraction failure: %s", e)

            # Source App
            try:
                result["source_app"] = session.source_app_user_model_id or ""
            except Exception as e:
                logger.debug("WinRT media property extraction failure: %s", e)

            # Playback status
            if PlaybackStatus:
                try:
                    pb = session.get_playback_info()
                    if pb:
                        result["is_playing"] = (pb.playback_status == PlaybackStatus.PLAYING)
                except Exception as e:
                    logger.debug("WinRT media property extraction failure: %s", e)

        except Exception as e:
            logger.debug(f"Erro ao buscar dados de mídia: {e}")

        return result

    future = asyncio.run_coroutine_threadsafe(_do(), _media_thread_loop)
    try:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: future.result(timeout=8))
    except Exception as e:
        logger.debug(f"Timeout/erro na leitura de mídia: {e}")
        return result

async def control_media_action(action: str) -> bool:
    """
    Controla a reprodução de mídia diretamente via WinRT API na sessão ativa.
    Ações suportadas: 'play_pause', 'next', 'prev' / 'previous', ou sys_media_*.
    Retorna True se o comando foi aceito pelo player, False caso contrário.
    """
    if not _media_thread_loop or not MediaManager:
        return False

    async def _do():
        try:
            mgr = await MediaManager.request_async()
            session = None
            
            # Prioridade 1: sessão tocando no momento
            all_sessions = mgr.get_sessions()
            for s in all_sessions:
                try:
                    pb = s.get_playback_info()
                    if pb and PlaybackStatus and pb.playback_status == PlaybackStatus.PLAYING:
                        session = s
                        break
                except Exception as e:
                    logger.debug("WinRT media property extraction failure: %s", e)

            # Prioridade 2: sessão atual do Windows
            if not session:
                session = mgr.get_current_session()

            if not session:
                return False

            act = action.lower()
            if act in ("play_pause", "sys_media_playpause"):
                return await asyncio.wait_for(session.try_toggle_play_pause_async(), timeout=2.0)
            elif act in ("next", "sys_media_next"):
                return await asyncio.wait_for(session.try_skip_next_async(), timeout=2.0)
            elif act in ("prev", "previous", "sys_media_prev"):
                return await asyncio.wait_for(session.try_skip_previous_async(), timeout=2.0)

            return False
        except Exception as e:
            logger.debug(f"Falha ao executar controle WinRT '{action}': {e}")
            return False

    future = asyncio.run_coroutine_threadsafe(_do(), _media_thread_loop)
    try:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: future.result(timeout=4))
    except Exception as e:
        logger.debug(f"Timeout no controle de mídia WinRT: {e}")
        return False

def control_media_action_sync(action: str) -> bool:
    """Versão síncrona de controle de mídia com timeout seguro."""
    if not _media_thread_loop or not MediaManager:
        return False
    try:
        import concurrent.futures
        coro = control_media_action(action)
        future = asyncio.run_coroutine_threadsafe(coro, _media_thread_loop)
        return future.result(timeout=3.0)
    except Exception as e:
        logger.debug(f"Erro no controle síncrono de mídia: {e}")
        return False

