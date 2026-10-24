import React, { useState, useRef } from 'react';
import { hapticFeedback } from '../utils/haptics';
import { resolveIcon } from '../utils/iconRegistry';

function hexToRgb(hex) {
  if (!hex || typeof hex !== 'string') return '59, 130, 246';
  const clean = hex.replace('#', '');
  if (clean.length === 3) {
    const r = parseInt(clean[0] + clean[0], 16);
    const g = parseInt(clean[1] + clean[1], 16);
    const b = parseInt(clean[2] + clean[2], 16);
    return `${r}, ${g}, ${b}`;
  }
  if (clean.length === 6) {
    const r = parseInt(clean.substring(0, 2), 16);
    const g = parseInt(clean.substring(2, 4), 16);
    const b = parseInt(clean.substring(4, 6), 16);
    return `${r}, ${g}, ${b}`;
  }
  return '59, 130, 246';
}

export function DeckButton({ app, onLaunch, disabled, isRunning }) {
  const [isPressed, setIsPressed] = useState(false);
  const [justLaunched, setJustLaunched] = useState(false);
  const lastClickTimeRef = useRef(0);

  const handleClick = (e) => {
    e.preventDefault();
    if (disabled) return;

    const now = Date.now();
    // Cooldown de 800ms para prevenir múltiplos disparos acidentais no Mi 9
    if (now - lastClickTimeRef.current < 800) {
      return;
    }
    lastClickTimeRef.current = now;

    // Feedback háptico padronizado para o Xiaomi Mi 9
    hapticFeedback.light();

    setJustLaunched(true);
    setTimeout(() => setJustLaunched(false), 800);

    onLaunch(app.id);
  };

  const resolvedIcon = typeof app.icon === 'string' ? resolveIcon(app.icon) : app.icon;

  return (
    <button
      className={`deck-button ${isPressed ? 'pressed' : ''} ${justLaunched ? 'launched' : ''} ${disabled ? 'disabled' : ''} ${isRunning ? 'is-running' : ''}`}
      style={{
        '--app-color': app.color || '#3b82f6',
        '--app-color-rgb': hexToRgb(app.color || '#3b82f6'),
      }}
      onTouchStart={() => setIsPressed(true)}
      onTouchEnd={() => setIsPressed(false)}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      onClick={handleClick}
      disabled={disabled}
      type="button"
    >
      {/* LED Indicador de Aplicativo Ativo no Windows */}
      {isRunning && <span className="app-running-led" title="Aplicativo em execução no Windows" />}

      <div className="button-glow"></div>
      <div className="button-content">
        <div className="icon-container">
          {typeof resolvedIcon === 'string' ? (
            <img 
              src={resolvedIcon} 
              alt={`${app.name} icon`} 
              className="app-icon" 
            />
          ) : typeof resolvedIcon === 'function' ? (
            React.createElement(resolvedIcon, { className: 'app-icon', size: 38 })
          ) : null}
        </div>
        <span className="app-name">{app.name}</span>
        {app.category && <span className="app-category">{app.category}</span>}
      </div>
    </button>
  );
}
