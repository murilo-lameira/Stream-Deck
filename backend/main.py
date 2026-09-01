import os
import logging
import asyncio
import socket
import ctypes
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apps_config import APPS_MAP, launch_app
from audio_service import get_volume_state, set_volume_level, toggle_mute, get_mic_mute_state
from zeroconf import ServiceInfo, Zeroconf

import base64
try:
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus
    from winrt.windows.storage.streams import Buffer
except ImportError:
    MediaManager = None
    PlaybackStatus = None
    Buffer = None

# Carrega variaveis de ambiente
load_dotenv()

# Muda o nome da janela do CMD para ficar mais amigável no Gerenciador de Tarefas
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW("Stream Deck Backend Server")

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "mi9_deck_secret_2026")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Configuracao de Logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("streamdeck.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("streamdeck.server")

# Gerenciador de WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await asyncio.wait_for(connection.send_json(message), timeout=1.0)
            except Exception:
                pass

manager = ConnectionManager()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não importa se o IP é acessível, só precisa gerar tráfego UDP
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

import threading

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

def _start_media_thread():
    t = threading.Thread(target=_media_thread_func, daemon=True, name="winrt-media-thread")
    t.start()
    _media_thread_ready.wait(timeout=5)

async def _fetch_media_in_dedicated_thread() -> dict:
    """Submete a coroutine de leitura de mídia ao loop da thread dedicada."""
    result = {"title": "", "artist": "", "source_app": "", "is_playing": False, "thumbnail": ""}
    
    if not _media_thread_loop or not MediaManager:
        return result
    
    async def _do():
        try:
            mgr = await MediaManager.request_async()
            
            # Prioridade 1: sessão com status PLAYING
            session = None
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
            
            # Título e artista
            try:
                info = await asyncio.wait_for(session.try_get_media_properties_async(), timeout=3.0)
                if info:
                    result["title"] = info.title or ""
                    result["artist"] = info.artist or ""
                    # Thumbnail
                    if info.thumbnail and Buffer:
                        try:
                            stream = await asyncio.wait_for(info.thumbnail.open_read_async(), timeout=3.0)
                            buf = Buffer(stream.size)
                            await asyncio.wait_for(stream.read_async(buf, stream.size, 0), timeout=3.0)
                            from winrt.windows.storage.streams import DataReader
                            reader = DataReader.from_buffer(buf)
                            b = bytearray(stream.size)
                            reader.read_bytes(b)
                            result["thumbnail"] = base64.b64encode(b).decode('utf-8')
                        except Exception:
                            pass
            except Exception:
                pass
            
            # Source app
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
            logger.debug(f"Erro ao buscar mídia: {e}")
        
        return result
    
    # Envia a coroutine para o loop da thread dedicada e aguarda resultado
    future = asyncio.run_coroutine_threadsafe(_do(), _media_thread_loop)
    try:
        return await asyncio.get_event_loop().run_in_executor(None, lambda: future.result(timeout=8))
    except Exception as e:
        logger.debug(f"Timeout/erro na leitura de mídia: {e}")
        return result


async def media_monitor_task():
    """Tarefa em background que lê os metadados da música atual e o status do microfone."""
    _start_media_thread()
    
    last_title = None
    last_artist = None
    last_source_app = None
    last_is_playing = None
    last_mic_mute = None
    last_thumbnail = None
    last_conn_count = 0
    
    while True:
        logger.info("Media monitor loop tick")
        try:
            current_conns = len(manager.active_connections)
            
            media_info = await _fetch_media_in_dedicated_thread()
            
            title = media_info.get("title", "")
            artist = media_info.get("artist", "")
            source_app = media_info.get("source_app", "")
            is_playing = media_info.get("is_playing", False)
            thumbnail = media_info.get("thumbnail", "")
            
            mic_muted = await asyncio.to_thread(get_mic_mute_state)
            
            # Broadcast se algo mudou ou se há nova conexão
            if (title != last_title or artist != last_artist or 
                source_app != last_source_app or is_playing != last_is_playing or
                mic_muted != last_mic_mute or thumbnail != last_thumbnail or
                current_conns > last_conn_count):
                
                last_title = title
                last_artist = artist
                last_source_app = source_app
                last_is_playing = is_playing
                last_mic_mute = mic_muted
                last_thumbnail = thumbnail
                last_conn_count = current_conns
                
                if current_conns > 0:
                    logger.info(f"Broadcasting: title='{title}', artist='{artist}', is_playing={is_playing}")
                    await manager.broadcast({
                        "type": "system_status",
                        "now_playing": {
                            "title": title,
                            "artist": artist,
                            "source_app": source_app,
                            "is_playing": is_playing,
                            "thumbnail": thumbnail
                        },
                        "mic_muted": mic_muted
                    })
                    
        except Exception as e:
            logger.error(f"Erro no monitor de mídia: {e}")
            
        logger.info("Loop tick end")
        await asyncio.sleep(1)

zeroconf_instance = None
zeroconf_info = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global zeroconf_instance, zeroconf_info
    ip = get_local_ip()
    
    logger.info(f"Stream Deck Backend inicializado na porta {PORT}")
    logger.info(f"Token configurado: {'*' * (len(AUTH_TOKEN) - 4) + AUTH_TOKEN[-4:] if len(AUTH_TOKEN) > 4 else '****'}")
    logger.info(f"Aplicativos disponiveis: {list(APPS_MAP.keys())}")
    
    # Iniciar mDNS
    try:
        from zeroconf.asyncio import AsyncZeroconf
        zeroconf_instance = AsyncZeroconf()
        zeroconf_info = ServiceInfo(
            "_http._tcp.local.",
            "StreamDeck._http._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=PORT,
            server="streamdeck.local.",
        )
        await zeroconf_instance.async_register_service(zeroconf_info)
        logger.info(f"mDNS Service registrado! Celular pode acessar: http://streamdeck.local:{PORT}")
    except Exception as e:
        logger.error(f"Erro ao iniciar mDNS ZeroConf: {e}", exc_info=True)

    # Iniciar Task de Mídia
    task = asyncio.create_task(media_monitor_task())
    
    yield
    
    task.cancel()
    if zeroconf_instance and zeroconf_info:
        await zeroconf_instance.async_unregister_service(zeroconf_info)
        await zeroconf_instance.async_close()
    logger.info("Stream Deck Backend finalizado.")

app = FastAPI(
    title="Stream Deck Mobile - Windows Launcher Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_ip = websocket.client.host if websocket.client else "desconhecido"
    logger.info(f"Nova tentativa de conexao WebSocket recebida de {client_ip}")

    # ==========================================
    # 1. Handshake de Seguranca Inicial
    # ==========================================
    try:
        auth_payload = await websocket.receive_json()
        token_recebido = auth_payload.get("auth_token")

        if token_recebido != AUTH_TOKEN:
            logger.warning(f"Falha de autenticacao de {client_ip}. Fechando conexao com codigo 1008.")
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Token de autenticacao invalido ou ausente."
            )
            return

        # Autenticado com sucesso
        logger.info(f"Cliente {client_ip} autenticado com sucesso!")
        await manager.connect(websocket)
        
        vol_level, vol_muted = get_volume_state()
        await websocket.send_json({
            "type": "auth_success",
            "message": "Autenticado com sucesso no Stream Deck.",
            "available_apps": list(APPS_MAP.keys()),
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

    # ==========================================
    # 2. Loop de Processamento de Comandos
    # ==========================================
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            app_name = data.get("app")

            logger.info(f"Comando recebido de {client_ip}: action={action}, payload={data}")

            if action == "open" and app_name:
                success = launch_app(app_name)
                if success:
                    await websocket.send_json({
                        "type": "action_result",
                        "status": "success",
                        "app": app_name,
                        "message": f"Aplicativo '{app_name}' disparado com sucesso."
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

# Servir Frontend Estatico (Vite Build)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    logger.warning("Pasta frontend/dist nao encontrada. O Frontend estatico nao sera servido.")
