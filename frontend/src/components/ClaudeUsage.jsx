import React, { useState, useEffect } from 'react';

const CIRC = 326.73;
const STALE_MS = 15 * 60 * 1000;

function ringColor(p) {
  if (p >= 90) return '#F2555A';
  if (p >= 70) return '#E8A33D';
  return '#D97757';
}

function formatReset(resetsAt, now) {
  if (typeof resetsAt !== 'number') return '—';
  const diffMs = resetsAt * 1000 - now;
  if (diffMs <= 0) return 'agora';
  if (diffMs < 24 * 3600 * 1000) {
    const totalMin = Math.max(1, Math.round(diffMs / 60000));
    const h = Math.floor(totalMin / 60);
    const m = totalMin % 60;
    if (h === 0) return `em ${m} min`;
    return `em ${h} h ${m} min`;
  }
  const d = new Date(resetsAt * 1000);
  const dia = d.toLocaleDateString('pt-BR', { weekday: 'short' });
  const hora = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', hour12: false });
  return `${dia}, ${hora}`;
}

function formatUpdated(updatedAt, now) {
  if (typeof updatedAt !== 'number') return null;
  const min = Math.floor((now - updatedAt * 1000) / 60000);
  if (min < 1) return 'agora há pouco';
  return `Atualizado há ${min} min`;
}

function Gauge({ title, windowLabel, pct, footer }) {
  const has = typeof pct === 'number' && Number.isFinite(pct);
  const p = has ? Math.max(0, Math.min(100, Math.round(pct))) : 0;
  const color = ringColor(p);
  const offset = CIRC * (1 - p / 100);
  return (
    <div className="usage-card">
      <div className="usage-card-head">
        <span className="usage-card-title">{title}</span>
        <span className="usage-card-window">{windowLabel}</span>
      </div>
      <div className="usage-ring">
        <svg viewBox="0 0 120 120" aria-hidden="true">
          <circle cx="60" cy="60" r="52" fill="none" stroke="#1C1C1A" strokeWidth="10" />
          {has && (
            <circle
              className="usage-ring-fill"
              cx="60" cy="60" r="52" fill="none"
              stroke={color} strokeWidth="10" strokeLinecap="round"
              strokeDasharray={CIRC}
              style={{ strokeDashoffset: offset }}
              transform="rotate(-90 60 60)"
            />
          )}
        </svg>
        <div className="usage-ring-label">
          <span className="usage-ring-pct" style={{ color: has ? color : '#A3A29C' }}>
            {has ? `${p}%` : '—'}
          </span>
          {has && <span className="usage-ring-sub">usado</span>}
        </div>
      </div>
      <div className="usage-card-foot">
        <span>{footer.label}</span>
        <span className="usage-card-foot-val">{footer.value}</span>
      </div>
    </div>
  );
}

export function ClaudeUsage({ claudeUsage }) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 30000);
    return () => clearInterval(id);
  }, []);

  const u = claudeUsage || null;
  const updatedText = u ? formatUpdated(u.updated_at, now) : null;
  const stale = u && typeof u.updated_at === 'number' && now - u.updated_at * 1000 > STALE_MS;
  const noData = !u || (!u.five_hour && !u.seven_day && typeof u.context_pct !== 'number');

  return (
    <div className="usage-page">
      <div className="usage-top">
        <div className="usage-brand">
          <svg className="usage-mascot" viewBox="0 0 24 18" shapeRendering="crispEdges" aria-hidden="true">
            <g className="usage-mascot-body">
              <rect x="5" y="4" width="14" height="9" fill="#D97757" />
              <rect x="3" y="8" width="2" height="2" fill="#D97757" />
              <rect x="19" y="8" width="2" height="2" fill="#D97757" />
              <g className="usage-mascot-eyes">
                <rect x="8" y="6" width="1" height="2" fill="#000000" />
                <rect x="15" y="6" width="1" height="2" fill="#000000" />
              </g>
              <rect x="6" y="13" width="1" height="2" fill="#D97757" />
              <rect x="8" y="13" width="1" height="2" fill="#D97757" />
              <rect x="15" y="13" width="1" height="2" fill="#D97757" />
              <rect x="17" y="13" width="1" height="2" fill="#D97757" />
            </g>
          </svg>
          <div className="usage-brand-text">
            <span className="usage-brand-kicker">Claude Code</span>
            <span className="usage-brand-title">Limites da conta</span>
          </div>
        </div>
        {updatedText && (
          <div className="usage-updated" style={stale ? { color: '#E8A33D' } : undefined}>
            <span className="usage-dot" />
            {updatedText}
          </div>
        )}
      </div>

      <div className="usage-grid">
        <Gauge
          title="Sessão atual"
          windowLabel="janela de 5 h"
          pct={u?.five_hour?.used_percentage}
          footer={{ label: 'Renova', value: formatReset(u?.five_hour?.resets_at, now) }}
        />
        <Gauge
          title="Semana"
          windowLabel="todos os modelos"
          pct={u?.seven_day?.used_percentage}
          footer={{ label: 'Renova', value: formatReset(u?.seven_day?.resets_at, now) }}
        />
        <Gauge
          title="Contexto"
          windowLabel="sessão atual"
          pct={u?.context_pct}
          footer={{ label: 'Modelo', value: u?.model || '—' }}
        />
      </div>

      {noData && (
        <div className="usage-empty">Abra uma sessão do Claude Code no PC para ver os limites</div>
      )}
    </div>
  );
}
