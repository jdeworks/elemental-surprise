export function SteamIcon({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="steamGrad" x1="32" y1="0" x2="32" y2="64">
          <stop offset="0%" stopColor="#FFFFFF"/>
          <stop offset="100%" stopColor="#CCCCCC"/>
        </linearGradient>
      </defs>
      <ellipse cx="20" cy="44" rx="8" ry="12" fill="url(#steamGrad)" fillOpacity="0.7"/>
      <ellipse cx="32" cy="40" rx="8" ry="14" fill="url(#steamGrad)" fillOpacity="0.8"/>
      <ellipse cx="44" cy="44" rx="8" ry="12" fill="url(#steamGrad)" fillOpacity="0.7"/>
      <ellipse cx="26" cy="28" rx="6" ry="10" fill="url(#steamGrad)" fillOpacity="0.5"/>
      <ellipse cx="38" cy="28" rx="6" ry="10" fill="url(#steamGrad)" fillOpacity="0.5"/>
    </svg>
  );
}
