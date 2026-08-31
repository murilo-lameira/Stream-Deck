import React from 'react';
import { X, AlertTriangle, PowerOff } from 'lucide-react';

export function ConfirmModal({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <AlertTriangle size={20} className="modal-icon" color="#ef4444" />
            <h2>{title}</h2>
          </div>
          <button className="btn-close" onClick={onCancel} aria-label="Cancelar">
            <X size={20} />
          </button>
        </div>

        <div className="modal-form">
          <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '10px' }}>
            {message}
          </p>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onCancel} style={{ flex: 1, justifyContent: 'center' }}>
              Cancelar
            </button>
            <button 
              type="button" 
              className="btn-primary" 
              onClick={onConfirm}
              style={{ background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)', boxShadow: '0 4px 15px rgba(239, 68, 68, 0.3)' }}
            >
              <PowerOff size={16} /> Desligar Agora
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

