/**
 * Stream Deck - Pixel Agents Bridge Local
 * Localizado em: scripts/pixel_agents_bridge.js
 * 
 * Executado automaticamente pelo atalho global 'squad' quando disparado nesta pasta.
 * Sincroniza a governança (MAIN.md) e os agentes no Obsidian, depois ativa o Squad no Pixel Agents.
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const VAULT_DIR = path.join(ROOT_DIR, 'StreamDeck-Mi9');

// Função que assegura a existência e integridade do MAIN.md e prompts dos agentes
function ensureObsidianGovernance() {
  if (!fs.existsSync(VAULT_DIR)) return;

  const metaDir = path.join(VAULT_DIR, '00 - Meta');
  const promptsDir = path.join(VAULT_DIR, 'gemini-scribe', 'Prompts');

  if (!fs.existsSync(metaDir)) fs.mkdirSync(metaDir, { recursive: true });
  if (!fs.existsSync(promptsDir)) fs.mkdirSync(promptsDir, { recursive: true });

  const mainPath = path.join(metaDir, 'MAIN.md');
  if (!fs.existsSync(mainPath)) {
    const mainContent = `# 🧠 Central de Governança & Guia de Leitura dos Agentes

Este documento é a **Bússola de Operação (MAIN)** do *Vault* Obsidian para o projeto **Stream Deck Mobile**.

---

## 🎯 Regras de Ouro de Documentação
1. **Limite Estrito de Linhas:** Nenhum arquivo \`.md\` pode ultrapassar **200 linhas**.
2. **Modularidade:** Documentos grandes devem ser fragmentados por escopo.
3. **Padrão de Encoding:** Todo arquivo deve ser salvo estritamente em **UTF-8** sem BOM.
4. **Links Bidirecionais:** Use links do Obsidian no padrão \`[[Nome do Arquivo]]\`.

---

## 🗺️ Mapa de Categorias e Quando Ler/Alterar

| Pasta | Conteúdo Principal | Quando o Agente DEVE LER | Quando o Agente DEVE ALTERAR |
|---|---|---|---|
| **00 - Meta** | Regras, guia de governança e índice geral. | No início de qualquer sessão ou tarefa complexa. | Apenas ao criar novas categorias ou regras globais. |
| **01 - Arquitetura** | Visão do sistema, protocolo WebSocket e redes/mDNS. | Ao mexer no backend (\`main.py\`), comunicação ou conectividade. | Ao alterar rotas, contratos de dados ou fluxo de portas. |
| **02 - Backlog** | Histórico de entregas (\`V1-V8\`) e Roadmap (\`V9-V10\`). | Antes de propor novas tarefas ou refatorações. | Após concluir features ou planejar novas sprints. |
| **03 - Design** | Diretrizes visuais, Glassmorphism, OLED Blackout, Slider iOS. | Ao alterar componentes React, CSS ou ícones SVG. | Ao introduzir novos estilos visuais, temas ou componentes UI. |
| **04 - Integracoes** | Especificações de integrações externas (n8n, Alexa, Webhooks). | Ao planejar ou implementar fluxos de automação residencial. | Ao criar ou modificar payloads de integração ou endpoints REST. |
| **05 - Aplicativos** | Mapeamento detalhado de apps (Páginas 1, 2 e 3) e regras Windows. | Antes de adicionar ou editar botões/executáveis. | Sempre que um novo app, jogo ou comando de sistema for inserido. |

[[Índice Geral]]
`;
    fs.writeFileSync(mainPath, mainContent, 'utf8');
    console.log('[Pixel Squad] 📄 MAIN.md criado em 00 - Meta/');
  }

  console.log('[Pixel Squad] 🧠 Governança e MAIN.md sincronizados no Obsidian com sucesso!');
}

// Dispara a sincronização de governança antes de exportar o Squad
ensureObsidianGovernance();

// Mapeamento dos 5 agentes especializados para o Pixel Agents
const SQUAD = [
  {
    id: 'squad-dev',
    name: 'Dev (Backend & Windows)',
    actions: [
      { tool: 'Edit', input: { file_path: 'backend/main.py' }, desc: 'Otimizando rotas e orquestrador assíncrono' },
      { tool: 'Edit', input: { file_path: 'backend/apps_config.py' }, desc: 'Gerenciando processos nativos e foco Windows' },
      { tool: 'Read', input: { file_path: 'backend/services/media_service.py' }, desc: 'Auditando serviço WinRT de mídia' }
    ]
  },
  {
    id: 'squad-ui',
    name: 'UI/UX (Frontend & OLED)',
    actions: [
      { tool: 'Edit', input: { file_path: 'frontend/src/App.css' }, desc: 'Refinando tema OLED True Black e Glassmorphism' },
      { tool: 'Edit', input: { file_path: 'frontend/src/components/DeckButton.jsx' }, desc: 'Ajustando feedback tátil e LED de app ativo' },
      { tool: 'Read', input: { file_path: 'frontend/src/components/DeckSwiper.jsx' }, desc: 'Revisando layout de slides para Mi 9' }
    ]
  },
  {
    id: 'squad-qa',
    name: 'QA (Testes & Resiliência)',
    actions: [
      { tool: 'Bash', input: { command: 'npm --prefix frontend run build' }, desc: 'Validando compilação do bundle de produção' },
      { tool: 'Read', input: { file_path: 'frontend/src/hooks/useWebSocket.js' }, desc: 'Testando resiliência do heartbeat e reconexão' }
    ]
  },
  {
    id: 'squad-reviewer',
    name: 'Revisor (Arquitetura & Segurança)',
    actions: [
      { tool: 'Read', input: { file_path: 'backend/routers/deck_router.py' }, desc: 'Auditando handshake de tokens e segurança de portas' },
      { tool: 'Grep', input: { query: 'running_apps' }, desc: 'Verificando integridade dos contratos WebSocket' }
    ]
  },
  {
    id: 'squad-doc',
    name: 'Documentador (Obsidian & Governança)',
    actions: [
      { tool: 'Write', input: { file_path: 'StreamDeck-Mi9/00 - Meta/MAIN.md' }, desc: 'Validando teto de 200 linhas e regras de governança' },
      { tool: 'Edit', input: { file_path: 'StreamDeck-Mi9/02 - Backlog/Features.md' }, desc: 'Atualizando checklist de features e entregas' }
    ]
  }
];

module.exports = {
  SQUAD,
  ensureObsidianGovernance
};
