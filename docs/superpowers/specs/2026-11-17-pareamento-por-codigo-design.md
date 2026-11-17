# Pareamento por código de 4 dígitos (notificação do Windows) — Design

**Data:** 2026-11-17 · **Branch base:** `feat/claude-app`

## 1. Intenção
O usuário não quer mais lidar com token (copiar link, colar, digitar). Quer parear o Mi 9
como um 2FA: toca em **Parear** no celular, aparece um código de 4 dígitos numa
**notificação do Windows** no PC, ele digita o código no celular e pronto — o celular fica
autorizado de vez. O token continua existindo por baixo dos panos, mas nunca é visto.

## 2. Objetivos, não-objetivos e anti-objetivos
**Objetivos**
- Parear sem copiar link nem ver token: um toque + 4 dígitos.
- Funcionar com o PC em outra tela (jogo, vídeo): o código vem por notificação do Windows.
- Depois de pareado, nunca mais pedir nada (token salvo no `localStorage`, como hoje).
- Avisar o usuário quando *qualquer* aparelho tentar parear (a notificação aparece no PC).

**Não-objetivos**
- Tokens por aparelho, lista de aparelhos pareados ou revogação individual.
- QR code, HTTPS, push no celular.
- Nome "Stream Deck" na notificação (pode aparecer como Python/PowerShell; fica para depois).

**Anti-objetivos (é falha mesmo que funcione)**
- O código chegar ao celular por qualquer caminho que não seja o usuário digitando
  (resposta HTTP, log acessível pela rede, WebSocket).
- Adivinhar o código por força bruta ser viável.
- Falha ao mostrar a notificação resultar em pareamento liberado.
- Mudar o contrato do hook do Claude ou do WebSocket (`auth_token` no handshake continua igual).

## 3. Abordagens consideradas (como mostrar a notificação)
| | Abordagem | Prós | Contras |
|---|---|---|---|
| **1** | **`winrt-Windows.UI.Notifications`** | Mesma família `winrt` já usada na mídia; API oficial; 1 dependência pequena | Precisa de um AppUserModelID registrado; o nome exibido pode ser "Python"/"PowerShell" |
| 2 | Subprocesso PowerShell | Zero dependência | ~0,5 s por chamada; script em string, frágil |
| 3 | `win11toast`/`winotify` | 1 linha | Dependência de terceiro embrulhando a mesma API |

**Escolhida: 1** (decisão do usuário).

## 4. Fluxo
```
Mi 9 (sem token válido) ── toca "Parear" ──▶ POST /api/v1/deck/pair/request
   backend gera código (4 dígitos), guarda hash + validade, mostra toast no Windows
   backend ──▶ {"pair_id", "expires_in": 120}            (NUNCA o código)
Usuário lê o código no PC e digita no Mi 9
Mi 9 ── POST /api/v1/deck/pair/confirm {"pair_id","code"} ──▶ backend
   certo  → 200 {"auth_token"} → PWA salva no localStorage e conecta no /ws (fluxo atual)
   errado → 401 {"attempts_left"}; na 5ª falha o pedido é invalidado
```

## 5. Backend
**Novo serviço `backend/services/pairing_service.py`** (estado só em memória, relógio injetável)
- Pedidos por IP do cliente: `{pair_id, client_ip, code_hash, expires_at, attempts}`.
  - `pair_id = secrets.token_urlsafe(16)`; código = `f"{secrets.randbelow(10000):04d}"`.
  - Guarda só o hash do código (`hashlib.sha256`); compara com `hmac.compare_digest`.
  - No máximo **1 pedido ativo por IP** (novo `request` do mesmo IP substitui o anterior) e
    no máximo **3 pedidos ativos no total** (acima disso → `429`).
  - `confirm` só vale do **mesmo IP** que fez o `request` (senão `410`).
- Limites (decisão do Claude, para tornar força bruta inviável):
  - Validade do código: **120 s**. Uso único: some ao acertar.
  - **5 tentativas** por código; na 5ª errada o pedido é invalidado.
  - Intervalo mínimo entre `request`s do mesmo IP: **10 s** → `429`.
  - **Trava global por chutes errados** (revisão Gemini: contar pedidos invalidados era
    burlável trocando de código após 4 erros): **15 chutes errados em janela deslizante de
    15 min**, somando todos os IPs e pedidos (substituídos ou expirados contam igual) →
    pareamento bloqueado por **15 min** (`423`); ao fim da trava o histórico zera. Teto real:
    15 chutes a cada ~15 min (10.000 códigos → anos).
  - `429`/`423` trazem `{"retry_after": <segundos>}`.
- Trava causada por um aparelho estranho na LAN bloqueia também o celular legítimo (DoS
  aceito, decisão do Claude); o pareamento por link (`GET /api/v1/deck/pairing`, loopback)
  continua funcionando durante a trava.
- Todas as chamadas WinRT em `asyncio.to_thread` (regra do AGENTS.md).

**Notificação (`backend/services/notification_service.py`)**
- `show_pairing_code(code: str, client_ip: str) -> bool` usando
  `winrt-Windows.UI.Notifications` (+ `winrt-Windows.Data.Xml.Dom` para o XML do toast).
- Texto: título "Stream Deck — código de pareamento", corpo "**1234** · expira em 2 min",
  linha "Pedido de 192.168.x.y. Se não foi você, ignore."
- AppUserModelID: usar o do PowerShell
  (`{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe`), que já
  vem registrado no Windows; o toast aparece como "Windows PowerShell". O construtor
  **verifica na prática** que o toast aparece e registra o resultado.
- Se mostrar lançar exceção → retorna `False` → a rota responde `503` "Não foi possível
  mostrar o código no PC" e **descarta** o pedido. Toast suprimido sem exceção (Foco
  Assistido) não é detectável: o usuário usa Win+N ou gera outro código. Sem fallback para
  PowerShell em subprocesso (mesma API). Nunca há caminho que revele o código ao celular.

**Guarda de rede `require_lan`** (nova, em `routers/security_deps.py`, no padrão de
`require_loopback`; revisão Gemini — o CORS do app é `allow_origins=["*"]`):
- `request.client.host` privado ou loopback (`ipaddress`), senão `403`;
- hostname do `Host` ∈ {`localhost`, `127.0.0.1`, `::1`, `streamdeck.local`} ou IP privado
  (anti DNS rebinding), senão `403`;
- `Origin`, se presente, com hostname na mesma regra, senão `403`;
- `Sec-Fetch-Site == "cross-site"` → `403`.
- Testes usam override (como `loopback_override`), pois o `TestClient` usa `testclient`.

**Rotas novas** em `routers/pairing_router.py`, ambas com `Depends(require_lan)`:
- `POST /api/v1/deck/pair/request` — sem token (é justamente quem não tem).
  Respostas: `200 {"pair_id","expires_in"}`, `429`, `423`, `503`.
- `POST /api/v1/deck/pair/confirm` — corpo Pydantic `{pair_id: str (≤64), code: str (^\d{4}$)}`.
  Respostas: `200 {"auth_token"}`, `401 {"attempts_left"}`, `410` (expirado, invalidado,
  outro IP ou `pair_id` desconhecido), `423` (trava global).

**WebSocket — código de fechamento próprio para token recusado** (revisão Gemini: hoje o
`/ws` fecha com `1008` por 5 motivos, inclusive timeout e erro interno):
- Token inválido passa a fechar com **`4401`** (reason "Token de autenticacao invalido").
  Origem rejeitada, timeout, payload malformado e erro no handshake continuam `1008`.
- Atualizar o teste existente que espera `1008` para token inválido.
- O token entregue é o `get_auth_token()` atual (mesmo token para todos os aparelhos).
- Nada é logado com o código. O log registra só "pedido de pareamento de <ip>" e o resultado.

**Mantido como está:** `GET /api/v1/deck/pairing` (loopback, fallback por link), o
`?token=` na URL do PWA, o handshake do `/ws`, o hook do Claude.

## 6. Frontend (PWA)
- **`useWebSocket`:**
  - Fechamento **`4401`** (token recusado) → **apaga o token** (`localStorage` e estado) e
    não reconecta. Sem token, `connect()` já não abre socket, então `visibilitychange` e
    `online` não tiram o app da tela de pareamento.
  - `1008` volta a reconectar normalmente (desfaz a parada de retry por `1008` feita em
    2026-11-16, que travaria um aparelho pareado após um timeout passageiro).
- **Tela de pareamento** (novo `components/PairingScreen.jsx`), em tela cheia no lugar do
  deck, mostrada sempre que não há token (inclusive após `4401`). Substitui o aviso "Abra o
  link de pareamento". Tem um link discreto **Endereço do PC** que abre o `SettingsModal`.
  - Estado 1: botão grande **Parear com o PC** + "O código aparece numa notificação no PC".
  - Estado 2: 4 campos de dígito (`inputMode="numeric"`, autoavanço, colar 4 dígitos
    funciona), contagem regressiva, dica fixa "Não apareceu? Veja as notificações (Win+N)"
    e botão "Gerar novo código" (desabilitado durante o `retry_after` de um `429`).
  - Erros: "Código errado — N tentativas restantes", "Expirou — gere outro",
    "Aguarde N s", "Muitas tentativas — tente em N min", "Não consegui mostrar o código no PC".
  - Sucesso: salva o token (`STORAGE_KEY_TOKEN`), `setAuthToken`, conecta; toast "Pareado!".
- Base da API HTTP: `new URL(wsUrl)` trocando `ws:`→`http:` e `wss:`→`https:`, mantendo
  host e porta (ignora o path).
- **SettingsModal** (contrato muda; revisão Gemini — hoje salvar regrava o token):
  - Sai o campo "Token de Autenticação" e o botão "Copiar Link de Conexão".
  - `onSave({ url })` só mexe na URL; `App` nunca grava token a partir do modal.
  - O campo de URL é sincronizado com `currentUrl` a cada abertura.
  - Novo botão **Parear de novo** → callback `onRepair()` que apaga o token (o app cai na
    tela de pareamento) e fecha o modal. Se houver URL editada, ela é salva antes.
  - "Restaurar Padrão" só restaura a URL. Uma única instância do modal em `App.jsx`
    (hoje há duas, uma no blackout).
- Tema OLED, botões ≥ 48 px, sem `innerHTML`.

## 7. Testes
- Pytest (serviço, com relógio e notificação injetáveis/mocados):
  código com 4 dígitos e zero à esquerda; acerto devolve token e consome o pedido;
  erro decrementa `attempts_left`; 5ª falha invalida (`410` depois); expiração (`410`);
  `request` novo do mesmo IP invalida o anterior; `confirm` de outro IP → `410`; cooldown
  10 s por IP e limite de 3 pedidos ativos (`429` com `retry_after`); trava após 15 chutes
  errados em 15 min **mesmo trocando de pedido a cada 4 erros** (`423`) e liberação após
  15 min; falha da notificação → `503` e nenhum pedido fica ativo; `require_lan`: IP
  público, `Host` externo, `Origin` externo e `Sec-Fetch-Site: cross-site` → `403`; o
  código nunca aparece em nenhuma resposta (`assert code not in response.text`); `code`
  não numérico → `422`; `/ws` com token inválido fecha com `4401` e com timeout segue `1008`.
- Notificação real: verificação manual (o toast aparece com o código) — registrar.
- Frontend: `npm --prefix frontend run build` + E2E manual no Mi 9.

## 8. Divisão entre os agentes
- `streamdeck_backend`: seção 5 + testes. `streamdeck_frontend`: seção 6.
- **Revisor:** Gemini via CLI do Antigravity (`agy`, skill `gemini`, somente leitura) revisa
  cada task e o diff final (pedido do usuário). `vault-guardian`: nota no cofre.

## 9. Riscos e pontos a verificar
- Toast de app não empacotado exige AUMID registrado; se o do PowerShell não funcionar
  nesta máquina, parar e avisar o usuário (não trocar de abordagem por conta própria).
- Foco Assistido / "Não perturbe" do Windows em jogo pode esconder o toast: ele fica na
  Central de Notificações (Win+N). Documentar na tela de pareamento.

## 10. Deixado para quem implementa
Nomes internos, layout exato da tela de pareamento (tema OLED), texto final dos erros,
se as rotas ficam num router novo.
