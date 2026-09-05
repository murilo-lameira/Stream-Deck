# 🎨 Diretrizes Visuais & Glassmorphism

O design do Stream Deck Mobile foi planejado especificamente para oferecer sofisticação visual sem comprometer a longevidade da tela AMOLED do Xiaomi Mi 9.

---

## 1. Estilo Glassmorphism
Simula vidro fosco translúcido com profundidade suave:
* **Fundo dos Botões:** `rgba(255, 255, 255, 0.4)` no modo claro ou `rgba(10, 10, 15, 0.72)` no modo escuro.
* **Desfoque:** `backdrop-filter: blur(12px)`.
* **Bordas e Relevo:** `border: 1px solid rgba(255, 255, 255, 0.08)`.
* **Acentos Coloridos:** Cada botão possui uma cor de destaque (`--app-color`) projetada em uma linha superior de 2px e um gradiente radial suave.

---

## 2. Modo Escuro & Standby OLED (Blackout)
* **Preto Puro (#000000):** No painel AMOLED, pixels pretos têm seus emissores desligados fisicamente, gerando consumo de energia próximo a zero e prevenindo *burn-in*.
* **OLED Standby:** Quando o PC é desligado ou a conexão cai, a interface é desmontada e substituída por uma tela 100% preta.
* **Double-Tap:** Toque duplo rápido em qualquer ponto da tela preta abre o modal de configurações para redefinir o IP se necessário.
## 3. Indicador Visual de App Ativo (LED Neon)
* **LED Pulsante:** Botões com processos em execução no Windows exibem um ponto luminoso verde neon no canto superior direito (`#10b981`).
* **Animação:** Efeito `ledPulse` suave alternando escala e intensidade de glow, simulando hardware físico ativo.

---

## 4. Haptic Feedback (Resposta Tátil)
* **Vibration API:** Disparos de micro-vibrações nativas no Mi 9:
  * `light (25ms)`: Toque padrão nos botões de aplicativos.
  * `medium (45ms)`: Alternância de mute ou tema escuro/claro.
  * `selection (12ms)`: Passos no slider de volume e transição de páginas.
  * `warning / success`: Padrões compostos para ações críticas e confirmações.

[[Componentes de Mídia]]
[[Responsividade e Orientação]]
[[MAIN]]
