
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
[[Arquitetura e Comunicação]]

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
**Correções e Polimento (v1.0.1)**
- [x] **Ícone do Obsidian:** Otimização do vetor SVG do Obsidian para carregamento inline instantâneo na grade de botões.
- [x] **Estabilidade do OLED Blackout:** Correção do ciclo de reconexão do WebSocket para manter a tela 100% preta de forma contínua e sem piscar quando o PC for desligado.
- [x] **Toque Duplo Mobile:** Adicionado detector de duplo toque para abrir configurações na tela de Blackout no smartphone.

- [x] **Legendas e Nomes dos Apps:** Exibição dos nomes dos aplicativos abaixo de cada ícone em todas as orientações (Portrait e Landscape), com tipografia nítida e responsiva mantendo o padrão Glassmorphism/OLED.

- [x] **Reorganização e Novos Apps:** Criação do atalho para o OBS Studio na tela inicial e transferência do botão de Desligar (Power) e Mutar Microfone para a categoria de Controle de Mídia (Página 2), com readequação total do CSS Grid para comportar os novos layouts.

- [x] **Tipografia Moderna e Translúcida:** Aplicação da fonte **Plus Jakarta Sans / Outfit** com estilo translúcido refinado (gba(241, 245, 249, 0.70)) e sombras suaves para os nomes dos aplicativos abaixo dos ícones.

- [x] **Foco de Janelas (Foreground):** Implementação na API Windows (`ctypes.windll.user32`) que procura processos rodando em segundo plano e automaticamente os traz para o primeiro plano (com simulação de tecla ALT para evitar bloqueios de foco), evitando que instâncias redundantes sejam abertas quando o usuário clica nos botões.

**Backlog V7 (Próximas Tarefas)**
- [x] **Redesign da Caixa de Música:** Alterar o design atual (Widget Now Playing) para um novo layout e experiência visual.
