import { useState, useEffect } from 'react';
import { toPublicUrl } from '../data/loader';

interface SaveStateEntry {
  id: string;
  name: string;
  description: string;
  elementCount: number;
  recipeCount: number;
  tags: string[];
}

interface SaveStateData {
  discovered: string[];
  discoveredRecipes: string[];
  lastUsed: Record<string, number>;
  workspace: { id: string; type: string; x: number; y: number }[];
}

const TAG_LABELS: Record<string, string> = {
  milestones: 'Milestones',
  groups: 'Groups',
  themed: 'Themed',
};

export function SaveStateBrowser({
  onLoad,
  onClose,
}: {
  onLoad: (data: SaveStateData) => void;
  onClose: () => void;
}) {
  const [entries, setEntries] = useState<SaveStateEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [activeTag, setActiveTag] = useState<string | null>(null);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    fetch(toPublicUrl('./savestates/index.json'))
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: SaveStateEntry[]) => {
        setEntries(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const lowerSearch = search.toLowerCase();
  const filtered = entries.filter((e) => {
    if (activeTag && !e.tags.includes(activeTag)) return false;
    if (search) {
      const text = `${e.name} ${e.description}`.toLowerCase();
      if (!text.includes(lowerSearch)) return false;
    }
    return true;
  });

  const allTags = [...new Set(entries.flatMap((e) => e.tags))];

  const handleConfirm = async (id: string) => {
    setApplying(true);
    try {
      const resp = await fetch(toPublicUrl(`./savestates/save-${id}.json`));
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: SaveStateData = await resp.json();
      onLoad(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setApplying(false);
      setConfirmId(null);
    }
  };

  return (
    <>
      <div className="modal-backdrop" aria-hidden onClick={onClose} />
      <div
        className="modal save-state-modal"
        role="dialog"
        aria-labelledby="save-state-modal-title"
        aria-modal="true"
      >
        <div className="modal-header">
          <h2 id="save-state-modal-title">Save State Presets</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 6L6 18" />
              <path d="M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="save-state-controls">
          <input
            type="text"
            placeholder="Search save states..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="save-state-search"
          />
          <div className="save-state-tags">
            <button
              type="button"
              className={`save-state-tag ${activeTag === null ? 'active' : ''}`}
              onClick={() => setActiveTag(null)}
            >
              All
            </button>
            {allTags.map((tag) => (
              <button
                key={tag}
                type="button"
                className={`save-state-tag ${activeTag === tag ? 'active' : ''}`}
                onClick={() => setActiveTag(activeTag === tag ? null : tag)}
              >
                {TAG_LABELS[tag] || tag}
              </button>
            ))}
          </div>
        </div>

        <div className="modal-body">
          {loading && <p className="modal-empty">Loading save states...</p>}
          {error && <p className="modal-empty" style={{ color: '#f44' }}>Error: {error}</p>}
          {!loading && !error && filtered.length === 0 && (
            <p className="modal-empty">No save states match your search.</p>
          )}
          {!loading && !error && (
            <div className="save-state-list">
              {filtered.map((entry) => (
                <div key={entry.id} className="save-state-card">
                  {confirmId === entry.id ? (
                    <div className="save-state-confirm">
                      <p>Replace your current progress with <strong>{entry.name}</strong>?</p>
                      <div className="save-state-confirm-actions">
                        <button
                          type="button"
                          className="save-state-confirm-btn save-state-confirm-yes"
                          onClick={() => handleConfirm(entry.id)}
                          disabled={applying}
                        >
                          {applying ? 'Loading...' : 'Yes, load it'}
                        </button>
                        <button
                          type="button"
                          className="save-state-confirm-btn save-state-confirm-no"
                          onClick={() => setConfirmId(null)}
                          disabled={applying}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      type="button"
                      className="save-state-card-btn"
                      onClick={() => setConfirmId(entry.id)}
                    >
                      <div className="save-state-card-header">
                        <span className="save-state-card-name">{entry.name}</span>
                        <span className="save-state-card-counts">
                          {entry.elementCount} elements
                        </span>
                      </div>
                      <p className="save-state-card-desc">{entry.description}</p>
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="save-state-warning">
          Loading a save replaces your current progress.
        </div>
      </div>
    </>
  );
}
