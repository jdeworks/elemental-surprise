import fs from 'node:fs';
import path from 'node:path';
import { loadGameData, type ElementDef } from './lib/load-data.js';

const BG = '#252830';

const GROUP_COLORS: Record<string, [string, string]> = {
  Nature:     ['#43A047', '#2E7D32'],
  Space:      ['#5C6BC0', '#283593'],
  Materials:  ['#8D6E63', '#4E342E'],
  Life:       ['#66BB6A', '#388E3C'],
  Animals:    ['#FFA726', '#E65100'],
  Humanity:   ['#EC407A', '#AD1457'],
  Knowledge:  ['#AB47BC', '#6A1B9A'],
  Science:    ['#26C6DA', '#00838F'],
  Tools:      ['#78909C', '#37474F'],
  Society:    ['#FF7043', '#BF360C'],
  Fantasy:    ['#7E57C2', '#4527A0'],
  Food:       ['#EF5350', '#B71C1C'],
  Culture:    ['#FFCA28', '#F57F17'],
  Technology: ['#42A5F5', '#1565C0'],
  AI:         ['#26A69A', '#00695C'],
};

// All hand-crafted icons are drawn assuming a dark bg rect is placed underneath.
// Draw area: roughly 10-54 (44px usable in 64px viewBox) for consistent sizing.
const SYMBOL_PATHS: Record<string, string> = {
  // ── Starter elements ──────────────────────────────────────────────
  fire:
    '<defs><linearGradient id="fg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFDD00"/><stop offset="60%" stop-color="#FF8800"/><stop offset="100%" stop-color="#FF4400"/></linearGradient></defs>' +
    '<path d="M32 10c0 0-14 14-14 26a14 14 0 0028 0C46 24 32 10 32 10z" fill="url(#fg)"/>' +
    '<path d="M32 22c0 0-7 8-7 14a7 7 0 0014 0C39 30 32 22 32 22z" fill="#FFFF88" opacity="0.8"/>',
  water:
    '<defs><linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#88DDFF"/><stop offset="100%" stop-color="#0088FF"/></linearGradient></defs>' +
    '<path d="M32 10c0 0-16 16-16 26a16 16 0 0032 0C48 26 32 10 32 10z" fill="url(#wg)"/>' +
    '<ellipse cx="26" cy="34" rx="4" ry="6" fill="white" opacity="0.35"/>',
  earth:
    '<circle cx="32" cy="32" r="20" fill="#6D9B47" stroke="#4E7A30" stroke-width="1.5"/>' +
    '<path d="M22 18c4-2 10 2 16-1s7 6 3 10-3 8-8 10-10-2-14-4 0-8 3-12z" fill="#8B6E4E" opacity="0.7"/>' +
    '<path d="M38 42c3-1 8 1 10 4s-2 4-6 2-6-3-4-6z" fill="#8B6E4E" opacity="0.6"/>',
  wind:
    '<path d="M14 24h24c6 0 6-10 0-10" fill="none" stroke="#90CAF9" stroke-width="3.5" stroke-linecap="round"/>' +
    '<path d="M14 34h18c5 0 5 8 0 8" fill="none" stroke="#64B5F6" stroke-width="3" stroke-linecap="round"/>' +
    '<path d="M14 44h12c4 0 4-7 0-7" fill="none" stroke="#42A5F5" stroke-width="2.5" stroke-linecap="round"/>',

  // ── Basic combination results ─────────────────────────────────────
  steam:
    '<path d="M18 50c2-10 8-8 6-18s6-6 4-16" fill="none" stroke="#7CB8D4" stroke-width="3.5" stroke-linecap="round"/>' +
    '<path d="M32 52c2-10 8-8 6-18s6-6 4-16" fill="none" stroke="#5DADE2" stroke-width="3.5" stroke-linecap="round"/>' +
    '<path d="M46 50c2-10 8-8 6-18s6-6 4-16" fill="none" stroke="#7CB8D4" stroke-width="3" stroke-linecap="round"/>',
  lava:
    '<ellipse cx="32" cy="42" rx="20" ry="12" fill="#D84315"/>' +
    '<ellipse cx="32" cy="40" rx="16" ry="8" fill="#FF6D00"/>' +
    '<circle cx="24" cy="38" r="4" fill="#FFD600" opacity="0.8"/>' +
    '<circle cx="38" cy="36" r="3" fill="#FFAB00" opacity="0.7"/>' +
    '<path d="M28 32c-2-8 0-16 4-20 4 4 6 12 4 20z" fill="#FF6D00"/>',
  dust:
    '<circle cx="22" cy="22" r="4" fill="#A68B73"/>' +
    '<circle cx="42" cy="18" r="3.5" fill="#C4A882"/>' +
    '<circle cx="16" cy="40" r="3" fill="#8B7355"/>' +
    '<circle cx="38" cy="36" r="5" fill="#B89C7D"/>' +
    '<circle cx="48" cy="44" r="3" fill="#C4A882"/>' +
    '<circle cx="28" cy="48" r="3.5" fill="#8B7355"/>' +
    '<circle cx="32" cy="30" r="2" fill="#A68B73"/>',
  energy:
    '<polygon points="36,8 18,32 28,32 26,56 48,28 36,28" fill="#FFD600" stroke="#F57F17" stroke-width="1.5"/>',
  mud:
    '<ellipse cx="32" cy="42" rx="20" ry="14" fill="#5D4037"/>' +
    '<ellipse cx="32" cy="40" rx="16" ry="10" fill="#795548"/>' +
    '<circle cx="24" cy="38" r="4" fill="#4E342E" opacity="0.6"/>' +
    '<circle cx="40" cy="36" r="3" fill="#3E2723" opacity="0.5"/>' +
    '<ellipse cx="32" cy="44" rx="8" ry="3" fill="#6D4C41" opacity="0.6"/>',
  rain:
    '<path d="M14 30a14 14 0 0136 0" fill="#78909C"/>' +
    '<ellipse cx="32" cy="32" rx="20" ry="6" fill="#607D8B"/>' +
    '<line x1="20" y1="42" x2="18" y2="52" stroke="#42A5F5" stroke-width="2.5" stroke-linecap="round"/>' +
    '<line x1="32" y1="42" x2="30" y2="54" stroke="#42A5F5" stroke-width="2.5" stroke-linecap="round"/>' +
    '<line x1="44" y1="42" x2="42" y2="50" stroke="#42A5F5" stroke-width="2.5" stroke-linecap="round"/>',

  // ── Nature & weather ──────────────────────────────────────────────
  stone:
    '<polygon points="32,12 50,24 46,48 18,48 14,24" fill="#7E8C8D" stroke="#566573" stroke-width="1.5"/>' +
    '<polygon points="32,12 40,22 36,36 24,36 20,22" fill="#ABB2B9" opacity="0.5"/>',
  sun:
    '<circle cx="32" cy="32" r="12" fill="#FFD600"/>' +
    '<g stroke="#FFAB00" stroke-width="3" stroke-linecap="round">' +
    '<line x1="32" y1="10" x2="32" y2="16"/><line x1="32" y1="48" x2="32" y2="54"/>' +
    '<line x1="10" y1="32" x2="16" y2="32"/><line x1="48" y1="32" x2="54" y2="32"/>' +
    '<line x1="16" y1="16" x2="20" y2="20"/><line x1="44" y1="44" x2="48" y2="48"/>' +
    '<line x1="48" y1="16" x2="44" y2="20"/><line x1="20" y1="44" x2="16" y2="48"/>' +
    '</g>',
  moon:
    '<path d="M36 12a20 20 0 100 40 16 16 0 010-40z" fill="#FDD835"/>' +
    '<circle cx="28" cy="28" r="2" fill="#F9A825" opacity="0.3"/>' +
    '<circle cx="34" cy="42" r="1.5" fill="#F9A825" opacity="0.3"/>',
  star:
    '<polygon points="32,10 37,24 52,24 40,34 44,48 32,40 20,48 24,34 12,24 27,24" fill="#FFD600" stroke="#F9A825" stroke-width="1"/>',
  ice:
    '<polygon points="32,10 44,20 44,44 32,54 20,44 20,20" fill="#4FC3F7" stroke="#29B6F6" stroke-width="1.5"/>' +
    '<polygon points="32,16 38,22 38,42 32,48 26,42 26,22" fill="#81D4FA" opacity="0.5"/>' +
    '<line x1="32" y1="10" x2="32" y2="54" stroke="#B3E5FC" stroke-width="1" opacity="0.4"/>',
  snow:
    '<g stroke="#81D4FA" stroke-width="2.5" fill="none">' +
    '<line x1="32" y1="10" x2="32" y2="54"/>' +
    '<line x1="13" y1="21" x2="51" y2="43"/>' +
    '<line x1="51" y1="21" x2="13" y2="43"/>' +
    '</g>' +
    '<g fill="#B3E5FC">' +
    '<circle cx="32" cy="10" r="3.5"/><circle cx="32" cy="54" r="3.5"/>' +
    '<circle cx="13" cy="21" r="3"/><circle cx="51" cy="43" r="3"/>' +
    '<circle cx="51" cy="21" r="3"/><circle cx="13" cy="43" r="3"/>' +
    '</g>' +
    '<circle cx="32" cy="32" r="4" fill="#E1F5FE"/>',
  lightning:
    '<polygon points="36,8 18,32 28,32 26,56 48,28 36,28" fill="#FFD600" stroke="#F57F17" stroke-width="1.5"/>',
  cloud:
    '<ellipse cx="32" cy="38" rx="18" ry="10" fill="#78909C"/>' +
    '<circle cx="22" cy="30" r="10" fill="#90A4AE"/>' +
    '<circle cx="36" cy="26" r="12" fill="#B0BEC5"/>' +
    '<ellipse cx="32" cy="38" rx="18" ry="10" fill="#90A4AE"/>',
  mountain:
    '<polygon points="32,12 54,52 10,52" fill="#607D8B"/>' +
    '<polygon points="32,12 40,26 24,26" fill="#ECEFF1"/>' +
    '<polygon points="44,34 54,52 34,52" fill="#546E7A"/>',
  ocean:
    '<rect x="10" y="20" width="44" height="30" rx="4" fill="#1565C0"/>' +
    '<path d="M10 30c8-5 14 5 22 0s14 5 22 0" fill="none" stroke="#42A5F5" stroke-width="2.5"/>' +
    '<path d="M10 38c8-5 14 5 22 0s14 5 22 0" fill="none" stroke="#1E88E5" stroke-width="2"/>',
  tree:
    '<rect x="28" y="38" width="8" height="16" rx="2" fill="#6D4C41"/>' +
    '<circle cx="32" cy="28" r="14" fill="#43A047"/>' +
    '<circle cx="24" cy="24" r="9" fill="#66BB6A" opacity="0.7"/>',
  flower:
    '<circle cx="32" cy="32" r="5" fill="#FFD600"/>' +
    '<g fill="#EC407A">' +
    '<circle cx="32" cy="20" r="6"/><circle cx="43" cy="27" r="6"/>' +
    '<circle cx="40" cy="40" r="6"/><circle cx="24" cy="40" r="6"/>' +
    '<circle cx="21" cy="27" r="6"/>' +
    '</g>',
  plant:
    '<path d="M32 54V30" stroke="#4CAF50" stroke-width="3"/>' +
    '<path d="M32 30c-10-12-22-6-18 2s12 4 18-2z" fill="#66BB6A"/>' +
    '<path d="M32 40c8-10 18-4 14 2s-10 2-14-2z" fill="#43A047"/>',
  volcano:
    '<polygon points="32,14 52,52 12,52" fill="#795548"/>' +
    '<polygon points="26,14 38,14 42,20 22,20" fill="#D84315"/>' +
    '<path d="M28 14c-2-6 0-10 4-12 4 2 6 6 4 12" fill="#FF6D00"/>' +
    '<circle cx="32" cy="6" r="3" fill="#FFAB00" opacity="0.6"/>',
  river:
    '<path d="M18 10c4 8-4 14 0 22s-4 14 0 22" fill="none" stroke="#42A5F5" stroke-width="6" stroke-linecap="round"/>' +
    '<path d="M18 10c4 8-4 14 0 22s-4 14 0 22" fill="none" stroke="#64B5F6" stroke-width="3" stroke-linecap="round"/>',
  lake:
    '<ellipse cx="32" cy="34" rx="20" ry="16" fill="#1976D2"/>' +
    '<ellipse cx="28" cy="30" rx="8" ry="4" fill="#42A5F5" opacity="0.5"/>' +
    '<path d="M14 42c6-1 10 1 14 0s8-1 14 0" fill="none" stroke="#64B5F6" stroke-width="1.5" opacity="0.5"/>',
  island:
    '<ellipse cx="32" cy="44" rx="22" ry="10" fill="#1565C0"/>' +
    '<ellipse cx="32" cy="38" rx="14" ry="8" fill="#FFD54F"/>' +
    '<rect x="30" y="20" width="4" height="18" rx="1" fill="#6D4C41"/>' +
    '<circle cx="34" cy="20" r="8" fill="#43A047"/>',
  desert:
    '<rect x="10" y="32" width="44" height="22" rx="4" fill="#FFB74D"/>' +
    '<path d="M10 36c8-6 14 0 22-4s14 2 22-2" fill="none" stroke="#FFA726" stroke-width="2"/>' +
    '<circle cx="44" cy="18" r="8" fill="#FFD600"/>',

  // ── Animals ───────────────────────────────────────────────────────
  animal:
    '<ellipse cx="32" cy="36" rx="16" ry="12" fill="#FF8A65"/>' +
    '<circle cx="24" cy="30" r="4" fill="#FFF"/><circle cx="40" cy="30" r="4" fill="#FFF"/>' +
    '<circle cx="24" cy="31" r="2" fill="#333"/><circle cx="40" cy="31" r="2" fill="#333"/>' +
    '<ellipse cx="32" cy="38" rx="3" ry="2" fill="#333"/>',
  whale:
    '<path d="M12 32c0-10 8-18 20-18s20 8 20 16c0 10-6 14-14 14h-12c-8 0-14-4-14-12z" fill="#2196F3"/>' +
    '<path d="M52 30c4-6 8-10 10-8s-2 8-6 12" fill="#1976D2"/>' +
    '<circle cx="22" cy="28" r="3" fill="#E3F2FD"/><circle cx="22" cy="29" r="1.5" fill="#0D47A1"/>' +
    '<path d="M16 40c4 2 8 2 12 0" fill="none" stroke="#E3F2FD" stroke-width="1.5" stroke-linecap="round"/>' +
    '<path d="M32 50c-2-4 0-6 2-4s4 0 2 4" fill="#42A5F5"/>',
  fish:
    '<ellipse cx="30" cy="32" rx="16" ry="10" fill="#FF7043"/>' +
    '<polygon points="48,32 58,22 58,42" fill="#FF5722"/>' +
    '<circle cx="20" cy="30" r="3" fill="#FFF"/><circle cx="20" cy="30" r="1.5" fill="#333"/>' +
    '<path d="M30 26c4-2 8 0 10 2" fill="none" stroke="#E64A19" stroke-width="1.5"/>',
  bird:
    '<ellipse cx="32" cy="34" rx="12" ry="10" fill="#FFA726"/>' +
    '<circle cx="32" cy="24" r="8" fill="#FFB74D"/>' +
    '<circle cx="28" cy="22" r="2" fill="#333"/>' +
    '<polygon points="38,24 48,22 38,28" fill="#FF5722"/>' +
    '<path d="M20 34l-8 8" stroke="#FFA726" stroke-width="2.5" stroke-linecap="round"/>' +
    '<path d="M44 34l8 8" stroke="#FFA726" stroke-width="2.5" stroke-linecap="round"/>',
  butterfly:
    '<path d="M32 18v28" stroke="#5D4037" stroke-width="2"/>' +
    '<ellipse cx="22" cy="24" rx="10" ry="8" fill="#E040FB" opacity="0.9"/>' +
    '<ellipse cx="42" cy="24" rx="10" ry="8" fill="#7C4DFF" opacity="0.9"/>' +
    '<ellipse cx="24" cy="38" rx="8" ry="6" fill="#E040FB" opacity="0.7"/>' +
    '<ellipse cx="40" cy="38" rx="8" ry="6" fill="#7C4DFF" opacity="0.7"/>' +
    '<circle cx="30" cy="16" r="2" fill="#5D4037"/><circle cx="34" cy="16" r="2" fill="#5D4037"/>',
  cat:
    '<circle cx="32" cy="34" r="14" fill="#FF8A65"/>' +
    '<polygon points="18,20 22,34 12,34" fill="#FF8A65"/>' +
    '<polygon points="46,20 42,34 52,34" fill="#FF8A65"/>' +
    '<circle cx="26" cy="32" r="3" fill="#FFF"/><circle cx="38" cy="32" r="3" fill="#FFF"/>' +
    '<circle cx="26" cy="33" r="1.5" fill="#333"/><circle cx="38" cy="33" r="1.5" fill="#333"/>' +
    '<path d="M30 38c1 1 3 1 4 0" fill="none" stroke="#333" stroke-width="1.5"/>',
  dog:
    '<circle cx="32" cy="32" r="14" fill="#A1887F"/>' +
    '<ellipse cx="20" cy="22" rx="6" ry="8" fill="#8D6E63"/>' +
    '<ellipse cx="44" cy="22" rx="6" ry="8" fill="#8D6E63"/>' +
    '<circle cx="26" cy="30" r="3" fill="#FFF"/><circle cx="38" cy="30" r="3" fill="#FFF"/>' +
    '<circle cx="26" cy="31" r="1.5" fill="#333"/><circle cx="38" cy="31" r="1.5" fill="#333"/>' +
    '<ellipse cx="32" cy="38" rx="4" ry="3" fill="#333"/>',

  // ── Humanity ──────────────────────────────────────────────────────
  human:
    '<circle cx="32" cy="18" r="8" fill="#FFCC80"/>' +
    '<path d="M20 52V40a12 12 0 0124 0v12" fill="#42A5F5"/>',
  heart:
    '<path d="M32 50C20 40 10 32 10 24a10 10 0 0122 0 10 10 0 0122 0c0 8-10 16-22 26z" fill="#E53935"/>',
  brain:
    '<path d="M32 14c-10 0-16 8-16 16s6 20 16 20 16-10 16-20-6-16-16-16z" fill="#F48FB1"/>' +
    '<path d="M32 14v40" stroke="#E91E63" stroke-width="1.5"/>' +
    '<path d="M22 24c5 4 5 12 0 16" stroke="#E91E63" stroke-width="1.5" fill="none"/>' +
    '<path d="M42 24c-5 4-5 12 0 16" stroke="#E91E63" stroke-width="1.5" fill="none"/>',
  skull:
    '<circle cx="32" cy="28" r="16" fill="#BDBDBD"/>' +
    '<rect x="26" y="40" width="12" height="10" rx="2" fill="#BDBDBD"/>' +
    '<circle cx="25" cy="26" r="4.5" fill="#252830"/><circle cx="39" cy="26" r="4.5" fill="#252830"/>' +
    '<path d="M28 36h8" stroke="#252830" stroke-width="2"/>' +
    '<line x1="30" y1="44" x2="30" y2="48" stroke="#252830" stroke-width="1.5"/>' +
    '<line x1="34" y1="44" x2="34" y2="48" stroke="#252830" stroke-width="1.5"/>',
  bone:
    '<rect x="22" y="28" width="20" height="8" rx="2" fill="#ECEFF1"/>' +
    '<circle cx="20" cy="26" r="5" fill="#ECEFF1"/><circle cx="20" cy="38" r="5" fill="#ECEFF1"/>' +
    '<circle cx="44" cy="26" r="5" fill="#ECEFF1"/><circle cx="44" cy="38" r="5" fill="#ECEFF1"/>',

  // ── Materials ─────────────────────────────────────────────────────
  metal:
    '<rect x="14" y="14" width="36" height="36" rx="6" fill="#78909C" stroke="#546E7A" stroke-width="1.5"/>' +
    '<rect x="20" y="20" width="24" height="24" rx="3" fill="#90A4AE"/>' +
    '<line x1="20" y1="32" x2="44" y2="32" stroke="#B0BEC5" stroke-width="1.5"/>' +
    '<line x1="32" y1="20" x2="32" y2="44" stroke="#B0BEC5" stroke-width="1" opacity="0.5"/>',
  diamond:
    '<polygon points="32,8 52,26 32,56 12,26" fill="#4FC3F7" stroke="#29B6F6" stroke-width="1.5"/>' +
    '<polygon points="32,8 42,26 32,46 22,26" fill="#81D4FA" opacity="0.6"/>' +
    '<line x1="12" y1="26" x2="52" y2="26" stroke="#29B6F6" stroke-width="1"/>',
  glass:
    '<rect x="18" y="12" width="28" height="40" rx="4" fill="#81D4FA" opacity="0.5" stroke="#4FC3F7" stroke-width="1.5"/>' +
    '<rect x="22" y="16" width="8" height="12" rx="2" fill="#E1F5FE" opacity="0.6"/>',
  gold:
    '<rect x="12" y="24" width="40" height="24" rx="4" fill="#FFD600" stroke="#F9A825" stroke-width="1.5"/>' +
    '<rect x="16" y="28" width="32" height="16" rx="2" fill="#FFEE58" opacity="0.5"/>' +
    '<text x="32" y="40" text-anchor="middle" fill="#F57F17" font-family="Arial,sans-serif" font-size="14" font-weight="bold">Au</text>',

  // ── Knowledge & culture ───────────────────────────────────────────
  book:
    '<rect x="14" y="12" width="34" height="40" rx="3" fill="#5C6BC0"/>' +
    '<rect x="18" y="12" width="30" height="40" rx="3" fill="#7986CB"/>' +
    '<rect x="22" y="18" width="22" height="3" rx="1" fill="#E8EAF6"/>' +
    '<rect x="22" y="24" width="16" height="2" rx="1" fill="#C5CAE9"/>' +
    '<rect x="22" y="29" width="18" height="2" rx="1" fill="#C5CAE9"/>',
  music:
    '<circle cx="24" cy="44" r="7" fill="#E91E63"/><circle cx="24" cy="44" r="3" fill="#F48FB1"/>' +
    '<rect x="29" y="16" width="4" height="30" rx="1" fill="#E91E63"/>' +
    '<path d="M31 16h14c0 8-14 10-14 0z" fill="#E91E63"/>',
  crown:
    '<polygon points="12,42 16,24 26,34 32,18 38,34 48,24 52,42" fill="#FFD600" stroke="#F9A825" stroke-width="1.5"/>' +
    '<rect x="12" y="42" width="40" height="8" rx="2" fill="#FFD600" stroke="#F9A825" stroke-width="1"/>' +
    '<circle cx="22" cy="26" r="2.5" fill="#E53935"/>' +
    '<circle cx="32" cy="20" r="2.5" fill="#42A5F5"/>' +
    '<circle cx="42" cy="26" r="2.5" fill="#43A047"/>',
  sword:
    '<rect x="30" y="8" width="4" height="34" rx="1" fill="#90A4AE"/>' +
    '<polygon points="30,8 34,8 32,4" fill="#B0BEC5"/>' +
    '<rect x="22" y="40" width="20" height="5" rx="2" fill="#8D6E63"/>' +
    '<rect x="29" y="44" width="6" height="12" rx="2" fill="#6D4C41"/>',
  shield:
    '<path d="M32 10l18 6v14c0 12-8 20-18 24-10-4-18-12-18-24V16z" fill="#42A5F5" stroke="#1E88E5" stroke-width="1.5"/>' +
    '<path d="M32 18l10 4v8c0 8-4 12-10 14-6-2-10-6-10-14v-8z" fill="#1E88E5"/>',

  // ── Tools & technology ────────────────────────────────────────────
  gear:
    '<circle cx="32" cy="32" r="8" fill="none" stroke="#90A4AE" stroke-width="5"/>' +
    '<circle cx="32" cy="32" r="4" fill="#90A4AE"/>' +
    '<g fill="#90A4AE"><rect x="29" y="10" width="6" height="10" rx="2"/><rect x="29" y="44" width="6" height="10" rx="2"/>' +
    '<rect x="10" y="29" width="10" height="6" rx="2"/><rect x="44" y="29" width="10" height="6" rx="2"/></g>',
  house:
    '<polygon points="32,12 52,30 12,30" fill="#EF5350"/>' +
    '<rect x="16" y="30" width="32" height="22" fill="#FFCC80"/>' +
    '<rect x="26" y="38" width="12" height="14" rx="1" fill="#8D6E63"/>' +
    '<rect x="20" y="34" width="6" height="6" rx="1" fill="#81D4FA"/>',
  computer:
    '<rect x="10" y="12" width="44" height="30" rx="4" fill="#37474F"/>' +
    '<rect x="14" y="16" width="36" height="22" rx="2" fill="#64B5F6"/>' +
    '<rect x="22" y="44" width="20" height="4" rx="1" fill="#546E7A"/>' +
    '<rect x="18" y="48" width="28" height="3" rx="1" fill="#455A64"/>',
  rocket:
    '<path d="M32 8c-8 12-10 24-10 34h20c0-10-2-22-10-34z" fill="#ECEFF1" stroke="#78909C" stroke-width="1.5"/>' +
    '<path d="M22 42l-6 12h8z" fill="#42A5F5"/>' +
    '<path d="M42 42l6 12h-8z" fill="#42A5F5"/>' +
    '<circle cx="32" cy="26" r="5" fill="#42A5F5"/>' +
    '<path d="M28 50c2 4 3 6 4 6s2-2 4-6" fill="#FF6D00"/>',
  robot:
    '<rect x="16" y="20" width="32" height="28" rx="4" fill="#607D8B"/>' +
    '<rect x="22" y="26" width="8" height="6" rx="2" fill="#4FC3F7"/>' +
    '<rect x="34" y="26" width="8" height="6" rx="2" fill="#4FC3F7"/>' +
    '<rect x="26" y="38" width="12" height="4" rx="2" fill="#90A4AE"/>' +
    '<rect x="28" y="10" width="8" height="12" rx="3" fill="#78909C"/>' +
    '<circle cx="32" cy="10" r="3" fill="#EF5350"/>',

  // ── Science ───────────────────────────────────────────────────────
  atom:
    '<circle cx="32" cy="32" r="5" fill="#EF5350"/>' +
    '<ellipse cx="32" cy="32" rx="20" ry="8" fill="none" stroke="#42A5F5" stroke-width="2"/>' +
    '<ellipse cx="32" cy="32" rx="20" ry="8" fill="none" stroke="#66BB6A" stroke-width="2" transform="rotate(60 32 32)"/>' +
    '<ellipse cx="32" cy="32" rx="20" ry="8" fill="none" stroke="#FFA726" stroke-width="2" transform="rotate(-60 32 32)"/>',
  dna:
    '<path d="M22 8c0 12 20 12 20 24s-20 12-20 24" fill="none" stroke="#E53935" stroke-width="3"/>' +
    '<path d="M42 8c0 12-20 12-20 24s20 12 20 24" fill="none" stroke="#1E88E5" stroke-width="3"/>' +
    '<line x1="24" y1="20" x2="40" y2="20" stroke="#78909C" stroke-width="1.5"/>' +
    '<line x1="22" y1="32" x2="42" y2="32" stroke="#78909C" stroke-width="1.5"/>' +
    '<line x1="24" y1="44" x2="40" y2="44" stroke="#78909C" stroke-width="1.5"/>',
  magnet:
    '<path d="M20 20v20a12 12 0 0024 0V20" fill="none" stroke="#EF5350" stroke-width="8" stroke-linecap="round"/>' +
    '<rect x="14" y="14" width="12" height="10" rx="2" fill="#F44336"/>' +
    '<rect x="38" y="14" width="12" height="10" rx="2" fill="#1E88E5"/>',
  telescope:
    '<rect x="14" y="26" width="30" height="12" rx="3" fill="#546E7A"/>' +
    '<circle cx="48" cy="32" r="8" fill="#37474F" stroke="#546E7A" stroke-width="2"/>' +
    '<circle cx="48" cy="32" r="4" fill="#64B5F6"/>' +
    '<rect x="18" y="38" width="4" height="16" rx="1" fill="#455A64"/>' +
    '<rect x="28" y="38" width="4" height="12" rx="1" fill="#455A64"/>',

  // ── Food ──────────────────────────────────────────────────────────
  food:
    '<ellipse cx="32" cy="38" rx="20" ry="14" fill="#78909C" stroke="#546E7A" stroke-width="1.5"/>' +
    '<path d="M16 34c4-6 12-8 16-8s12 2 16 8" fill="#FF7043"/>' +
    '<circle cx="26" cy="30" r="3.5" fill="#66BB6A"/><circle cx="38" cy="32" r="3" fill="#EF5350"/>',
  bread:
    '<ellipse cx="32" cy="34" rx="18" ry="14" fill="#D4A054"/>' +
    '<ellipse cx="32" cy="30" rx="16" ry="10" fill="#E8B96C"/>' +
    '<path d="M20 28c4-2 8 0 12-1s8 1 12 0" fill="none" stroke="#C49244" stroke-width="1.5"/>',
  egg:
    '<path d="M32 12c-10 0-16 10-16 22a16 16 0 0032 0c0-12-6-22-16-22z" fill="#F5F5DC"/>' +
    '<ellipse cx="32" cy="36" rx="10" ry="8" fill="#FFD54F" opacity="0.3"/>',

  // ── Fantasy ───────────────────────────────────────────────────────
  dragon:
    '<path d="M16 44c2-12 8-18 16-20s14 2 18 10c2 4 2 8-2 10s-8 2-14 2c-6 0-12 0-18-2z" fill="#4CAF50"/>' +
    '<path d="M32 24c-2-6-1-14 0-16 1 2 2 10 0 16z" fill="#66BB6A"/>' +
    '<path d="M40 24c-1-5 0-12 1-14 1 2 1 9 0 14z" fill="#66BB6A"/>' +
    '<circle cx="24" cy="34" r="3.5" fill="#FFD600"/><circle cx="24" cy="34.5" r="1.5" fill="#1B5E20"/>' +
    '<circle cx="36" cy="32" r="3.5" fill="#FFD600"/><circle cx="36" cy="32.5" r="1.5" fill="#1B5E20"/>' +
    '<path d="M20 42c3 2 6 2 8 0" fill="none" stroke="#2E7D32" stroke-width="1.5"/>' +
    '<path d="M48 38l8-4-4 6z" fill="#4CAF50"/>',
  magic:
    '<polygon points="32,8 36,24 52,24 40,34 44,50 32,42 20,50 24,34 12,24 28,24" fill="#7E57C2"/>' +
    '<polygon points="32,16 34,24 42,24 36,30 38,40 32,36 26,40 28,30 22,24 30,24" fill="#EDE7F6"/>' +
    '<circle cx="32" cy="28" r="3" fill="#FFEB3B"/>',
  unicorn:
    '<circle cx="32" cy="34" r="14" fill="#F8BBD0"/>' +
    '<polygon points="32,8 28,22 36,22" fill="#FFD600" stroke="#F9A825" stroke-width="1"/>' +
    '<circle cx="26" cy="32" r="3" fill="#FFF"/><circle cx="26" cy="32.5" r="1.5" fill="#7B1FA2"/>' +
    '<path d="M34 40c3 0 6 0 8-2" fill="none" stroke="#E91E63" stroke-width="2" stroke-linecap="round"/>',
  ghost:
    '<path d="M18 54V30a14 14 0 0128 0v24l-7-6-7 6-7-6z" fill="#B0BEC5"/>' +
    '<circle cx="26" cy="30" r="4" fill="#37474F"/><circle cx="38" cy="30" r="4" fill="#37474F"/>' +
    '<ellipse cx="32" cy="40" rx="4" ry="3" fill="#37474F"/>',
  vampire:
    '<circle cx="32" cy="26" r="12" fill="#E0E0E0"/>' +
    '<path d="M20 22l6-10h-2l-6 10z" fill="#212121"/><path d="M44 22l-6-10h2l6 10z" fill="#212121"/>' +
    '<circle cx="27" cy="24" r="3" fill="#C62828"/><circle cx="37" cy="24" r="3" fill="#C62828"/>' +
    '<path d="M27 34l2 6 3-6z" fill="#FFF"/><path d="M37 34l-2 6-3-6z" fill="#FFF"/>' +
    '<path d="M18 40c2 6 12 10 14 10s12-4 14-10" fill="#C62828"/>',

  // ── AI & tech ─────────────────────────────────────────────────────
  ai:
    '<rect x="12" y="12" width="40" height="40" rx="10" fill="#00897B"/>' +
    '<text x="32" y="40" text-anchor="middle" fill="white" font-family="Arial,sans-serif" font-size="22" font-weight="bold">AI</text>',
  chip:
    '<rect x="18" y="18" width="28" height="28" rx="3" fill="#37474F"/>' +
    '<rect x="22" y="22" width="20" height="20" rx="2" fill="#4CAF50"/>' +
    '<g stroke="#78909C" stroke-width="2"><line x1="14" y1="26" x2="18" y2="26"/><line x1="14" y1="32" x2="18" y2="32"/><line x1="14" y1="38" x2="18" y2="38"/>' +
    '<line x1="46" y1="26" x2="50" y2="26"/><line x1="46" y1="32" x2="50" y2="32"/><line x1="46" y1="38" x2="50" y2="38"/>' +
    '<line x1="26" y1="14" x2="26" y2="18"/><line x1="32" y1="14" x2="32" y2="18"/><line x1="38" y1="14" x2="38" y2="18"/>' +
    '<line x1="26" y1="46" x2="26" y2="50"/><line x1="32" y1="46" x2="32" y2="50"/><line x1="38" y1="46" x2="38" y2="50"/></g>',

  // ── Society ───────────────────────────────────────────────────────
  flag:
    '<rect x="16" y="10" width="3" height="46" rx="1" fill="#90A4AE"/>' +
    '<rect x="19" y="14" width="30" height="20" rx="2" fill="#E53935"/>' +
    '<rect x="19" y="14" width="30" height="10" rx="2" fill="#FF7043"/>',
  money:
    '<circle cx="32" cy="32" r="18" fill="#FFD600" stroke="#F9A825" stroke-width="2"/>' +
    '<text x="32" y="40" text-anchor="middle" fill="#F57F17" font-family="Arial,sans-serif" font-size="24" font-weight="bold">$</text>',
  castle:
    '<rect x="14" y="28" width="36" height="26" fill="#90A4AE"/>' +
    '<rect x="10" y="22" width="8" height="32" fill="#78909C"/><rect x="46" y="22" width="8" height="32" fill="#78909C"/>' +
    '<rect x="8" y="18" width="4" height="6" fill="#78909C"/><rect x="16" y="18" width="4" height="6" fill="#78909C"/>' +
    '<rect x="44" y="18" width="4" height="6" fill="#78909C"/><rect x="52" y="18" width="4" height="6" fill="#78909C"/>' +
    '<rect x="28" y="38" width="8" height="16" rx="4" fill="#546E7A"/>',

  // ── Space ─────────────────────────────────────────────────────────
  planet:
    '<circle cx="32" cy="32" r="16" fill="#7E57C2"/>' +
    '<ellipse cx="32" cy="32" rx="26" ry="6" fill="none" stroke="#B39DDB" stroke-width="2.5" transform="rotate(-20 32 32)"/>' +
    '<path d="M20 26c4-2 8 0 12-1s8 2 12 0" fill="none" stroke="#9575CD" stroke-width="2" opacity="0.5"/>',
  comet:
    '<circle cx="42" cy="22" r="8" fill="#81D4FA"/>' +
    '<path d="M36 26L8 52" stroke="#4FC3F7" stroke-width="4" stroke-linecap="round" opacity="0.7"/>' +
    '<path d="M38 28L14 48" stroke="#B3E5FC" stroke-width="2" stroke-linecap="round" opacity="0.5"/>',
  satellite:
    '<rect x="24" y="24" width="16" height="16" rx="3" fill="#78909C"/>' +
    '<rect x="6" y="28" width="18" height="8" rx="2" fill="#42A5F5"/>' +
    '<rect x="40" y="28" width="18" height="8" rx="2" fill="#42A5F5"/>' +
    '<circle cx="32" cy="32" r="3" fill="#4FC3F7"/>',
};

const GROUP_SYMBOLS: Record<string, string> = {
  Nature:     '<path d="M32 16c-8 0-14 8-14 18s14 20 14 20 14-10 14-20-6-18-14-18z" fill="FG" opacity="0.3"/>',
  Space:      '<polygon points="32,14 36,26 48,26 38,34 42,46 32,38 22,46 26,34 16,26 28,26" fill="FG" opacity="0.3"/>',
  Materials:  '<polygon points="32,12 48,22 48,42 32,52 16,42 16,22" fill="none" stroke="FG" stroke-width="2" opacity="0.3"/>',
  Life:       '<circle cx="32" cy="32" r="16" fill="none" stroke="FG" stroke-width="2" opacity="0.25"/><circle cx="32" cy="32" r="8" fill="FG" opacity="0.15"/>',
  Animals:    '<circle cx="24" cy="22" r="8" fill="FG" opacity="0.2"/><circle cx="40" cy="22" r="8" fill="FG" opacity="0.2"/><circle cx="32" cy="36" r="12" fill="FG" opacity="0.2"/>',
  Humanity:   '<circle cx="32" cy="22" r="10" fill="FG" opacity="0.2"/><path d="M18 54v-8a14 14 0 0128 0v8" fill="FG" opacity="0.2"/>',
  Knowledge:  '<rect x="18" y="14" width="28" height="36" rx="3" fill="FG" opacity="0.2"/><rect x="22" y="20" width="20" height="3" rx="1" fill="FG" opacity="0.15"/>',
  Science:    '<circle cx="32" cy="32" r="5" fill="FG" opacity="0.3"/><ellipse cx="32" cy="32" rx="20" ry="8" fill="none" stroke="FG" stroke-width="1.5" opacity="0.2"/><ellipse cx="32" cy="32" rx="20" ry="8" fill="none" stroke="FG" stroke-width="1.5" opacity="0.2" transform="rotate(60 32 32)"/>',
  Tools:      '<circle cx="32" cy="32" r="8" fill="none" stroke="FG" stroke-width="3" opacity="0.25"/><rect x="29" y="10" width="6" height="10" rx="2" fill="FG" opacity="0.2"/><rect x="29" y="44" width="6" height="10" rx="2" fill="FG" opacity="0.2"/>',
  Society:    '<polygon points="32,14 50,30 14,30" fill="FG" opacity="0.2"/><rect x="18" y="30" width="28" height="20" fill="FG" opacity="0.15"/>',
  Fantasy:    '<polygon points="32,10 38,28 56,28 42,38 46,56 32,46 18,56 22,38 8,28 26,28" fill="FG" opacity="0.15"/>',
  Food:       '<circle cx="32" cy="34" r="18" fill="FG" opacity="0.15"/><ellipse cx="32" cy="34" rx="18" ry="12" fill="FG" opacity="0.1"/>',
  Culture:    '<polygon points="32,12 38,28 56,28 42,38 46,56 32,46 18,56 22,38 8,28 26,28" fill="FG" opacity="0.12"/>',
  Technology: '<rect x="14" y="14" width="36" height="36" rx="4" fill="none" stroke="FG" stroke-width="2" opacity="0.2"/><rect x="22" y="22" width="20" height="20" rx="2" fill="FG" opacity="0.1"/>',
  AI:         '<circle cx="32" cy="26" r="12" fill="FG" opacity="0.2"/><path d="M20 38c0 10 24 10 24 0" fill="none" stroke="FG" stroke-width="2" opacity="0.2"/><line x1="32" y1="38" x2="32" y2="52" stroke="FG" stroke-width="2" opacity="0.2"/>',
};

function getInitials(name: string): string {
  const words = name.replace(/[^a-zA-Z0-9\s]/g, '').trim().split(/\s+/);
  if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase();
  }
  return (words[0][0] + words[1][0]).toUpperCase();
}

function createSvg(el: ElementDef): string {
  const id = el.id;

  if (SYMBOL_PATHS[id]) {
    return `<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg"><rect width="64" height="64" rx="14" fill="${BG}"/>${SYMBOL_PATHS[id]}</svg>`;
  }

  const group = el.group ?? 'Other';
  const [c1, c2] = GROUP_COLORS[group] ?? ['#9E9E9E', '#616161'];
  const initials = getInitials(el.name);
  const fontSize = initials.length > 2 ? 18 : 22;
  const bgSymbol = (GROUP_SYMBOLS[group] ?? '').replace(/FG/g, 'white');

  return [
    '<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">',
    '<defs>',
    `<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="${c1}"/><stop offset="100%" stop-color="${c2}"/></linearGradient>`,
    '</defs>',
    '<rect width="64" height="64" rx="14" fill="url(#g)"/>',
    bgSymbol,
    `<text x="32" y="${initials.length > 2 ? 40 : 41}" text-anchor="middle" fill="white" font-family="Arial,Helvetica,sans-serif" font-size="${fontSize}" font-weight="bold">${initials}</text>`,
    '</svg>',
  ].join('');
}

const args = process.argv.slice(2);
const dataFlag = args.indexOf('--data');
const dataDir = dataFlag !== -1 && args[dataFlag + 1]
  ? path.resolve(args[dataFlag + 1])
  : path.resolve(import.meta.dirname, '..', 'public');

const { elements } = loadGameData(dataDir);
const outDir = path.join(dataDir, 'icons');
fs.mkdirSync(outDir, { recursive: true });

let created = 0;
let handcrafted = 0;

for (const el of Object.values(elements)) {
  const svg = createSvg(el);
  const slug = (el.group ?? 'Other').toLowerCase();
  const groupDir = path.join(outDir, slug);
  fs.mkdirSync(groupDir, { recursive: true });
  const filePath = path.join(groupDir, `${el.id}.svg`);
  fs.writeFileSync(filePath, svg);

  if (SYMBOL_PATHS[el.id]) handcrafted++;
  else created++;
}

console.log(`Icons: ${handcrafted} hand-crafted, ${created} generated.`);
console.log(`Total: ${handcrafted + created} icons in ${outDir}`);
