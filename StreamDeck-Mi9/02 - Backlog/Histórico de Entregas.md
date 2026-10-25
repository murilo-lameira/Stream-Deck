# 📜 Histórico de Entregas (Versões V1 a V8)

Registro cronológico das funcionalidades concebidas, desenvolvidas e validadas no Stream Deck Mobile.

## Versão V8.7 - Otimização de Performance, ETag & UX Tátil
- [x] **Endpoint REST para Capas de Mídia (PERF-02):** Novo endpoint /api/v1/deck/media/art com ETag e cache HTTP, reduzindo o payload WebSocket de 150KB para < 1KB.
- [x] **Cooldown Anti-Duplo Clique (UX-02):** Cooldown de 800ms em DeckButton.jsx via useRef.
- [x] **Isolamento de Gestos Swiper (UX-03):** swiper-no-swiping no VolumeSlider.jsx.
- [x] **Testes Automatizados:** 35 testes aprovados no Pytest e build do Vite validado.

---

## Versão V8.9 - Restauração de Gestos no Swiper & Compatibilidade de Pareamento
- [x] **Restauração de Arraste de Slides no Swiper:** Remoção de `button` do parâmetro `focusableElements` do Swiper (`DeckSwiper.jsx`), permitindo deslizar páginas mesmo iniciando o toque sobre qualquer botão do grid.
- [x] **Arbitragem Anti-Disparo Acidental:** Ativação de `preventClicks={true}`, `preventClicksPropagation={true}` e guarda `if (e.defaultPrevented) return;` em `DeckButton.jsx` impedindo a execução de apps durante o arrasto de páginas.
- [x] **Isolamento de Gestos & Aceleração Touch:** Atualização para `noSwipingSelector=".swiper-no-swiping"`, sensibilidade `touchRatio={1.2}`, threshold de 8px e CSS `touch-action: pan-y;` contra interceptação do Chrome Android.
- [x] **Retrocompatibilidade de Autenticação WebSocket:** Implementação de `is_valid_token()` em `auth_service.py` aceitando token persistido e rotação dinâmica com tolerância retroativa para o Xiaomi Mi 9.
- [x] **Suite de Testes Pytest:** 48 testes automatizados validados com 100% de sucesso.

---

## Versão V8.8 - Conclusão do Backlog, Token Criptográfico & Arquitetura Modular
- [x] **Token Criptográfico & Rotação (SEC-05):** Geração segura via uth_service.py (secrets.token_urlsafe(32)) e pareamento zero-touch via query parameter ?token=....
- [x] **Rate-Limiter Drop-Oldest (PERF-03):** Implementação em VolumeSlider.jsx (20Hz/50ms com leading & trailing edge) para eliminação de buffer bloat em Wi-Fi.
- [x] **Desacoplamento Modular (ARCH-01):** Refatoração de pps_config.py em config/apps_registry.py, services/window_service.py e services/process_service.py com fachada retrocompatível.
- [x] **Higienização de Exceções (ARCH-02):** Blocos pass em media_service.py substituídos por logs estruturados logger.debug.
- [x] **Command Registry Pattern (ARCH-03):** Roteamento WebSocket migrado para o dicionário ACTION_HANDLERS (incluindo 	oggle_mic).

---
## Versão V1 - MVP Fundamental
- [x] Ambiente Python, FastAPI e Uvicorn configurados.
- [x] Endpoint WebSocket com verificação de Token de segurança.
- [x] Lançamento de processos Windows via subprocess.
- [x] Projeto React + Vite com Swiper e Lucide-react.
- [x] Suporte a PWA para exibição em tela cheia mobile.

## Versão V2 - Infraestrutura & Estética
- [x] Script `iniciar_streamdeck.vbs` para execução oculta sem terminais visíveis.
- [x] Migração de tema para Glassmorphism translúcido com fundo preto puro.
- [x] Transições de página com animação fluida `EffectCreative`.

## Versão V3 - Otimização AMOLED
- [x] **Standby OLED (Blackout):** Tela 100% preta ao desconectar, economizando bateria.
- [x] **Double-Tap de Emergência:** Dois toques rápidos na tela preta abrem configurações.
- [x] **Wake Lock API:** Prevenção contra desligamento da tela do aparelho.
- [x] **Controle de Sistema:** Atalho de desligamento com diálogo de confirmação.

## Versão V4 - Multimídia com Ctypes
- [x] Injeção de teclas multimídia virtuais do Windows (`keybd_event`).
- [x] Aba de Mídia dedicada no Swiper.
- [x] Hook customizado `useWakeLock.js`.

## Versão V5 - Central de Volume iOS
- [x] Slider de volume vertical com arrasto tátil e vibração háptica (`VolumeSlider.jsx`).
- [x] Integração com Windows Core Audio (`pycaw`) para leitura bidirecional absoluta.

## Versão V6 - Arquitetura Unificada
- [x] Autodescoberta de IP local via ZeroConf mDNS (`streamdeck.local`).
- [x] Servidor unificado: FastAPI servindo o build estático do frontend na porta 8000.
- [x] Widget Now Playing: Leitura de título, artista e capa via `WinRT`.
- [x] Botão de microfone com manipulação de canais de comunicação.

## Versão V7 - Refinamento Visual
- [x] Glow dinâmico no card Now Playing baseado na cor dominante do álbum via canvas.
- [x] Eliminação do sistema de categorias rígidas, usando listas diretas por página.
- [x] Inteligência de foco (`bring_to_foreground`) com injeção de ALT.

## Versão V8 - Integração do Setup
- [x] Ícone e atalho nativo para o sistema de câmeras residenciais (**VMS**).
- [x] Ícone e atalho para o dashboard de diagnóstico (**CheckUP Windows**).
- [x] Auto-sync de IP no frontend e scripts de inicialização otimizados.
## Versão V8.5 - Arquitetura Modular, Resiliência & Haptics
- [x] **Modularização do Backend:** Separação do `main.py` em `services/` (`media`, `network`, `system`), `managers/` (`connection_manager`) e `routers/` (`deck_router`).
- [x] **Lançamento Não-Bloqueante:** Processamento assíncrono com `asyncio.to_thread` evitando micro-travamentos do servidor ao abrir programas pesados.
- [x] **Auto-Sincronização de IP sem Dead Code:** Sincronização em tempo real do WebSocket com a URL do navegador.
- [x] **Heartbeat & Resiliência Mobile:** Pings periódicos de 15s, recuperação de sockets zumbis e reconexão automática ao acordar o celular (`visibilitychange` / `online`).
- [x] **Haptic Feedback (Vibração Tátil):** Utilitário `haptics.js` com vibrações padronizadas para cliques, sliders, troca de slides e alertas.
- [x] **Indicador Visual de App Ativo (LED Neon):** Detecção de processos do Windows via `psutil` com LED verde pulsante no botão do app correspondente.
- [x] **Modo OLED True Black Puro:** Fundo preto `#000000` estrito no tema escuro desligando pixels da tela AMOLED do Mi 9.

## Versão V8.6 - Hardening de Segurança, AppSec & Desempenho
- [x] **Mitigação de Path Traversal:** Sanitização de caminho canônico (`backend/main.py`) impedindo fuga do diretório do build estático.
- [x] **Proteção contra CSWSH:** Validação estrita de cabeçalho `Origin` no handshake WebSocket (`backend/routers/deck_router.py`).
- [x] **Autenticação Mandatória:** Proteção de `PUT /api/v1/deck/catalog` e `/api/agents/orchestrate` com Bearer token.
- [x] **Proteção Anti-SSRF:** Bloqueio de hosts loopback e endereços IP restritos na ação `call_webhook` (`backend/services/macro_service.py`).
- [x] **Desacoplamento Assíncrono do CoreAudio:** Envoltório `asyncio.to_thread` nas chamadas Pycaw do `deck_router.py`.
- [x] **Timeout e Timing Attack Defense:** Timeout de 5s no handshake WS e comparação de token com `hmac.compare_digest`.
- [x] **Screen Wake Lock Nativo W3C:** Hook `useWakeLock.js` modernizado com fallback gracioso para `NoSleep.js`.
- [x] **Suite de Testes Automatizados:** 24 testes com 100% de aprovação no Pytest e compilação limpa no Vite.

## Versão V8.7 - Otimização de Thumbnails REST & Ergonomia de Gestos
- [x] **Endpoint REST de Capa com Cache ETag (`/api/v1/deck/media/art`):** Servidor binário com cabeçalhos `Cache-Control` e resposta 304 `Not Modified`.
- [x] **Redução Drástica de Payload WebSocket:** `system_status` migrado de ~150KB (base64) para < 1KB (apenas URL com hash para cache no celular).
- [x] **Isolamento de Gestos no Swiper:** Adicionada diretiva `noSwiping={true}` e classe `swiper-no-swiping` no `VolumeSlider.jsx`, eliminando troca de tela acidental.
- [x] **Cooldown Anti-Spam no DeckButton:** Janela de 800ms impedindo abertura concorrente de programas pesados no Windows ao tocar rápido no Mi 9.
- [x] **NowPlaying com Cache de Cor Dominante:** Eliminação de flickering e cálculo redundante via `dominantColorCache` em memória.
- [x] **Expansão da Suite Pytest:** 35 testes automatizados com 100% de aprovação (`pytest backend/tests`).

---

[[Roadmap e Planejamento Futuro]]
[[Auditoria e Seguranca]]
[[MAIN]]
