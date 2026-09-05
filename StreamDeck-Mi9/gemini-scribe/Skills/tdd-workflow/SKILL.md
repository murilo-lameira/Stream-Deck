---
name: tdd-workflow
description: >-
  Executa o ciclo de Desenvolvimento Orientado a Testes (TDD) para o Stream Deck Mi9.
  Use ao criar novas rotas FastAPI, integrar serviços nativos (Pycaw, WinRT, psutil) ou refatorar lógica de backend e WebSocket.
user-invocable: true
metadata:
  origin: "ECC + StreamDeck"
  version: "1.0.0"
---

# 🧪 TDD Workflow (Stream Deck Mi9)

Este runbook estabelece o ciclo de testes estrito (**RED -> GREEN -> REFACTOR**) para o backend FastAPI e integrações do Windows.

---

## 🎯 Ciclo em 3 Etapas

```mermaid
graph LR
    A[1. RED: Escrever Teste com Falha] --> B[2. GREEN: Implementar Código Mínimo]
    B --> C[3. REFACTOR: Limpeza & Tipagem]
    C --> D[4. Validação & Handshake QA]
```

### 1. Etapa RED (Teste Primeiro)
- Crie ou atualize o teste em `backend/tests/` antes de alterar o código-fonte.
- Utilize `pytest` com mocks assíncronos para chamadas bloqueantes de sistema (Win32, Pycaw).
- Garanta que o teste falhe pelo motivo esperado.

### 2. Etapa GREEN (Código Funcional)
- Implemente apenas o código necessário para fazer o teste passar.
- Certifique-se de envolver operações de I/O e Win32 em `asyncio.to_thread`.

### 3. Etapa REFACTOR (Refatoração Limpa)
- Modularize a lógica no service (`services/`) ou router (`routers/`) apropriado.
- Adicione tipagem estrita com Pydantic (`schemas/`).

---

## 📋 Comandos de Execução
```bash
# Executar todos os testes com pytest
.\backend\venv\Scripts\pytest backend/tests/ -v

# Executar teste específico
.\backend\venv\Scripts\pytest backend/tests/test_audio.py -v
```
