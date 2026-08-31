# 📱 Stream Deck Mobile - Revivendo Hardware com IA e WebSockets

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/PWA-5A0FC8?style=for-the-badge&logo=pwa&logoColor=white" alt="PWA" />
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
  <img src="https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white" alt="Google Gemini" />
</div>
<br>

<!-- Cole a imagem do projeto aqui -->
![Stream Deck Mobile no Xiaomi Mi 9](docs/images/image-2.png)

## ♻️ O Propósito do Projeto
Todos nós temos aquele smartphone antigo guardado na gaveta. Neste projeto, o objetivo foi dar um **novo destino e utilidade a um Xiaomi Mi 9 descartado**. Ao invés de se tornar lixo eletrônico, aproveitamos sua tela AMOLED belíssima e seu hardware touch para transformá-lo em um **Controlador de Mídia e Lançador de Aplicativos Remoto (Stream Deck)** para Windows.

O projeto foi inteiramente desenhado para ser premium, com baixa latência, interface responsiva e operação local (Wi-Fi), funcionando como uma ponte inteligente entre o mobile e o desktop.

---

## 🧠 O "Segundo Cérebro" (Obsidian)
A complexidade de unir APIs nativas do Windows, WebSockets assíncronos e uma interface React PWA exigiu uma organização extrema. 
Utilizamos o **Obsidian como nosso Segundo Cérebro** durante todo o desenvolvimento. A arquitetura, decisões técnicas, backlog de tarefas (Kanban) e diário de desenvolvimento foram estruturados em um *Vault* local. Isso garantiu uma escalabilidade limpa e evitou que nos perdêssemos nas regras de negócio.

---

## 🛠️ Tecnologias e Arquitetura

O ecossistema foi dividido em duas camadas principais que se comunicam em tempo real via **WebSockets**:

### 1. O Motor (Backend - Python / FastAPI)
O servidor roda silenciosamente no Windows e atua como o "cérebro" das operações:
- **FastAPI & Uvicorn:** Hospedam simultaneamente a interface web e a conexão WebSocket em uma única porta (`8000`), garantindo uma inicialização com apenas 1 clique.
- **Integração Profunda com Windows:**
  - `Pycaw / Comtypes`: Controle absoluto do volume do Windows e mutagem direta no dispositivo de captura (Microfone).
  - `WinRT (Windows.Media.Control)`: Extração em tempo real da música tocando no Spotify, YouTube ou Edge para enviar ao celular.
  - `Ctypes (windll.user32)`: Implementação de foco de janelas avançado. Quando você clica em um app (ex: VS Code) que já está aberto, o backend não abre uma nova janela redundante; ele encontra o processo, simula um "Alt-Tab" invisível (bypass do bloqueio de foreground do Windows) e puxa a janela para a sua cara.
- **ZeroConf (mDNS):** O servidor anuncia a si mesmo na rede local. O celular se conecta diretamente via `http://streamdeck.local:8000`, eliminando a necessidade de digitar IPs locais dinâmicos.

### 2. A Interface (Frontend - React / Vite)
Criada para imersão total e pensada para telas AMOLED:
- **PWA (Progressive Web App):** Roda em tela cheia (Fullscreen API) sem barras de navegação do browser. Bloqueia o "sleep" da tela usando *Wake Lock API*.
- **Design Glassmorphism:** Botões translúcidos sobre o fundo `#000000` (preto absoluto), que economiza bateria no painel OLED do Mi 9 e evita o temido "Burn-in".
- **Resiliência:** Sistema de reconexão automática. Se o celular perder o Wi-Fi ou o PC reiniciar, a interface exibe uma tela preta ("Standby") e tenta reconectar silenciosamente a cada 3 segundos.
- **Responsividade:** Grades modulares em CSS puro que reagem a orientações retrato (Portrait) e paisagem (Landscape) dinamicamente, otimizando o número de colunas.

---

## 🚀 Como Executar no seu Setup

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/murilo-lameira/Stream-Deck.git
   ```
2. **Crie o seu `.env` na pasta backend:**
   ```env
   HOST=0.0.0.0
   PORT=8000
   AUTH_TOKEN=seu_token_secreto
   ```
3. **Instale as dependências (Python e Node):**
   - No frontend: `npm install` e `npm run build`
   - No backend: `pip install -r requirements.txt`
4. **Inicialize:**
   Dê dois cliques no arquivo `iniciar_streamdeck.vbs`. Ele subirá o backend de forma invisível.
5. **No Celular:**
   Acesse `http://streamdeck.local:8000`, adicione a página à Tela Inicial (PWA) e insira seu token nas configurações.

---

## 🎯 Conclusão
O que era uma sucata tecnológica na gaveta agora é uma central de comando luxuosa que substitui hardwares caríssimos de mercado. Um brinde à reciclagem tecnológica aliada à programação criativa!
