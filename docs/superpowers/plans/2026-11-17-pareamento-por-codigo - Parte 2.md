# Pareamento por Código — Plano (Parte 2)

Continuação de [[2026-11-17-pareamento-por-codigo]]. As restrições globais e o foco de revisão de lá
valem aqui.

### Task 4: Rotas de pareamento · Agente: `streamdeck_backend`
**Arquivos:** Create `backend/routers/pairing_router.py`; Modify `backend/schemas/deck_schemas.py`,
`backend/main.py` (`include_router`); Test `backend/tests/test_pairing_router.py`.
**Consome:** `require_lan`/`lan_override` (T1), `pairing_service.pairing` (T2, acessado pelo módulo em
tempo de chamada, para o monkeypatch funcionar).
**Produz:**
- `PairConfirmInput(pair_id: str = Field(max_length=64), code: str = Field(pattern=r"^\d{4}$"))`.
- `POST /api/v1/deck/pair/request` e `POST /api/v1/deck/pair/confirm`, ambas `Depends(require_lan)`,
  devolvendo `JSONResponse(status_code, body)` do serviço. IP do cliente = `request.client.host`
  (em teste com override use o valor que o `TestClient` der).
- [ ] Testes (`lan_override`; `pairing` monkeypatched com instância de `notify` mock):
  `test_pair_request_forbidden_without_override` (403); `test_pair_flow_ok` (request → código
  capturado do mock → confirm → 200 com `auth_token == test_token`); `test_pair_confirm_wrong_401`;
  `test_pair_confirm_bad_code_422` (`"12a4"`); `test_pair_request_503_when_notify_fails`;
  `test_pair_responses_never_contain_code`.
- [ ] Ver falhar, implementar, suíte verde. Commit `feat(pairing): rotas de pedido e confirmacao`.

### Task 5: `useWebSocket` e contrato do `SettingsModal` · Agente: `streamdeck_frontend`
**Arquivos:** Modify `frontend/src/hooks/useWebSocket.js`, `frontend/src/components/SettingsModal.jsx`,
`frontend/src/App.jsx`.
**Produz (`useWebSocket(url, authToken, { onAuthRejected })`):**
- close `4401` → status `'ERROR'`, sem reconectar, chama `onAuthRejected()`.
- close `1008` → volta ao fluxo normal de `scheduleReconnect()` (desfaz a parada de retry atual).
- [ ] `App.jsx`: `onAuthRejected` apaga `STORAGE_KEY_TOKEN` e faz `setAuthToken('')`.
  `handleSaveSettings({ url })` só mexe na URL. Novo `handleRepair()` apaga o token. **Uma única**
  instância de `SettingsModal` (fora do ramo do blackout, renderizada nos dois casos).
- [ ] `SettingsModal({ isOpen, onClose, currentUrl, onSave, onRepair })`: sem campo de token nem
  "Copiar Link de Conexão"; `url` ressincronizado com `currentUrl` a cada abertura (`useEffect` em
  `isOpen`); botão **Parear de novo** (salva a URL se mudou e chama `onRepair`); "Restaurar Padrão"
  só restaura a URL.
- [ ] `grep -n "currentAuthToken\|setToken" frontend/src` vazio; build verde.
  Commit `fix(pwa): token so muda por pareamento e 4401 volta para a tela de pareamento`.

### Task 6: `PairingScreen` · Agente: `streamdeck_frontend`
**Arquivos:** Create `frontend/src/components/PairingScreen.jsx`, `frontend/src/utils/apiBase.js`;
Modify `frontend/src/App.jsx`, `frontend/src/App.css`.
**Produz:** `httpBaseFromWs(wsUrl: string) -> string` (`new URL`; `ws:`→`http:`, `wss:`→`https:`,
mantém host e porta, sem path) e `PairingScreen({ wsUrl, onPaired, onOpenSettings })`.
- [ ] Sem token → `App` renderiza `PairingScreen` em tela cheia no lugar do deck (e não o aviso
  "Abra o link de pareamento").
- [ ] Estado 1: botão **Parear com o PC** (≥ 48 px) e "O código aparece numa notificação no PC".
  `POST {base}/api/v1/deck/pair/request`.
- [ ] Estado 2: 4 campos de 1 dígito (`inputMode="numeric"`, autoavanço, Backspace volta, colar
  "1234" preenche tudo); envia ao completar o 4º; contagem `m:ss`; dica fixa "Não apareceu? Veja as
  notificações (Win+N)"; botão "Gerar novo código" desabilitado durante `retry_after`.
- [ ] Respostas: 200 confirm → `onPaired(auth_token)` (App salva no `localStorage`, `setAuthToken`,
  toast "Pareado!"); 401 → "Código errado — N tentativas restantes" e limpa os campos; 410 → "Expirou —
  gere outro" e volta ao estado 1; 429 → "Aguarde N s"; 423 → "Muitas tentativas — tente em N min";
  503 → "Não consegui mostrar o código no PC"; falha de rede → "Sem conexão com o PC".
- [ ] Link discreto **Endereço do PC** → `onOpenSettings()`. Tema OLED, sem `innerHTML`.
- [ ] Build verde. Commit `feat(pwa): tela de pareamento por codigo`.

### Task 7: E2E, revisão final e cofre · Claude + Gemini + `vault-guardian`
- [ ] Reiniciar o backend (pedir confirmação ao usuário) e instalar as dependências novas no venv.
- [ ] E2E no Mi 9 com o usuário: apagar o token (Parear de novo) → Parear → toast no PC → digitar →
  conecta; código errado mostra tentativas; deixar expirar; desligar e religar o PC → continua pareado.
- [ ] Revisão final do diff da branch pelo Gemini (`gemini-4-hydrogen-xhigh`, `--mode plan`) contra o
  spec, focando no Foco de revisão. Uma onda de correção pelos agentes de domínio.
- [ ] `vault-guardian`: atualizar `StreamDeck-Mi9/` (nota de pareamento, SEC) e `.agents/MEMORY.md`
  (sem commitar o cofre sem o usuário pedir).
- [ ] Suíte e build verdes; relatório final.
