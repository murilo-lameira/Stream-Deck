# 📜 Histórico de Entregas (Versões V1 a V8)

Registro cronológico das funcionalidades concebidas, desenvolvidas e validadas no Stream Deck Mobile.

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

[[Roadmap e Planejamento Futuro]]
[[MAIN]]
