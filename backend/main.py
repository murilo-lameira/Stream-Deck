import os
import sys
import ctypes
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from services.network_service import get_local_ip, NetworkDiscoveryService
from services.telemetry_service import system_telemetry_loop
from routers.deck_router import router as deck_router

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Carrega variáveis de ambiente
load_dotenv()

# Nome amigável na janela de console no Windows
if os.name == 'nt':
    ctypes.windll.kernel32.SetConsoleTitleW("Stream Deck Backend Server")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# Configuração de Logs com Rotação Automática (5MB por arquivo, 3 backups)
log_file_path = os.path.join(os.path.dirname(__file__), "streamdeck.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("streamdeck.server")

discovery_service = NetworkDiscoveryService(PORT)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ip = get_local_ip()
    logger.info(f"Stream Deck Backend inicializado na porta {PORT} (IP: {ip})")
    
    await discovery_service.start()
    telemetry_task = asyncio.create_task(system_telemetry_loop())

    yield

    telemetry_task.cancel()
    await discovery_service.stop()
    logger.info("Stream Deck Backend finalizado.")

app = FastAPI(
    title="Stream Deck Mobile - Windows Launcher Backend",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas do Stream Deck
app.include_router(deck_router)

@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/api/agents/orchestrate")
@app.get("/api/agents/orchestrate")
async def trigger_orchestration_endpoint():
    """Dispara a orquestração dos agentes via requisição HTTP (ideal para n8n/Alexa)."""
    from services.agent_service import orchestrate_agents
    results = await orchestrate_agents()
    return {"status": "success", "results": results}

# Servir Frontend Estático (Vite Build)
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.isdir(frontend_path):
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.isdir(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    logger.warning("Pasta frontend/dist não encontrada. O Frontend estático não será servido.")

if __name__ == "__main__":
    if "--orchestrate" in sys.argv:
        from services.agent_service import orchestrate_agents
        asyncio.run(orchestrate_agents())
    else:
        import uvicorn
        uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
