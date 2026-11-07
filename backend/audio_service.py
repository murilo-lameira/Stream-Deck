"""
Fachada de compatibilidade retroativa para audio_service.
Re-exporta funções do módulo modular services.audio_service.
"""

from services.audio_service import (
    get_volume_state,
    set_volume_level,
    toggle_mute,
    get_mic_mute_state,
    set_mic_mute_state,
    toggle_mic_mute,
)

__all__ = [
    "get_volume_state",
    "set_volume_level",
    "toggle_mute",
    "get_mic_mute_state",
    "set_mic_mute_state",
    "toggle_mic_mute",
]
