import React, { useState, useEffect } from 'react';
import { X, Save, RotateCcw, Server, Link2 } from 'lucide-react';
import { getDefaultWebSocketUrl } from '../config/constants';

export function SettingsModal({
  isOpen,
  onClose,
  currentUrl,
  onSave,
  onRepair,
}) {
  const [url, setUrl] = useState(currentUrl);

  // Ressincroniza a URL com o valor salvo a cada abertura do modal
  useEffect(() => {
    if (isOpen) setUrl(currentUrl);
  }, [isOpen, currentUrl]);

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    onSave({ url });
    onClose();
  };

  const handleReset = () => {
    setUrl(getDefaultWebSocketUrl());
  };

  const handleRepair = () => {
    const trimmed = url.trim();
    if (trimmed && trimmed !== currentUrl) onSave({ url: trimmed });
    onRepair();
    onClose();
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

          <div className="pairing-shortcut-box">
            <button type="button" className="btn-secondary" onClick={handleRepair}>
              <Link2 size={16} /> Parear de novo
            </button>
            <span className="form-hint">
              Apaga o pareamento deste aparelho e pede um novo código do PC.
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
