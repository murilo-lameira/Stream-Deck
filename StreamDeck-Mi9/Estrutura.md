# Estrutura do Projeto

O repositório do "Stream Deck Mobile" está organizado em módulos bem definidos, permitindo fácil manutenção entre o backend Python e o frontend Web (React).

## Diretório Raiz (`/`)
- `iniciar_streamdeck.vbs`: Script responsável por acionar instâncias ocultas e desanexadas do Backend e Frontend em segundo plano, evitando janelas de terminais abertas.
- `setup_autostart.ps1`: Script PowerShell que adiciona o `.vbs` acima nas chaves Run do Registro do Windows (`HKCU`), permitindo o início automático com o sistema operacional.

## Frontend (`/frontend/`)
A interface do usuário rodando no celular via rede local.

- `src/App.jsx`: Componente principal responsável pelo gerenciamento de estado (modo escuro, autenticação), escuta de web-sockets e controle dinâmico da injeção de classes.
- `src/App.css` e `src/index.css`: Concentram toda a mágica visual (Glassmorphism, Modo Escuro, Media Queries de Orientação e animações em CSS puro).
- `src/components/DeckSwiper.jsx`: A tela (Swiper) configurada com `EffectCreative` que separa dinamicamente as categorias de Jogos e Produtividade.
- `src/components/DeckButton.jsx`: Renderiza a unidade visual de botão contendo ícones (SVGs), emitindo sinais via WebSocket quando tocado.
- `src/config/apps.js`: Arquivo de configuração que injeta e mapeia todos os botões que aparecerão no frontend.
- `src/assets/icons/`: Diretório exclusivo armazenando todos os SVGs dos aplicativos, para que o renderizador construa as logos locais perfeitamente focadas e centralizadas.

## Backend (`/backend/`)
O servidor responsável por receber conexões TCP na porta 8000 (via FastAPI) e controlar o computador real.

- `main.py`: Ponto de entrada FastAPI. Possui as definições do servidor ASGI (Uvicorn), roteamento HTTP/WebSocket e o ciclo de vida da autenticação de token.
- `apps_config.py`: Núcleo de mapeamento e rotina de acionamentos:
  - Armazena um dicionário ligando os IDs dos aplicativos (vindos do `apps.js` do frontend) para os executáveis do Windows (ou atalhos e URIs).
  - Implementa a função de despacho através de _Fire-and-Forget_ usando tanto `subprocess.Popen` com separação de _process group_, quanto a instrução nativa do SO `os.startfile()` perfeita para links (.lnk) e UWP schemas (`whatsapp:`).
- `venv/`: Ambiente virtual do Python, isolando dependências.

[[Tecnologias]]

