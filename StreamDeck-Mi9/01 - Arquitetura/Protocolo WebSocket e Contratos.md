# 📡 Protocolo WebSocket e Contratos de Dados

A comunicação de baixa latência é realizada através de um canal WebSocket contínuo em `ws://streamdeck.local:8000/ws`.

---

## 1. Handshake de Autenticação (Cliente -> Servidor)
Enviado imediatamente no evento `onopen`:
```json
{
  "auth_token": "mi9_deck_secret_2026"
}
```
* **Sucesso:** Servidor responde com status e dados iniciais de volume.
* **Falha:** Servidor encerra com código **WebSocket 1008 (Policy Violation)**.

---

## 2. Disparo de Ação / Aplicativo (Cliente -> Servidor)
```json
{
  "action": "open",
  "app": "vscode"
}
```

---

## 3. Controle de Mídia e Áudio (Cliente -> Servidor)
* **Alterar Volume:**
  ```json
  { "action": "set_volume", "level": 75 }
  ```
* **Alternar Mute Master:**
  ```json
  { "action": "toggle_mute" }
  ```
* **Controles Multimídia (Simulação de Teclas Virtuais):**
  ```json
  { "action": "open", "app": "sys_media_playpause" }
  { "action": "open", "app": "sys_media_next" }
  { "action": "open", "app": "sys_media_prev" }
  { "action": "open", "app": "sys_mic_mute" }
  ```

---

## 4. Telemetria e Status em Tempo Real (Servidor -> Cliente)
Broadcast transmitido sempre que houver alteração de estado ou nova conexão:
## 4. Heartbeat (Cliente -> Servidor e Servidor -> Cliente)
Disparado a cada 15s pelo cliente para manter o canal ativo e detectar quedas:
* **Cliente:** `{ "action": "ping" }`
* **Servidor:** `{ "type": "pong" }`

---

## 5. Telemetria e Status em Tempo Real (Servidor -> Cliente)
Broadcast transmitido sempre que houver alteração de estado, nova conexão ou processo aberto:
```json
{
  "type": "system_status",
  "now_playing": {
    "title": "Cedo Ou Tarde",
    "artist": "NX Zero",
    "source_app": "Spotify.exe",
    "is_playing": true,
    "thumbnail": "base64_string_aqui..."
  },
  "mic_muted": false
  "mic_muted": false,
  "running_apps": ["vscode", "chrome", "spotify", "obsidian"]
}
```

E atualização direta de processos após disparo de app:
```json
{
  "type": "running_apps_update",
  "running_apps": ["vscode", "chrome", "spotify", "obsidian"]
}
```

[[Visão Geral e Camadas]]
[[MAIN]]
