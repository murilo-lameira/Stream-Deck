import React, { useEffect, useRef, useState, useMemo } from 'react';
import { Music, Play, Pause, SkipForward } from 'lucide-react';
import spotifyIcon from '../assets/icons/spotify.svg';
import chromeIcon from '../assets/icons/chrome.svg';
import { hapticFeedback } from '../utils/haptics';

// Cache em memória para cores dominantes já extraídas (evita recálculo e previne flickering)
const dominantColorCache = new Map();

/**
 * Extrai a cor dominante de uma imagem (URL ou base64) usando canvas.
 * Retorna uma string RGB no formato "r, g, b".
 */
function extractDominantColor(src, callback) {
  if (!src) {
    callback(null);
    return;
  }

  if (dominantColorCache.has(src)) {
    callback(dominantColorCache.get(src));
    return;
  }

  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    try {
      const canvas = document.createElement('canvas');
      // Amostra compacta para alto desempenho no processador mobile do Mi 9
      canvas.width = 16;
      canvas.height = 16;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        callback(null);
        return;
      }
      ctx.drawImage(img, 0, 0, 16, 16);
      const data = ctx.getImageData(0, 0, 16, 16).data;

      let r = 0, g = 0, b = 0, count = 0;
      for (let i = 0; i < data.length; i += 4) {
        const alpha = data[i + 3];
        if (alpha < 128) continue; // ignora pixels transparentes
        r += data[i];
        g += data[i + 1];
        b += data[i + 2];
        count++;
      }
      if (count === 0) {
        callback(null);
        return;
      }
      const rgb = `${Math.round(r / count)}, ${Math.round(g / count)}, ${Math.round(b / count)}`;
      dominantColorCache.set(src, rgb);
      callback(rgb);
    } catch {
      // Protege contra cross-origin / canvas tainted
      callback(null);
    }
  };
  img.onerror = () => callback(null);
  img.src = src;
}

export function NowPlaying({
  title,
  artist,
  sourceApp,
  isPlaying,
  thumbnail,
  thumbnailUrl,
  thumbnail_url,
  onLaunch,
  disabled
}) {
  const [glowColor, setGlowColor] = useState(null);
  const [urlFailed, setUrlFailed] = useState(false);
  const activeUrl = thumbnailUrl || thumbnail_url;

  // Se a URL remota mudar, reseta o fallback de erro
  useEffect(() => {
    setUrlFailed(false);
  }, [activeUrl]);

  // Resolve fonte de imagem: prioriza thumbnail_url (cache HTTP), com fallback para base64
  const imageSrc = useMemo(() => {
    if (!urlFailed && activeUrl) {
      return activeUrl;
    }
    if (thumbnail) {
      if (thumbnail.startsWith('data:') || thumbnail.startsWith('http') || thumbnail.startsWith('/')) {
        return thumbnail;
      }
      return `data:image/png;base64,${thumbnail}`;
    }
    return null;
  }, [activeUrl, urlFailed, thumbnail]);

  const prevSrcRef = useRef(null);

  useEffect(() => {
    if (!imageSrc) {
      if (!title) {
        setGlowColor(null);
      }
      prevSrcRef.current = null;
      return;
    }

    if (imageSrc === prevSrcRef.current) return;
    prevSrcRef.current = imageSrc;

    // Resposta instantânea se cor já estiver em cache
    if (dominantColorCache.has(imageSrc)) {
      setGlowColor(dominantColorCache.get(imageSrc));
      return;
    }

    // Mantém o glowColor prévio até a nova cor ser calculada (elimina flickering)
    extractDominantColor(imageSrc, (color) => {
      if (color) {
        setGlowColor(color);
      }
    });
  }, [imageSrc, title]);

  const getAppIcon = () => {
    if (!sourceApp) return null;
    const lowerApp = sourceApp.toLowerCase();
    if (lowerApp.includes('spotify')) {
      return <img src={spotifyIcon} className="np-app-icon" alt="Spotify" />;
    } else if (lowerApp.includes('chrome') || lowerApp.includes('edge') || lowerApp.includes('opera') || lowerApp.includes('brave')) {
      return <img src={chromeIcon} className="np-app-icon" alt="Browser" />;
    }
    return <Music className="np-app-icon fallback" size={16} />;
  };

  const hasMedia = !!title;

  const glowStyle = glowColor && hasMedia ? {
    boxShadow: `0 0 25px 8px rgba(${glowColor}, 0.35), 0 8px 32px rgba(0,0,0,0.4)`,
    borderColor: `rgba(${glowColor}, 0.65)`,
    background: `radial-gradient(ellipse at 25% 50%, rgba(${glowColor}, 0.18) 0%, transparent 70%), rgba(18, 18, 24, 0.75)`,
    '--np-accent': `rgba(${glowColor}, 1)`,
  } : {};

  return (
    <div
      className={"now-playing-banner apple-style " + (hasMedia ? 'active' : 'idle')}
      style={glowStyle}
    >
      {/* Aura Difusa de Fundo */}
      {glowColor && hasMedia && (
        <div 
          className="np-ambient-aura"
          style={{ background: `radial-gradient(circle, rgba(${glowColor}, 0.45) 0%, transparent 70%)` }}
        />
      )}

      <div className="np-art-container">
        {imageSrc ? (
          <>
            <img 
              src={imageSrc} 
              className="np-thumbnail" 
              alt="Art" 
              onError={() => {
                if (!urlFailed && activeUrl) {
                  setUrlFailed(true);
                }
              }}
            />
            <div className="np-app-badge">
              {getAppIcon()}
            </div>
          </>
        ) : hasMedia ? (
          getAppIcon()
        ) : (
          <Music className="np-app-icon fallback" size={20} />
        )}
      </div>
      
      <div className="np-info">
        {hasMedia ? (
          <>
            <span className="np-title">{title}</span>
            {artist && <span className="np-artist">{artist}</span>}
          </>
        ) : (
          <span className="np-title idle-text">Nenhuma mídia reproduzindo</span>
        )}
      </div>

      {/* Controles Rápidos Inline */}
      {hasMedia && onLaunch && (
        <div className="np-inline-controls">
          <button 
            type="button"
            className="np-mini-btn"
            disabled={disabled}
            onClick={(e) => {
              e.stopPropagation();
              hapticFeedback.light();
              onLaunch('sys_media_playpause');
            }}
            title={isPlaying ? "Pausar" : "Reproduzir"}
            aria-label="Play/Pause"
          >
            {isPlaying ? <Pause size={17} /> : <Play size={17} />}
          </button>
          <button 
            type="button"
            className="np-mini-btn"
            disabled={disabled}
            onClick={(e) => {
              e.stopPropagation();
              hapticFeedback.light();
              onLaunch('sys_media_next');
            }}
            title="Próxima Faixa"
            aria-label="Próxima Faixa"
          >
            <SkipForward size={17} />
          </button>
        </div>
      )}

      {/* Equalizador Animado */}
      <div className={"np-eq-container " + (hasMedia && isPlaying ? 'playing' : '')}>
        <div className="eq-bar"></div>
        <div className="eq-bar"></div>
        <div className="eq-bar"></div>
        <div className="eq-bar"></div>
      </div>

      {/* Linha de Progresso com Pulso Glow */}
      {hasMedia && isPlaying && (
        <div className="np-progress-glow-line" />
      )}
    </div>
  );
}
