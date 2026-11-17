/**
 * Converte a URL do WebSocket (ws://host:porta/ws) na base HTTP do mesmo servidor.
 * Retorna '' quando a URL e invalida.
 */
export function httpBaseFromWs(wsUrl) {
  try {
    const url = new URL(String(wsUrl || '').trim());
    if (url.protocol === 'ws:') return `http://${url.host}`;
    if (url.protocol === 'wss:') return `https://${url.host}`;
    return '';
  } catch {
    return '';
  }
}
