from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AuthPayload(BaseModel):
    """Payload de autenticação enviado no handshake inicial do WebSocket."""
    auth_token: str = Field(..., description="Token de segurança configurado no .env")

class DeckActionPayload(BaseModel):
    """Payload de comando enviado pelo cliente Stream Deck via WebSocket."""
    action: str = Field(..., description="Nome da ação (ex: 'open', 'set_volume', 'toggle_mute', 'run_macro', 'call_webhook', 'ping')")
    app: Optional[str] = Field(None, description="Identificador do aplicativo para a ação 'open'")
    level: Optional[int] = Field(None, ge=0, le=100, description="Nível de volume absoluto (0 a 100)")
    macro: Optional[str] = Field(None, description="Nome da macro a ser executada")
    url: Optional[str] = Field(None, description="URL do webhook a ser chamado")

class TriggerPayload(BaseModel):
    """Payload recebido no endpoint REST /api/trigger."""
    action: str = Field(..., description="Ação desejada: 'open', 'set_volume', 'toggle_mute', 'toggle_mic', 'run_macro', 'call_webhook'")
    app: Optional[str] = None
    level: Optional[int] = Field(None, ge=0, le=100)
    macro: Optional[str] = None
    url: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class VolumeState(BaseModel):
    level: int = Field(..., ge=0, le=100)
    muted: bool

class NowPlayingState(BaseModel):
    title: str = ""
    artist: str = ""
    source_app: str = ""
    is_playing: bool = False
    thumbnail: str = ""

class SystemStatusMessage(BaseModel):
    type: str = "system_status"
    now_playing: NowPlayingState
    mic_muted: bool
    running_apps: List[str]

class ActionResultMessage(BaseModel):
    type: str = "action_result"
    status: str
    app: Optional[str] = None
    message: str

