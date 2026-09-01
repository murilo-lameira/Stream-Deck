Set WshShell = CreateObject("WScript.Shell")

' Iniciar o backend (FastAPI/Uvicorn) em processo oculto (0)
backendCmd = "cmd.exe /c ""cd /d """"F:\Faculdade\Projetos\Stream Deck\backend"""" && venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"""
WshShell.Run backendCmd, 0, False

