# Tecnologias Utilizadas

A base da infraestrutura que torna o projeto Stream Deck rápido, assíncrono e leve no desktop.

## Frontend (Interface Web Mobile)
- **React.js & Vite:** Framework front-end principal para a montagem de interfaces unificadas. O `Vite` garante hot-reloads instatâneos durante o desenvolvimento e build ultrarrápido (HMR).
- **Swiper.js:** Biblioteca especializada em controle de gestos e paginação em dispositivos de toque (touch). Utilizado para emular um comportamento nativo nas abas, agrupando as categorias usando animações de transição premium (`EffectCreative`).
- **Lucide-react:** Pacote iconográfico mínimo usado majoritariamente no Hub/Header para indicadores de status do WebSocket e configurações, substituindo ícones pesados de PNG.
- **CSS3 Moderno:** Utilização em massa de propriedades modernas, cobrindo CSS Grid dinâmicos e suporte nativo ao `@media (orientation: landscape)` somados a `backdrop-filter` para os desfoques de lente do projeto.
- **Screen Wake Lock API:** API nativa do navegador invocada ativamente (`navigator.wakeLock.request('screen')`) atrelada ao evento `visibilitychange`. Previne que o sistema operacional móvel entre em modo de suspensão de tela enquanto a interface de controle estiver ativa.

## Backend (Controle do Sistema Operacional)
- **Python 3:** Linguagem mãe para interação transparente com subsistemas Windows, lidando perfeitamente bem com manipulação de processos e sistema de arquivos.
- **FastAPI:** Framework backend absurdamente veloz, moderno e assíncrono, operando sob ASGI (`uvicorn`). Construído em cima do `starlette`, lida impecavelmente com conexões prolongadas via WebSockets.
- **WebSockets:** O protocolo responsável pela baixa latência (sem a sobrecarga de cabeçalhos do protocolo HTTP tradicional). A conexão de rede é bidirecional o que permite enviar sinais de "Click" para abrir aplicativos instantaneamente e receber relatórios de status em tempo real na interface (ex: Falha, Sucesso, Desconectado).

## Automação Desktop (Windows Scripting)
- **VBScript (.vbs):** Linguagem padrão de scripting do Windows. O arquivo instanciador principal `.vbs` invoca funções assíncronas do WshShell via `cmd.exe` usando as diretrizes `, 0, False`, a chave mestre para criar processos fantasmas invisíveis na barra de tarefas.
- **PowerShell:** Empregado no registro do autostart, possuindo controle avançado via cmdlets para manipular adequadamente o `HKCU` no registro do sistema garantindo a auto-partida no login, sem requerer privilégios adicionais de Administrador ou causar alertas UAC de elevação.

[[Tecnologias]]

- **pycaw (Python Core Audio Windows Library):** Utilizado no backend para manipula��o e leitura direta dos endpoints de �udio do Windows (Master Volume Scalar e Mute).
