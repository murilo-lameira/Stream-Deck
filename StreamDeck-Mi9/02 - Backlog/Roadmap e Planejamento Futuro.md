# 🚀 Roadmap e Planejamento Futuro (V9 e V10)

Próximos passos planejados para expandir o ecossistema do Stream Deck Mobile com inteligência artificial, automação residencial e flexibilidade.

---

## Versão V9 - Automações n8n & Agente Alexa

### 1. Gatilhos Externos REST no Backend
- [ ] Implementar endpoint `POST /api/trigger` protegido por Bearer Token.
- [ ] Permitir acionamento de qualquer app ou macro remotamente via HTTP pelo n8n.

### 2. Despacho de Webhooks pelo Stream Deck
- [ ] Criar ação do tipo `call_webhook` no WebSocket para disparar fluxos no n8n.
- [ ] Suporte a envio de parâmetros contextuais (horário, estado de mídia, botão clicado).

### 3. Integração Bidirecional com Alexa
- [ ] Criação de rotinas e Skills da Alexa conectadas ao n8n.
- [ ] Agente inteligente (Gemini / LangChain no n8n) interpretando comandos de voz como *"Alexa, preparar estúdio de gravação"* e disparando as ações no Windows e na iluminação residencial.

---

## Versão V10 - Stream Deck 2.0 (Customização Dinâmica)

### 1. Editor Web de Botões (Drag & Drop)
- [ ] Interface visual para adicionar, reordenar e excluir botões diretamente pelo celular ou PC.
- [ ] Persistência de layout em `config/apps.json` em vez de código hardcoded.

### 2. Páginas Infinitas & Pastas
- [ ] Suporte a criar N páginas no Swiper dinamicamente.
- [ ] Suporte a pastas de atalhos (tocar em um botão para abrir sub-grade).

### 3. Widget de Câmera RTSP ao Vivo
- [ ] Modal com mini-stream ao vivo em baixa latência da câmera do portão/garagem via VMS.

[[Histórico de Entregas]]
[[MAIN]]
