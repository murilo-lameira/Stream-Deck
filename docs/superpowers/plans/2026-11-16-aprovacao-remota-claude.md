# Aprovação Remota do Claude Code — Plano de Implementação

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: superpowers:subagent-driven-development, usando os agentes
> do projeto (coluna "Agente" de cada task). Os passos usam checkbox (`- [ ]`).
> Continua em [[2026-11-16-aprovacao-remota-claude - Parte 2]] (Tasks 5–8).

**Objetivo:** pedidos `PermissionRequest` do Claude Code aparecem no Mi 9 e são respondidos ali.
**Arquitetura:** hook de comando → script stdlib → `POST /api/v1/claude/permission` (só loopback + Bearer)
→ `PermissionBroker` em memória → broadcast no `/ws` → modal no PWA → ação WS resolve o Future.
**Stack:** FastAPI/Pydantic v2, pytest + pytest-asyncio, React 18 + Vite, Python stdlib (script).
**Spec:** `docs/superpowers/specs/2026-11-16-aprovacao-remota-claude-design.md`

## Restrições globais
- Timeouts: backend **120 s**, script **125 s**, hook **150 s**. Limite de **10** pedidos pendentes.
- Resumo cortado em **300** caracteres. O projeto exibido é o nome da pasta de `cwd`.
- Mensagem de deny: `Negado pelo Stream Deck (celular).`
- Qualquer falha resulta em **sem decisão** (script sai 0 com stdout vazio). Nunca aprovar sozinho.
- UTF-8 sem BOM, LF. Arquivos `.md` com no máximo 200 linhas.
- Testes: `backend\venv\Scripts\pytest backend\tests`. Build: `npm --prefix frontend run build`.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Foco de revisão
1. Dois clientes respondem ao mesmo pedido → a 1ª resposta vence e o outro recebe "Pedido expirado" (T4).
2. `tool_input` enorme, multilinha ou com acentos → resumo ≤ 300 e intacto em UTF-8 (T2). O script lê
   stdin como UTF-8 mesmo no Windows cp1252 (T5).
3. Nome de ferramenta desconhecido (`mcp__srv__tool`) ou corpo sem `tool_input` → resumo em JSON, sem 422 (T3).
4. O celular reconecta durante a espera → recebe o pedido com o `expires_in` restante (T2/T4).
5. Backend fora do ar ou reiniciado durante a espera → o script não imprime nada (T5).

---

### Task 1: Segurança do backend (token e loopback) · Agente: `streamdeck_backend`
**Arquivos:** Modify `backend/services/auth_service.py` (`is_valid_token`), `backend/routers/deck_router.py:41-54`;
Create `backend/routers/security_deps.py`; Test `backend/tests/test_auth_service.py`.
**Produz:** `require_loopback(request: Request) -> None` (403 se `request.client.host` ∉ {`127.0.0.1`,`::1`}).
**Produz:** fixture `loopback_override` em `backend/tests/conftest.py`, que faz
`app.dependency_overrides[require_loopback] = lambda: None` e limpa no teardown.

- [ ] Testes que falham:
  - `test_legacy_token_rejected`: `is_valid_token("mi9_deck_secret_2026") is False`.
  - `test_pairing_forbidden_from_lan`: sem override → `GET /api/v1/deck/pairing` == 403
    (o TestClient usa o host `testclient`).
  - `test_pairing_uses_lan_ip(loopback_override)`: com `get_local_ip` mockado para `"192.168.0.9"`,
    `pairing_url.startswith("http://192.168.0.9:")`.
  - Ajustar `test_endpoint_get_pairing_info` para usar `loopback_override`.
- [ ] Rodar `backend\venv\Scripts\pytest backend\tests\test_auth_service.py -v` e confirmar que os novos falham.
- [ ] Implementar: tirar o 2º `compare_digest` de `is_valid_token` (a rotação em `get_auth_token` fica);
  a rota de pairing ganha `Depends(require_loopback)` e passa a usar `host = get_local_ip()`.
- [ ] Rodar a suíte inteira até ficar verde.
- [ ] Commit `fix(security): rejeita token legado e restringe pareamento ao loopback`.

### Task 2: `PermissionBroker` · Agente: `streamdeck_backend`
**Arquivos:** Create `backend/services/claude_permission_service.py`; Test `backend/tests/test_claude_permission_service.py`.
**Produz:**
- `summarize(tool_name: str, tool_input: dict) -> str`: `Bash` → `command`; `Edit`/`Write`/`Read` → `file_path`;
  o resto → `json.dumps(tool_input, ensure_ascii=False, separators=(",", ":"))`. Corta em 300.
- `class PermissionBroker(broadcast: Callable[[dict], Awaitable[None]], timeout_s: float = 120.0, max_pending: int = 10)`:
  - `async submit(tool_name, tool_input, cwd) -> str | None`: `None` se cheio. Faz broadcast de
    `{"type":"claude_permission_request","request_id","tool_name","summary","project","expires_in"}`.
  - `async wait(request_id) -> Literal["allow","deny"] | None`: no timeout faz broadcast de
    `claude_permission_resolved` com `outcome:"expired"` e retorna `None`. Sempre remove do pendente.
  - `async resolve(request_id, decision) -> bool`: `False` se o id for desconhecido ou já resolvido.
    Se resolver, faz broadcast com `outcome=decision`.
  - `async cancel(request_id) -> None`: faz broadcast com `outcome:"cancelled"`.
  - `pending_messages() -> list[dict]`: mensagens `claude_permission_request` com `expires_in` restante (int, ≥ 0).
- Instância global: `broker = PermissionBroker(manager.broadcast)`.

- [ ] Testes (pytest-asyncio, `broadcast` = `AsyncMock`):
  - `summarize`: `test_summarize_bash`, `test_summarize_file_tools`, `test_summarize_unknown_tool_json`,
    `test_summarize_truncates_300` (entrada de 10 000 caracteres com "ação\n" → `len == 300`, acento preservado).
  - Broker: `test_submit_broadcasts_request` (project == `"Stream Deck"` para `cwd="F:/x/Stream Deck"`);
    `test_resolve_allow` (wait → `"allow"`); `test_wait_timeout_expired` (`timeout_s=0.05` → `None` + outcome
    expired); `test_resolve_twice_second_false`; `test_full_returns_none` (`max_pending=1`);
    `test_pending_messages_expires_in_decreases`.
- [ ] Ver os testes falhando, implementar, ver os testes passando.
- [ ] Commit `feat(claude): broker de pedidos de permissao`.

### Task 3: Rota HTTP do hook · Agente: `streamdeck_backend`
**Arquivos:** Create `backend/routers/claude_router.py`; Modify `backend/schemas/deck_schemas.py`, `backend/main.py`
(`include_router`); Test `backend/tests/test_claude_router.py`.
**Consome:** `require_loopback`, `verify_bearer_token`, `broker`, `manager.active_connections`.
**Produz:** `ClaudePermissionHookInput(tool_name: str, tool_input: dict = {}, cwd: str = "", session_id: str | None = None)`,
com `model_config = ConfigDict(extra="ignore")`. Também `POST /api/v1/claude/permission` → `200 {"behavior": ...}` ou `204`.

- [ ] Testes (`loopback_override`, Bearer válido; `broker` monkeypatched com uma instância de `timeout_s` curto):
  `test_hook_forbidden_from_lan` (403); `test_hook_requires_token` (401); `test_hook_no_clients_204`;
  `test_hook_allow_flow` (com conexão fake em `manager.active_connections`, uma task resolve "allow"
  → 200 `{"behavior":"allow"}`); `test_hook_deny_flow`; `test_hook_timeout_204`;
  `test_hook_minimal_body` (`{"tool_name":"mcp__srv__tool"}` → não 422); `test_hook_full_204`.
- [ ] Implementar: `asyncio.wait` corre `broker.wait(rid)` contra `_watch_disconnect(request)`, que verifica
  `await request.is_disconnected()` a cada 1 s. Se desconectar, chama `broker.cancel(rid)` e retorna 204.
  Cancelar a task perdedora.
- [ ] Ver os testes passando e a suíte verde. Commit `feat(claude): rota do hook PermissionRequest`.

### Task 4: Ação WebSocket e reenvio ao reconectar · Agente: `streamdeck_backend`
**Arquivos:** Modify `backend/schemas/deck_schemas.py` (`DeckActionPayload`), `backend/routers/deck_router.py`
(`ACTION_HANDLERS` e o handshake após `auth_success`); Test `backend/tests/test_action_handlers.py`.
**Produz:** os campos `request_id: Optional[str] = Field(None, max_length=64)` e `decision: Optional[Literal["allow","deny"]] = None`,
a ação `"claude_permission_response"` e `handle_claude_permission_response(websocket, command)`.

- [ ] Testes: adicionar `"claude_permission_response"` em `test_action_handlers_registry`;
  `test_permission_response_resolves` (broker mock → `resolve` awaited com `("abc","allow")`);
  `test_permission_response_unknown_id` (`resolve` → False → `send_json` com `status:"error"` e
  `message:"Pedido expirado"`); `test_permission_response_invalid_decision` (`DeckActionPayload(decision="maybe")`
  → `ValidationError`); `test_pending_resent_on_auth` (após `auth_success`, cada item de
  `broker.pending_messages()` é enviado ao socket).
- [ ] Implementar, rodar a suíte e confirmar que está verde.
- [ ] Commit `feat(claude): resposta de permissao via WebSocket`.
