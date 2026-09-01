import React from 'react';
import { Music } from 'lucide-react';
import spotifyIcon from '../assets/icons/spotify.svg';
import chromeIcon from '../assets/icons/chrome.svg';

export function NowPlaying({ title, artist, sourceApp, isPlaying }) {
  // Define qual ícone usar com base no source_app do Windows
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

  return (
    <div className={"now-playing-banner apple-style " + (hasMedia ? 'active' : 'idle')}>
      <div className="np-art-container">
        {hasMedia ? (
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

