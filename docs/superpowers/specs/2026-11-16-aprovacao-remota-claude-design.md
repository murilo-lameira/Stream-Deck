# Aprovação remota do Claude Code pelo Stream Deck — Design

**Data:** 2026-11-16 · **Branch base:** `feat/claude-app`

## 1. Intenção
O Mi 9 fica fixo no setup, sempre ligado e com o PWA aberto. O usuário manda uma
tarefa ao Claude Code no PC e vai para outra tela (vídeo, jogo). Quando o Claude pede
permissão, o pedido fica parado numa janela que ele não está olhando. O objetivo é que
o pedido apareça no Mi 9 e seja respondido ali com **Permitir** ou **Negar**.

Inspirado no projeto "Phone Box" (reel do @igao.ia). Daquele projeto, este escopo só
traz a aprovação remota.

## 2. Objetivos, não-objetivos e anti-objetivos
**Objetivos**
- Mostrar no Mi 9 cada pedido de permissão do Claude Code: ferramenta, comando ou
  arquivo e projeto.
- Responder Permitir/Negar pelo celular, e a resposta destrava o Claude na hora.
- Fechar as brechas de token que hoje permitiriam a qualquer um na LAN responder.

**Não-objetivos**
- Notificação push com o PWA fechado (exige HTTPS, que não existe hoje).
- Painel de sessões, consumo e limites, e o hook `Notification`. Ficam para depois.
- QR code de pareamento.
- "Permitir sempre" (`updatedPermissions`).

**Anti-objetivos (é falha mesmo que funcione)**
- Qualquer caminho de erro que **aprove** sozinho. Toda falha cai no prompt normal do PC.
- A rota do hook acessível pela rede local.
- O Claude ficar travado mais que o timeout quando o celular some.

## 3. Abordagens consideradas
| | Abordagem | Prós | Contras |
|---|---|---|---|
| A | Hook `type: "http"` direto no backend | Sem script, só config | Comportamento com backend desligado não está claro na doc (risco de seguir sem perguntar). Envio do token em header não foi confirmado. |
| **B** | **Hook `type: "command"` → script Python → backend** | Toda falha vira "sem decisão" e cai no prompt do PC. O token é lido do `.env`. | Um arquivo a mais |
| C | Só o hook `Notification` (avisa, aprova no PC) | Trivial | Não resolve: o usuário continua precisando ir ao PC |

**Escolhida: B** (decisão do usuário). Com ela, o pior caso é o fluxo de hoje.

## 4. Fluxo
```
Claude Code ──PermissionRequest (stdin JSON)──▶ scripts/claude_permission_hook.py
   script ──POST 127.0.0.1:8000/api/v1/claude/permission (Bearer)──▶ backend
   backend ──broadcast WS "claude_permission_request"──▶ Mi 9 (modal)
   Mi 9 ──WS action "claude_permission_response"──▶ backend resolve o Future
   backend ──200 {"behavior": "allow"|"deny"}──▶ script ──stdout hookSpecificOutput──▶ Claude
```

## 5. Contrato do hook (Claude Code)
Entrada em stdin (campos usados): `session_id`, `cwd`, `hook_event_name`, `tool_name`,
`tool_input`. Saída quando houver decisão:
```json
{"hookSpecificOutput": {"hookEventName": "PermissionRequest",
  "decision": {"behavior": "deny", "message": "Negado pelo Stream Deck (celular)."}}}
```
Para allow: `{"behavior": "allow"}`, sem `updatedInput`. **Sem decisão = sair com código 0 e
stdout vazio**, e o Claude mostra o prompt normal no PC. Regras `deny` do usuário
continuam valendo mesmo com allow (comportamento do Claude Code).

## 6. Script `scripts/claude_permission_hook.py`
- Só biblioteca padrão (`json`, `urllib.request`, `sys`, `pathlib`), para rodar com o Python
  do venv sem dependências.
- Lê o `AUTH_TOKEN` de `backend/.env` (caminho relativo ao script). Sem token → sai sem decisão.
- POST com `Authorization: Bearer <token>` e timeout de rede de **125 s**.
- Resposta `200` com `behavior` válido → imprime o JSON da seção 5. Qualquer outra coisa
  (`204`, `4xx`/`5xx`, conexão recusada, timeout, JSON inválido) → sai 0 sem stdout.
- Nunca escreve nada em stdout fora da decisão. Logs vão para stderr.

**Registro do hook** (decisão do Claude): em `~/.claude/settings.json` do usuário, para
valer em qualquer projeto. A instalação é feita após a aprovação do plano.
```json
{"hooks": {"PermissionRequest": [{"matcher": "*", "hooks": [{"type": "command",
  "command": "\"F:/Faculdade/Projetos/Stream Deck/backend/venv/Scripts/python.exe\" -I \"F:/Faculdade/Projetos/Stream Deck/scripts/claude_permission_hook.py\"",
  "timeout": 150}]}]}}
```
O `timeout` do hook (150 s) é maior que o do script (125 s), que é maior que o do backend (120 s).
Assim o script sempre termina limpo antes de ser morto.

## 7. Backend
**Novo serviço `backend/services/claude_permission_service.py`**
- `pending: dict[str, PendingRequest]`, em que `PendingRequest` guarda um `asyncio.Future` e metadados.
- `request_id = secrets.token_urlsafe(16)`.
- `summarize(tool_name, tool_input) -> str`: `Bash` → `command`; `Edit`/`Write`/`Read` →
  `file_path`; o resto → `json.dumps` compacto. Corta em **300 caracteres**.
- Projeto exibido = nome da pasta de `cwd` (não o caminho completo).

**Nova rota `POST /api/v1/claude/permission`** (router novo `routers/claude_router.py`)
1. Rejeita com `403` se `request.client.host` não for `127.0.0.1`/`::1`.
2. Exige Bearer via `verify_bearer_token` (`401`).
3. Valida o corpo com Pydantic (`ClaudePermissionHookInput`, com campos extras ignorados).
4. Sem nenhuma conexão WS autenticada (`manager.active_connections` vazio) → `204` na hora.
5. Cria o pedido e faz broadcast de:
   `{"type":"claude_permission_request","request_id","tool_name","summary","project","expires_in":120}`
6. `await asyncio.wait_for(future, 120)`.
   - Resolvido → `200 {"behavior": ...}` e broadcast de
     `{"type":"claude_permission_resolved","request_id","outcome":"allow"|"deny"}`.
   - Timeout → broadcast com `outcome:"expired"` e retorna `204`.
   - Cliente HTTP desconectou (o Claude cancelou) → remove o pedido, broadcast com `"cancelled"`.
     Como o FastAPI não cancela o handler sozinho, uma tarefa paralela verifica
     `request.is_disconnected()` a cada 1 s (decisão do Claude, com teste).
7. Sempre remove de `pending` no `finally`.
8. Limite de **10 pedidos pendentes**. Acima disso → `204` imediato, e o pedido vai para o
   PC (decisão do Claude).

Conexão WS morta na lista: aceita-se que o fallback aconteça só após os 120 s, sem
heartbeat novo (decisão do Claude, para manter simples).

**WebSocket**: nova ação `claude_permission_response` em `ACTION_HANDLERS`, com novos
campos opcionais no `DeckActionPayload`: `request_id: str | None` e
`decision: Literal["allow","deny"] | None`. A primeira resposta vence. `request_id`
desconhecido ou já resolvido → `action_result` de erro "Pedido expirado".

Não há chamadas bloqueantes (Win32/COM), então `asyncio.to_thread` não é necessário.

**Reconexão do celular**: ao autenticar no WS, o backend reenvia os pedidos ainda pendentes
para aquele cliente, com o `expires_in` restante.

## 8. Frontend (PWA)
- Novo `components/ClaudePermissionModal.jsx`. O `ConfirmModal` não é reaproveitado porque
  tem o texto "Desligar Agora" fixo.
- `useWebSocket` trata `claude_permission_request` e `claude_permission_resolved` e expõe uma
  fila de pedidos e `respondPermission(request_id, decision)`.
- O modal mostra: ferramenta, projeto, resumo (fonte monoespaçada, texto puro, nunca
  `innerHTML`), contagem regressiva e "1 de N" quando houver fila.
- Botões grandes: **Negar** (esquerda, cinza) e **Permitir** (direita, verde). Tocar no
  fundo **não** fecha o modal.
- Ao chegar um pedido: `navigator.vibrate` (padrão já usado nos haptics).
- Ao receber `resolved` (ou expirar), remove o pedido da fila e mostra um toast.

```
┌──────────────────────────────┐
│ ⚠ Claude pede permissão  1/1 │
│ Bash · Stream Deck           │
│ ┌──────────────────────────┐ │
│ │ npm --prefix frontend ru…│ │
│ └──────────────────────────┘ │
│ expira em 1:47               │
│ [  Negar  ]   [ Permitir ]   │
└──────────────────────────────┘
```

## 9. Segurança (entra junto)
1. `is_valid_token` **deixa de aceitar** `mi9_deck_secret_2026`. O `get_auth_token` continua
   rotacionando se o `.env` ainda tiver esse valor.
2. Frontend: remove `DEFAULT_AUTH_TOKEN` de `config/constants.js`, do fallback em `App.jsx`
   e do botão de reset em `SettingsModal.jsx`. Sem token salvo, mostra o aviso
   "Abra o link de pareamento".
3. `GET /api/v1/deck/pairing` passa a responder só para loopback (`403` para LAN) e monta a
   URL **sempre com `get_local_ip()`**. Hoje ela usa `request.url.hostname`, o que geraria
   um link `localhost` inútil para o Mi 9.
4. A nova rota do hook exige loopback **e** Bearer.
5. A checagem de loopback vira uma dependência FastAPI (`require_loopback`). Os testes a
   sobrescrevem via `app.dependency_overrides`, porque o `TestClient` usa o host
   `"testclient"`. Há também um teste próprio que prova o 403 para um host de LAN.
6. Testes afetados: `test_action_handlers_registry` (conjunto exato de ações) e
   `test_endpoint_get_pairing_info` (passa a precisar da sobrescrita de loopback).

Nenhuma automação (n8n, Alexa, `/api/trigger`) usa o token antigo (confirmado pelo usuário),
então não há migração a fazer.

**Repareamento (custo único):** o usuário abre `http://localhost:8000/api/v1/deck/pairing`
no PC, copia o `pairing_url` e abre esse link no Mi 9. A URL também já aparece no log de
inicialização.

## 10. Testes (Pytest)
- Rota: não loopback → 403; token inválido → 401; sem clientes WS → 204; fluxo allow e
  fluxo deny; timeout → 204 + broadcast `expired` (timeout injetável para o teste ser rápido).
- WS: resposta com id desconhecido; `decision` inválida rejeitada pelo Pydantic; primeira
  resposta vence.
- Auth: o token antigo é rejeitado; pairing via LAN → 403.
- Script: funções puras testáveis (`build_output`, `load_token`), e servidor indisponível →
  stdout vazio.
- Build do frontend: `npm --prefix frontend run build`.

## 11. Divisão entre os agentes
- `streamdeck_architect`: revisa o contrato (seções 5, 7 e 9) antes e o diff no fim.
- `streamdeck_backend`: seções 6, 7 e 9 (backend) e o script.
- `streamdeck_frontend`: seções 8 e 9 (frontend).
- `streamdeck_qa`: seção 10.
- `vault-guardian`: nota no cofre `StreamDeck-Mi9/` e `MEMORY.md`.

## 12. Riscos e pontos a verificar
- Confirmar na prática que o app desktop do Claude (aba Code) executa hooks de
  `~/.claude/settings.json`. Se não executar, vale só para o CLI.
- Enquanto o hook espera, o prompt do PC não aparece. O teto de 2 min limita isso.

## 13. Deixado para quem implementa
Nomes internos, estilo visual exato do modal (seguindo o tema OLED), padrão de vibração e a
mensagem do toast.
