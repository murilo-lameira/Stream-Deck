# 🎵 Componentes de Mídia (Now Playing e Slider iOS)

A Página 2 é dedicada à reprodução multimídia e controle de som com foco em usabilidade tátil.

---

## 1. Widget Now Playing com Glow Dinâmico & Controles Inline
* **Extração de Cor:** O componente `NowPlaying.jsx` renderiza a thumbnail do álbum em um elemento `<canvas>` 16x16 invisível.
* **Cor Dominante & Ambient Aura:** Uma função algorítmica calcula a média RGB dos pixels e projeta uma aura difusa e translúcida (`filter: blur(28px)`) no card.
* **Controles Inline Rápidos:** Botões dedicados de `Play/Pause` e `Próxima Faixa` diretamente no card de mídia para controle instantâneo sem trocar de página.
* **Linha de Pulso de Progresso:** Uma barra luminosa de 2px pulsa sutilmente na base do banner enquanto a mídia estiver ativa.

---

## 2. Slider Tátil de Volume (Estilo iOS Control Center)
* **Cápsula Vertical Slim:** Altura expressiva de 88px de largura com bordas amplamente arredondadas.
* **Interação Contínua:** Permite deslizar o dedo no eixo Y para ajustar o volume de 0 a 100% em tempo real.
* **Catraca Tátil Háptica:** Emite micro-vibrações (`triggerHaptic(12)`) a cada **10%** de variação de volume, simulando um encoder rotativo com dentes.
* **Gradiente de Volume Alto:** Quando o volume ultrapassa 80%, a barra transiciona do branco para um degradê âmbar/alaranjado com brilho dinâmico.
* **Ícone Reativo:** O alto-falante na base altera o desenho conforme a faixa de volume e indica silenciamento ativo em vermelho.

[[Diretrizes de Design]]
[[MAIN]]
