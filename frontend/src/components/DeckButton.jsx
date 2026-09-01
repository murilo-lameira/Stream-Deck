import React, { useState } from 'react';

export function DeckButton({ app, onLaunch, disabled }) {
  const [isPressed, setIsPressed] = useState(false);
  const [justLaunched, setJustLaunched] = useState(false);

  const handleClick = (e) => {
    e.preventDefault();
    if (disabled) return;

    // Feedback haptico para mobile (vibracao curta no Xiaomi Mi 9)
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate(35);
      } catch (err) {
        // Ignora navegadores que bloqueiem vibracao sem interacao previa
      }
    }

    setJustLaunched(true);
    setTimeout(() => setJustLaunched(false), 500);

    onLaunch(app.id);
  };

  return (
    <button
      className={`deck-button ${isPressed ? 'pressed' : ''} ${justLaunched ? 'launched' : ''} ${disabled ? 'disabled' : ''}`}
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
