import os
import sys
sys.path.append(r"f:\Faculdade\Projetos\Stream Deck\backend")
from apps_config import launch_app

for app in ["vscode", "chrome", "gemini", "obsidian"]:
    res = launch_app(app)
    print(f"{app}: {res}")
