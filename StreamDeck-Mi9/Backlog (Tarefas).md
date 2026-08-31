
**Backlog V1 (Conclu√≠do)**
- [x] Iniciar ambiente Python, instalar FastAPI e Uvicorn.
- [x] Criar endpoint WebSocket com verifica√ß√£o de Token.
- [x] Testar abertura do VS Code via script Python (subprocess).
- [x] Criar projeto Vite/React e instalar Swiper e Lucide-react.
- [x] Configurar index.html do Vite para PWA (tela cheia no celular).
- [x] Criar layout de grade (Grid) fatiado de 6 em 6 bot√µes por tela.
- [x] Conectar front-end ao WebSocket e enviar comando de teste.

**Backlog V2 (Conclu√≠do)**

**Infraestrutura e Automa√ß√£o**
- [x] Criar script `iniciar_streamdeck.vbs` para execu√ß√£o oculta dos servidores no Windows.
- [x] Desenvolver script `setup_autostart.ps1` para registrar o VBS na inicializa√ß√£o do sistema atrav√©s do Registro do Windows (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).

**Interface e Design (Frontend)**
- [x] **Migra√ß√£o de Tema:** Refatorar o `index.css` e o `App.css` para um design "Glassmorphism".
- [x] **Modo Escuro (Dark Mode):** Adicionar bot√£o de toggle de tema Claro/Escuro (com fundo `Preto Puro #000000`).
- [x] **Responsividade (Landscape/Portrait):** Esconder cabe√ßalho e textos dos bot√µes no modo horizontal para focar apenas nos √≠cones.
- [x] **Atualiza√ß√£o de √çcones:** Trocar as logos antigas por SVGs customizados na pasta `assets/icons/`.
- [x] **Agrupamento de Telas:** Criar uma tela dedicada apenas para a categoria "Jogos" usando o `DeckSwiper`.
- [x] **Anima√ß√£o Premium:** Implementar transi√ß√£o fluida nas p√°ginas com `EffectCreative` (Swiper).

**Regras de Neg√≥cio e Integra√ß√£o (Backend/Frontend)**
- [x] **Mapeamento de Apps:** Configurar execut√°veis, URIs (`whatsapp:`) e atalhos (`.lnk`) no `apps_config.py` e replic√°-los na interface, garantindo que o backend use `os.startfile` para links.

[[Design]]
[[Arquitetura e Comunica√ß√£o]]

**Backlog V3 (ConcluÌdo)**
- [x] **Standby OLED (Blackout):** Esconder toda a interface quando desconectado do WebSocket, exibindo uma tela #000000 absoluta (economizando bateria da tela AMOLED).
- [x] **Double-Tap de EmergÍncia:** Criar um evento invisÌvel no modo Blackout que abra o menu de configuraÁıes (caso o servidor mude de IP).
- [x] **Wake Lock API:** Impedir que o celular bloqueie a tela sozinho durante o uso, solicitando a Wake Lock e restaurando via isibilitychange.
- [x] **Controle de Sistema (Shutdown):** Mapear bot„o "Desligar PC" chamando nativamente shutdown /s /t 0.
- [x] **UX de SeguranÁa (Frontend):** Inserir um prompt (window.confirm) prevenindo cliques acidentais no bot„o de Desligar PC.

**Backlog V4 (ConcluÌdo)**
- [x] **Controle Nativo de MÌdia e Volume:** UtilizaÁ„o de \ctypes\ no backend Python para despachar KeyEvents virtuais (Volume, Play/Pause, Next, Prev) do Windows.
- [x] **Agrupamento de P·ginas:** CriaÁ„o de nova aba "MÌdia e Controle" no \DeckSwiper\.
- [x] **PWA Perfeito:** AdiÁ„o de \icon.svg\ e par‚metros no \manifest.json\ para permitir instalaÁ„o nativa do Stream Deck na tela principal do celular.
- [x] **Clean Code:** RefatoraÁ„o do \App.jsx\ com a extraÁ„o da lÛgica de WakeLock para o hook \useWakeLock.js\.

**Backlog V5 (ConcluÌdo)**
- [x] **Slider de Volume iOS (Control Center):** CriaÁ„o do componente \VolumeSlider.jsx\ estilo c·psula arredondada t·til, com preenchimento din‚mico vertical e feedback t·til (vibraÁ„o).
- [x] **IntegraÁ„o Core Audio Windows (\pycaw\):** Controle absoluto e leitura bidirecional em tempo real do nÌvel de volume master e estado de mute do Windows no backend.
- [x] **Layout de MÌdia Dedicado:** ReformulaÁ„o da tela de MÌdia combinando o slider iOS com botıes de reproduÁ„o (Play/Pause, Prev, Next).
- [x] **CorreÁ„o de Layout Responsivo:** Ajuste da grade (Grid) da tela de mÌdias para manter os botıes idÍnticos ao modo normal e perfeitamente quadrados no modo paisagem (Landscape).

**Backlog V6 (Concluido)**
- [x] **Autodescoberta de IP (mDNS / ZeroConf):** Utilizacao da biblioteca zeroconf no backend para anunciar o endereco \streamdeck.local\, eliminando a necessidade do usuario digitar IP manualmente no celular.
- [x] **Servidor Unificado (FastAPI + Vite Build):** Compilacao do Frontend React para arquivos estaticos e configuracao do FastAPI para servir tudo na mesma porta (8000), desativando o servidor de desenvolvimento do Vite e simplificando o ecossistema.
- [x] **Widget Now Playing (Musica Atual):** Captura dos metadados de midia do Windows via \winrt-Windows.Media.Control\ rodando em uma Background Task (asyncio) no backend, com broadcast pelo WebSocket e exibicao dinamica na interface.
- [x] **Botao de Mute do Microfone:** Manipulacao nativa de dispositivo de captura via \pycaw\ com atualizacao dinamica de cor e icone (Laranja para Ativo, Vermelho para Mudo) diretamente na tela de Aplicativos do Deck.
