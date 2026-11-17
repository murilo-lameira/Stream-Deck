import React, { useState, useEffect, useRef } from 'react';
import { ShieldQuestion } from 'lucide-react';
import { hapticFeedback } from '../utils/haptics';

function formatRemaining(deadline) {
  const total = Math.max(Math.ceil((deadline - Date.now()) / 1000), 0);
  const m = Math.floor(total / 60);
  const s = String(total % 60).padStart(2, '0');
  return `${m}:${s}`;
}

const ARMING_DELAY_MS = 800;

export function ClaudePermissionModal({ request, position, total, onRespond }) {
  const [, setTick] = useState(0);
  const [sent, setSent] = useState(false);
  const [armed, setArmed] = useState(false);
  const armedAtRef = useRef(Infinity);
  const lastPointerDownRef = useRef(null);

  // Atraso de armamento: evita toque acidental logo que o modal aparece
  useEffect(() => {
    const id = setTimeout(() => {
      armedAtRef.current = Date.now();
      setArmed(true);
    }, ARMING_DELAY_MS);
    return () => clearTimeout(id);
  }, []);

  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, []);

  const respond = (decision) => {
    if (sent || !armed) return;
    // Ignora clique cujo toque comecou antes do armamento
    const down = lastPointerDownRef.current;
    if (down !== null && down < armedAtRef.current) return;
    setSent(true);
    hapticFeedback.medium();
    if (!onRespond(request.request_id, decision)) setSent(false);
  };

  return (
    <div className="modal-backdrop claude-perm-backdrop" role="dialog" aria-modal="true"
      onPointerDownCapture={() => { lastPointerDownRef.current = Date.now(); }}>
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
        {request.truncated && (
          <div className="claude-perm-truncated">
            (truncado — {request.summary_length} caracteres no total; confira no PC)
          </div>
        )}

        <div className="claude-perm-timer">Expira em {formatRemaining(request.deadline)}</div>

        <div className={`claude-perm-actions${armed ? '' : ' claude-perm-arming'}`}>
          <button type="button" className="claude-perm-btn claude-perm-deny" disabled={sent || !armed} onClick={() => respond('deny')}>
            Negar
          </button>
          <button type="button" className="claude-perm-btn claude-perm-allow" disabled={sent || !armed} onClick={() => respond('allow')}>
            {armed ? 'Permitir' : 'Armando…'}
          </button>
        </div>
      </div>
    </div>
  );
}
