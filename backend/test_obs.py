import os
lnk = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Obsidian.lnk")
print("Caminho:", lnk)
print("Existe:", os.path.exists(lnk))
os.startfile(lnk)
print("Disparado com sucesso!")
