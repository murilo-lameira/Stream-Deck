# 🌐 Rede, Autodescoberta (mDNS) e Resiliência

Para proporcionar uma experiência sem atrito ("plug and play"), o Stream Deck adota estratégias dinâmicas de resolução de endereçamento.

---

## 1. Autodescoberta mDNS (ZeroConf)
* O backend utiliza a biblioteca `zeroconf` para anunciar o serviço localmente:
  * **Serviço:** `_http._tcp.local.`
  * **Nome de Domínio:** `http://streamdeck.local:8000`
* O celular pode se conectar diretamente por esse endereço sem a necessidade de saber o IP numérico do computador.

---

## 2. Mecanismo de Auto-Sincronização de IP (Frontend)
Ao acessar o Stream Deck por um novo IP no navegador (ex: após mudança de roteador para `192.168.15.16:8000`):
1. O hook de inicialização do React compara `window.location.hostname` com o valor gravado em `localStorage`.
2. Se o usuário estiver acessando por um IP válido diferente do salvo, o `localStorage` é sobrescrito automaticamente com `ws://${window.location.hostname}:8000/ws`.
3. Isso evita que o celular fique preso tentando se conectar ao IP antigo da rede anterior.

---

## 3. Considerações sobre Roteadores Adicionais (Access Point / AP)
Ao adicionar um roteador secundário:
* **Duplo NAT:** Se o roteador secundário operar como roteador independente (distribuindo IPs como `192.168.3.x`), os aparelhos conectados a ele ficam isolados do computador (`192.168.15.x`).
* **Solução:** Configurar o segundo roteador no **Modo Ponto de Acesso (AP / Bridge)** com DHCP desativado e cabo na porta LAN, unificando a sub-rede.
* **Isolamento de AP:** Desativar a opção *AP Isolation* para permitir tráfego entre Wi-Fi e cabo.

[[Visão Geral e Camadas]]
[[MAIN]]
