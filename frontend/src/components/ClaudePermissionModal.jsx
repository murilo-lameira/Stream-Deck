import React, { useState, useEffect, useRef } from 'react';
import { hapticFeedback } from '../utils/haptics';

function formatRemaining(deadline) {
  const total = Math.max(Math.ceil((deadline - Date.now()) / 1000), 0);
  const m = Math.floor(total / 60);
  const s = String(total % 60).padStart(2, '0');
  return `${m}:${s}`;
}

const ARMING_DELAY_MS = 800;

function Mascot({ state }) {
  return (
    <div className={`claude-perm-mascot claude-perm-mascot-${state}`}>
      <svg viewBox="0 0 24 18" shapeRendering="crispEdges" aria-hidden="true">
        <rect x="6" y="16" width="12" height="1" fill="#1C1C1A" />
        <g className="cpm-body">
          <rect x="5" y="4" width="14" height="9" fill="#D97757" />
          <rect x="3" y="8" width="2" height="2" fill="#D97757" />
          <g className="cpm-arm">
            <rect x="19" y="3" width="2" height="5" fill="#D97757" />
            <rect x="19" y="8" width="1" height="2" fill="#D97757" />
          </g>
          <g className="cpm-eyes">
            <rect x="8" y="6" width="1" height="2" fill="#000000" />
            <rect x="15" y="6" width="1" height="2" fill="#000000" />
          </g>
          <rect x="6" y="13" width="1" height="2" fill="#D97757" />
          <rect x="8" y="13" width="1" height="2" fill="#D97757" />
          <rect x="15" y="13" width="1" height="2" fill="#D97757" />
          <rect x="17" y="13" width="1" height="2" fill="#D97757" />
        </g>
      </svg>
    </div>
  );
}

export function ClaudePermissionModal({ request, position, total, onRespond }) {
  const [, setTick] = useState(0);
  const [sent, setSent] = useState(false);
  const [decision, setDecision] = useState(null);
  const [armed, setArmed] = useState(false);
  const armedAtRef = useRef(Infinity);
  const lastPointerDownRef = useRef(null);
  const initialMsRef = useRef(Math.max(request.deadline - Date.now(), 1));

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

  const respond = (choice) => {
    if (sent || !armed) return;
    // Ignora clique cujo toque comecou antes do armamento
    const down = lastPointerDownRef.current;
    if (down !== null && down < armedAtRef.current) return;
    setSent(true);
    setDecision(choice);
    hapticFeedback.medium();
    if (!onRespond(request.request_id, choice)) {
      setSent(false);
      setDecision(null);
    }
  };

  const remainingMs = Math.max(request.deadline - Date.now(), 0);
  const pct = Math.min(100, Math.round((remainingMs / initialMsRef.current) * 100));
  const mascotState = decision === 'allow' ? 'allow' : decision === 'deny' ? 'deny' : 'idle';

  return (
    <div className="claude-perm-overlay" role="dialog" aria-modal="true"
      onPointerDownCapture={() => { lastPointerDownRef.current = Date.now(); }}>
      <div className="claude-perm-topbar">
        <div className="claude-perm-brand">
          <span className="claude-perm-live-dot" />
          Claude Code
        </div>
        <div className="claude-perm-position">{position} de {total}</div>
      </div>

      <div className="claude-perm-main">
        <div className="claude-perm-left">
          <Mascot state={mascotState} />
          {decision === null && (
            <div className="claude-perm-heading">
              <h1 className="claude-perm-title">Posso rodar isso?</h1>
              <div className="claude-perm-tags">
                <span className="claude-perm-tag claude-perm-tag-tool">{request.tool_name}</span>
                {request.project && <span className="claude-perm-tag">{request.project}</span>}
              </div>
            </div>
          )}
          {decision === 'allow' && <h1 className="claude-perm-title">Permitido</h1>}
          {decision === 'deny' && <h1 className="claude-perm-title">Negado</h1>}
        </div>

        <div className="claude-perm-right">
          {request.description && (
            <p className="claude-perm-desc">{request.description}</p>
          )}
          <div className="claude-perm-cmd">
            <pre className="claude-perm-summary">{request.summary}</pre>
          </div>
          {request.truncated && (
            <div className="claude-perm-truncated">
              (truncado — {request.summary_length} caracteres no total; confira no PC)
            </div>
          )}

          <div className="claude-perm-countdown">
            <div className="claude-perm-bar"><div className="claude-perm-bar-fill" style={{ width: `${pct}%` }} /></div>
            <div className="claude-perm-clock">
              <span>Expira em</span>
              <span className="claude-perm-clock-time">{formatRemaining(request.deadline)}</span>
            </div>
          </div>

          <div className="claude-perm-actions">
            <button type="button" className="claude-perm-btn claude-perm-deny" disabled={sent || !armed} onClick={() => respond('deny')}>
              Negar
            </button>
            <button type="button" className="claude-perm-btn claude-perm-allow" disabled={sent || !armed} onClick={() => respond('allow')}>
              {armed ? 'Permitir' : 'Armando…'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
