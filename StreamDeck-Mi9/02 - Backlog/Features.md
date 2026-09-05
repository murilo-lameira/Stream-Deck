# 📋 Backlog de Funcionalidades & Melhorias (Stream Deck)

> Marque com um `[x]` as opções que deseja implementar. Quando terminar de escolher, me avise para iniciarmos a execução!

---

## 🛠️ 1. Correções & Arquitetura de Código
- [x] **1.1. Auto-Sincronização de IP sem Dead Code:** Corrigir a inicialização do estado no `App.jsx` para que o frontend sempre detecte e conecte ao IP correto do PC dinamicamente ao trocar de rede/roteador.
- [x] **1.2. Execução Não-Bloqueante de Apps no Backend:** Migrar lançadores de processos no Windows (`apps_config.py`) para `asyncio.to_thread` / chamadas assíncronas, evitando qualquer micro-travamento do servidor ao abrir programas pesados.
- [x] **1.3. Heartbeat & Reconexão Rápida no WebSocket:** Implementar ping/pong explícito a cada 15s para detectar e recuperar instantaneamente oscilações de Wi-Fi no Mi 9.
- [x] **1.4. Modularização do Backend:** Dividir o `main.py` em módulos especializados (`services/media.py`, `services/network.py`, `routers/deck.py`).

---

## 🎨 2. Design, UX & Otimizações para o Mi 9
- [x] **2.1. Haptic Feedback (Vibração Tátil):** Vibrar o celular brevemente (`navigator.vibrate`) ao tocar em qualquer botão, simulando a sensação física de um Elgato Stream Deck.
- [x] **2.2. Indicador Visual de App Ativo (LED/Glow):** Adicionar um LED verde neon discreto nos botões cujos programas já estiverem abertos/em execução no Windows.
- [x] **2.3. Modo OLED True Black:** Refinar o CSS do tema escuro para preto absoluto (`#000000`), economizando bateria na tela AMOLED do Mi 9 e realçando o efeito de vidro (glassmorphism).
- [ ] **2.4. Telemetria Rápida no Header:** Adicionar mini-widgets no topo do celular mostrando uso de CPU/RAM do PC e a latência (ping) do WebSocket.
- [x] **2.5. Transições com Física Fluida (Framer Motion):** Animações suaves estilo iOS ao trocar de página no deck e ao abrir os controles de volume.

---

## 🌐 3. Novas Integrações & Automação
- [ ] **3.1. Integração com n8n & Alexa:**
  - [ ] Criar aba/botões dedicados para disparar webhooks do n8n (rotinas de iluminação, cenas de estudo/game).
  - [ ] Suporte a comandos de voz via Alexa refletindo o status no painel do Stream Deck.
- [x] **3.2. Atalho Dedicado VMS (Câmeras de Casa):** Botão com ícone personalizado para abrir o painel de monitoramento de câmeras.
- [x] **3.3. Atalho Dedicado Projeto Checkup:** Botão e status em tempo real do nosso projeto de checkup.
- [ ] **3.4. Sistema de Macros / Múltiplas Ações:** Criar botões que executam sequências (ex: *"Modo Estudo"* -> Abre VS Code, abre Notion, ajusta volume em 40% e bota o microfone no mudo).
- [ ] **3.5. Soundboard Embutido:** Aba para disparar efeitos sonoros e memes com reprodução instantânea no PC.
