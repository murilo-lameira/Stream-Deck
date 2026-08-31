import React from 'react';
import { Music } from 'lucide-react';

export function NowPlaying({ title, artist }) {
  return (
    <div className="now-playing-banner">
      <Music className="now-playing-icon" size={16} />
      <div className="now-playing-text-container">
        <div className="now-playing-text">
          {title ? (
            <>
              <span className="np-title">{title}</span>
              {artist && <span className="np-artist"> • {artist}</span>}
            </>
          ) : (
            <span className="np-title" style={{ opacity: 0.7 }}>Nenhuma mídia...</span>
          )}
        </div>
      </div>
    </div>
  );
}

