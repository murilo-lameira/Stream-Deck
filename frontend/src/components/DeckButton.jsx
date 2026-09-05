import React, { useState } from 'react';
import { hapticFeedback } from '../utils/haptics';

export function DeckButton({ app, onLaunch, disabled, isRunning }) {
  const [isPressed, setIsPressed] = useState(false);
  const [justLaunched, setJustLaunched] = useState(false);

  const handleClick = (e) => {
    e.preventDefault();
    if (disabled) return;

    // Feedback haptico padronizado para o Xiaomi Mi 9
    hapticFeedback.light();

    setJustLaunched(true);
    setTimeout(() => setJustLaunched(false), 500);

    onLaunch(app.id);
  };

  return (
    <button
      className={`deck-button ${isPressed ? 'pressed' : ''} ${justLaunched ? 'launched' : ''} ${disabled ? 'disabled' : ''} ${isRunning ? 'is-running' : ''}`}
      style={{
        '--app-color': app.color || '#3b82f6',
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
          {app.icon && (
            typeof app.icon === 'string' ? (
              <img 
                src={app.icon} 
                alt={`${app.name} icon`} 
                className="app-icon" 
              />
            ) : (
              <app.icon className="app-icon" size={38} />
            )
          )}
        </div>
        <span className="app-name">{app.name}</span>
        {app.category && <span className="app-category">{app.category}</span>}
      </div>
    </button>
  );
}
