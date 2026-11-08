Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
targetScript = FSO.BuildPath(scriptDir, "scripts\iniciar_streamdeck.vbs")
WshShell.Run """" & targetScript & """", 0, False
