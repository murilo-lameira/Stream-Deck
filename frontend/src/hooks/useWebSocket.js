import { useState, useEffect, useRef, useCallback } from 'react';
import { hapticFeedback } from '../utils/haptics';

export function useWebSocket(url, authToken) {
  const [status, setStatus] = useState('CONNECTING'); // 'CONNECTING' | 'CONNECTED' | 'AUTHENTICATED' | 'RECONNECTING' | 'ERROR'
  const [lastMessage, setLastMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  
  const [volume, setVolumeState] = useState({ level: 50, muted: false });
  const [systemStatus, setSystemStatus] = useState({ nowPlaying: null, micMuted: false, metrics: null });
  const [runningApps, setRunningApps] = useState([]);
  const [catalog, setCatalog] = useState(null);
  const [permissionQueue, setPermissionQueue] = useState([]);
  
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const heartbeatTimerRef = useRef(null);
  const lastActivityRef = useRef(0);
  const isUnmountedRef = useRef(false);
  const seenPermissionIdsRef = useRef(new Set());

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

  const connectRef = useRef(null);

  const scheduleReconnect = useCallback(() => {
    clearReconnectTimer();
    clearHeartbeatTimer();
    if (isUnmountedRef.current) return;
    
    setStatus('RECONNECTING');
    reconnectTimerRef.current = setTimeout(() => {
      if (!isUnmountedRef.current && connectRef.current) {
        connectRef.current(true);
      }
    }, 2500); // Tentar reconectar a cada 2.5 segundos
  }, []);

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
      } catch {}
      wsRef.current = null;
    }

    if (!url) return;

    // Sem token nao ha handshake possivel: nao abre o WebSocket e orienta o pareamento
    if (!authToken) {
      setStatus('ERROR');
      setErrorMessage('Abra o link de pareamento');
      return;
    }

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
              try { ws.close(); } catch {}
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
            // Servidor reenvia os pedidos pendentes logo apos auth_success
            seenPermissionIdsRef.current = new Set();
            setPermissionQueue([]);
            if (data.volume) {
              setVolumeState(data.volume);
            }
            if (data.running_apps) {
              setRunningApps(data.running_apps);
            }
            if (data.catalog) {
              setCatalog(data.catalog);
            }
          } else if (data.type === 'catalog_updated') {
            if (data.catalog) {
              setCatalog(data.catalog);
            }
          } else if (data.type === 'volume_state') {
            setVolumeState({ level: data.level, muted: data.muted });
          } else if (data.type === 'system_status') {
            setSystemStatus({
              nowPlaying: data.now_playing,
              micMuted: data.mic_muted,
              metrics: data.system_metrics || null
            });
            if (data.running_apps) {
              setRunningApps(data.running_apps);
            }
          } else if (data.type === 'running_apps_update') {
            if (data.running_apps) {
              setRunningApps(data.running_apps);
            }
          } else if (data.type === 'claude_permission_request') {
            const item = {
              request_id: data.request_id,
              tool_name: data.tool_name,
              summary: data.summary,
              project: data.project,
              truncated: data.truncated === true,
              summary_length: Number(data.summary_length) || 0,
              deadline: Date.now() + (Number(data.expires_in) || 0) * 1000
            };
            if (!seenPermissionIdsRef.current.has(item.request_id)) {
              seenPermissionIdsRef.current.add(item.request_id);
              hapticFeedback.warning();
              setPermissionQueue((prev) => (
                prev.some((p) => p.request_id === item.request_id) ? prev : [...prev, item]
              ));
            }
          } else if (data.type === 'action_result' && data.status === 'error' && data.request_id) {
            seenPermissionIdsRef.current.delete(data.request_id);
            setPermissionQueue((prev) => prev.filter((p) => p.request_id !== data.request_id));
          } else if (data.type === 'claude_permission_resolved') {
            setPermissionQueue((prev) => prev.filter((p) => p.request_id !== data.request_id));
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
    connectRef.current = connect;
  }, [connect]);

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

  const respondPermission = useCallback((requestId, decision) => {
    if (status !== 'AUTHENTICATED') return false;
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return false;
    try {
      wsRef.current.send(JSON.stringify({
        action: 'claude_permission_response',
        request_id: requestId,
        decision
      }));
      return true;
    } catch (err) {
      console.error('Erro ao enviar resposta de permissao:', err);
      return false;
    }
  }, [status]);

  // Remove localmente pedidos cujo prazo venceu (o servidor tambem envia "expired")
  useEffect(() => {
    if (permissionQueue.length === 0) return undefined;
    const next = Math.min(...permissionQueue.map((p) => p.deadline));
    const timer = setTimeout(() => {
      const now = Date.now();
      setPermissionQueue((prev) => prev.filter((p) => p.deadline > now));
    }, Math.max(next - Date.now(), 0) + 50);
    return () => clearTimeout(timer);
  }, [permissionQueue]);

  return {
    status,
    lastMessage,
    errorMessage,
    sendAction,
    volume,
    systemStatus,
    runningApps,
    catalog,
    changeVolume,
    toggleMute,
    permissionQueue,
    respondPermission,
    reconnect: connect
  };
}
