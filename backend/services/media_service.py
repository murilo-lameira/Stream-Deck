import asyncio
import base64
import logging
import threading
from typing import Dict, Any

logger = logging.getLogger("streamdeck.media")

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
    result = {"title": "", "artist": "", "source_app": "", "is_playing": False, "thumbnail": ""}
    
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
                except Exception:
                    pass

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
                            result["thumbnail"] = base64.b64encode(b).decode('utf-8')
                        except Exception:
                            pass
            except Exception:
                pass

            # Source App
            try:
                result["source_app"] = session.source_app_user_model_id or ""
            except Exception:
                pass

            # Playback status
            if PlaybackStatus:
                try:
                    pb = session.get_playback_info()
                    if pb:
                        result["is_playing"] = (pb.playback_status == PlaybackStatus.PLAYING)
                except Exception:
                    pass

        except Exception as e:
            logger.debug(f"Erro ao buscar dados de mídia: {e}")

        return result

    future = asyncio.run_coroutine_threadsafe(_do(), _media_thread_loop)
    try:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: future.result(timeout=8))
    except Exception as e:
        logger.debug(f"Timeout/erro na leitura de mídia: {e}")
        return result
