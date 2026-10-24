# 🛡️ Backlog de Auditoria Técnica, Segurança & Performance

Este documento reúne todos os apontamentos identificados na auditoria técnica de AppSec, Concorrência e UX Mobile do Stream Deck Mi9, estruturados por prioridade de mitigação.

---

## 🔒 1. Segurança & Hardening (AppSec)

- [x] **SEC-01 `[CRÍTICO]` Mitigação de Path Traversal no Servidor Estático:**
  - **Arquivo:** `backend/main.py:98-103`
  - **Problema:** Concatenação de `full_path` sem validação de caminho canônico permitia download de arquivos fora de `frontend/dist`.
  - **Status:** Concluído e coberto por testes automatizados (`test_static_path_traversal_prevention`).

- [x] **SEC-02 `[CRÍTICO]` Proteção contra Cross-Site WebSocket Hijacking (CSWSH):**
  - **Arquivo:** `backend/routers/deck_router.py:101-117` e `backend/main.py:68-74`
  - **Problema:** Ausência de validação de `Origin` no handshake do WebSocket.
  - **Status:** Concluído e coberto por testes automatizados (`test_websocket_rejects_unauthorized_origin`).

- [x] **SEC-03 `[ALTO]` Autenticação Obrigatória em Todos os Endpoints Modificadores:**
  - **Arquivo:** `backend/routers/deck_router.py:40-53` e `backend/main.py:83-89`
  - **Problema:** `PUT /api/v1/deck/catalog` e `/api/agents/orchestrate` abertos sem exigir Bearer Token.
  - **Status:** Concluído e coberto por testes automatizados (`test_put_catalog_requires_auth`, `test_orchestrate_requires_auth`).

- [x] **SEC-04 `[ALTO]` Bloqueio de SSRF no Disparador de Webhooks:**
  - **Arquivo:** `backend/services/macro_service.py:80-90`
  - **Problema:** Ação `call_webhook` permitia envio de requisições arbitrárias para `localhost` e interfaces restritas da LAN.
  - **Status:** Concluído e coberto por testes automatizados (`test_dispatch_webhook_ssrf_protection`).

- [x] **SEC-05 `[MÉDIO]` Geração Criptográfica e Rotação do Token de Pareamento:**
  - **Arquivo:** `backend/routers/deck_router.py:18` e `.env`
  - **Problema:** Token padrão estático compartilhado no repositório. Criar gerador `secrets.token_urlsafe(32)` com pareamento por QR Code.

- [x] **SEC-06 `[BAIXO]` Timeout Estrito no Handshake WebSocket (Slowloris DoS):**
  - **Arquivo:** `backend/routers/deck_router.py:107-109`
  - **Problema:** Conexões pendentes sem envio de token travam o socket indefinidamente. Aplicado timeout de 5 segundos.
  - **Status:** Concluído e validado.

---

## ⚡ 2. Desempenho & Concorrência

- [x] **PERF-01 `[ALTO]` Desacoplamento Assíncrono de Chamadas COM/Pycaw:**
  - **Arquivo:** `backend/routers/deck_router.py:77, 82, 87, 122, 194, 201, 208`
  - **Problema:** Chamadas síncronas para `IAudioEndpointVolume` congelavam o loop principal do FastAPI/Uvicorn.
  - **Status:** Concluído com delegação para `asyncio.to_thread`.

- [x] **PERF-02 `[MÉDIO]` Otimização do Payload de Capas de Mídia (Thumbnail):**
  - **Arquivo:** `backend/services/telemetry_service.py:35, 68-78` e `backend/routers/deck_router.py:63-101`
  - **Problema:** Transmissão de Base64 de até 180KB a cada ciclo de telemetria.
  - **Status:** Concluído com endpoint REST `/api/v1/deck/media/art`, cabeçalhos ETag, suporte a 304 Not Modified e cache HTTP. Payload WebSocket reduzido para < 1KB.

- [x] **PERF-03 `[MÉDIO]` Algoritmo Drop-Oldest no Controle Analógico de Volume:**
  - **Arquivo:** `frontend/src/components/VolumeSlider.jsx:52-55`
  - **Problema:** Eliminar jitter e buffer bloat em redes Wi-Fi instáveis descartando amostras obsoletas no cliente.

---

## 📱 3. UI/UX & Resiliência Mobile

- [x] **UX-01 `[ALTO]` Modernização do Screen Wake Lock API:**
  - **Arquivo:** `frontend/src/hooks/useWakeLock.js:1-38`
  - **Problema:** Substituir uso exclusivo de `NoSleep.js` (vídeo oculto) por `navigator.wakeLock.request('screen')` nativo.
  - **Status:** Concluído com ciclo de vida W3C e fallback transparente.

- [x] **UX-02 `[MÉDIO]` Cooldown e Feedback Visual contra Cliques Repetidos:**
  - **Arquivo:** `frontend/src/components/DeckButton.jsx:27-46`
  - **Problema:** Evitar abertura de múltiplas instâncias de executáveis pesados no Windows com bloqueio temporário na UI.
  - **Status:** Concluído com cooldown de 800ms via `useRef` e feedback háptico sincronizado.

- [x] **UX-03 `[MÉDIO]` Isolamento de Gestos Conflitantes (Swiper vs. Slider):**
  - **Arquivo:** `frontend/src/components/DeckSwiper.jsx` e `VolumeSlider.jsx`
  - **Problema:** Evitar troca acidental de tela horizontal durante arraste vertical do volume.
  - **Status:** Concluído com `noSwiping={true}` e classe CSS `swiper-no-swiping` no container do slider.

---

## 🏗️ 4. Arquitetura & Qualidade de Código

- [x] **ARCH-01 `[MÉDIO]` Desacoplamento Modular de `apps_config.py`:**
  - Segregação de responsabilidades entre Registro de Apps, Driver Win32 ctypes e Gerenciador de Processos.
- [x] **ARCH-02 `[MÉDIO]` Higienização de Exceções Silenciosas em `media_service.py`:**
  - Substituição de blocos `pass` por telemetria e logs em nível `DEBUG`.
- [x] **ARCH-03 `[MÉDIO]` Command Registry Pattern no Roteador WebSocket:**
  - Substituição de cascata imperativa de `if/elif` por dicionário de handlers assíncronos tipados.

---

[[Features]]
[[Roadmap e Planejamento Futuro]]
[[MAIN]]