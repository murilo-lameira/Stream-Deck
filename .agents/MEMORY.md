# 🧠 Project Memory & Active Context — Stream Deck Mi9

Este arquivo preserva as decisões arquiteturais, preferências operacionais, armadilhas técnicas resolvidas (gotchas) e lições aprendidas entre sessões de agentes.

---

## 📌 1. Visão Geral e Stack do Projeto

- **Nome:** Stream Deck Mi9 (Mobile PWA + Python Host no Windows 11).
- **Backend:** Python (FastAPI + Uvicorn), WebSockets bidirecionais em `/ws/streamdeck`, mDNS Zeroconf para autodescoberta (`streamdeck.local:8000`).
- **Frontend:** PWA responsivo (Vue.js + Tailwind CSS) servido estaticamente em `:8000`.
- **Arquitetura Backend Modular:**
  - `backend/routers/`: Endpoints HTTP/REST (`apps.py`, `system.py`, etc.).
  - `backend/services/`: Lógica de domínio (`audio_service.py`, `media_service.py`, `process_service.py`).
  - `backend/managers/`: Gerenciamento de conexões e broadcast (`connection_manager.py`).
  - `backend/apps_config.py`: Catálogo de atalhos e executáveis permitidos.

---

## 🛑 2. Regra de Ouro: Portão de Aprovação do Usuário (HITL Gate)

- **Princípio:** Antes de iniciar qualquer alteração ou criação de código de produção, o agente deve apresentar ao usuário um resumo claro contendo:
  1. Arquivos afetados (`[MODIFY]`, `[NEW]`, `[DELETE]`).
  2. Endpoints / funções adicionadas.
  3. Riscos ou dependências.
- **Ação:** Aguardar a aprovação explícita do usuário antes de disparar a Fase 2 (Implementação).

---

## ⚠️ 3. Gotchas e Lições do Windows 11 (Crítico)

1. **Chamadas Bloqueantes de Sistema:**
   - Funções do Pycaw (`IAudioEndpointVolume`), WinRT (`GlobalSystemMediaTransportControlsSessionManager`) e Win32 (`ctypes.windll.user32`) são síncronas e bloqueantes.
   - **Regra:** Envolva SEMPRE qualquer chamada Win32/COM/Audio em `asyncio.to_thread` para não travar o loop de eventos assíncrono do FastAPI e WebSocket.

2. **Nomes de Executáveis e Processos Especiais:**
   - **WhatsApp (Windows Store):** Roda sob o processo `WhatsApp.Root.exe` (não `WhatsApp.exe`).
   - **Abas do Chrome:** Detectadas inspecionando títulos de janelas associados a `chrome.exe` (ex: `YouTube`, `Google Gemini`, `GitHub`).
   - **Foco de Janelas:** Usar `ShowWindow(hwnd, SW_RESTORE)` e simular `ALT` com `keybd_event` para contornar restrições de primeiro plano no Windows 11.

3. **Terminal PowerShell no Windows:**
   - Evite passar caracteres `&` soltos dentro de strings de comandos inline `python -c "..."` no PowerShell, pois causam erro de parser antes de atingir o interpretador. Use scripts scratch em arquivo quando necessário.

---

## 🏛️ 4. Governança do Cofre Obsidian (`StreamDeck-Mi9/`)

- **Regra de Ouro de Tamanho:** NENHUM arquivo markdown (`.md`) pode ultrapassar **200 linhas**.
- **Encoding Obrigatório:** Salvar sempre em **UTF-8 sem BOM**.
- **Blocos Mermaid:** Usar sempre ` ```mermaid ` na abertura e ` ``` ` no fechamento em linhas isoladas.
- **Estrutura de Pastas:**
  - `00 - Meta/`: Bússola (`MAIN.md`), índices e governança.
  - `01 - Arquitetura/`: Protocolos, diagramas interativos (Archify) e contratos.
  - `02 - Backlog/`: Features, roadmap e histórico de entregas.
  - `03 - Design/`: UI, layout, cores e responsividade.
  - `04 - Integracoes/`: n8n, Alexa e webhooks.
  - `05 - Aplicativos/`: Catálogo de apps e regras de execução.
  - `gemini-scribe/`: Prompts de agentes e catálogo de Skills.

---

## 🤖 5. Ciclo de Vida dos Agentes & Loop de 5 Fases

- **Pipeline em Fases:**
  $$\text{Fase 1 (Plano)} \longrightarrow \mathbf{\text{Gate: Aprovação do Usuário}} \longrightarrow \text{Fase 2 (Dev + TDD)} \longrightarrow \text{Fase 3 (QA + Security)} \longrightarrow \text{Fase 4 (Docs)}$$
- **Princípio da Economia de Contexto:**
  - Documentadores e QAs só atuam nas etapas finais.
  - Se o QA encontrar falhas no código ou UI, rejeita e devolve o chamado para o Dev correspondente com o diagnóstico antes de registrar no Obsidian.

---

## 🧰 6. Skills Modulares Registradas no Workspace

| Skill | Finalidade Principal |
| :--- | :--- |
| **`create-agent`** | Criação, governança e registro de novas personas no pipeline. |
| **`archify`** | Compilação de diagramas interativos HTML/SVG (`node bin/archify.mjs deliver`). |
| **`tdd-workflow`** | Ciclo RED -> GREEN -> REFACTOR com pytest e mocks assíncronos. |
| **`security-review`** | Auditoria de segurança, sanitização de inputs e proteção do WebSocket. |
| **`api-design`** | Contratos REST e envelopes padronizados de WebSocket. |
