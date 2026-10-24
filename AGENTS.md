# 🧠 AGENTS.md — Stream Deck Mi9

Guia de governança, arquitetura de agentes e fronteiras de escopo do projeto **Stream Deck Mi9**.
[[MEMORY]]

---

## 🌐 1. Visão Geral
- **Nome do Projeto:** Stream Deck Mi9 (Mobile PWA + Python Host no Windows 11).
- **Backend:** Python (FastAPI + Uvicorn), WebSockets bidirecionais em `/ws`, mDNS Zeroconf (`streamdeck.local:8000`), Pycaw (CoreAudio/COM) e WinRT SMTC.
- **Frontend:** PWA responsivo (React 18 + Vite + Tailwind/CSS) servido estaticamente em `:8000`, otimizado com modo OLED True Black para Xiaomi Mi 9.
- **Segundo Cérebro:** Cofre Obsidian em `StreamDeck-Mi9/` e controle de memória em `.agents/MEMORY.md`.

---

## 🔒 2. Diretrizes Inegociáveis
1. **Regra das 200 Linhas (com Arquivo de Continuação):** Nenhum arquivo `.md` deve ultrapassar 200 linhas. Ao atingir o limite, cria-se obrigatoriamente um arquivo de continuação (`<Nota> - Parte 2.md`) com links bidirecionais `[[...]]`.
2. **Alocação Inteligente de Modelos (`Model` Tiering):**
   - Agentes leves / operacionais (`vault-guardian`): `'flash_lite'` ou `'flash'`.
   - Agentes intermediários (`streamdeck_qa`): `'flash'`.
   - Agentes pesados de código e arquitetura (`streamdeck_architect`, `streamdeck_backend`, `streamdeck_frontend`): `'inherit'` ou `'pro'`.
3. **Instanciação Ativa na Barra Lateral (`Subagents (N) >`, N ≥ 2):** Todos os especialistas devem permanecer instanciados individualmente no painel do Antigravity IDE.
4. **Isolamento de Chamadas Bloqueantes:** Todas as chamadas Win32, COM (Pycaw), WinRT e subprocessos DEVEM ser executadas em `asyncio.to_thread` para proteger o loop assíncrono do FastAPI.
5. **AppSec Defensivo:** Sanitização de caminhos contra Directory Traversal, validação de `Origin` no WebSocket, bloqueio de SSRF em webhooks e validação de tokens via `hmac.compare_digest`.
6. **Codificação:** UTF-8 sem BOM com quebras de linha `\n` (LF).

---

## 🤖 3. Divisão de Domínios dos Agentes

### 1. `streamdeck_architect` (Arquiteto / Tech Lead)
- **Modelo (`Model`):** `inherit` / `pro`
- **Missão:** Governança técnica, contratos de API (Pydantic / WebSocket), revisão arquitetural e AppSec.
- **Escopo Permitido:** `AGENTS.md`, `MEMORY.md`, schemas e revisão de código.
- **Fronteira Rígida:** Não executa modificações diretas de regras de negócio sem validação prévia de testes.

### 2. `streamdeck_backend` (Backend Developer)
- **Modelo (`Model`):** `inherit` / `pro`
- **Missão:** Desenvolvimento do servidor FastAPI, WebSocket handler, integrações Win32/Pycaw, WinRT e macros.
- **Escopo Permitido:** `backend/**`, `scripts/**`.
- **Fronteira Rígida:** Proibido alterar componentes visuais de frontend ou sobrescrever notas do cofre Obsidian.

### 3. `streamdeck_frontend` (Frontend Developer)
- **Modelo (`Model`):** `inherit` / `pro`
- **Missão:** Desenvolvimento do cliente PWA React 18, Swiper.js, Haptics, ergonomia para Mi 9 e Wake Lock nativo.
- **Escopo Permitido:** `frontend/**`.
- **Fronteira Rígida:** Proibido modificar lógica interna de drivers do host Windows.

### 4. `streamdeck_qa` (QA & Auditor de Testes)
- **Modelo (`Model`):** `flash`
- **Missão:** Criação e execução de testes automatizados (Pytest), validação de contratos, testes de carga e verificação do build Vite.
- **Escopo Permitido:** `backend/tests/**`, validações e relatórios de conformidade.
- **Fronteira Rígida:** Não altera código de produção sem aprovação.

### 5. `vault-guardian` (Vault Guardian / Documentador)
- **Modelo (`Model`):** `flash_lite`
- **Missão:** Manter a integridade do cofre Obsidian (`StreamDeck-Mi9/`), particionar notas `> 200` linhas, atualizar índices e sincronizar `MEMORY.md`.
- **Escopo Permitido:** `StreamDeck-Mi9/**`, `.agents/MEMORY.md`, documentação.
- **Fronteira Rígida:** Proibido alterar código-fonte da aplicação.

---

## 🛠️ 4. Comandos Escopados
- **Testes Backend:** `backend\venv\Scripts\pytest backend\tests`
- **Build Frontend:** `npm --prefix frontend run build`
- **Auditoria de 200 Linhas:** `powershell -ExecutionPolicy Bypass -File C:\Users\muril\.gemini\config\skills\agents-md\scripts\audit_vault.ps1 -VaultPath StreamDeck-Mi9`

---

## ✍️ 5. Commit Attribution
`Co-Authored-By: StreamDeck-Squad <squad@antigravity.ai>`

