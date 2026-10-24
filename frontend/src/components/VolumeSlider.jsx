import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Volume2, Volume1, Volume, VolumeX } from 'lucide-react';

const THROTTLE_WINDOW_MS = 50; // Janela fixa de 50ms (taxa de 20Hz)

export function VolumeSlider({ volume, onVolumeChange, onToggleMute, disabled }) {
  // volume = { level: 0-100, muted: boolean }
  const [localLevel, setLocalLevel] = useState(volume?.level ?? 50);
  const [isDragging, setIsDragging] = useState(false);
  const sliderRef = useRef(null);

  // Rate-Limiter Determinístico / Drop-Oldest (20Hz)
  const lastEmitTimeRef = useRef(0);
  const throttleTimerRef = useRef(null);
  const pendingLevelRef = useRef(null);
  const currentLevelRef = useRef(volume?.level ?? 50);
  const lastEmittedLevelRef = useRef(volume?.level ?? 50);
  const lastDetentRef = useRef(Math.floor((volume?.level ?? 50) / 10));

  // Sincroniza estado externo quando não estiver arrastando
  useEffect(() => {
    if (!isDragging && volume) {
      setLocalLevel(volume.level);
      currentLevelRef.current = volume.level;
      lastEmittedLevelRef.current = volume.level;
      lastDetentRef.current = Math.floor(volume.level / 10);
    }
  }, [volume, isDragging]);

  // Limpeza de timers no desmonte
  useEffect(() => {
    return () => {
      if (throttleTimerRef.current) {
        clearTimeout(throttleTimerRef.current);
      }
    };
  }, []);

  const triggerHaptic = (ms = 15) => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate(ms);
      } catch {}
    }
  };

  const calculateLevelFromY = useCallback((clientY) => {
    if (!sliderRef.current) return currentLevelRef.current;
    const rect = sliderRef.current.getBoundingClientRect();
    const height = rect.height;
    const offsetY = rect.bottom - clientY;
    const rawPercent = (offsetY / height) * 100;
    return Math.max(0, Math.min(100, Math.round(rawPercent)));
  }, []);

  const emitVolumeChange = (newLevel) => {
    // Atualização visual e tátil imediata (60-120Hz smooth UI no Xiaomi Mi 9)
    setLocalLevel(newLevel);
    currentLevelRef.current = newLevel;
    
    // Feedback háptico de catraca mecânica a cada 10%
    const currentDetent = Math.floor(newLevel / 10);
    if (currentDetent !== lastDetentRef.current) {
      lastDetentRef.current = currentDetent;
      triggerHaptic(12);
    }
    
    // Algoritmo Drop-Oldest / Rate-Limiter determinístico (20Hz / 50ms)
    const now = Date.now();
    const elapsed = now - lastEmitTimeRef.current;

    if (elapsed >= THROTTLE_WINDOW_MS) {
      // Leading Edge: decorrido >= 50ms, emite imediatamente
      if (throttleTimerRef.current) {
        clearTimeout(throttleTimerRef.current);
        throttleTimerRef.current = null;
      }
      pendingLevelRef.current = null;
      lastEmitTimeRef.current = now;
      lastEmittedLevelRef.current = newLevel;
      onVolumeChange(newLevel);
    } else {
      // Drop-Oldest: descarta amostras intermediárias e mantém apenas o valor mais recente
      pendingLevelRef.current = newLevel;

      // Agenda emissão trailing edge para o término exato da janela caso ainda não agendado
      if (!throttleTimerRef.current) {
        const remainingTime = THROTTLE_WINDOW_MS - elapsed;
        throttleTimerRef.current = setTimeout(() => {
          throttleTimerRef.current = null;
          if (pendingLevelRef.current !== null) {
            const levelToEmit = pendingLevelRef.current;
            pendingLevelRef.current = null;
            lastEmitTimeRef.current = Date.now();
            lastEmittedLevelRef.current = levelToEmit;
            onVolumeChange(levelToEmit);
          }
        }, remainingTime);
      }
    }
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

      // Limpa timer de throttle pendente
      if (throttleTimerRef.current) {
        clearTimeout(throttleTimerRef.current);
        throttleTimerRef.current = null;
      }

      // Garante que o valor final seja sempre emitido ao soltar o dedo
      const finalLevel = pendingLevelRef.current !== null ? pendingLevelRef.current : currentLevelRef.current;
      pendingLevelRef.current = null;
      lastEmitTimeRef.current = Date.now();

      if (finalLevel !== lastEmittedLevelRef.current) {
        lastEmittedLevelRef.current = finalLevel;
        onVolumeChange(finalLevel);
      }

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
    <div className={`ios-volume-container swiper-no-swiping ${disabled ? 'disabled' : ''}`}>
      <div 
        ref={sliderRef}
        className={`ios-volume-capsule swiper-no-swiping ${isDragging ? 'dragging' : ''} ${isMuted ? 'muted' : ''} ${!isMuted && localLevel > 80 ? 'high-volume' : ''}`}
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
        <div className="ios-volume-icon-wrapper" onClick={handleIconClick}>
          {renderIcon('volume-speaker-icon')}
        </div>
      </div>
      <span className="ios-volume-label">Volume</span>
    </div>
  );
}
