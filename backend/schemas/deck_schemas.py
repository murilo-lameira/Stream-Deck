from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field

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
    request_id: Optional[str] = Field(None, max_length=64, description="Id do pedido de permissao do Claude Code")
    decision: Optional[Literal["allow", "deny"]] = Field(None, description="Decisao do usuario: 'allow' ou 'deny'")

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
    has_thumbnail: bool = False
    thumbnail_url: str = ""
    thumbnail: Optional[str] = ""

class SystemStatusMessage(BaseModel):
    type: str = "system_status"
    now_playing: NowPlayingState
    mic_muted: bool
    running_apps: List[str]
    system_metrics: Optional[Dict[str, Any]] = None

class ActionResultMessage(BaseModel):
    type: str = "action_result"
    status: str
    app: Optional[str] = None
    message: str


class ClaudePermissionHookInput(BaseModel):
    """Entrada do hook PermissionRequest do Claude Code (campos extras ignorados)."""
    model_config = ConfigDict(extra="ignore")

    tool_name: str
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    cwd: str = ""
    session_id: Optional[str] = None


class PairConfirmInput(BaseModel):
    pair_id: str = Field(max_length=64)
    code: str = Field(pattern=r"^\d{4}$")


class UsageWindow(BaseModel):
    used_percentage: float = Field(..., ge=0, le=100)
    resets_at: int = Field(..., ge=0)


class ClaudeUsageInput(BaseModel):
    """Limites da conta enviados pelo script de barra de status do Claude Code."""
    model_config = ConfigDict(extra="ignore")

    five_hour: Optional[UsageWindow] = None
    seven_day: Optional[UsageWindow] = None
    context_pct: Optional[float] = Field(default=None, ge=0, le=100)
    model: Optional[str] = Field(default=None, max_length=64)
