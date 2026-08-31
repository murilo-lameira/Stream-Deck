import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Volume2, Volume1, Volume, VolumeX } from 'lucide-react';

export function VolumeSlider({ volume, onVolumeChange, onToggleMute, disabled }) {
  // volume = { level: 0-100, muted: boolean }
  const [localLevel, setLocalLevel] = useState(volume?.level ?? 50);
  const [isDragging, setIsDragging] = useState(false);
  const sliderRef = useRef(null);
  const throttleTimeoutRef = useRef(null);

  // Sincroniza estado externo quando não estiver arrastando
  useEffect(() => {
    if (!isDragging && volume) {
      setLocalLevel(volume.level);
    }
  }, [volume, isDragging]);

  const triggerHaptic = (ms = 15) => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate(ms);
      } catch (e) {}
    }
  };

  const calculateLevelFromY = useCallback((clientY) => {
    if (!sliderRef.current) return localLevel;
    const rect = sliderRef.current.getBoundingClientRect();
    const height = rect.height;
    const offsetY = rect.bottom - clientY;
    const rawPercent = (offsetY / height) * 100;
    return Math.max(0, Math.min(100, Math.round(rawPercent)));
  }, [localLevel]);

  const emitVolumeChange = (newLevel) => {
    setLocalLevel(newLevel);
    
    // Throttling para não saturar o WebSocket durante o deslize suave
    if (throttleTimeoutRef.current) {
      clearTimeout(throttleTimeoutRef.current);
    }
    
    throttleTimeoutRef.current = setTimeout(() => {
      onVolumeChange(newLevel);
    }, 40);
  };

  const handlePointerDown = (e) => {
    if (disabled) return;
    e.preventDefault();
    setIsDragging(true);
    triggerHaptic(20);

    const newLevel = calculateLevelFromY(e.clientY || e.touches?.[0]?.clientY);
    emitVolumeChange(newLevel);

    const handlePointerMove = (moveEvent) => {
      const clientY = moveEvent.clientY || moveEvent.touches?.[0]?.clientY;
      if (clientY !== undefined) {
        const lvl = calculateLevelFromY(clientY);
        emitVolumeChange(lvl);
      }
    };

    const handlePointerUp = () => {
      setIsDragging(false);
      triggerHaptic(15);
      window.removeEventListener('mousemove', handlePointerMove);
      window.removeEventListener('mouseup', handlePointerUp);
      window.removeEventListener('touchmove', handlePointerMove);
      window.removeEventListener('touchend', handlePointerUp);
      window.removeEventListener('touchcancel', handlePointerUp);
    };

    window.addEventListener('mousemove', handlePointerMove, { passive: false });
    window.addEventListener('mouseup', handlePointerUp);
    window.addEventListener('touchmove', handlePointerMove, { passive: false });
    window.addEventListener('touchend', handlePointerUp);
    window.addEventListener('touchcancel', handlePointerUp);
  };

  const handleIconClick = (e) => {
    e.stopPropagation();
    if (disabled) return;
    triggerHaptic(30);
    onToggleMute();
  };

  const isMuted = volume?.muted || localLevel === 0;
  const displayLevel = isMuted ? 0 : localLevel;

  // Seleciona o ícone dinâmico do alto-falante
  const renderIcon = (colorClass) => {
    const size = 22;
    if (isMuted) return <VolumeX size={size} className={colorClass} />;
    if (localLevel < 33) return <Volume size={size} className={colorClass} />;
    if (localLevel < 67) return <Volume1 size={size} className={colorClass} />;
    return <Volume2 size={size} className={colorClass} />;
  };

  return (
    <div className={`ios-volume-container ${disabled ? 'disabled' : ''}`}>
      <div 
        ref={sliderRef}
        className={`ios-volume-capsule ${isDragging ? 'dragging' : ''} ${isMuted ? 'muted' : ''}`}
        onMouseDown={handlePointerDown}
        onTouchStart={handlePointerDown}
      >
        {/* Barra de preenchimento que sobe do fundo */}
        <div 
          className="ios-volume-fill" 
          style={{ height: `${displayLevel}%` }}
        />

        {/* Indicador numérico no topo */}
        <div className="ios-volume-value">
          {isMuted ? 'MUDO' : `${localLevel}%`}
        </div>

        {/* Ícone no rodapé da cápsula */}
        <div className="ios-volume-icon-wrapper">
          {renderIcon('volume-speaker-icon')}
        </div>
      </div>
      <span className="ios-volume-label">Volume</span>
    </div>
  );
}

