import os
import logging
import asyncio
import socket
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
                await connection.send_json(message)
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

async def media_monitor_task():
    """Tarefa em background que lê os metadados da música atual e o status do microfone."""
    last_title = None
    last_artist = None
    last_source_app = None
    last_is_playing = None
    last_mic_mute = None
    last_conn_count = 0
    
    while True:
        try:
            current_conns = len(manager.active_connections)
            
            # 1. Checa música
            title = ""
            artist = ""
            source_app = ""
            is_playing = False
            
            if MediaManager:
                sessions = await MediaManager.request_async()
                if sessions:
                    current_session = None
                    try:
                        all_sessions = sessions.get_sessions()
                        
                        # 1. Tenta achar uma sessão que esteja tocando
                        for s in all_sessions:
                            pb = s.get_playback_info()
                            if pb and pb.playback_status == PlaybackStatus.PLAYING:
                                current_session = s
                                break
                                
                        # 2. Se nenhuma estiver tocando, pega a primeira que tem um título válido
                        if not current_session:
                            for s in all_sessions:
                                temp_info = await s.try_get_media_properties_async()
                                if temp_info and temp_info.title:
                                    current_session = s
                                    break
                    except Exception:
                        pass
                        
                    # 3. Fallback para o padrão do Windows
                    if not current_session:
                        current_session = sessions.get_current_session()
                        
                    if current_session:
                        info = await current_session.try_get_media_properties_async()
                        if info:
                            title = info.title or ""
                            artist = info.artist or ""
                    
                    try:
                        source_app = current_session.source_app_user_model_id or ""
                    except Exception:
                        source_app = ""
                    
                    if PlaybackStatus:
                        try:
                            playback_info = current_session.get_playback_info()
                            if playback_info:
                                is_playing = (playback_info.playback_status == PlaybackStatus.PLAYING)
                        except Exception:
                            is_playing = False
            
            # 2. Checa Mic
            mic_muted = get_mic_mute_state()
            
            # 3. Faz Broadcast se algo mudou ou se há nova conexão
            if (title != last_title or artist != last_artist or 
                source_app != last_source_app or is_playing != last_is_playing or
                mic_muted != last_mic_mute or
                current_conns > last_conn_count):
                
                last_title = title
                last_artist = artist
                last_source_app = source_app
                last_is_playing = is_playing
                last_mic_mute = mic_muted
                last_conn_count = current_conns
                
                if current_conns > 0:
                    await manager.broadcast({
                        "type": "system_status",
                        "now_playing": {
                            "title": title,
                            "artist": artist,
                            "source_app": source_app,
                            "is_playing": is_playing
                        },
                        "mic_muted": mic_muted
                    })
                    
        except Exception as e:
            logger.error(f"Erro no monitor de mídia: {e}")
            
        await asyncio.sleep(1) # Checa a cada 1 segundo

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
