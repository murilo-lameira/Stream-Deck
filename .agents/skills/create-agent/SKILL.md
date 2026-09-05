---
name: create-agent
description: >-
  Cria, configura e registra novos agentes especializados no ecossistema Stream Deck Mi9.
  Use esta skill sempre que o usuário solicitar a criação de um novo agente, definição de personas,
  atribuição de ferramentas/skills modulares ou expansão do pipeline em fases de desenvolvimento.
user-invocable: true
metadata:
  version: "1.1.0"
  architecture: "ECC + OpenMAIC + Staged Loop"
---

# 🤖 Create Agent Skill

Esta skill define o Procedimento Operacional Padrão (SOP) para criar, parametrizar e integrar novos agentes de IA no ecossistema do **Stream Deck Mi9**. Ela combina o rigor de engenharia do **ECC (Enterprise Coding Companion)** e os princípios modulares do **OpenMAIC** com o pipeline em fases do projeto.

---

## 🧰 Catálogo de Skills Modulares Disponíveis

Ao configurar um agente, atribua a ele apenas as skills necessárias para o seu papel:

| Skill | Escopo & Utilidade | Agentes Recomendados |
| :--- | :--- | :--- |
| **`tdd-workflow`** | Ciclo RED -> GREEN -> REFACTOR com pytest e mocks | Backend Dev, QA Tester |
| **`security-review`** | Checklist de segurança Win32, sanitização de inputs e WebSocket | Arquiteto, QA Tester |
| **`api-design`** | Contratos REST FastAPI e envelopes de WebSocket | Planejador, Backend Dev |
| **`archify`** | Geração e validação de diagramas interativos em HTML/SVG | Planejador, Vault Guardian |
| **`create-agent`** | Criação, parametrização e registro de novas personas | Planejador / Arquiteto |

---

## 🎯 Princípios Fundamentais (ECC + OpenMAIC)

1. **Fase e Momento Claros:** Todo agente pertence a uma fase explícita (Planejamento, Implementação, QA ou Docs).
2. **Separação de Papéis vs. Habilidades:**
   - **Persona:** Define identidade, limites e regras de atuação.
   - **Skills:** Conhecimento procedimental e checklists executáveis.
3. **Loop de Engenharia Rígido:**
   $$\text{Plan (Fase 1)} \longrightarrow \text{Dev + TDD (Fase 2)} \longrightarrow \text{QA Gate (Fase 3)} \longrightarrow \text{Vault Guardian (Fase 4)}$$
4. **Governança do Vault:** Nenhum arquivo markdown pode ultrapassar 200 linhas; codificação estritamente em UTF-8 sem BOM.

---

## 📋 SOP em 4 Etapas para Criação de um Novo Agente

```mermaid
graph TD
    A[Etapa 1: Definição de Escopo & Fase] --> B[Etapa 2: Seleção de Skills & YAML]
    B --> C[Etapa 3: Registro no Vault & Orquestração]
    C --> D[Etapa 4: Validação & Feedback Loop]
```

### Etapa 1: Definição de Escopo e Fase
- **Identificador:** `kebab-case` (ex: `security-auditor`, `audio-specialist`).
- **Fase de Atuação:** `Fase 1 (Arquitetura)`, `Fase 2 (Dev/UI)`, `Fase 3 (QA)` ou `Fase 4 (Docs)`.
- **Skills Associadas:** Selecionadas da tabela acima.

---

### Etapa 2: Geração do Prompt de Sistema
Crie o prompt em `StreamDeck-Mi9/gemini-scribe/Prompts/<agent-id>.md`:

```markdown
---
name: "<Nome do Agente>"
description: "<Breve resumo da especialidade e escopo>"
version: 1
override_system_prompt: false
phase: "<Fase 1 | 2 | 3 | 4>"
tags: ["<tag1>", "<tag2>"]
skills_assigned: ["tdd-workflow", "api-design"]
tools_allowed: ["read_file", "write_to_file", "run_command"]
---

Você é o <Nome do Agente> do Stream Deck Mobile.
Sua missão é <descrever a missão principal>.

Diretrizes Estritas:
- <Diretriz técnica 1: modularização em services/routers>
- <Diretriz técnica 2: chamadas assíncronas com asyncio.to_thread>
- <Diretriz técnica 3: validação de contratos com Pydantic>
```

---

### Etapa 3: Registro na Governança e Orquestração
1. Salve o prompt na pasta `StreamDeck-Mi9/gemini-scribe/Prompts/<agent-id>.md`.
2. Atualize o fluxo de fases em `StreamDeck-Mi9/01 - Arquitetura/Orquestracao de Agentes e Loop de Feedback.md`.
3. Sincronize o papel no `squad-bridge.js` se aplicável.

---

### Etapa 4: Validação e Feedback Loop
1. Verifique a sintaxe YAML e integridade do UTF-8.
2. Certifique-se de que a saída respeite o handoff entre fases.
3. Realize commit e push para o repositório Git.
