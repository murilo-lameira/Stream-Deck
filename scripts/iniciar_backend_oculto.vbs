Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Obtém diretório do projeto dinamicamente a partir de scripts/
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
projectDir = FSO.GetParentFolderName(scriptDir)
backendDir = FSO.BuildPath(projectDir, "backend")
pythonExe = FSO.BuildPath(backendDir, "venv\Scripts\python.exe")

' Define diretório de trabalho no backend
WshShell.CurrentDirectory = backendDir

' Inicia o backend em processo único invisível (0)
cmd = """" & pythonExe & """ -m uvicorn main:app --host 0.0.0.0 --port 8000"
WshShell.Run cmd, 0, False
