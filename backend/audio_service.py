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



def _get_capture_volumes():
    """
    Retorna uma lista de interfaces IAudioEndpointVolume para todos os
    dispositivos de captura relevantes (eConsole + eCommunications).
    Apps de chamada (Discord, WhatsApp, Meet) usam eCommunications;
    o endpoint eConsole cobre o restante.
    """
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from pycaw.constants import EDataFlow, ERole
    from comtypes import CLSCTX_ALL

    interfaces = []
    device_enumerator = AudioUtilities.GetDeviceEnumerator()

    for role in (ERole.eConsole.value, ERole.eCommunications.value):
        try:
            device = device_enumerator.GetDefaultAudioEndpoint(EDataFlow.eCapture.value, role)
            iface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol = iface.QueryInterface(IAudioEndpointVolume)
            # Evita duplicatas (pode ser o mesmo dispositivo físico)
            if not any(v is vol for v in interfaces):
                interfaces.append(vol)
        except Exception:
            pass

    return interfaces


def get_mic_mute_state() -> bool:
    try:
        vols = _get_capture_volumes()
        if not vols:
            return False
        # Considera mutado se o endpoint principal (eConsole) estiver mutado
        return bool(vols[0].GetMute())
    except Exception as e:
        logger.error(f"Erro ao obter estado do microfone: {e}")
        return False


def toggle_mic_mute() -> bool:
    """
    Muta/desmuta o microfone em TODOS os endpoints de captura ativos
    (eConsole e eCommunications), garantindo que apps de chamada como
    Discord, WhatsApp Web e Google Meet sejam afetados.
    """
    try:
        vols = _get_capture_volumes()
        if not vols:
            logger.warning("Nenhum dispositivo de captura encontrado.")
            return False

        # Determina novo estado com base no endpoint principal
        current_mute = bool(vols[0].GetMute())
        new_mute = 0 if current_mute else 1

        for vol in vols:
            try:
                vol.SetMute(new_mute, None)
            except Exception as e:
                logger.warning(f"Não foi possível mutar um endpoint de captura: {e}")

        logger.info(f"Microfone {'mutado' if new_mute else 'desmutado'} em {len(vols)} endpoint(s).")
        return bool(new_mute)
    except Exception as e:
        logger.error(f"Erro ao alternar microfone: {e}")
        return False

