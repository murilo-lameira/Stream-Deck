# Aprovação Remota do Claude Code — Plano (Parte 2)

Continuação de [[2026-11-16-aprovacao-remota-claude]]. As restrições globais e o foco de revisão de lá
valem aqui.

### Task 5: Script do hook · Agente: `streamdeck_backend`
**Arquivos:** Create `scripts/claude_permission_hook.py`; Test `backend/tests/test_hook_script.py`
(importa o script via `importlib.util.spec_from_file_location`).
**Produz:**
- `ENDPOINT = "http://127.0.0.1:8000/api/v1/claude/permission"`, `HTTP_TIMEOUT_S = 125.0`.
- `DENY_MESSAGE = "Negado pelo Stream Deck (celular)."`
- `load_token(env_path: Path) -> str | None`: lê `AUTH_TOKEN=` de `backend/.env`
  (`Path(__file__).resolve().parent.parent / "backend" / ".env"`).
- `build_output(behavior: str) -> dict | None`: `None` se o valor não for `allow`/`deny`. Para deny, inclui `message`.
- `request_decision(payload: dict, token: str, url: str = ENDPOINT, timeout: float = HTTP_TIMEOUT_S) -> str | None`:
  `None` em qualquer exceção ou status ≠ 200.
- `main() -> int`: lê stdin com `sys.stdin.buffer.read().decode("utf-8")`. Imprime o JSON só quando há decisão.
  Sempre retorna 0. Logs vão para stderr.

- [ ] Testes: `test_build_output_allow`
  (`== {"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}`);
  `test_build_output_deny_has_message`; `test_build_output_invalid_none`; `test_load_token`
  (`tmp_path`, com outra linha antes); `test_load_token_missing_none`;
  `test_main_server_down_prints_nothing` (url → porta fechada `127.0.0.1:1`, stdin com acentos, `capsys.out == ""`,
  retorno 0); `test_main_allow_prints_json` (`request_decision` monkeypatched → `"allow"`).
- [ ] Ver os testes falhando, implementar, ver os testes passando.
- [ ] Teste manual: `echo {"tool_name":"Bash","tool_input":{"command":"dir"}} | backend\venv\Scripts\python -I scripts\claude_permission_hook.py`
  com o backend desligado. Esperado: nada no stdout e código de saída 0.
- [ ] Commit `feat(claude): script do hook PermissionRequest`.

### Task 6: Segurança do frontend · Agente: `streamdeck_frontend`
**Arquivos:** Modify `frontend/src/config/constants.js` (remover `DEFAULT_AUTH_TOKEN`), `frontend/src/App.jsx:7,52`,
`frontend/src/components/SettingsModal.jsx:3,26`.
- [ ] O token inicial vira `localStorage.getItem(STORAGE_KEY_TOKEN) || ''`. Sem token, não conectar e
  mostrar o aviso "Abra o link de pareamento" (no estilo dos avisos de status já existentes).
- [ ] O botão de reset do SettingsModal passa a limpar o token (`''`) em vez de restaurar o padrão.
- [ ] `grep -r "mi9_deck_secret_2026" frontend/src` não retorna nada. `npm --prefix frontend run build` passa.
- [ ] Commit `fix(security): remove token padrao do PWA`.

### Task 7: Modal de permissão no PWA · Agente: `streamdeck_frontend`
**Arquivos:** Create `frontend/src/components/ClaudePermissionModal.jsx`; Modify `frontend/src/hooks/useWebSocket.js`,
`frontend/src/App.jsx`, `frontend/src/App.css`.
**Consome:** as mensagens WS da Task 2 e a ação `claude_permission_response` da Task 4.
**Produz (`useWebSocket`):** `permissionQueue: Array<{request_id, tool_name, summary, project, deadline}>`, em que
`deadline = Date.now() + expires_in*1000`, e `respondPermission(requestId: string, decision: 'allow'|'deny') -> void`.
- [ ] `claude_permission_request` → adiciona à fila (ignora `request_id` duplicado) e chama `hapticFeedback.warning()`.
  `claude_permission_resolved` → remove da fila.
- [ ] `ClaudePermissionModal({ request, position, total, onRespond })`:
  - título "Claude pede permissão" e "position de total";
  - `tool_name · project`;
  - `summary` em `<pre>`, como texto puro;
  - contagem `m:ss` até `deadline`;
  - botões **Negar** (esquerda, cinza) e **Permitir** (direita, verde), com ≥ 48 px de altura;
  - tocar no fundo não fecha;
  - tema OLED.
- [ ] Em `App.jsx`: renderizar com `permissionQueue[0]`. Mostrar toast no `claude_permission_resolved`:
  allow → "Permitido", deny → "Negado", expired → "Expirou — responda no PC", cancelled → "Cancelado no PC".
- [ ] `npm --prefix frontend run build` passa. Commit `feat(pwa): modal de aprovacao do Claude Code`.

### Task 8: Instalação, verificação ponta a ponta e revisão · Agentes: `streamdeck_architect` + Claude
- [ ] **Pedir confirmação ao usuário** e então adicionar em `~/.claude/settings.json` (merge, sem sobrescrever) o
  bloco `hooks.PermissionRequest` da seção 6 do spec (`timeout: 150`).
- [ ] O usuário repareia o Mi 9: `http://localhost:8000/api/v1/deck/pairing` no PC → abrir o `pairing_url` no celular.
- [ ] E2E com backend e PWA no ar:
  - um comando que pede permissão aparece no Mi 9;
  - Negar → o Claude recebe a mensagem;
  - Permitir → o comando roda;
  - sem resposta por 120 s → o prompt aparece no PC;
  - backend desligado → o prompt aparece no PC na hora.
- [ ] Confirmar se a aba Code do app desktop executa o hook (risco da seção 12 do spec) e registrar o resultado.
- [ ] `streamdeck_architect` revisa o diff da branch inteira contra o spec (contrato, AppSec, `to_thread`).
- [ ] `streamdeck_qa`: `backend\venv\Scripts\pytest backend\tests` verde e build verde. Relatório final.
