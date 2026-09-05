/**
 * Utilitario para Haptic Feedback nativo via Vibration API.
 * Otimizado especialmente para a resposta tatil do Xiaomi Mi 9.
 */
export const hapticFeedback = {
  light: () => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate(25);
      } catch (_e) {}
    }
  },

  medium: () => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate(45);
      } catch (_e) {}
    }
  },

  success: () => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate([30, 40, 30]);
      } catch (_e) {}
    }
  },

  warning: () => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate([50, 60, 50]);
      } catch (_e) {}
    }
  },

  selection: () => {
    if (typeof window !== 'undefined' && window.navigator && window.navigator.vibrate) {
      try {
        window.navigator.vibrate(12);
      } catch (_e) {}
    }
  }
};
