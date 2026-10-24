import { useEffect, useRef } from 'react';
import NoSleep from 'nosleep.js';

/**
 * Hook para manter a tela do celular acesa durante o uso como Stream Deck.
 * Prioriza a Screen Wake Lock API nativa do W3C (ótima para economia de bateria no Xiaomi Mi 9 OLED)
 * e faz fallback transparente para NoSleep.js em contextos HTTP não-seguros.
 */
export function useWakeLock() {
  const wakeLockRef = useRef(null);
  const noSleepRef = useRef(null);

  useEffect(() => {
    let isMounted = true;

    if (!noSleepRef.current) {
      noSleepRef.current = new NoSleep();
    }

    const enableFallback = () => {
      if (!isMounted) return;
      if (noSleepRef.current && !noSleepRef.current.isEnabled) {
        noSleepRef.current.enable()
          .then(() => console.log('[WakeLock] NoSleep.js fallback ativado com sucesso.'))
          .catch((err) => console.warn('[WakeLock] Erro ao ativar NoSleep fallback:', err));

        document.removeEventListener('click', enableFallback, false);
        document.removeEventListener('touchstart', enableFallback, false);
      }
    };

    const requestWakeLock = async () => {
      // 1. Tenta a API padrão moderna do navegador
      if (typeof navigator !== 'undefined' && 'wakeLock' in navigator) {
        try {
          wakeLockRef.current = await navigator.wakeLock.request('screen');
          console.log('[WakeLock] Screen Wake Lock nativo ativado com sucesso.');

          wakeLockRef.current.addEventListener('release', () => {
            console.log('[WakeLock] Screen Wake Lock nativo foi liberado.');
          });
          return;
        } catch (err) {
          console.warn('[WakeLock] Falha ao solicitar WakeLock nativo, ativando fallback NoSleep:', err);
        }
      }

      // 2. Fallback para NoSleep.js (exige interação de clique/toque no DOM)
      document.addEventListener('click', enableFallback, false);
      document.addEventListener('touchstart', enableFallback, false);
    };

    requestWakeLock();

    // Reativa o WakeLock se a aba voltar a ficar visível
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !wakeLockRef.current) {
        requestWakeLock();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      isMounted = false;
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('click', enableFallback, false);
      document.removeEventListener('touchstart', enableFallback, false);

      if (wakeLockRef.current) {
        wakeLockRef.current.release().catch(() => {});
        wakeLockRef.current = null;
      }

      if (noSleepRef.current && noSleepRef.current.isEnabled) {
        noSleepRef.current.disable();
      }
    };
  }, []);
}
