---
name: api-design
description: >-
  Padrões de design de contratos REST e envelopes WebSocket para o ecossistema Stream Deck Mi9.
  Use ao planejar novas rotas HTTP, mensagens de broadcast ou sincronização de estado cliente-servidor.
user-invocable: true
metadata:
  origin: "ECC + StreamDeck"
  version: "1.0.0"
---

# 📐 API Design Patterns (REST & WebSocket)

Padronização de contratos para manter o cliente mobile (PWA) e o backend FastAPI perfeitamente sincronizados.

---

## 🌐 Convenções REST FastAPI

- **Rotas:** Sempre no plural, minúsculas e kebab-case (`/api/v1/apps`, `/api/v1/audio/volume`).
- **Verbos:**
  - `GET`: Leitura de estado (idempotente).
  - `POST`: Execução de ações (ex: abrir app, toggle mute).
  - `PUT / PATCH`: Atualizações parciais de configuração.

### Códigos de Status HTTP Padrão
- `200 OK`: Sucesso com corpo de retorno.
- `204 No Content`: Ação executada com sucesso sem payload de retorno.
- `400 Bad Request`: Payload malformado.
- `422 Unprocessable Entity`: Erro de validação Pydantic.
- `500 Internal Server Error`: Falha interna capturada e logada.

---

## ⚡ Formato dos Envelopes WebSocket

Todas as mensagens trocadas no endpoint `/ws/streamdeck` devem seguir o envelope padronizado:

```json
{
  "event": "volume_changed | media_updated | apps_updated | ping",
  "data": { ... },
  "timestamp": 1741190000.0
}
```
