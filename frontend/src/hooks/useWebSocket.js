import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebSocket(url, authToken) {
  const [status, setStatus] = useState('CONNECTING'); // 'CONNECTING' | 'CONNECTED' | 'AUTHENTICATED' | 'RECONNECTING' | 'ERROR'
  const [lastMessage, setLastMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  
  const [volume, setVolumeState] = useState({ level: 50, muted: false });
  const [systemStatus, setSystemStatus] = useState({ nowPlaying: null, micMuted: false });
  
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const isUnmountedRef = useRef(false);

  const clearReconnectTimer = () => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
  };

  const scheduleReconnect = useCallback(() => {
    clearReconnectTimer();
    if (isUnmountedRef.current) return;
    
    setStatus('RECONNECTING');
    reconnectTimerRef.current = setTimeout(() => {
      if (!isUnmountedRef.current) {
        connect();
      }
    }, 3000); // Tentar reconectar a cada 3 segundos
  }, [url, authToken]);

  const connect = useCallback(() => {
    clearReconnectTimer();
    
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      try {
        wsRef.current.close();
      } catch (e) {
        // ignore
      }
      wsRef.current = null;
    }

    if (!url) return;

    setStatus('CONNECTING');
    setErrorMessage('');

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isUnmountedRef.current) return;
        setStatus('CONNECTED');
        // Handshake imediato com o token de seguranca
        ws.send(JSON.stringify({ auth_token: authToken }));
      };

      ws.onmessage = (event) => {
        if (isUnmountedRef.current) return;
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);

          if (data.type === 'auth_success') {
            setStatus('AUTHENTICATED');
            if (data.volume) {
              setVolumeState(data.volume);
            }
          } else if (data.type === 'volume_state') {
            setVolumeState({ level: data.level, muted: data.muted });
          } else if (data.type === 'system_status') {
            setSystemStatus({
              nowPlaying: data.now_playing,
              micMuted: data.mic_muted
            });
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

    return () => {
      isUnmountedRef.current = true;
      clearReconnectTimer();
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
    changeVolume,
    toggleMute,
    reconnect: connect
  };
}
