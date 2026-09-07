# 🤖 Orquestração de Agentes e Loop de Feedback

Este documento descreve o fluxo de execução em fases dos agentes do StreamDeck Mi9, incluindo o **Portão de Aprovação do Usuário (Human-in-the-Loop)** antes de qualquer implementação.

---

## 🔄 Fluxo de Execução com Gate de Aprovação

```mermaid
graph TD
    subgraph Fase1["Fase 1: Planejamento & Arquitetura"]
        A[Demanda / Requisito do Usuário] --> B[Planejador & Arquiteto]
        B --> C[Proposta de Mudanças & Contratos]
    end

    subgraph GateUser["🛑 Gate: Aprovação do Usuário"]
        C --> D{Usuário Aprovou o Plano?}
        D -- Não (Ajustar) --> B
    end

    subgraph Fase2["Fase 2: Implementação & TDD"]
        D -- Sim --> E[Backend Dev]
        D -- Sim --> F[Frontend & UI Dev]
        E --> G[Testes Unitários & Endpoints]
        F --> H[Componentes & Telas]
    end

    subgraph Fase3["Fase 3: Testes & Validação"]
        G --> I[QA Engineer]
        H --> I
        I --> J{Aprovado nos Testes?}
        J -- Não (Bugs/Falhas) --> E
        J -- Não (Quebras de UI) --> F
    end

    subgraph Fase4["Fase 4: Documentação & Vault"]
        J -- Sim --> K[Documentador & Vault Guardian]
        K --> L[Atualização do Obsidian & MEMORY.md]
        L --> M[Entrega Concluída no Git]
    end

    style Fase1 fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4
    style GateUser fill:#313244,stroke:#fab387,stroke-width:3px,color:#f38ba8
    style Fase2 fill:#181825,stroke:#a6e3a1,stroke-width:2px,color:#cdd6f4
    style Fase3 fill:#11111b,stroke:#f9e2af,stroke-width:2px,color:#cdd6f4
    style Fase4 fill:#181825,stroke:#cba6f7,stroke-width:2px,color:#cdd6f4
```

---

## 📋 Papéis e Responsabilidades por Fase

### 1. Fase 1: Planejamento e Arquitetura
- **Agentes:** 🧠 Planejador / Arquiteto de Software (`api-design`).
- **Momento:** Ativo no início da demanda.
- **Responsabilidade:** Análise de viabilidade, mapeamento de arquivos e elaboração do plano de mudanças detalhado.

### 🛑 Gate de Aprovação do Usuário (Human-in-the-Loop)
- **Momento:** Entre a Fase 1 e a Fase 2.
- **Regra Estrita:** NENHUMA linha de código de produção é alterada antes de o usuário revisar o plano e responder com aprovação explícita.

### 2. Fase 2: Implementação Técnica & TDD
- **Agentes:** 💻 Backend Dev (`tdd-workflow`) e 🎨 Frontend / UI Designer.
- **Momento:** Disparados somente após aprovação do plano pelo usuário.
- **Responsabilidade:** Escrita de código-fonte modular (`backend/`, `frontend/`) e testes automatizados.

### 3. Fase 3: Validação e Qualidade (QA)
- **Agentes:** 🧪 QA Engineer & Tester (`security-review`).
- **Momento:** Acionado após a conclusão da implementação.
- **Responsabilidade:** Execução de linters, testes e auditoria de segurança. Falhas retornam em loop para o Dev.

### 4. Fase 4: Documentação e Acervo
- **Agentes:** 📝 Documentador & Vault Guardian.
- **Momento:** Acionado após aprovação pelo QA. Atualiza o Obsidian, `MEMORY.md` e sincroniza com o Git.
