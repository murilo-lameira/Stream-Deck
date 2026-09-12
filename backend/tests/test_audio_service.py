from unittest.mock import MagicMock, patch
from audio_service import set_volume_level, toggle_mute, get_volume_state

def test_set_volume_level_clamping():
    mock_volume = MagicMock()
    mock_volume.GetMute.return_value = 0
    mock_speakers = MagicMock()
    mock_speakers.EndpointVolume = mock_volume

    with patch("pycaw.pycaw.AudioUtilities.GetSpeakers", return_value=mock_speakers):
        # Testa clamp para valores acima de 100
        level, is_muted = set_volume_level(150)
        assert level == 100
        mock_volume.SetMasterVolumeLevelScalar.assert_called_with(1.0, None)

        # Testa clamp para valores negativos
        level, is_muted = set_volume_level(-20)
        assert level == 0
        mock_volume.SetMasterVolumeLevelScalar.assert_called_with(0.0, None)

        # Testa valor normal (45%)
        level, is_muted = set_volume_level(45)
        assert level == 45
        mock_volume.SetMasterVolumeLevelScalar.assert_called_with(0.45, None)

def test_toggle_mute():
    mock_volume = MagicMock()
    mock_volume.GetMute.return_value = 0
    mock_volume.GetMasterVolumeLevelScalar.return_value = 0.5
    mock_speakers = MagicMock()
    mock_speakers.EndpointVolume = mock_volume

    with patch("pycaw.pycaw.AudioUtilities.GetSpeakers", return_value=mock_speakers):
        level, is_muted = toggle_mute()
        assert is_muted is True
        mock_volume.SetMute.assert_called_with(1, None)

