# 🧠 Central de Governança & Guia de Leitura dos Agentes

Este documento é a **Bússola de Operação (MAIN)** do *Vault* Obsidian para o projeto **Stream Deck Mobile**. Ele estabelece as regras obrigatórias que qualquer agente de IA ou desenvolvedor deve seguir ao inspecionar, criar ou alterar documentações.

---

## 🎯 Regras de Ouro de Documentação
1. **Limite Estrito de Linhas:** Nenhum arquivo `.md` pode ultrapassar **200 linhas**.
2. **Modularidade:** Documentos grandes devem ser fragmentados por escopo (ex: histórico de versões separado do roadmap).
3. **Padrão de Encoding:** Todo arquivo deve ser salvo estritamente em **UTF-8** sem BOM.
4. **Links Bidirecionais:** Use links do Obsidian no padrão `[[Nome do Arquivo]]` para manter o grafo conectado.

---

## 🗺️ Mapa de Categorias e Quando Ler/Alterar

| Pasta | Conteúdo Principal | Quando o Agente DEVE LER | Quando o Agente DEVE ALTERAR |
|---|---|---|---|
| **00 - Meta** | Regras, guia de governança e índice geral. | No início de qualquer sessão ou tarefa complexa. | Apenas ao criar novas categorias ou regras globais. |
| **01 - Arquitetura** | Visão do sistema, protocolo WebSocket e redes/mDNS. | Ao mexer no backend (`main.py`), comunicação ou conectividade. | Ao alterar rotas, contratos de dados ou fluxo de portas. |
| **02 - Backlog** | Histórico de entregas (`V1-V7`) e Roadmap (`V8-V10`). | Antes de propor novas tarefas ou refatorações. | Após concluir features ou planejar novas sprints. |
| **03 - Design** | Diretrizes visuais, Glassmorphism, OLED Blackout, Slider iOS. | Ao alterar componentes React, CSS ou ícones SVG. | Ao introduzir novos estilos visuais, temas ou componentes UI. |
| **04 - Integracoes** | Especificações de integrações externas (n8n, Alexa, Webhooks). | Ao planejar ou implementar fluxos de automação residencial. | Ao criar ou modificar payloads de integração ou endpoints REST. |
| **05 - Aplicativos** | Mapeamento detalhado de apps (Páginas 1, 2 e 3) e regras Windows. | Antes de adicionar ou editar botões/executáveis. | Sempre que um novo app, jogo ou comando de sistema for inserido. |

---

## 🚀 Pipeline Orquestrado dos Agentes (Feedback Loop)
1. **Fase 1 - Construção (Dev & UI/UX):** Trabalham em paralelo produzindo backend, regras do Windows e interfaces.
2. **Fase 2 - Revisão (Revisor):** Audita contratos de WebSocket, segurança de tokens e consistência.
3. **Fase 3 - Homologação & Testes (QA):** Executa builds e testes. Se encontrar falha, **reabre o ciclo devolvendo feedback para Dev e UI/UX**.
4. **Fase 4 - Governança & Finalização (Documentador):** **Só atua no final**, após a aprovação formal do QA, atualizando notas, backlogs e garantindo a regra de `< 200 linhas`.

[[Índice Geral]]
