# 🎵 Componentes de Mídia (Now Playing e Slider iOS)

A Página 2 é dedicada à reprodução multimídia e controle de som com foco em usabilidade tátil.

---

## 1. Widget Now Playing com Glow Dinâmico
* **Extração de Cor:** O componente `NowPlaying.jsx` renderiza a thumbnail do álbum em um elemento `<canvas>` 16x16 invisível.
* **Cor Dominante:** Uma função algorítmica calcula a média RGB dos pixels e define a variável CSS `--np-accent`.
* **Efeito Neon Rápido:** O card ganha uma sombra externa difusa e linha superior correspondentes à cor do álbum atual, com transição ágil de `0.15s ease`.

---

## 2. Slider Tátil de Volume (Estilo iOS Control Center)
* **Cápsula Vertical Slim:** Altura expressiva de 88px de largura com bordas amplamente arredondadas.
* **Interação Contínua:** Permite deslizar o dedo no eixo Y para ajustar o volume de 0 a 100% em tempo real.
* **Feedback Háptico:** Emite micro-vibrações (`navigator.vibrate(10)`) durante o ajuste para simular atrito mecânico.
* **Ícone Reativo:** O alto-falante na base altera o desenho conforme a faixa de volume e indica silenciamento ativo em vermelho.

[[Diretrizes de Design]]
[[MAIN]]
