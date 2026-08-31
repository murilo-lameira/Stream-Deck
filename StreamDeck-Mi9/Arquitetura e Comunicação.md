- **Backend:** Python + FastAPI (porta 8000).
- **Frontend:** React + Vite (Compilado para HTML/CSS/JS estático em `/dist`).
- **Web Server:** O FastAPI agora não só fornece a API e WebSockets, como também hospeda os arquivos do Frontend.
- **Autodescoberta:** ZeroConf mDNS embutido. O celular acessa via `http://streamdeck.local:8000`.
- **Comunicação:** WebSocket (ws://streamdeck.local:8000/ws).

**Contrato de Dados**
- Cliente envia auth: `{"auth_token": "SENHA_AQUI"}`
- Cliente envia comando de app: `{"action": "open", "app": "NOME_DO_APP"}`
- Cliente envia controle de volume: `{"action": "set_volume", "level": 80}` ou `{"action": "toggle_mute"}`
- Servidor transmite status da máquina: `{"type": "system_status", "now_playing": {"title": "X", "artist": "Y"}, "mic_muted": true}`

[[Mapeamento de Aplicativos]]