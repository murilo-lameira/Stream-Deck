# 📱 Stream Deck Mobile - App Launcher para Windows

O projeto **Stream Deck Mobile** nasceu com um propósito ecológico e prático: **dar um novo destino e utilidade para um smartphone antigo que já estava descartado**. Aproveitando o display AMOLED de um Xiaomi Mi 9, transformamos um aparelho sem uso em um controlador de mídia e lançador de aplicativos remoto, premium e de baixa latência para o Windows, operando inteiramente via rede local (Wi-Fi).

Para gerenciar a complexidade e estruturar todas as etapas do desenvolvimento, utilizamos o **Obsidian como nosso "Segundo Cérebro"**. Todo o planejamento, backlog de tarefas, problemas resolvidos e decisões de arquitetura foram armazenados e organizados em um *Vault* dedicado, o que garantiu uma evolução limpa e escalável para o projeto.

<div align="center">
  <img src="https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI_2.0-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/WebSockets-010101?style=for-the-badge&logo=socketdotio&logoColor=white" alt="WebSockets" />
  <img src="https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/PWA_AMOLED-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white" alt="PWA" />
  <img src="https://img.shields.io/badge/Windows_11_API-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/mDNS_ZeroConf-0A84FF?style=for-the-badge&logo=apple&logoColor=white" alt="mDNS" />
  <img src="https://img.shields.io/badge/Obsidian_Vault-483699?style=for-the-badge&logo=obsidian&logoColor=white" alt="Obsidian" />
  <img src="https://img.shields.io/badge/AI_Agents_Squad-FF6F00?style=for-the-badge&logo=robotframework&logoColor=white" alt="AI Agents" />
  <img src="https://img.shields.io/badge/n8n_Ready-EA4B71?style=for-the-badge&logo=n8n&logoColor=white" alt="n8n" />
</div>
<br>

<!-- Espaço para a foto do projeto -->
![Foto do Projeto](docs/images/image-2.png)

![Print do projeto](docs/images/image.png)
![printo 2 do projeto](docs/images/image-1.png)


Abaixo, apresentamos um resumo **extremamente detalhado** da arquitetura, regras de negócio e implementação final do sistema.

---

## 🏗 Arquitetura do Sistema

O projeto é estruturado em uma arquitetura cliente-servidor leve em tempo real via **WebSockets**:

1. **Backend (Python / FastAPI):** Responsável por escutar os comandos na rede local, validar a segurança da conexão, invocar executáveis do Windows de forma não-bloqueante, controlar áudio/microfone nativo e anunciar o serviço na rede via mDNS (`streamdeck.local`). Também é o responsável por servir os arquivos estáticos do frontend.
2. **Frontend (React / Vite PWA):** Responsável por exibir a interface gráfica moderna (Glassmorphism / OLED Blackout), controle de volume dinâmico estilo iOS, banner de reprodução de mídia em tempo real e atalhos rápidos.

---

## 🔙 Backend: Especificações e Regras Estritas

Localizado na pasta `backend/`, o servidor foi projetado para ser leve, rápido e não-bloqueante.

### Tecnologias Utilizadas
* **FastAPI:** Framework web assíncrono de alta performance.
* **Uvicorn:** Servidor ASGI para rodar a aplicação.
* **WebSockets:** Protocolo de comunicação bidirecional em tempo real.
* **Pycaw / Comtypes:** Controle do Windows Core Audio (Volume absoluto e Microfone).
* **WinRT (`winrt-Windows.Media.Control`):** Captura em tempo real dos metadados de reprodução (Spotify, YouTube, navegadores).
* **Zeroconf (mDNS):** Descoberta automática de IP na rede local via domínio `streamdeck.local`.
* **Python-dotenv:** Gerenciamento seguro de variáveis de ambiente.

### Regras de Negócio Implementadas
* **Padrão "Fire and Forget" (Não-bloqueante):** 
  * O backend apenas dá o gatilho inicial para abrir o aplicativo e responde imediatamente. 
  * Utiliza `os.startfile()` para atalhos e links, e `subprocess.Popen()` com flags apropriadas (`CREATE_NEW_PROCESS_GROUP` e `STARTF_USESHOWWINDOW`) para garantir que os aplicativos abram com suas janelas visíveis sem travar a thread assíncrona do FastAPI.
* **Handshake de Segurança (Token):**
  * O servidor possui um endpoint em `/ws`. 
  * Ao receber uma conexão, aguarda a primeira mensagem: `{"auth_token": "SEU_TOKEN"}`.
  * Se o token estiver incorreto, a conexão é abortada imediatamente com código **WebSocket 1008 (Policy Violation)**.
* **Mapeamento de Caminhos (`apps_config.py`):**
  * Mapeamento com `os.path.expandvars()` para ler variáveis do Windows (`%LOCALAPPDATA%`, `%PROGRAMFILES%`, `%APPDATA%`), funcionando para qualquer usuário.

---

## 🎨 Frontend: Especificações e Regras Estritas

Localizado na pasta `frontend/`, a aplicação foi estruturada como um **Progressive Web App (PWA)** focado em fluidez e imersão.

### Tecnologias Utilizadas
* **React + Vite:** Construção modular e compilação ultra-rápida.
* **Swiper.js:** Paginação tátil em blocos de aplicativos (chunks).
* **Lucide-react:** Ícones vetoriais modernos.
* **NoSleep.js / Wake Lock API:** Prevenção contra desligamento da tela do celular.

### Regras de Negócio Implementadas
* **Modo PWA e Tela Cheia (Imersão):**
  * Configurado com `display: fullscreen` no `manifest.json` e bloqueio de zoom no `index.html`.
  * Tema `#000000` (preto absoluto) para economia de energia em telas AMOLED.
* **Resiliência e Auto-Reconexão:**
  * O hook customizado `useWebSocket.js` gerencia os estados da conexão (`CONNECTED`, `AUTHENTICATED`, `RECONNECTING`, `ERROR`).
  * Loop automático de reconexão a cada **3 segundos** em caso de oscilação do Wi-Fi.
* **Now Playing & Controles de Mídia:**
  * Componente `NowPlaying.jsx` com suporte a título, artista e scroll suave de texto longo.
  * `VolumeSlider.jsx` vertical inspirado no iOS Control Center, com feedback tátil de vibração (`navigator.vibrate`).
* **Design Responsivo (Portrait & Landscape):**
  * Ajuste automático para modo horizontal mantendo a proporção quadrada perfeita dos botões.

---

## 📂 Estrutura de Diretórios (Modular 2.0)

```text
Stream Deck/
├── backend/
│   ├── managers/                 # connection_manager.py (Broadcast seguro)
│   ├── routers/                  # deck_router.py (WebSockets e endpoints)
│   ├── services/                 # network_service, system_service, media_service
│   ├── apps_config.py            # Executáveis Windows e foco inteligente
│   ├── main.py                   # FastAPI unificado + Orquestrador de Agentes
│   ├── requirements.txt          # Dependências Python
│   └── .env                      # Configuração de portas e tokens
├── frontend/
│   ├── public/                   # Manifest PWA e ícones
│   ├── src/
│   │   ├── assets/               # Ícones vetoriais SVG (VMS, CheckUP, etc.)
│   │   ├── components/           # DeckButton, VolumeSlider, NowPlaying, Modais
│   │   ├── config/               # Catálogo de botões (apps.js)
│   │   ├── hooks/                # useWebSocket com Heartbeat e useWakeLock
│   │   ├── utils/                # haptics.js (Xiaomi Mi 9 vibrator API)
│   │   └── App.jsx               # Aplicação React 19
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── pixel_agents_bridge.js    # Ponte local para o comando global 'squad'
├── StreamDeck-Mi9/               # Segundo Cérebro no Obsidian (< 200 linhas/doc)
│   ├── 00 - Meta/                # MAIN.md e Índice Geral
│   ├── 01 - Arquitetura/         # Protocolos, Camadas e Pipeline de Agentes
│   ├── 02 - Backlog/             # Histórico de Entregas e Features.md
│   ├── 03 - Design/              # OLED Blackout, Haptics e Glassmorphism
│   ├── 04 - Integracoes/         # Webhooks n8n e automação Alexa
│   ├── 05 - Aplicativos/         # Catálogo de Executáveis e Regras Windows
│   └── gemini-scribe/Prompts/    # Prompts especializados dos 5 subagentes
├── iniciar_streamdeck.vbs        # Inicialização silenciosa do servidor
└── README.md                     # Documentação oficial
```

---

## 🚀 Como Executar o Projeto

Com a arquitetura unificada (V6), o backend Python hospeda o frontend pré-compilado e o WebSocket simultaneamente na mesma porta.

### 1. Inicialização Rápida (1 Clique)
Basta dar dois cliques no arquivo:
```text
iniciar_streamdeck.vbs
```
Ele iniciará o servidor FastAPI silenciosamente em segundo plano na porta **8000** e registrará o mDNS na rede local.

### 2. Inicialização Manual via Terminal
Se preferir rodar pelo terminal para visualizar os logs:
```powershell
cd "backend"
.\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Acessando pelo Smartphone (Xiaomi Mi 9)
1. Conecte o celular na **mesma rede Wi-Fi** do computador.
2. Abra o navegador no smartphone e acesse:
   * **Via mDNS (Recomendado):** `http://streamdeck.local:8000`
   * **Ou via IP Local:** `http://<SEU_IP_LOCAL>:8000` (ex: `http://192.168.15.16:8000`)
3. No navegador (Google Chrome), toque nos três pontinhos e selecione **"Adicionar à tela inicial"** ou **"Instalar Aplicativo"** para rodar como PWA nativo em tela cheia OLED.
4. Ao tocar no ícone de engrenagem, configure o Token (definido no `.env` do backend) se necessário.

---

## ✨ Recursos Especiais Implementados (Versão 2.0.0)
* **Pipeline Orquestrado de Agentes com Feedback Loop:** Arquitetura autônoma (Dev, UI/UX, Revisor, QA e Documentador). O QA valida as entregas e devolve correções para Dev/UI antes que o Documentador finalize as notas no Obsidian.
* **Detecção Inteligente de Abas e WebApps:** Suporte em tempo real para identificar **YouTube**, **Google Gemini** e **GitHub** abertos no Chrome através da Win32 API, além de apps nativos da Windows Store como **WhatsApp (`WhatsApp.Root.exe`)** e **Logitech G HUB**.
* **LED Neon Indicador Pulsante:** Indicador verde neon no canto superior direito de cada botão para informar visualmente quais aplicativos estão em execução no computador.
* **Auto-Descoberta mDNS & Auto-Sync de IP:** Acesso por `streamdeck.local:8000` com resolução de hostname e sincronização automática de endereço de WebSocket no PWA.
* **Now Playing Banner com Glow Reativo:** Sincronização em tempo real de metadados de música (Spotify/YouTube/Windows Media Control) com efeito de iluminação neon no card gerado a partir da cor dominante da capa do álbum.
* **Controle de Microfone e Mute Global:** Mute de microfone inteligente atuando em múltiplos canais simultaneamente (`eConsole` e `eCommunications`), cobrindo Discord, WhatsApp e Google Meet com feedback visual dinâmico.
* **OLED True Black & Standby:** Fundo preto absoluto (`#000000`) que desliga os pixels da tela AMOLED do Xiaomi Mi 9 para economia de bateria, com sensor de duplo toque.
* **Feedback Tátil Háptico:** Vibração tátil refinada no Mi 9 em cada toque, seleção e troca de slide.
* **Ecossistema Integrado:** Atalhos para **VMS CFTV** (com ícone dedicado de câmera) e diagnóstico de hardware com **CheckUP Windows** (com paleta púrpura `#8C4FFF`).
* **Design Responsivo Portrait & Landscape:** Grade de 2x4 (retrato) ou 4x2 (paisagem) que se adapta dinamicamente mantendo proporções perfeitas.

---

## 🗺️ Roadmap de Evolução & Automações Futuras

### 1. 🤖 Integração com Alexa & Fluxos de Agente no n8n
* **Webhooks Bidirecionais:** Implementação de endpoints REST (`POST /api/trigger`) no FastAPI para que o n8n ou a Alexa executem macros e ações no computador remotamente.
* **Acionamento por Voz (Alexa -> n8n -> Stream Deck):** Comandos de voz como *"Alexa, preparar estúdio"* disparam fluxos inteligentes no n8n que abrem o OBS, abrem o CheckUP, mutam o microfone e ativam a iluminação da sala.
* **Cenas Físicas (Stream Deck -> n8n -> Casa Inteligente):** Botões dedicados no Xiaomi Mi 9 para despachar webhooks no n8n acionando lâmpadas inteligentes, ar condicionado e avisos sonoros na Alexa.

### 2. 📹 Monitoramento e Central de Segurança
* **Miniatura RTSP ao Vivo:** Abrir um modal flutuante no celular com streaming de baixa latência da câmera do portão/garagem via VMS.

### 3. 🎨 Stream Deck 2.0 (Customização Dinâmica)
* **Editor Web Drag & Drop:** Interface para reorganizar, criar novos botões e escolher cores sem necessidade de alterar arquivos de código.
* **Páginas Ilimitadas:** Paginação dinâmica e criação de pastas/subpastas de atalhos.

---
*Documentação oficial do projeto Stream Deck Mobile.*

