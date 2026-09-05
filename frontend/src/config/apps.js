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
import githubIcon from '../assets/icons/github.svg';
import youtubeIcon from '../assets/icons/youtube.svg';
import logitechIcon from '../assets/icons/logitech.svg';
import vmsIcon from '../assets/icons/vms.svg';
import checkupIcon from '../assets/icons/checkup.svg';

import mediaPlayIcon from '../assets/icons/media-play.svg';
import mediaNextIcon from '../assets/icons/media-next.svg';
import mediaPrevIcon from '../assets/icons/media-prev.svg';
import volMuteIcon from '../assets/icons/vol-mute.svg';
import micIcon from '../assets/icons/mic.svg';

// Página 1: Aplicativos principais
export const PAGE1_APPS = [
  { id: 'vscode',   name: 'VS Code',    icon: vscodeIcon,   color: '#007ACC' },
  { id: 'discord',  name: 'Discord',    icon: discordIcon,  color: '#5865F2' },
  { id: 'whatsapp', name: 'WhatsApp',   icon: whatsappIcon, color: '#25D366' },
  { id: 'chrome',   name: 'Chrome',     icon: chromeIcon,   color: '#EA4335' },
  { id: 'spotify',  name: 'Spotify',    icon: spotifyIcon,  color: '#1DB954' },
  { id: 'gemini',   name: 'Gemini',     icon: geminiIcon,   color: '#8E24AA' },
  { id: 'youtube',  name: 'YouTube',    icon: youtubeIcon,  color: '#FF0000' },
  { id: 'obsidian', name: 'Obsidian',   icon: obsidianIcon, color: '#7c3aed' },
];

// Página 2: Mídia (não alterar)
export const MEDIA_APPS = [
  { id: 'sys_media_prev',      name: 'Anterior',    icon: mediaPrevIcon, color: '#10b981' },
  { id: 'sys_media_playpause', name: 'Play/Pause',  icon: mediaPlayIcon, color: '#10b981' },
  { id: 'sys_media_next',      name: 'Próxima',     icon: mediaNextIcon, color: '#10b981' },
  { id: 'sys_vol_mute',        name: 'Mutar',       icon: volMuteIcon,   color: '#ef4444' },
  { id: 'sys_mic_mute',        name: 'Microfone',   icon: micIcon,       color: '#f59e0b' },
  { id: 'shutdown_pc',         name: 'Desligar PC', icon: powerIcon,     color: '#ff4444' },
];

// Página 3: Ferramentas, Jogos & Monitoramento (8 botões - Grade 2x4)
export const PAGE3_APPS = [
  { id: 'obs',     name: 'OBS Studio',  icon: obsIcon,      color: '#ffffff' },
  { id: 'github',  name: 'GitHub',      icon: githubIcon,   color: '#ffffff' },
  { id: 'ghub',    name: 'G HUB',       icon: logitechIcon, color: '#00B8FC' },
  { id: 'vms',     name: 'VMS Câmeras', icon: vmsIcon,      color: '#00d2ff' },
  { id: 'checkup', name: 'CheckUP',     icon: checkupIcon,  color: '#8C4FFF' },
  { id: 'lol',     name: 'League',      icon: lolIcon,      color: '#D4AF37' },
  { id: 'steam',   name: 'Steam',       icon: steamIcon,    color: '#66c0f4' },
  { id: 'blitz',   name: 'Blitz',       icon: blitzIcon,    color: '#ED1F34' },
];


