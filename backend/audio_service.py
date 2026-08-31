import logging
from typing import Tuple, Optional

logger = logging.getLogger("streamdeck.audio")

def get_volume_state() -> Tuple[int, bool]:
    """Retorna (level 0-100, is_muted)"""
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        if not speakers:
            return 50, False
        volume = speakers.EndpointVolume
        level = int(round(volume.GetMasterVolumeLevelScalar() * 100))
        muted = bool(volume.GetMute())
        return level, muted
    except Exception as e:
        logger.error(f"Erro ao obter volume do sistema: {e}")
        return 50, False

def set_volume_level(level_percent: int) -> Tuple[int, bool]:
    """Define o volume (0-100) e desmuta se volume > 0. Retorna (level, is_muted)"""
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        if not speakers:
            return level_percent, False
        volume = speakers.EndpointVolume
        # Clamp entre 0 e 100
        clamped = max(0, min(100, level_percent))
        volume.SetMasterVolumeLevelScalar(clamped / 100.0, None)
        if clamped > 0 and volume.GetMute():
            volume.SetMute(0, None)
        return clamped, bool(volume.GetMute())
    except Exception as e:
        logger.error(f"Erro ao definir volume: {e}")
        return level_percent, False

def toggle_mute() -> Tuple[int, bool]:
    """Alterna estado de mute. Retorna (level, is_muted)"""
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        if not speakers:
            return 50, False
        volume = speakers.EndpointVolume
        current_mute = volume.GetMute()
        new_mute = 0 if current_mute else 1
        volume.SetMute(new_mute, None)
        level = int(round(volume.GetMasterVolumeLevelScalar() * 100))
        return level, bool(new_mute)
    except Exception as e:
        logger.error(f"Erro ao alternar mute: {e}")
        return 50, False



def get_mic_mute_state() -> bool:
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from pycaw.constants import EDataFlow, ERole
        from comtypes import CLSCTX_ALL
        device_enumerator = AudioUtilities.GetDeviceEnumerator()
        device = device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eCapture.value, ERole.eConsole.value)
        interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        return bool(volume.GetMute())
    except Exception as e:
        logger.error(f"Erro ao obter estado do microfone: {e}")
        return False

def toggle_mic_mute() -> bool:
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from pycaw.constants import EDataFlow, ERole
        from comtypes import CLSCTX_ALL
        device_enumerator = AudioUtilities.GetDeviceEnumerator()
        device = device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eCapture.value, ERole.eConsole.value)
        interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        current_mute = volume.GetMute()
        new_mute = 0 if current_mute else 1
        volume.SetMute(new_mute, None)
        return bool(new_mute)
    except Exception as e:
        logger.error(f"Erro ao alternar microfone: {e}")
        return False
