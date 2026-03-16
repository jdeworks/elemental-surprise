import { useState, useEffect, useRef } from 'react';

export interface LoadingProgress {
  phase: string;
  loaded: number;
  total: number;
}

export function LoadingBar({ progress }: { progress: LoadingProgress | null }) {
  const [smoothPct, setSmoothPct] = useState(0);
  const rafRef = useRef<number>(0);

  const targetPct = progress ? Math.round((progress.loaded / Math.max(progress.total, 1)) * 100) : 0;

  useEffect(() => {
    // Smoothly animate towards target
    const animate = () => {
      setSmoothPct(prev => {
        if (prev >= targetPct) return targetPct;
        return prev + Math.max(1, Math.ceil((targetPct - prev) * 0.15));
      });
      rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  }, [targetPct]);

  return (
    <div className="loading-screen">
      <h1>Elemental Surprise</h1>
      <div className="loading-bar-container">
        <div className="loading-bar-fill" style={{ width: `${smoothPct}%` }} />
      </div>
      <p className="loading-phase">
        {progress ? progress.phase : 'Initializing...'}
        {progress && progress.total > 0 && (
          <span className="loading-count"> ({progress.loaded}/{progress.total})</span>
        )}
      </p>
    </div>
  );
}
