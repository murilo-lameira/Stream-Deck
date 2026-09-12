import os
from apps_config import APPS_MAP, APP_PROCESS_NAMES, SYSTEM_KEYS

def test_apps_map_contains_core_apps():
    required_apps = ["vscode", "discord", "chrome", "spotify", "gemini", "obsidian", "checkup"]
    for app_id in required_apps:
        assert app_id in APPS_MAP
        assert len(APPS_MAP[app_id]) > 0
        assert isinstance(APPS_MAP[app_id][0], str)

def test_system_keys_mapping():
    expected_keys = ["sys_vol_up", "sys_vol_down", "sys_vol_mute", "sys_media_next", "sys_media_prev", "sys_media_playpause"]
    for key in expected_keys:
        assert key in SYSTEM_KEYS
        assert isinstance(SYSTEM_KEYS[key], int)

def test_checkup_path_is_string():
    assert "checkup" in APPS_MAP
    path = APPS_MAP["checkup"][0]
    assert isinstance(path, str)
    assert len(path) > 0

