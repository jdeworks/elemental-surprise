export function WindIcon({ size = 32 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M8 24H48" stroke="#88CCEE" strokeWidth="4" strokeLinecap="round"/>
      <path d="M16 32H44" stroke="#AAEEFF" strokeWidth="3" strokeLinecap="round"/>
      <path d="M12 40H40" stroke="#88CCEE" strokeWidth="4" strokeLinecap="round"/>
      <circle cx="52" cy="16" r="4" fill="#AAEEFF" fillOpacity="0.6"/>
      <circle cx="56" cy="28" r="3" fill="#AAEEFF" fillOpacity="0.4"/>
      <circle cx="50" cy="44" r="5" fill="#AAEEFF" fillOpacity="0.5"/>
    </svg>
  );
}
