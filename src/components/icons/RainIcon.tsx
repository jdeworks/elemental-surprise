export function RainIcon({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="rainCloud" x1="32" y1="0" x2="32" y2="32">
          <stop offset="0%" stopColor="#FFFFFF"/>
          <stop offset="100%" stopColor="#AADDEE"/>
        </linearGradient>
      </defs>
      <ellipse cx="32" cy="16" rx="24" ry="12" fill="url(#rainCloud)"/>
      <line x1="20" y1="28" x2="16" y2="44" stroke="#4488CC" strokeWidth="3" strokeLinecap="round"/>
      <line x1="32" y1="28" x2="32" y2="48" stroke="#4488CC" strokeWidth="3" strokeLinecap="round"/>
      <line x1="44" y1="28" x2="48" y2="44" stroke="#4488CC" strokeWidth="3" strokeLinecap="round"/>
      <line x1="26" y1="30" x2="24" y2="40" stroke="#6699CC" strokeWidth="2" strokeLinecap="round"/>
      <line x1="38" y1="30" x2="40" y2="42" stroke="#6699CC" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}
