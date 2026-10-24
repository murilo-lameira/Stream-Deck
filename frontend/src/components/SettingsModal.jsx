import React, { useState } from 'react';
import { X, Save, RotateCcw, Shield, Server, Copy, Check } from 'lucide-react';
import { DEFAULT_AUTH_TOKEN, getDefaultWebSocketUrl } from '../config/constants';

export function SettingsModal({
  isOpen,
  onClose,
  currentUrl,
  currentAuthToken,
  onSave,
}) {
  const [url, setUrl] = useState(currentUrl);
  const [token, setToken] = useState(currentAuthToken);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    onSave({ url, token });
    onClose();
  };

  const handleReset = () => {
    setUrl(getDefaultWebSocketUrl());
    setToken(DEFAULT_AUTH_TOKEN);
  };

  const handleCopyPairingLink = async () => {
    let host = window.location.host;
    try {
      if (url) {
        const wsParsed = new URL(url.replace('ws://', 'http://').replace('wss://', 'https://'));
        if (wsParsed.hostname && wsParsed.hostname !== 'localhost' && wsParsed.hostname !== '127.0.0.1') {
          host = wsParsed.host;
        }
      }
    } catch {}

    const protocol = window.location.protocol || 'http:';
    const pairingUrl = `${protocol}//${host}/?token=${encodeURIComponent(token)}`;

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(pairingUrl);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = pairingUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    } catch (err) {
      console.error('Falha ao copiar link de conexão mobile:', err);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <Server size={20} className="modal-icon" />
            <h2>Configurações do Stream Deck</h2>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Fechar">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSave} className="modal-form">
          <div className="form-group">
            <label htmlFor="server-url">
              <Server size={16} /> Endereço do WebSocket
            </label>
            <input
              id="server-url"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="ws://192.168.1.100:8000/ws"
              required
            />
            <span className="form-hint">
              No Mi 9, use o IP do seu computador na rede Wi-Fi.
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="auth-token">
              <Shield size={16} /> Token de Autenticação
            </label>
            <input
              id="auth-token"
              type="text"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Token de segurança (.env)"
              required
            />
            <span className="form-hint">
              Deve ser idêntico ao <code>AUTH_TOKEN</code> no arquivo <code>backend/.env</code>.
            </span>
          </div>

          <div className="pairing-shortcut-box">
            <button
              type="button"
              className={`btn-copy-link ${copied ? 'copied' : ''}`}
              onClick={handleCopyPairingLink}
              title="Copiar link com token embutido para parear o Xiaomi Mi 9 rapidamente"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
              <span>{copied ? 'Link de Conexão Copiado!' : 'Copiar Link de Conexão'}</span>
            </button>
            <span className="form-hint">
              Abra este link no Mi 9 para conectar e autenticar com um toque.
            </span>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={handleReset}>
              <RotateCcw size={16} /> Restaurar Padrão
            </button>
            <button type="submit" className="btn-primary">
              <Save size={16} /> Salvar e Reconectar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
