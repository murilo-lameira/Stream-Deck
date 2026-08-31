# 📱 Stream Deck Mobile - App Launcher para Windows

Este documento apresenta um resumo **extremamente detalhado** da arquitetura, regras de negócio e implementação do projeto **Stream Deck Mobile**. O objetivo deste sistema é transformar um smartphone (com foco na tela AMOLED do Xiaomi Mi 9) em um lançador de aplicativos remoto e não-bloqueante para um computador Windows, operando inteiramente via rede local (Wi-Fi).

---

## 🏗 Arquitetura do Sistema

O projeto é dividido em dois microsserviços principais que se comunicam em tempo real via **WebSockets**:

1. **Backend (Python / FastAPI):** Responsável por escutar os comandos na rede local, validar a segurança da conexão e invocar os executáveis do Windows de forma isolada.
2. **Frontend (React / Vite):** Responsável por exibir a interface gráfica otimizada para mobile (PWA), lidar com interações por toque e enviar comandos para o servidor.

---

## 🔙 Backend: Especificações e Regras Estritas

Localizado na pasta ackend/, o servidor foi projetado para ser leve, rápido e não-bloqueante.

### Tecnologias Utilizadas
* **FastAPI:** Framework web assíncrono de alta performance.
* **Uvicorn:** Servidor ASGI para rodar a aplicação.
* **WebSockets:** Protocolo de comunicação bidirecional em tempo real.
* **Python-dotenv:** Gerenciamento de variáveis de ambiente.

### Regras de Negócio Implementadas
* **Padrão "Fire and Forget" (Não-bloqueante):** 
  * A premissa central do backend é que ele apenas dá o gatilho inicial para abrir o aplicativo e **esquece**. 
  * É estritamente utilizado subprocess.Popen() com a flag CREATE_NEW_PROCESS_GROUP (no Windows). Isso garante que o aplicativo lançado (ex: VS Code, Chrome) rode em um processo filho totalmente desanexado, permitindo que a thread assíncrona do FastAPI continue respondendo a novos comandos instantaneamente. O uso de subprocess.run() foi proibido.
* **Handshake de Segurança (Token):**
  * O servidor possui um endpoint em /ws. 
  * Ao receber uma conexão, ele aguarda a primeira mensagem contendo um JSON: {"auth_token": "SEU_TOKEN"}.
  * Se o token não for enviado ou não bater com o AUTH_TOKEN do arquivo .env, a conexão é abortada imediatamente com o código **WebSocket 1008 (Policy Violation)**.
* **Mapeamento de Caminhos (apps_config.py):**
  * Os caminhos dos executáveis foram mapeados usando os.path.expandvars() para ler variáveis do Windows nativamente (como %LOCALAPPDATA% e %PROGRAMFILES%), garantindo que o código funcione independentemente do nome do usuário.

---

## 🎨 Frontend: Especificações e Regras Estritas

Localizado na pasta rontend/, a aplicação foi estruturada como um **Progressive Web App (PWA)** focado em fluidez e imersão.

### Tecnologias Utilizadas
* **React + Vite:** Para construção da interface de forma modular e compilação ultrarrápida.
* **Swiper.js:** Para a mecânica de paginação de aplicativos em blocos (chunks).
* **Lucide-react:** Biblioteca de ícones vetoriais modernos.

### Regras de Negócio Implementadas
* **Modo PWA e Tela Cheia (Imersão):**
  * O arquivo manifest.json (na pasta public/) está configurado com "display": "fullscreen", "start_url": "/" e "scope": "/".
  * O index.html contém as meta tags mobile-web-app-capable, bloqueio estrito de zoom (maximum-scale=1.0, user-scalable=no), e a 	heme-color setada como #000000 (preto absoluto). O objetivo é não parecer um site, e sim um aplicativo nativo do sistema operacional.
* **Resiliência e Auto-Reconexão:**
  * O hook customizado useWebSocket.js foi criado para gerenciar o estado da conexão (CONNECTED, AUTHENTICATED, RECONNECTING, ERROR).
  * Ele realiza o envio automático do uth_token logo após a abertura do canal (onopen).
  * Em caso de queda do Wi-Fi ou falha no servidor, o cliente possui um loop de "retry" que tenta restabelecer a conexão a cada **3 segundos**, exibindo um badge pulsante vermelho na interface ("Reconectando...").
* **Interface, Chunking e Feedback Tátil:**
  * **Dark Mode OLED:** Cores ajustadas para usar fundo preto e preservar a bateria em telas AMOLED (como a do Mi 9), com bordas neon brilhantes.
  * **Chunking (Swiper):** A lista global de apps (pps.js) é automaticamente fatiada em grades de 6 botões (2 colunas x 3 linhas). O usuário desliza para os lados para ver mais apps, guiado por pontos brancos no rodapé (inspirado na Home Screen do iOS).
  * Ao tocar em um botão, o celular executa uma pequena vibração 
avigator.vibrate(35) para feedback tátil, confirmando a ação.

---

## 📂 Estrutura de Diretórios Final

`	ext
Stream Deck/
├── backend/
│   ├── venv/                     # Ambiente virtual Python
│   ├── .env                      # Variáveis (AUTH_TOKEN, HOST, PORT)
│   ├── .env.example
│   ├── requirements.txt          # Dependências Python
│   ├── apps_config.py            # Dicionário de caminhos (VS Code, Chrome, etc)
│   ├── main.py                   # Lógica WebSocket e FastAPI
│   └── test_backend.py           # Script de teste de carga e segurança
├── frontend/
│   ├── public/
│   │   └── manifest.json         # Configurações PWA (fullscreen, theme-color)
│   ├── index.html                # Meta-tags de bloqueio de zoom e viewport
│   ├── vite.config.js            # Servidor configurado com host: "0.0.0.0"
│   ├── package.json
│   └── src/
│       ├── config/
│       │   ├── apps.js           # Catálogo de botões (Ícones, Nomes, Cores)
│       │   └── constants.js      # URL do Websocket e IP dinâmico
│       ├── hooks/
│       │   └── useWebSocket.js   # Controle da conexão e reconexão
│       ├── components/
│       │   ├── Header.jsx        # Cabeçalho com status pulsante
│       │   ├── DeckButton.jsx    # Componente visual do botão individual
│       │   ├── DeckSwiper.jsx    # Container fatiador de grids
│       │   └── SettingsModal.jsx # Tela para configurar IP/Token direto no app
│       ├── App.jsx               # Entrypoint dos componentes e Toasts
│       ├── App.css               # Estilos dos componentes
│       └── index.css             # Estilos globais OLED e resets de touch
└── README.md                     # Esta documentação
`

---

## 🚀 Como Executar o Projeto

Com a arquitetura unificada (V6), você não precisa mais rodar dois servidores (Node e Python). O Python hospeda o frontend pré-compilado e o WebSocket na mesma porta.

### 1. Inicialização Rápida (1 Clique)
Basta dar dois cliques no arquivo:
```powershell
iniciar_streamdeck.vbs
```
Ele iniciará o servidor FastAPI silenciosamente em segundo plano na porta **8000** e registrará o mDNS na rede local.

### 2. Inicialização Manual via Terminal
Se preferir rodar pelo terminal para ver os logs:
```powershell
cd "backend"
.\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Acessando pelo Xiaomi Mi 9 (Mobile)
1. Conecte o celular na **mesma rede Wi-Fi** do computador.
2. Abra o navegador no smartphone e acesse:
   * **Via mDNS (Recomendado):** `http://streamdeck.local:8000`
   * **Ou via IP Local:** `http://<SEU_IP_LOCAL>:8000` (ex: `http://192.168.15.16:8000`)
3. No navegador (Chrome), toque nos três pontinhos e selecione **"Adicionar à tela inicial"** ou **"Instalar Aplicativo"** para rodar como PWA nativo em tela cheia OLED.
4. Ao tocar no ícone de engrenagem, configure o Token (definido no `.env` do backend) se necessário.

---

## ✨ Recursos Especiais Implementados
* **Auto-Descoberta mDNS:** Acesso direto por `streamdeck.local:8000` sem precisar verificar o IP local toda vez.
* **Now Playing Banner:** Sincronização em tempo real de metadados de música (Spotify/YouTube/Windows Media Control) exibida no topo da tela de mídias.
* **Controle de Microfone e Mute Global:** Mute de microfone inteligente com feedback visual dinâmico (botão fica vermelho e muda para "Mic Off").
* **OLED Standby Mode:** Tela 100% preta de economia de bateria quando desconectado.
* **Design Responsivo Portrait & Landscape:** Grade e botões perfeitamente proporcionais em qualquer orientação do aparelho.

---
*Documentação gerada para o projeto Stream Deck Mobile.*

