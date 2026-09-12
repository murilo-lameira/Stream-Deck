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
import micOffIcon from '../assets/icons/mic-off.svg';

import { AppWindow, Terminal, Globe, Music, Gamepad2, Settings } from 'lucide-react';

const ICON_MAP = {
  vscode: vscodeIcon,
  discord: discordIcon,
  chrome: chromeIcon,
  spotify: spotifyIcon,
  gemini: geminiIcon,
  'league-of-legends': lolIcon,
  lol: lolIcon,
  steam: steamIcon,
  obsidian: obsidianIcon,
  whatsapp: whatsappIcon,
  power: powerIcon,
  obs: obsIcon,
  blitz: blitzIcon,
  github: githubIcon,
  youtube: youtubeIcon,
  logitech: logitechIcon,
  ghub: logitechIcon,
  vms: vmsIcon,
  checkup: checkupIcon,
  'media-play': mediaPlayIcon,
  'media-next': mediaNextIcon,
  'media-prev': mediaPrevIcon,
  'vol-mute': volMuteIcon,
  mic: micIcon,
  'mic-off': micOffIcon,
};

const LUCIDE_FALLBACKS = {
  terminal: Terminal,
  globe: Globe,
  music: Music,
  game: Gamepad2,
  settings: Settings,
  app: AppWindow,
};

/**
 * Retorna o asset do ícone correspondente à chave fornecida.
 * Suporta SVGs locais e componentes Lucide de fallback.
 */
export function resolveIcon(iconKey) {
  if (!iconKey) return AppWindow;
  
  const lower = String(iconKey).toLowerCase().trim();
  if (ICON_MAP[lower]) {
    return ICON_MAP[lower];
  }
  if (LUCIDE_FALLBACKS[lower]) {
    return LUCIDE_FALLBACKS[lower];
  }
  return AppWindow;
}
