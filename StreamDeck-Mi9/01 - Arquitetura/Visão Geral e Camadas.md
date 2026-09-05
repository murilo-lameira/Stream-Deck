# 🏛️ Visão Geral da Arquitetura

O **Stream Deck Mobile** opera em uma arquitetura cliente-servidor leve, de alta performance e baixa latência, desenhada para rodar em hardware antigo reaproveitado (como o Xiaomi Mi 9).

---

## 🧩 Camadas do Sistema

```text
┌───────────────────────────────────────────────────────────┐
│                    Xiaomi Mi 9 (Cliente)                  │
│       React 19 + Vite PWA (OLED Blackout / Glassmorphism) │
└─────────────────────────────▲─────────────────────────────┘
                              │
                    WebSocket & HTTP (Porta 8000)
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                 Windows 11 Host (Backend)                 │
│    Python + FastAPI + Uvicorn (ZeroConf mDNS + WinRT)     │
└──────┬──────────────────────┬──────────────────────┬──────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Pycaw Áudio │      │ WinRT Mídia  │      │ Ctypes Foco  │
│  Mic / Master│      │ Metadados    │      │ Alt-Tab Win  │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

## 1. Backend (Python / FastAPI)
## 1. Backend Modular (FastAPI 2.0.0)
* **Porta Unificada (8000):** Hospeda simultaneamente o endpoint WebSocket (`/ws`), rotas de API e os arquivos estáticos pré-compilados do frontend (`/assets` e `index.html`).
* **Processo Oculto:** Inicialização em segundo plano via VBScript (`iniciar_streamdeck.vbs`), consumindo menos de 80MB de memória RAM.
* **Estrutura Modular Desacoplada:**
  * `managers/connection_manager.py`: Controle thread-safe de clientes conectados e broadcasts com timeout.
  * `services/network_service.py`: Detecção de IP local e registro mDNS ZeroConf (`streamdeck.local`).
  * `services/media_service.py`: Thread isolada WinRT para metadados de música sem conflito COM.
  * `services/system_service.py`: Monitoramento assíncrono de processos ativos via `psutil`.
  * `routers/deck_router.py`: Rota WebSocket, handshake por token e comandos assíncronos não-bloqueantes (`asyncio.to_thread`).
* **APIs Nativas:**
  * `Pycaw`: Manipulação de volume e mute de microfone.
  * `WinRT`: Leitura de música em reprodução sem bibliotecas pesadas.
  * `ctypes`: Foco forçado de janelas através da API `user32.dll`.
  * `ctypes`: Foco forçado de janelas através da API `user32.dll` com injeção de tecla ALT.

## 2. Frontend (React / Vite PWA)
* **Single Page Application (SPA):** Empacotada para execução fluida sem reload de página.
* **PWA Instalável:** Executado em tela cheia sem barras de navegador.
* **Resiliência:** Auto-reconexão com intervalo inteligente e fallback para modo Standby OLED.
* **Resiliência & Heartbeat:** Ping periódico de 15s, recuperação de sockets zumbis e reconexão automática ao acordar o celular (`visibilitychange` / `online`).
* **Haptics & OLED:** Vibração tátil nativa (`navigator.vibrate`) e tema OLED True Black (`#000000`).

[[Protocolo WebSocket e Contratos]]
[[Rede e Autodescoberta]]
[[MAIN]]
