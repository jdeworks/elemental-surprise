import './Tutorial.css';

const STEPS = [
  {
    title: 'Welcome to Elemental Surprise!',
    text: 'Combine elements to discover new ones. Start with Fire, Water, Earth, and Wind.',
  },
  {
    title: 'Spawn Elements',
    text: 'Click any element in the sidebar to add it to your workspace.',
  },
  {
    title: 'Combine Elements',
    text: 'Drag one element onto another in the workspace. Green means a new discovery, grey means already found, red means no recipe.',
  },
  {
    title: 'Get Hints',
    text: 'Stuck? Click the "Hint" button to highlight two elements you can combine for a new discovery.',
  },
];

interface TutorialProps {
  onClose: () => void;
}

export function Tutorial({ onClose }: TutorialProps) {
  return (
    <>
      <div className="tutorial-backdrop" onClick={onClose} />
      <div className="tutorial-modal" role="dialog" aria-modal="true">
        <div className="tutorial-header">
          <h2>How to Play</h2>
          <button type="button" className="tutorial-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18" />
              <path d="M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="tutorial-body">
          {STEPS.map((step, i) => (
            <div key={i} className="tutorial-step">
              <div className="tutorial-step-number">{i + 1}</div>
              <div>
                <strong>{step.title}</strong>
                <p>{step.text}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="tutorial-footer">
          <button type="button" className="tutorial-start-btn" onClick={onClose}>
            Start Playing
          </button>
        </div>
      </div>
    </>
  );
}
