import React, { useEffect, useRef, useState } from 'react';
import { Music } from 'lucide-react';
import spotifyIcon from '../assets/icons/spotify.svg';
import chromeIcon from '../assets/icons/chrome.svg';

/**
 * Extrai a cor dominante de uma imagem base64 usando canvas.
 * Retorna uma string RGB no formato "r, g, b".
 */
function extractDominantColor(base64, callback) {
  const img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = () => {
    const canvas = document.createElement('canvas');
    // Amostra pequena para performance
    canvas.width = 16;
    canvas.height = 16;
    const ctx = canvas.getContext('2d');
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
    if (count === 0) { callback(null); return; }
    callback(`${Math.round(r / count)}, ${Math.round(g / count)}, ${Math.round(b / count)}`);
  };
  img.onerror = () => callback(null);
  img.src = `data:image/png;base64,${base64}`;
}

export function NowPlaying({ title, artist, sourceApp, isPlaying, thumbnail }) {
  const [glowColor, setGlowColor] = useState(null);
  const prevThumbnail = useRef(null);

  useEffect(() => {
    if (!thumbnail) { setGlowColor(null); return; }
    if (thumbnail === prevThumbnail.current) return;
    prevThumbnail.current = thumbnail;

    extractDominantColor(thumbnail, (color) => {
      setGlowColor(color);
    });
  }, [thumbnail]);

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
    boxShadow: `0 0 20px 6px rgba(${glowColor}, 0.45), 0 8px 32px rgba(0,0,0,0.08)`,
    borderColor: `rgba(${glowColor}, 0.6)`,
    background: `radial-gradient(ellipse at 30% 50%, rgba(${glowColor}, 0.12) 0%, transparent 65%), rgba(255, 255, 255, 0.4)`,
    '--np-accent': `rgba(${glowColor}, 1)`,
  } : {};

  return (
    <div
      className={"now-playing-banner apple-style " + (hasMedia ? 'active' : 'idle')}
      style={glowStyle}
    >
      <div className="np-art-container">
        {thumbnail ? (
          <>
            <img src={`data:image/png;base64,${thumbnail}`} className="np-thumbnail" alt="Art" />
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
          <span className="np-title idle-text">Nenhuma mídia...</span>
        )}
      </div>

      <div className={"np-eq-container " + (hasMedia && isPlaying ? 'playing' : '')}>
        <div className="eq-bar"></div>
        <div className="eq-bar"></div>
        <div className="eq-bar"></div>
        <div className="eq-bar"></div>
      </div>
    </div>
  );
}
