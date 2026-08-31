# Design e Interface UI/UX

## Estilo Visual: Glassmorphism
O frontend do Stream Deck foi projetado usando o conceito de **Glassmorphism**, um estilo moderno que simula vidro transl√∫cido (fosco) e fornece um aspecto premium e limpo.

Caracter√≠sticas adotadas:
- Caixas dos √≠cones (`.icon-container`) e bot√µes possuem fundo semi-transparente usando `rgba(255, 255, 255, 0.6)`.
- Efeito de desfoque de fundo implementado via CSS com `backdrop-filter: blur(12px)`.
- Sombreamento sutil para adicionar profundidade e destacar o relevo das bordas.

## Temas Claro e Escuro (Light / Dark Mode)
A interface permite a troca fluida de temas pelo cabe√ßalho do aplicativo. A prefer√™ncia √© salva diretamente no `localStorage` do dispositivo.

- **Tema Claro:** Baseia-se em um fundo suave e agrad√°vel com `radial-gradient` utilizando tons past√©is (azul claro / branco gelo), onde o vidro dos bot√µes esmaece perfeitamente.
- **Tema Escuro:** Emprega um fundo preto puro (`#000000`) aplicado ao `<html>` e `<body>` inteiro, proporcionando alt√≠ssimo contraste. O "vidro" dos √≠cones assume um tom escuro/grafite (`rgba(30, 41, 59)`). O preto absoluto evita qualquer borda indesejada e fica deslumbrante em telas AMOLED (como no Mi 9).

## Responsividade Din√¢mica (Portrait x Landscape)
A interface √© programada de forma h√≠brida utilizando *CSS Media Queries* para reagir √† orienta√ß√£o do celular:

- **Na Vertical (Portrait):** A interface exibe um cabe√ßalho fixo informando o t√≠tulo do aplicativo, status de conex√£o (Autenticado, Conectando, Erro), bot√£o de configura√ß√µes e bot√£o de altern√¢ncia de tema. A grade de bot√µes (Grid) exibe as categorias e nomes de cada app, formando at√© 4 linhas x 2 colunas.
- **Na Horizontal (Landscape):** A interface adota o estilo **"Modo Foco" (Minimalista)**. O cabe√ßalho, bot√µes, e todos os textos dos aplicativos desaparecem (`display: none`). Apenas os SVG's de √≠cones permanecem, e a grade se espande horizontalmente (2 linhas x 4 colunas) transformando o celular exatamente em um *Stream Deck* de bot√µes quadrados.

## Anima√ß√µes e Movimenta√ß√£o (Swiper)
Em vez de depender de scroll nativo que pode causar "esticamentos", a interface foi segmentada em slides atrav√©s da biblioteca **Swiper**.

- **Agrupamentos L√≥gicos:** Aplicativos padr√£o de Produtividade/M√≠dia/Comunica√ß√£o ficam no primeiro slide, enquanto a categoria `Jogos` (Steam, LoL, Discord) √© renderizada dinamicamente em uma tela secund√°ria.
- **Transi√ß√£o Premium:** Adotamos o m√≥dulo de Efeito Criativo (`EffectCreative`) que imita as transi√ß√µes visuais do iOS. Durante o deslize de p√°gina, o menu atual esmaece e √© empurrado em profundidade (escala e eixo Z) enquanto a pr√≥xima p√°gina desliza suavemente pelo eixo lateral por 550ms, garantindo o visual elegante.

[[Mapeamento de Aplicativos]]


## Modo Standby OLED (Blackout)
Para otimizar o uso de bateria de telas AMOLED enquanto o PC estiver desligado, o aplicativo monitora a perda de conex„o WebSocket.
- Ao identificar o estado \ERROR\ ou \RECONNECTING\, toda a interface web È "desmontada" da tela.
- Uma ˙nica \div\ com \100vw\ e \100vh\ contendo um fundo \#000000\ absoluto È injetada. 
- Sem pixels ligados, a tela do aparelho se apaga fisicamente. O mecanismo possui um backdoor oculto: executar um \double tap\ na tela aciona o Modal de ConfiguraÁıes, caso o servidor Python tenha mudado de IP na rede e vocÍ precise reconectar manualmente.

## Slider T·til de Volume (Estilo iOS Control Center)
Na aba de MÌdia, os botıes discretos de volume foram substituÌdos por uma **c·psula vertical transl˙cida** inspirada no design da Central de Controle da Apple:
- **Gestos de Arraste e Toque:** Suporta deslize contÌnuo do dedo no eixo Y com resposta instant‚nea e vibraÁ„o h·ptica curta no aparelho.
- **Preenchimento Din‚mico:** Uma barra branca sÛlida sobe a partir da base indicando a porcentagem exata (0% a 100%).
- **Õcone e AÁ„o de Mute:** O Ìcone do alto-falante na base altera seu formato dinamicamente (Vazio, Baixo, MÈdio, Alto, Mudo) e, ao ser tocado, alterna instantaneamente o estado de silenciamento.

### Refinamento Visual da Central de MÌdia
- **Simetria e Delicadeza:** O layout de MÌdia organiza uma coluna vertical com o Slider Slim iOS (88px) harmonizado lado a lado com uma grade 2x2 com **4 botıes perfeitamente idÍnticos em tamanho e formato**:
  - \Anterior\ (SkipBack)
  - \PrÛxima\ (SkipForward)
  - \Play / Pause\ (Play)
  - \Mutar / Desmutar\ (VolumeX / Volume2 com indicador vermelho ativo quando silenciado)

### PadronizaÁ„o Total dos Botıes de MÌdia (DeckButton)
- A tela de MÌdia utiliza o componente oficial \DeckButton\ para todos os comandos de reproduÁ„o e mute (\Anterior\, \Play/Pause\, \PrÛxima\, \Mutar\).
- Isso garante **100% de uniformidade visual**: cada bot„o possui o mesmo contÍiner de Ìcone com SVG de 56px, rÛtulo de texto, tag de categoria, efeito de relevo e resposta h·ptica do restante do ecossistema do Stream Deck.

### Iconografia SÛlida Padronizada (SVGs)
- Todos os Ìcones de controle de reproduÁ„o (\media-play\, \media-prev\, \media-next\, \ol-mute\ e \power\) foram remodelados como **vetores sÛlidos e preenchidos** (Full-Fill SVGs), exatamente no mesmo padr„o de densidade visual e preenchimento dos aplicativos de jogos (\discord.svg\ e \league-of-legends.svg\).
- Na tela 2 (MÌdia), os botıes ocupam exatamente as mesmas cÈlulas de grade que qualquer outro bot„o do sistema, mantendo apenas a c·psula vertical de volume com visual diferenciado.

### ResoluÁ„o de Responsividade Landscape (MÌdia)
- **Grade Adaptativa:** No modo horizontal (Landscape), a tela de mÌdia È dividida na proporÁ„o 1fr 2fr 1fr. Isso centraliza os botıes em uma subgrade 2x2 no centro, garantindo que os botıes de mÌdia adotem dimensıes e proporÁıes matematicamente idÍnticas aos botıes normais do aplicativo, eliminando o esticamento indesejado.
