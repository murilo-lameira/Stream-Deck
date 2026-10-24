"""
Fachada de compatibilidade retroativa para configurações e serviços de aplicativos.
Re-exporta símbolos modulares de config.apps_registry, services.window_service e services.process_service.
"""

from config.apps_registry import (
    APPS_MAP,
    APP_PROCESS_NAMES,
    SYSTEM_KEYS,
    WINDOW_TITLE_KEYWORDS,
)
from services.window_service import (
    simulate_key,
    bring_to_foreground,
)
from services.process_service import (
    launch_app,
    launch_app_async,
)

__all__ = [
    "APPS_MAP",
    "APP_PROCESS_NAMES",
    "SYSTEM_KEYS",
    "WINDOW_TITLE_KEYWORDS",
    "simulate_key",
    "bring_to_foreground",
    "launch_app",
    "launch_app_async",
]
