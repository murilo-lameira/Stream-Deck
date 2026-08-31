# Mapeamento de Aplicativos

Aqui ficam os caminhos absolutos dos programas que o Stream Deck vai controlar usando `subprocess.Popen()` ou `os.startfile()` no backend. Todos utilizam variÃ¡veis de ambiente como `%APPDATA%` e `%PROGRAMDATA%` para suporte cross-user.

- **VS Code:** `%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe`
- **Discord:** `%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe`
- **Google Chrome:** `%PROGRAMFILES%\Google\Chrome\Application\chrome.exe`
- **Spotify:** `%APPDATA%\Spotify\Spotify.exe`
- **Gemini (Atalho):** `%APPDATA%\Microsoft\Windows\Start Menu\Programs\apps do Chrome\Gemini.lnk`
- **League of Legends (Atalho):** `%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Riot Games\League of Legends.lnk`
- **Steam (Atalho):** `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Steam\Steam.lnk`
- **Obsidian (Atalho):** `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Obsidian.lnk`
- **WhatsApp (UWP):** `whatsapp:`- **Desligar PC (Nativo):** `shutdown /s /t 0` (Protegido via window.confirm)

## Controles de Sistema e Mídia (Nativos via \ctypes\)
- \sys_vol_up\: Aumenta volume
- \sys_vol_down\: Diminui volume
- \sys_vol_mute\: Muta o sistema
- \sys_media_playpause\: Toca/Pausa música
- \sys_media_next\: Próxima faixa
- \sys_media_prev\: Faixa anterior
