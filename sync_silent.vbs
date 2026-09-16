Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c " & Chr(34) & scriptDir & "\sync_daily.bat" & Chr(34), 0, False
Set WshShell = Nothing
Set FSO = Nothing
