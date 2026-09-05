import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { DeckSwiper } from './components/DeckSwiper';
import { SettingsModal } from './components/SettingsModal';
import { ConfirmModal } from './components/ConfirmModal';
import { 
  DEFAULT_AUTH_TOKEN, 
  getDefaultWebSocketUrl, 
  STORAGE_KEY_TOKEN, 
  STORAGE_KEY_SERVER 
} from './config/constants';
import { useWebSocket } from './hooks/useWebSocket';
import { useWakeLock } from './hooks/useWakeLock';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { hapticFeedback } from './utils/haptics';
import './App.css';

export function App() {
  const [wsUrl, setWsUrl] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY_SERVER);
    const defaultUrl = getDefaultWebSocketUrl();

    // Se o usuário abriu a página diretamente pelo IP do PC (ex: http://192.168.15.16:8000),
    // sincroniza automaticamente o WebSocket com esse IP para evitar tentar conectar no IP antigo.
    if (typeof window !== 'undefined' && window.location.hostname && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      const currentOriginWs = `ws://${window.location.hostname}:${window.location.port || '8000'}/ws`;
      if (!saved || saved.includes('localhost') || saved.includes('127.0.0.1') || saved !== currentOriginWs) {
        localStorage.setItem(STORAGE_KEY_SERVER, currentOriginWs);
        return currentOriginWs;
      }
    }

    return saved || defaultUrl;
  });

  const [authToken, setAuthToken] = useState(() => {
    return localStorage.getItem(STORAGE_KEY_TOKEN) || DEFAULT_AUTH_TOKEN;
  });

  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [pendingShutdown, setPendingShutdown] = useState(false);
  const [toast, setToast] = useState(null);

  const [isDarkMode, setIsDarkMode] = useState(() => {
    return localStorage.getItem('THEME') === 'dark';
  });

  const { 
    status, 
    lastMessage, 
    errorMessage, 
    sendAction, 
    volume, 
    systemStatus,
    runningApps,
    changeVolume, 
    toggleMute, 
    reconnect 
  } = useWebSocket(
    wsUrl,
    authToken
  );

  // Monitora feedback de mensagens do servidor
  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.type === 'action_result') {
      if (lastMessage.status === 'success') {
        showToast(lastMessage.message, 'success');
      } else {
        showToast(lastMessage.message || 'Erro ao executar ação.', 'error');
      }
    } else if (lastMessage.type === 'auth_success') {
      showToast('Conectado e Autenticado!', 'success');
    }
  }, [lastMessage]);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    if (type === 'success') {
      hapticFeedback.success();
    } else if (type === 'error') {
      hapticFeedback.warning();
    }
    setTimeout(() => {
      setToast(null);
    }, 2800);
  };

  const handleLaunch = (appId) => {
    if (appId === 'shutdown_pc') {
      hapticFeedback.warning();
      setPendingShutdown(true);
      return;
    }
    executeLaunch(appId);
  };

  const executeLaunch = (appId) => {
    const result = sendAction(appId);
    if (!result.success) {
      showToast(result.reason || 'Falha ao enviar comando', 'error');
    }
  };

  const confirmShutdown = () => {
    hapticFeedback.warning();
    setPendingShutdown(false);
    executeLaunch('shutdown_pc');
  };

  const handleSaveSettings = ({ url, token }) => {
    setWsUrl(url);
    setAuthToken(token);
    localStorage.setItem(STORAGE_KEY_SERVER, url);
    localStorage.setItem(STORAGE_KEY_TOKEN, token);
    showToast('Configurações salvas. Reconectando...', 'info');
  };

  const toggleTheme = () => {
    setIsDarkMode(prev => {
      const newTheme = !prev;
      localStorage.setItem('THEME', newTheme ? 'dark' : 'light');
      return newTheme;
    });
  };

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('theme-dark');
      document.body.classList.add('theme-dark');
    } else {
      document.documentElement.classList.remove('theme-dark');
      document.body.classList.remove('theme-dark');
    }
  }, [isDarkMode]);

  // Mantem a tela sempre ligada
  useWakeLock();

  const isDeckDisabled = status !== 'AUTHENTICATED';

  // Modo Standby OLED (Blackout) quando o computador esta desligado/recarregando
  const isBlackout = status === 'RECONNECTING';

  // Sensor de toque no celular para abrir configuracoes durante o Blackout
  const lastTapRef = useRef(0);
  const handleBlackoutTap = () => {
    const now = Date.now();
    if (now - lastTapRef.current < 450) {
      setIsSettingsOpen(true);
    }
    lastTapRef.current = now;
  };

  // Se o computador estiver desligado (RECONNECTING), mantem a tela 100% preta (OLED Blackout) sem piscar
  // Se o computador estiver desligado (RECONNECTING), mantem a tela 100% preta (OLED Blackout) com dica sutil
  if (isBlackout) {
    return (
      <div 
        style={{ 
          width: '100vw', 
          height: '100vh', 
          backgroundColor: '#000000',
          position: 'fixed',
          inset: 0,
          zIndex: 9999,
          cursor: 'pointer',
          userSelect: 'none',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'flex-end',
          paddingBottom: '24px'
        }}
        onClick={handleBlackoutTap}
        onTouchEnd={handleBlackoutTap}
      >
        <div style={{ color: 'rgba(255, 255, 255, 0.22)', fontSize: '0.75rem', textAlign: 'center', pointerEvents: 'none' }}>
          Conectando a {wsUrl}<br />
          <span style={{ fontSize: '0.65rem', opacity: 0.8 }}>Toque 2x na tela para alterar IP</span>
        </div>

        <SettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          currentUrl={wsUrl}
          currentAuthToken={authToken}
          onSave={handleSaveSettings}
        />
      </div>
    );
  }

  return (
    <div className={`app-container ${isDarkMode ? 'theme-dark' : ''}`}>
      <Header 
        status={status} 
        onOpenSettings={() => setIsSettingsOpen(true)} 
        isDarkMode={isDarkMode}
        onToggleTheme={toggleTheme}
      />

      <main className="app-main">
        {errorMessage && status === 'ERROR' && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{errorMessage}</span>
          </div>
        )}

        <DeckSwiper
          onLaunch={handleLaunch}
          disabled={isDeckDisabled}
          volume={volume}
          systemStatus={systemStatus}
          runningApps={runningApps}
          onVolumeChange={changeVolume}
          onToggleMute={toggleMute}
        />
      </main>

      {/* Toast flutuante de feedback */}
      {toast && (
        <div className={`toast-notification toast-${toast.type}`}>
          {toast.type === 'success' ? (
            <CheckCircle2 size={16} />
          ) : (
            <AlertCircle size={16} />
          )}
          <span>{toast.message}</span>
        </div>
      )}

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentUrl={wsUrl}
        currentAuthToken={authToken}
        onSave={handleSaveSettings}
      />

      <ConfirmModal
        isOpen={pendingShutdown}
        title="Desligar o PC?"
        message="Seu computador será desligado imediatamente. Certifique-se de ter salvo o seu trabalho!"
        onConfirm={confirmShutdown}
        onCancel={() => setPendingShutdown(false)}
      />
    </div>
  );
}

export default App;
