# 🤖 Integração com n8n & Alexa (Fluxos de Agente)

Arquitetura para transformar o Stream Deck em uma ponte para automação residencial e inteligência artificial conectada à Alexa.

---

## 1. Visão Geral da Arquitetura
A integração funciona em duas vias:
1. **Voz para o Computador:** Alexa -> n8n -> Stream Deck Backend -> Windows.
2. **Deck para a Casa Inteligente:** Celular -> Stream Deck Backend -> n8n -> Alexa / IoT.

---

## 2. Fluxo 1: Comando por Voz na Alexa
```text
[ Usuário ] -> Fala "Alexa, modo estúdio"
      │
      ▼
[ Skill Alexa / Webhook ] -> Dispara fluxo no n8n
      │
      ▼
[ Agente n8n ] -> Avalia regras e gera POST HTTP:
      │           URL: http://192.168.15.16:8000/api/trigger
      │           Header: Authorization: Bearer <AUTH_TOKEN>
      │           Payload: {"action": "open", "app": "obs"}
      ▼
[ Stream Deck Backend ] -> Abre OBS Studio, CheckUP e muta microfone
```

---

## 3. Fluxo 2: Botão de Cena no Stream Deck
```text
[ Toque no Celular ] -> Botão "Modo Noturno"
      │
      ▼
[ WebSocket ] -> {"action": "call_webhook", "target": "cena_noite"}
      │
      ▼
[ FastAPI Backend ] -> Encaminha para http://localhost:5678/webhook/cena_noite
      │
      ▼
[ n8n Automation ] -> Apaga luzes, liga ar-condicionado e comanda
                     a Alexa para emitir aviso sonoro de boa noite.
```

[[Catálogo de Aplicativos]]
[[MAIN]]
