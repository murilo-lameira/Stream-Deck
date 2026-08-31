import { useEffect, useRef } from 'react';
import NoSleep from 'nosleep.js';

export function useWakeLock() {
  const noSleepRef = useRef(null);

  useEffect(() => {
    noSleepRef.current = new NoSleep();

    const enableNoSleep = () => {
      if (noSleepRef.current && !noSleepRef.current.isEnabled) {
        noSleepRef.current.enable()
          .then(() => {
            console.log("NoSleep ativado via NoSleep.js (Fallback para HTTP)");
          })
          .catch((err) => {
            console.warn("Falha ao ativar NoSleep:", err);
          });
          
        // Remove os eventos após a primeira interação bem sucedida
        document.removeEventListener('click', enableNoSleep, false);
        document.removeEventListener('touchstart', enableNoSleep, false);
      }
    };

    // A biblioteca exige que a ativação ocorra durante uma interação do usuário (clique/toque)
    document.addEventListener('click', enableNoSleep, false);
    document.addEventListener('touchstart', enableNoSleep, false);

    return () => {
      document.removeEventListener('click', enableNoSleep, false);
      document.removeEventListener('touchstart', enableNoSleep, false);
      if (noSleepRef.current && noSleepRef.current.isEnabled) {
        noSleepRef.current.disable();
      }
    };
  }, []);
}
