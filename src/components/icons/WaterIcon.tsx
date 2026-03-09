export function WaterIcon({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="waterGrad" x1="32" y1="0" x2="32" y2="64">
          <stop offset="0%" stopColor="#88DDFF"/>
          <stop offset="100%" stopColor="#0088FF"/>
        </linearGradient>
      </defs>
      <path d="M32 8C32 8 16 28 16 40C16 52 24 56 32 56C40 56 48 52 48 40C48 28 32 8 32 8Z" fill="url(#waterGrad)"/>
      <ellipse cx="24" cy="36" rx="4" ry="6" fill="white" fillOpacity="0.5"/>
    </svg>
  );
}
