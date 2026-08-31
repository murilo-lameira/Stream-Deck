
**Backlog V1 (ConcluÃ­do)**
- [x] Iniciar ambiente Python, instalar FastAPI e Uvicorn.
- [x] Criar endpoint WebSocket com verificaÃ§Ã£o de Token.
- [x] Testar abertura do VS Code via script Python (subprocess).
- [x] Criar projeto Vite/React e instalar Swiper e Lucide-react.
- [x] Configurar index.html do Vite para PWA (tela cheia no celular).
- [x] Criar layout de grade (Grid) fatiado de 6 em 6 botÃµes por tela.
- [x] Conectar front-end ao WebSocket e enviar comando de teste.

**Backlog V2 (ConcluÃ­do)**

**Infraestrutura e AutomaÃ§Ã£o**
- [x] Criar script `iniciar_streamdeck.vbs` para execuÃ§Ã£o oculta dos servidores no Windows.
- [x] Desenvolver script `setup_autostart.ps1` para registrar o VBS na inicializaÃ§Ã£o do sistema atravÃ©s do Registro do Windows (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).

**Interface e Design (Frontend)**
- [x] **MigraÃ§Ã£o de Tema:** Refatorar o `index.css` e o `App.css` para um design "Glassmorphism".
- [x] **Modo Escuro (Dark Mode):** Adicionar botÃ£o de toggle de tema Claro/Escuro (com fundo `Preto Puro #000000`).
- [x] **Responsividade (Landscape/Portrait):** Esconder cabeÃ§alho e textos dos botÃµes no modo horizontal para focar apenas nos Ã­cones.
- [x] **AtualizaÃ§Ã£o de Ãcones:** Trocar as logos antigas por SVGs customizados na pasta `assets/icons/`.
- [x] **Agrupamento de Telas:** Criar uma tela dedicada apenas para a categoria "Jogos" usando o `DeckSwiper`.
- [x] **AnimaÃ§Ã£o Premium:** Implementar transiÃ§Ã£o fluida nas pÃ¡ginas com `EffectCreative` (Swiper).

**Regras de NegÃ³cio e IntegraÃ§Ã£o (Backend/Frontend)**
- [x] **Mapeamento de Apps:** Configurar executÃ¡veis, URIs (`whatsapp:`) e atalhos (`.lnk`) no `apps_config.py` e replicÃ¡-los na interface, garantindo que o backend use `os.startfile` para links.

[[Design]]
[[Arquitetura e ComunicaÃ§Ã£o]]

**Backlog V3 (Concluído)**
- [x] **Standby OLED (Blackout):** Esconder toda a interface quando desconectado do WebSocket, exibindo uma tela #000000 absoluta (economizando bateria da tela AMOLED).
- [x] **Double-Tap de Emergência:** Criar um evento invisível no modo Blackout que abra o menu de configurações (caso o servidor mude de IP).
- [x] **Wake Lock API:** Impedir que o celular bloqueie a tela sozinho durante o uso, solicitando a Wake Lock e restaurando via isibilitychange.
- [x] **Controle de Sistema (Shutdown):** Mapear botão "Desligar PC" chamando nativamente shutdown /s /t 0.
- [x] **UX de Segurança (Frontend):** Inserir um prompt (window.confirm) prevenindo cliques acidentais no botão de Desligar PC.

**Backlog V4 (Concluído)**
- [x] **Controle Nativo de Mídia e Volume:** Utilização de \ctypes\ no backend Python para despachar KeyEvents virtuais (Volume, Play/Pause, Next, Prev) do Windows.
- [x] **Agrupamento de Páginas:** Criação de nova aba "Mídia e Controle" no \DeckSwiper\.
- [x] **PWA Perfeito:** Adição de \icon.svg\ e parâmetros no \manifest.json\ para permitir instalação nativa do Stream Deck na tela principal do celular.
- [x] **Clean Code:** Refatoração do \App.jsx\ com a extração da lógica de WakeLock para o hook \useWakeLock.js\.

**Backlog V5 (Concluído)**
- [x] **Slider de Volume iOS (Control Center):** Criação do componente \VolumeSlider.jsx\ estilo cápsula arredondada tátil, com preenchimento dinâmico vertical e feedback tátil (vibração).
- [x] **Integração Core Audio Windows (\pycaw\):** Controle absoluto e leitura bidirecional em tempo real do nível de volume master e estado de mute do Windows no backend.
- [x] **Layout de Mídia Dedicado:** Reformulação da tela de Mídia combinando o slider iOS com botões de reprodução (Play/Pause, Prev, Next).
- [x] **Correção de Layout Responsivo:** Ajuste da grade (Grid) da tela de mídias para manter os botões idênticos ao modo normal e perfeitamente quadrados no modo paisagem (Landscape).

**Backlog V6 (Concluido)**
- [x] **Autodescoberta de IP (mDNS / ZeroConf):** Utilizacao da biblioteca zeroconf no backend para anunciar o endereco \streamdeck.local\, eliminando a necessidade do usuario digitar IP manualmente no celular.
- [x] **Servidor Unificado (FastAPI + Vite Build):** Compilacao do Frontend React para arquivos estaticos e configuracao do FastAPI para servir tudo na mesma porta (8000), desativando o servidor de desenvolvimento do Vite e simplificando o ecossistema.
- [x] **Widget Now Playing (Musica Atual):** Captura dos metadados de midia do Windows via \winrt-Windows.Media.Control\ rodando em uma Background Task (asyncio) no backend, com broadcast pelo WebSocket e exibicao dinamica na interface.
- [x] **Botao de Mute do Microfone:** Manipulacao nativa de dispositivo de captura via \pycaw\ com atualizacao dinamica de cor e icone (Laranja para Ativo, Vermelho para Mudo) diretamente na tela de Aplicativos do Deck.

**Publicação e Versionamento (GitHub)**
- [x] **Repositório Oficial:** Publicação do código-fonte completo no GitHub: [murilo-lameira/Stream-Deck](https://github.com/murilo-lameira/Stream-Deck).
- [x] **Configuração do .gitignore:** Proteção de variáveis de ambiente (.env), binários do ambiente virtual (env/) e pacotes do Node (
ode_modules/).
- [x] **Documentação de Instalação:** README.md completo com guia de execução rápida (1 clique com VBS) e manual, arquitetura unificada e recursos de auto-descoberta mDNS.
