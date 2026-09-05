# 📋 Catálogo Geral de Aplicativos Mapeados

Listagem consolidada dos botões ativos divididos pelas 3 páginas do Stream Deck.

---

## Página 1: Produtividade & Cotidiano
| ID | Nome no Deck | Executável / Destino | Cor |
|---|---|---|---|
| `vscode` | VS Code | `%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe` | `#007ACC` |
| `discord` | Discord | `%LOCALAPPDATA%\Discord\Update.exe --processStart Discord.exe` | `#5865F2` |
| `whatsapp` | WhatsApp | Protocolo nativo Windows `whatsapp:` | `#25D366` |
| `chrome` | Google Chrome | `%PROGRAMFILES%\Google\Chrome\Application\chrome.exe` | `#EA4335` |
| `spotify` | Spotify | `%APPDATA%\Spotify\Spotify.exe` | `#1DB954` |
| `gemini` | Google Gemini | Atalho Web App Chrome `.lnk` | `#8E24AA` |
| `youtube` | YouTube | Chrome com URL `https://youtube.com` | `#FF0000` |
| `obsidian` | Obsidian | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Obsidian.lnk` | `#7C3AED` |

---

## Página 2: Central de Mídia & Controles
| ID | Função | Mecanismo | Cor |
|---|---|---|---|
| `sys_media_prev` | Anterior | `ctypes keybd_event(0xB1)` | `#10B981` |
| `sys_media_playpause` | Play/Pause | `ctypes keybd_event(0xB3)` | `#10B981` |
| `sys_media_next` | Próxima | `ctypes keybd_event(0xB0)` | `#10B981` |
| `sys_vol_mute` | Mudo Master | `pycaw` Master Mute | `#EF4444` |
| `sys_mic_mute` | Mudo Mic | `pycaw` eConsole + eCommunications | `#F59E0B` |
| `shutdown_pc` | Desligar PC | `shutdown /s /t 0` (Com confirmação) | `#FF4444` |

---

## Página 3: Ferramentas, Jogos & Monitoramento
| ID | Nome no Deck | Executável / Destino | Cor |
|---|---|---|---|
| `obs` | OBS Studio | `%PROGRAMDATA%\...\OBS Studio.lnk` | `#FFFFFF` |
| `github` | GitHub | Chrome com URL `https://github.com` | `#FFFFFF` |
| `ghub` | Logitech G HUB | `%PROGRAMFILES%\LGHUB\lghub.exe` | `#00B8FC` |
| `vms` | VMS Câmeras | `%PROGRAMFILES%\VMS\VMS.exe` (Sistema CFTV) | `#00D2FF` |
| `checkup` | CheckUP | `F:\...\CheckUP Windows 1.2.0.exe` | `#8C4FFF` |
| `lol` | League of Legends | Atalho Riot Games `.lnk` | `#D4AF37` |
| `steam` | Steam | Atalho Steam `.lnk` | `#66C0F4` |
| `blitz` | Blitz.gg | Atalho Blitz `.lnk` | `#ED1F34` |

[[Regras de Execução no Windows]]
[[MAIN]]
