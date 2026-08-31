import vscodeIcon from '../assets/icons/vscode.svg';
import discordIcon from '../assets/icons/discord.svg';
import chromeIcon from '../assets/icons/chrome.svg';
import spotifyIcon from '../assets/icons/spotify.svg';
import geminiIcon from '../assets/icons/gemini.svg';
import lolIcon from '../assets/icons/league-of-legends.svg';
import steamIcon from '../assets/icons/steam.svg';
import obsidianIcon from '../assets/icons/obsidian.svg';
import whatsappIcon from '../assets/icons/whatsapp.svg';
import powerIcon from '../assets/icons/power.svg';
import obsIcon from '../assets/icons/obs.svg';
import blitzIcon from '../assets/icons/blitz.svg';

import mediaPlayIcon from '../assets/icons/media-play.svg';
import mediaNextIcon from '../assets/icons/media-next.svg';
import mediaPrevIcon from '../assets/icons/media-prev.svg';
import volMuteIcon from '../assets/icons/vol-mute.svg';
import micIcon from '../assets/icons/mic.svg';

export const APPS_LIST = [
  {
    id: 'obs',
    name: 'OBS Studio',
    category: 'Criador',
    icon: obsIcon,
    color: '#ffffff'
  },
  {
    id: 'vscode',
    name: 'VS Code',
    category: 'Desenvolvimento',
    icon: vscodeIcon,
    color: '#007ACC'
  },
  {
    id: 'discord',
    name: 'Discord',
    category: 'Comunicação',
    icon: discordIcon,
    color: '#5865F2'
  },
  {
    id: 'whatsapp',
    name: 'WhatsApp',
    category: 'Comunicação',
    icon: whatsappIcon,
    color: '#25D366'
  },
  {
    id: 'chrome',
    name: 'Chrome',
    category: 'Navegação',
    icon: chromeIcon,
    color: '#EA4335'
  },
  {
    id: 'spotify',
    name: 'Spotify',
    category: 'Música',
    icon: spotifyIcon,
    color: '#1DB954'
  },
  {
    id: 'gemini',
    name: 'Gemini',
    category: 'IA',
    icon: geminiIcon,
    color: '#8E24AA'
  },
  {
    id: 'lol',
    name: 'League of Legends',
    category: 'Jogos',
    icon: lolIcon,
    color: '#D4AF37'
  },
  {
    id: 'steam',
    name: 'Steam',
    category: 'Jogos',
    icon: steamIcon,
    color: '#66c0f4'
  },
  {
    id: 'blitz',
    name: 'Blitz',
    category: 'Jogos',
    icon: blitzIcon,
    color: '#ED1F34'
  },
  {
    id: 'obsidian',
    name: 'Obsidian',
    category: 'Produtividade',
    icon: obsidianIcon,
    color: '#7c3aed'
  },
  {
    id: 'sys_media_prev',
    name: 'Anterior',
    category: 'Mídia',
    icon: mediaPrevIcon,
    color: '#10b981'
  },
  {
    id: 'sys_media_playpause',
    name: 'Play/Pause',
    category: 'Mídia',
    icon: mediaPlayIcon,
    color: '#10b981'
  },
  {
    id: 'sys_media_next',
    name: 'Próxima',
    category: 'Mídia',
    icon: mediaNextIcon,
    color: '#10b981'
  },
  {
    id: 'sys_vol_mute',
    name: 'Mutar',
    category: 'Mídia',
    icon: volMuteIcon,
    color: '#ef4444'
  },
  {
    id: 'sys_mic_mute',
    name: 'Microfone',
    category: 'Mídia',
    icon: micIcon,
    color: '#f59e0b'
  },
  {
    id: 'shutdown_pc',
    name: 'Desligar PC',
    category: 'Mídia',
    icon: powerIcon,
    color: '#ff4444'
  }
];
