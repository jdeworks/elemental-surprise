import { getAllAchievements } from '../services/achievements';
import './AchievementsModal.css';

interface AchievementsModalProps {
  unlocked: string[];
  onClose: () => void;
}

export function AchievementsModal({ unlocked, onClose }: AchievementsModalProps) {
  const all = getAllAchievements();
  const unlockedSet = new Set(unlocked);

  return (
    <>
      <div className="modal-backdrop" aria-hidden onClick={onClose} />
      <div className="modal achievements-modal" role="dialog" aria-modal="true">
        <div className="modal-header">
          <h2>
            Achievements
            <span className="modal-counter">
              ({unlocked.length}/{all.length})
            </span>
          </h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18" />
              <path d="M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="modal-body">
          <div className="achievements-grid">
            {all.map(a => {
              const isUnlocked = unlockedSet.has(a.id);
              return (
                <div key={a.id} className={`achievement-card ${isUnlocked ? 'unlocked' : 'locked'}`}>
                  <div className="achievement-icon">{isUnlocked ? a.icon : '🔒'}</div>
                  <div className="achievement-info">
                    <div className="achievement-name">{isUnlocked ? a.name : '???'}</div>
                    <div className="achievement-desc">{isUnlocked ? a.description : 'Keep playing to unlock'}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}
