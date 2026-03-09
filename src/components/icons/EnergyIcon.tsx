export function EnergyIcon({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="energyGrad" x1="32" y1="0" x2="32" y2="64">
          <stop offset="0%" stopColor="#FFFF00"/>
          <stop offset="50%" stopColor="#FFAA00"/>
          <stop offset="100%" stopColor="#FF4400"/>
        </linearGradient>
      </defs>
      <polygon points="32,4 40,28 56,28 44,44 48,60 32,50 16,60 20,44 8,28 24,28" fill="url(#energyGrad)"/>
      <circle cx="32" cy="32" r="8" fill="#FFFF88" fillOpacity="0.6"/>
    </svg>
  );
}
