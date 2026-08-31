import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { DeckSwiper } from './components/DeckSwiper';
import { SettingsModal } from './components/SettingsModal';
import { ConfirmModal } from './components/ConfirmModal';
import { APPS_LIST } from './config/apps';
import { 
  DEFAULT_AUTH_TOKEN, 
  getDefaultWebSocketUrl, 
  STORAGE_KEY_TOKEN, 
  STORAGE_KEY_SERVER 
} from './config/constants';
import { useWebSocket } from './hooks/useWebSocket';
import { useWakeLock } from './hooks/useWakeLock';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import './App.css';

export function App() {
  const [wsUrl, setWsUrl] = useState(() => {
    return localStorage.getItem(STORAGE_KEY_SERVER) || getDefaultWebSocketUrl();
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
    setTimeout(() => {
      setToast(null);
    }, 2800);
  };

  const handleLaunch = (appId) => {
    if (appId === 'shutdown_pc') {
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
          userSelect: 'none'
        }}
        onClick={handleBlackoutTap}
        onTouchEnd={handleBlackoutTap}
      >
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
          apps={APPS_LIST}
          onLaunch={handleLaunch}
          disabled={isDeckDisabled}
          volume={volume}
          systemStatus={systemStatus}
          onVolumeChange={changeVolume}
          onToggleMute={toggleMute}
          chunkSize={8}
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
