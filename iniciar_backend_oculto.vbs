Set WshShell = CreateObject("WScript.Shell")
' Inicia o backend em modo invisível (0)
WshShell.Run "cmd.exe /c cd ""F:\Faculdade\Projetos\Stream Deck\backend"" && .\venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000", 0, False
WshShell.Run "cmd.exe /c cd /d ""F:\Faculdade\Projetos\Stream Deck\backend"" && .\venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000", 0, False
