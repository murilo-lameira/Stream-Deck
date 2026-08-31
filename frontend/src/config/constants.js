export const DEFAULT_AUTH_TOKEN = "mi9_deck_secret_2026";
export const STORAGE_KEY_TOKEN = "streamdeck_token";
export const STORAGE_KEY_SERVER = "streamdeck_server";

export function getDefaultWebSocketUrl() {
  const hostname = window.location.hostname || "localhost";
  return `ws://${hostname}:8000/ws`;
}
