---
name: security-review
description: >-
  Auditoria de segurança, sanitização de inputs e proteção do WebSocket e APIs do Stream Deck Mi9.
  Use ao expor novas rotas, criar manipuladores de comandos WebSocket ou integrar chamadas de sistema Windows.
user-invocable: true
metadata:
  origin: "ECC + StreamDeck"
  version: "1.0.0"
---

# 🛡️ Security Review & Checklist (Stream Deck Mi9)

Diretrizes de segurança para proteger o host Windows contra injeção de comandos, travamentos e exposição indevida na rede local.

---

## 🔒 Checklist de Segurança

### 1. Manipulação Segura de Processos e Atalhos
- ❌ **NUNCA:** Concatenar strings diretamente em `os.system()` ou `subprocess.Popen(shell=True)`.
- ✅ **SEMPRE:** Validar nomes de executáveis contra a whitelist em `backend/apps_config.py` e passar listas seguras para `subprocess.Popen([exe, arg])`.

### 2. Handshake e Mensageria WebSocket
- Valide a estrutura de cada payload JSON recebido via WebSocket com schemas Pydantic.
- Rejeite payloads malformados com resposta de erro imediata (`400 Bad Request` / `type: "error"`).
- Aplique rate-limiting nos comandos de volume/mídia para evitar sobrecarga do subsistema CoreAudio/WinRT.

### 3. Segredos e Variáveis de Ambiente
- Nenhum token, senha ou webhook do n8n/Discord deve ficar hardcoded no código.
- Utilize `.env` ignorado no `.gitignore`.
