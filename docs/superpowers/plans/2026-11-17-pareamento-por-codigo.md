# Pareamento por Código — Plano de Implementação

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: superpowers:subagent-driven-development com os agentes do
> projeto (coluna "Agente"). **Revisor de cada task e da revisão final: Gemini via `agy`** (skill
> `gemini`, `--mode plan`, somente leitura), pedido do usuário. Continua em
> [[2026-11-17-pareamento-por-codigo - Parte 2]] (Tasks 5–7).

**Objetivo:** o Mi 9 pareia digitando um código de 4 dígitos mostrado numa notificação do Windows.
**Arquitetura:** `PairingService` em memória (código com hash, limites, trava) → `pairing_router`
(`require_lan`) → toast WinRT via `asyncio.to_thread`; PWA mostra `PairingScreen` sem token; `/ws`
fecha com `4401` quando o token é recusado.
**Stack:** FastAPI/Pydantic v2, pytest + pytest-asyncio, `winrt-Windows.UI.Notifications`, React 18 + Vite.
**Spec:** `docs/superpowers/specs/2026-11-17-pareamento-por-codigo-design.md`

## Restrições globais
- Código: `f"{secrets.randbelow(10000):04d}"`, só o hash SHA-256 é guardado, comparação `hmac.compare_digest`.
- `CODE_TTL_S = 120`, `MAX_ATTEMPTS = 5`, `REQUEST_COOLDOWN_S = 10` (por IP), `MAX_ACTIVE = 3`,
  `LOCK_MAX_WRONG = 15` em `LOCK_WINDOW_S = 900` (janela deslizante, global) → trava `LOCK_DURATION_S = 900`.
- O código **nunca** sai do backend exceto no toast. Nada de logar o código.
- `429`/`423` com corpo `{"retry_after": int}`. Token recusado no `/ws` → close `4401`.
- AUMID do toast: `{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe`.
- WinRT sempre em `asyncio.to_thread`. UTF-8 sem BOM, LF, `.md` ≤ 200 linhas.
- Testes: `backend\venv\Scripts\pytest backend\tests`. Build: `npm --prefix frontend run build`.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Nunca commitar
  `.agents/MEMORY.md`, `.claude/agents/streamdeck_qa.md`, `StreamDeck-Mi9/**`, `frontend/dist`. Sem `git stash`.

**Ordem de execução:** Task 1 → **Task 3** → Task 2 → Task 4 → 5 → 6 → 7 (o serviço da Task 2 importa
a notificação da Task 3).

## Foco de revisão
1. Burla da trava: trocar de pedido a cada 4 erros, ou espalhar chutes entre IPs → ainda trava em 15 (T2).
2. O código aparece em alguma resposta, log ou exceção (T2/T4).
3. Falha do toast (exceção) libera ou mantém pedido ativo → deve ficar sem pedido e `503` (T2/T4).
4. Aparelho pareado sofre timeout de handshake (`1008`) → deve reconectar, não cair no pareamento (T5).
5. Salvar só a URL nas configurações apaga o token (T5).

---

### Task 1: `require_lan` e close `4401` · Agente: `streamdeck_backend`
**Arquivos:** Modify `backend/routers/security_deps.py`, `backend/routers/deck_router.py` (fechamento
por token inválido, ~l. 344-348); Test `backend/tests/test_security_deps.py`,
`backend/tests/test_websocket_auth.py`; Modify `backend/tests/conftest.py`.
**Produz:** `require_lan(request: Request) -> None` (403 "Endpoint restrito a rede local.") e fixture
`lan_override` (mesmo padrão de `loopback_override`).
- Regras de `require_lan`: `client.host` é IP privado ou loopback (`ipaddress`; valor não-IP → 403);
  hostname do `Host` ∈ {`localhost`,`127.0.0.1`,`::1`,`streamdeck.local`} ou IP privado/loopback;
  `Origin`, se presente, pela mesma regra; `Sec-Fetch-Site: cross-site` → 403. Reusar `_host_from_header`.
- [ ] Testes (fake `Request`, como os de `require_loopback`): aceita cliente `192.168.15.20` com Host
  `192.168.15.16:8000`; aceita Host `streamdeck.local:8000`; rejeita cliente `8.8.8.8`; rejeita Host
  `evil.example:8000`; rejeita `Origin: http://evil.example`; rejeita `Sec-Fetch-Site: cross-site`;
  rejeita cliente `testclient`.
- [ ] `test_websocket_auth_invalid_token` passa a esperar `4401`; payload malformado e origem
  maliciosa continuam `1008`.
- [ ] Ver falhar, implementar, suíte verde. Commit `feat(security): guarda require_lan e close 4401 para token recusado`.

### Task 2: `PairingService` · Agente: `streamdeck_backend`
**Arquivos:** Create `backend/services/pairing_service.py`; Test `backend/tests/test_pairing_service.py`.
**Produz:**
- `class PairingService(notify: Callable[[str, str], bool], clock: Callable[[], float] = time.monotonic,
  token_provider: Callable[[], str] = get_auth_token)` com as constantes globais como atributos de classe.
- `async request(client_ip: str) -> tuple[int, dict]`: `(200, {"pair_id","expires_in":120})`,
  `(429, {"retry_after"})`, `(423, {"retry_after"})`, `(503, {"detail":"Não foi possível mostrar o código no PC"})`.
  Chama `await asyncio.to_thread(self.notify, code, client_ip)`; `False` ou exceção → 503 e nenhum pedido fica.
- `confirm(pair_id: str, code: str, client_ip: str) -> tuple[int, dict]`: `(200, {"auth_token"})`,
  `(401, {"attempts_left"})`, `(410, {"detail":"Código expirado ou inválido"})`, `(423, {"retry_after"})`.
  Chute errado conta na janela global; ao atingir 15 → trava e zera a janela; `pair_id` de outro IP → 410
  (não conta chute).
- Instância global: `pairing = PairingService(notification_service.show_pairing_code)`
  (`show_pairing_code` vem da Task 3, executada **antes** desta — ver ordem abaixo).
- [ ] Testes (relógio fake, `notify` = `MagicMock(return_value=True)` capturando o código):
  `test_code_is_4_digits_with_leading_zero` (monkeypatch `secrets.randbelow` → 7 → `"0007"`);
  `test_confirm_ok_returns_token_and_consumes`; `test_wrong_code_decrements_attempts`;
  `test_fifth_wrong_invalidates` (6ª → 410); `test_expired_410` (clock +121);
  `test_new_request_same_ip_replaces`; `test_confirm_other_ip_410`; `test_cooldown_429_retry_after`;
  `test_max_active_429`; `test_lock_after_15_wrong_even_rotating_requests` (4 erros, novo request,
  repetir → 423); `test_lock_releases_after_900s`; `test_notify_false_503_no_pending`;
  `test_notify_raises_503_no_pending`; `test_code_not_in_any_response` (nenhum corpo contém o código).
- [ ] Ver falhar, implementar, ver passar. Commit `feat(pairing): servico de pareamento por codigo`.

### Task 3: Notificação do Windows · Agente: `streamdeck_backend`
**Arquivos:** Create `backend/services/notification_service.py`; Modify `backend/requirements.txt`
(`winrt-Windows.UI.Notifications`, `winrt-Windows.Data.Xml.Dom`), instalar no venv.
**Produz:** `show_pairing_code(code: str, client_ip: str) -> bool` (síncrona; quem chama usa `to_thread`).
- Toast `ToastGeneric`: título "Stream Deck — código de pareamento"; corpo "`<código>` · expira em 2 min";
  linha "Pedido de `<ip>`. Se não foi você, ignore." Escapar XML (`xml.sax.saxutils.escape`).
  `ToastNotificationManager.create_toast_notifier(AUMID).show(...)`. Qualquer exceção → log sem o
  código → `False`.
- [ ] Teste: `test_show_pairing_code_returns_false_on_error` (monkeypatch do notifier para levantar).
- [ ] **Verificação manual:** `backend\venv\Scripts\python -I -c "import sys; sys.path.insert(0,'backend');
  from services.notification_service import show_pairing_code as s; print(s('1234','192.168.15.20'))"` →
  `True` **e** o toast aparece no PC. Se não aparecer: parar e reportar `BLOCKED` (não trocar de abordagem).
- [ ] Commit `feat(pairing): notificacao do Windows com o codigo`.

### Task 4: Rotas de pareamento · Agente: `streamdeck_backend`
Ver [[2026-11-17-pareamento-por-codigo - Parte 2]].
