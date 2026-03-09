export function FireIcon({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="fireGrad" x1="32" y1="0" x2="32" y2="64">
          <stop offset="0%" stopColor="#FFDD00"/>
          <stop offset="50%" stopColor="#FF8800"/>
          <stop offset="100%" stopColor="#FF4400"/>
        </linearGradient>
      </defs>
      <path d="M32 4C32 4 20 20 20 32C20 44 26 52 32 60C38 52 44 44 44 32C44 20 32 4 32 4Z" fill="url(#fireGrad)"/>
      <path d="M32 16C32 16 26 24 26 32C26 38 28 42 32 46C36 42 38 38 38 32C38 24 32 16 32 16Z" fill="#FFFF88"/>
    </svg>
  );
}
