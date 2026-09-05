import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket(url, authToken) {
  const [status, setStatus] = useState('CONNECTING'); // 'CONNECTING' | 'CONNECTED' | 'AUTHENTICATED' | 'RECONNECTING' | 'ERROR'
  const [lastMessage, setLastMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  
  const [volume, setVolumeState] = useState({ level: 50, muted: false });
  const [systemStatus, setSystemStatus] = useState({ nowPlaying: null, micMuted: false });
  const [runningApps, setRunningApps] = useState([]);
  
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const heartbeatTimerRef = useRef(null);
  const lastActivityRef = useRef(0);
  const isUnmountedRef = useRef(false);

  const clearReconnectTimer = () => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const clearHeartbeatTimer = () => {
    if (heartbeatTimerRef.current) {
      clearInterval(heartbeatTimerRef.current);
      heartbeatTimerRef.current = null;
    }
  };

  const scheduleReconnect = useCallback(() => {
    clearReconnectTimer();
    clearHeartbeatTimer();
    if (isUnmountedRef.current) return;
    
    setStatus('RECONNECTING');
    reconnectTimerRef.current = setTimeout(() => {
      if (!isUnmountedRef.current) {
        connect(true);
      }
    }, 2500); // Tentar reconectar a cada 2.5 segundos
  }, [url, authToken]);

  const connect = useCallback((isRetry = false) => {
    clearReconnectTimer();
    clearHeartbeatTimer();
    
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      try {
        wsRef.current.close();
      } catch (_e) {}
      wsRef.current = null;
    }

    if (!url) return;

    if (!isRetry) {
      setStatus('CONNECTING');
    }
    setErrorMessage('');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isUnmountedRef.current) return;
        setStatus('CONNECTED');
        lastActivityRef.current = Date.now();
        // Handshake imediato com o token de seguranca
        ws.send(JSON.stringify({ auth_token: authToken }));

        // Inicia Heartbeat (Ping a cada 15s e detector de conexao zumbi)
        clearHeartbeatTimer();
        heartbeatTimerRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            try {
              ws.send(JSON.stringify({ action: 'ping' }));
            } catch (err) {
              console.warn('Falha ao enviar heartbeat ping:', err);
            }

            // Se faz mais de 25 segundos que o servidor nao responde nada, socket esta zumbi
            if (Date.now() - lastActivityRef.current > 25000) {
              console.warn('Conexao WebSocket inativa detectada (sem resposta do servidor). Forcando reconexao.');
              try { ws.close(); } catch (_e) {}
            }
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        if (isUnmountedRef.current) return;
        lastActivityRef.current = Date.now();

        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          if (data.type === 'auth_success') {
            setStatus('AUTHENTICATED');
            if (data.volume) {
              setVolumeState(data.volume);
            }
            if (data.running_apps) {
              setRunningApps(data.running_apps);
            }
          } else if (data.type === 'volume_state') {
            setVolumeState({ level: data.level, muted: data.muted });
          } else if (data.type === 'system_status') {
            setSystemStatus({
              nowPlaying: data.now_playing,
              micMuted: data.mic_muted
            });
            if (data.running_apps) {
              setRunningApps(data.running_apps);
            }
          } else if (data.type === 'running_apps_update') {
            if (data.running_apps) {
              setRunningApps(data.running_apps);
            }
          }
        } catch (e) {
          console.error('Erro ao processar mensagem do WebSocket:', e);
        }
      };

      ws.onerror = (event) => {
        if (isUnmountedRef.current) return;
        console.warn('Erro na conexao WebSocket:', event);
      };

      ws.onclose = (event) => {
        if (isUnmountedRef.current) return;
        clearHeartbeatTimer();
        
        if (event.code === 1008) {
          setStatus('ERROR');
          setErrorMessage('Token de autenticacao invalido ou rejeitado pelo servidor (Codigo 1008).');
          reconnectTimerRef.current = setTimeout(() => {
            if (!isUnmountedRef.current) scheduleReconnect();
          }, 5000);
        } else {
          setErrorMessage('Conexao perdida com o computador.');
          scheduleReconnect();
        }
      };
    } catch (err) {
      console.error('Falha ao instanciar WebSocket:', err);
      scheduleReconnect();
    }
  }, [url, authToken, scheduleReconnect]);

  useEffect(() => {
    isUnmountedRef.current = false;
    connect();

    // Listener para o Xiaomi Mi 9: quando a tela acende ou a aba volta a ser visivel
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          console.info('Dispositivo voltou a ficar ativo. Restabelecendo WebSocket...');
          connect();
        }
      }
    };

    const handleOnline = () => {
      console.info('Rede online detectada. Reconectando...');
      connect();
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnline);

    return () => {
      isUnmountedRef.current = true;
      clearReconnectTimer();
      clearHeartbeatTimer();
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendAction = useCallback((appName) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return { success: false, reason: 'Nao conectado ao servidor.' };
    }
    
    if (status !== 'AUTHENTICATED') {
      return { success: false, reason: 'Nao autenticado.' };
    }

    try {
      wsRef.current.send(JSON.stringify({
        action: 'open',
        app: appName
      }));
      return { success: true };
    } catch (err) {
      console.error('Erro ao enviar acao:', err);
      return { success: false, reason: err.message };
    }
  }, [status]);

  const changeVolume = useCallback((newLevel) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    try {
      wsRef.current.send(JSON.stringify({
        action: 'set_volume',
        level: Math.round(newLevel)
      }));
    } catch (err) {
      console.error('Erro ao enviar alteracao de volume:', err);
    }
  }, []);

  const toggleMute = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    try {
      wsRef.current.send(JSON.stringify({
        action: 'toggle_mute'
      }));
    } catch (err) {
      console.error('Erro ao alternar mute:', err);
    }
  }, []);

  return {
    status,
    lastMessage,
    errorMessage,
    sendAction,
    volume,
    systemStatus,
    runningApps,
    changeVolume,
    toggleMute,
    reconnect: connect
  };
}
