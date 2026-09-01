import React, { useMemo } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Pagination, EffectCreative } from 'swiper/modules';
import { DeckButton } from './DeckButton';
import { VolumeSlider } from './VolumeSlider';
import { NowPlaying } from './NowPlaying';

import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/effect-creative';

export function DeckSwiper({
  apps,
  onLaunch,
  disabled,
  volume,
  systemStatus,
  onVolumeChange,
  onToggleMute,
  chunkSize = 8
}) {
  const mainApps = useMemo(() => apps.filter(app => !['Jogos', 'Mídia'].includes(app.category)), [apps]);
  const mediaApps = useMemo(() => apps.filter(app => app.category === 'Mídia'), [apps]);
  const gamesApps = useMemo(() => apps.filter(app => app.category === 'Jogos'), [apps]);

  return (
    <div className="swiper-container-wrapper">
      <Swiper
        modules={[Pagination, EffectCreative]}
        effect="creative"
        creativeEffect={{
          prev: {
            shadow: false,
            translate: ['-20%', 0, -1],
            opacity: 0,
            scale: 0.9,
          },
          next: {
            translate: ['100%', 0, 0],
            opacity: 1,
            scale: 1,
          },
        }}
        speed={550}
        pagination={{
          clickable: true,
          bulletClass: 'custom-bullet',
          bulletActiveClass: 'custom-bullet-active',
        }}
        spaceBetween={0}
        slidesPerView={1}
        className="deck-swiper"
        touchRatio={1.1}
        resistanceRatio={0.7}
        preventClicks={false}
        preventClicksPropagation={false}
        touchStartPreventDefault={false}
      >
        {/* Slide 1: Aplicativos Principais */}
        <SwiperSlide className="deck-slide">
          <div className="grid-container">
            {mainApps.map((app) => (
              <DeckButton
                key={app.id}
                app={app}
                onLaunch={onLaunch}
                disabled={disabled}
              />
            ))}
          </div>
        </SwiperSlide>

        {/* Slide 2: Central de Controle & Mídia (com botões DeckButton idênticos) */}
        <SwiperSlide className="deck-slide">
          <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            <NowPlaying 
              title={systemStatus?.nowPlaying?.title} 
              artist={systemStatus?.nowPlaying?.artist} 
              sourceApp={systemStatus?.nowPlaying?.source_app}
              isPlaying={systemStatus?.nowPlaying?.is_playing}
              thumbnail={systemStatus?.nowPlaying?.thumbnail}
            />
            <div className="media-screen-grid">
              <div className="media-slider-slot">
                <VolumeSlider
                  volume={volume}
                  onVolumeChange={onVolumeChange}
                  onToggleMute={onToggleMute}
                  disabled={disabled}
                />
              </div>

              <div className="media-buttons-column">
                {mediaApps.map((app) => {
                  const isMicApp = app.id === 'sys_mic_mute';
                  const dynamicApp = isMicApp && systemStatus?.micMuted 
                    ? { ...app, color: '#ef4444', name: 'Mic Off' } 
                    : app;
                    
                  return (
                    <DeckButton
                      key={dynamicApp.id}
                      app={dynamicApp}
                      onLaunch={onLaunch}
                      disabled={disabled}
                    />
                  );
                })}
              </div>
            </div>
          </div>
        </SwiperSlide>

        {/* Slide 3: Jogos */}
        <SwiperSlide className="deck-slide">
          <div className="grid-container">
            {gamesApps.map((app) => (
              <DeckButton
                key={app.id}
                app={app}
                onLaunch={onLaunch}
                disabled={disabled}
              />
            ))}
          </div>
        </SwiperSlide>
      </Swiper>
    </div>
  );
}
