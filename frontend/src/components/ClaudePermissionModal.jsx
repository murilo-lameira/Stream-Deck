import React, { useState, useEffect } from 'react';
import { ShieldQuestion } from 'lucide-react';
import { hapticFeedback } from '../utils/haptics';

function formatRemaining(deadline) {
  const total = Math.max(Math.ceil((deadline - Date.now()) / 1000), 0);
  const m = Math.floor(total / 60);
  const s = String(total % 60).padStart(2, '0');
  return `${m}:${s}`;
}

export function ClaudePermissionModal({ request, position, total, onRespond }) {
  const [, setTick] = useState(0);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, []);

  const respond = (decision) => {
    if (sent) return;
    setSent(true);
    hapticFeedback.medium();
    if (!onRespond(request.request_id, decision)) setSent(false);
  };

  return (
    <div className="modal-backdrop claude-perm-backdrop" role="dialog" aria-modal="true">
      <div className="modal-content claude-perm-content">
        <div className="claude-perm-header">
          <div className="modal-title-group">
            <ShieldQuestion size={20} className="modal-icon" color="#fbbf24" />
            <h2>Claude pede permissão</h2>
          </div>
          <span className="claude-perm-position">{position} de {total}</span>
        </div>

        <div className="claude-perm-meta">
          {request.tool_name} · {request.project}
        </div>

        <pre className="claude-perm-summary">{request.summary}</pre>

        <div className="claude-perm-timer">Expira em {formatRemaining(request.deadline)}</div>

        <div className="claude-perm-actions">
          <button type="button" className="claude-perm-btn claude-perm-deny" disabled={sent} onClick={() => respond('deny')}>
            Negar
          </button>
          <button type="button" className="claude-perm-btn claude-perm-allow" disabled={sent} onClick={() => respond('allow')}>
            Permitir
          </button>
        </div>
      </div>
    </div>
  );
}
