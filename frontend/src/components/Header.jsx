import React from 'react';
import { Wifi, WifiOff, RefreshCw, Settings, ShieldCheck, ShieldAlert, Moon, Sun } from 'lucide-react';

export function Header({ status, onOpenSettings, isDarkMode, onToggleTheme }) {
  const getStatusBadge = () => {
    switch (status) {
      case 'AUTHENTICATED':
        return (
          <div className="status-badge authenticated">
            <span className="pulse-dot green"></span>
            <ShieldCheck size={14} className="badge-icon" />
            <span>Conectado</span>
          </div>
        );
      case 'CONNECTED':
        return (
          <div className="status-badge connecting">
            <span className="pulse-dot yellow"></span>
            <RefreshCw size={14} className="badge-icon spin" />
            <span>Autenticando...</span>
          </div>
        );
      case 'CONNECTING':
        return (
          <div className="status-badge connecting">
            <span className="pulse-dot yellow"></span>
            <Wifi size={14} className="badge-icon" />
            <span>Conectando...</span>
          </div>
        );
      case 'RECONNECTING':
        return (
          <div className="status-badge reconnecting">
            <span className="pulse-dot red"></span>
            <WifiOff size={14} className="badge-icon" />
            <span>Reconectando (3s)...</span>
          </div>
        );
      case 'ERROR':
      default:
        return (
          <div className="status-badge error">
            <span className="pulse-dot red"></span>
            <ShieldAlert size={14} className="badge-icon" />
            <span>Desconectado</span>
          </div>
        );
    }
  };

  return (
    <header className="app-header">
      <div className="brand-info">
        <h1 className="brand-title">STREAM DECK</h1>
        <span className="brand-subtitle">Launcher Windows (Mi 9)</span>
      </div>

      <div className="header-actions">
        {getStatusBadge()}
        <button 
          className="btn-settings-icon" 
          onClick={onToggleTheme} 
          title="Alternar Tema"
          aria-label="Alternar Tema"
        >
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <button 
          className="btn-settings-icon" 
          onClick={onOpenSettings} 
          title="Configurações de Conexão"
          aria-label="Configurações"
        >
          <Settings size={18} />
        </button>
      </div>
    </header>
  );
}
