import { useCallback, useEffect, useRef, useState } from 'react';
import type { WorkspaceElement } from '../services/storage';
import { hasRecipe, getAllRecipeKeysFromIndex, ensureRecipeBucketForKey, preloadRecipeBucketsForGroups, getElement, getRecipeReasoning } from '../data/loader';

export type AutoSolveSpeed = 'fast' | 'slow';

export interface AutoSolverConfig {
  active: boolean;
  paused: boolean;
  speed: AutoSolveSpeed;
  workspaceElements: WorkspaceElement[];
  discovered: string[];
  discoveredRecipes: string[];
  /** Move element A to element B's position (triggers CSS animation). */
  onMoveElement: (elementId: string, toX: number, toY: number) => void;
  /** Combine two workspace elements. Returns result type or null. */
  onCombine: (elementA: WorkspaceElement, elementB: WorkspaceElement) => Promise<string | null>;
  /** Spawn an element onto the workspace. */
  onSpawn: (type: string) => void;
}

export interface AutoSolverState {
  phase: 'idle' | 'searching' | 'moving' | 'combining' | 'spawning' | 'done';
  movingId: string | null;
  targetId: string | null;
  /** In slow mode, the reasoning text for the last combine (null otherwise). */
  lastReasoning: string | null;
}

const TIMING = {
  fast: { move: 400, postCombine: 200, spawn: 150 },
  slow: { move: 900, postCombine: 2500, spawn: 400 },
} as const;

export function useAutoSolver(config: AutoSolverConfig): AutoSolverState {
  const [phase, setPhase] = useState<AutoSolverState['phase']>('idle');
  const [movingId, setMovingId] = useState<string | null>(null);
  const [targetId, setTargetId] = useState<string | null>(null);
  const [lastReasoning, setLastReasoning] = useState<string | null>(null);

  // Refs for stable access inside async loop
  const activeRef = useRef(config.active);
  const pausedRef = useRef(config.paused);
  const speedRef = useRef(config.speed);
  const wsRef = useRef(config.workspaceElements);
  const discoveredRef = useRef(config.discovered);
  const recipesRef = useRef(config.discoveredRecipes);
  const onMoveRef = useRef(config.onMoveElement);
  const onCombineRef = useRef(config.onCombine);
  const onSpawnRef = useRef(config.onSpawn);

  activeRef.current = config.active;
  pausedRef.current = config.paused;
  speedRef.current = config.speed;
  wsRef.current = config.workspaceElements;
  discoveredRef.current = config.discovered;
  recipesRef.current = config.discoveredRecipes;
  onMoveRef.current = config.onMoveElement;
  onCombineRef.current = config.onCombine;
  onSpawnRef.current = config.onSpawn;

  // Preload recipe buckets when solver starts
  useEffect(() => {
    if (!config.active) return;
    const groups = new Set<string>();
    for (const id of config.discovered) {
      const el = getElement(id);
      if (el?.group) groups.add(el.group);
    }
    if (groups.size > 0) {
      preloadRecipeBucketsForGroups([...groups]).catch(() => {});
    }
  }, [config.active, config.discovered]);

  const findPairOnWorkspace = useCallback((): [WorkspaceElement, WorkspaceElement] | null => {
    const elements = wsRef.current;
    const knownRecipes = new Set(recipesRef.current);

    // Only pick pairs with undiscovered recipes — skip already-known combinations
    for (let i = 0; i < elements.length; i++) {
      for (let j = i + 1; j < elements.length; j++) {
        const a = elements[i], b = elements[j];
        if (!hasRecipe(a.type, b.type)) continue;
        const key = [a.type, b.type].sort().join('+');
        if (!knownRecipes.has(key)) return [a, b];
      }
    }
    return null;
  }, []);

  const findFrontierPair = useCallback((): [string, string] | null => {
    const disc = new Set(discoveredRef.current);
    const knownRecipes = new Set(recipesRef.current);
    // Use combo indexes (loaded at startup) to find ALL recipe keys,
    // not just recipes from loaded buckets
    const allKeys = getAllRecipeKeysFromIndex();
    const candidates: [string, string][] = [];

    for (const key of allKeys) {
      if (knownRecipes.has(key)) continue;
      const [a, b] = key.split('+');
      if (disc.has(a) && disc.has(b)) {
        candidates.push([a, b]);
      }
    }
    if (candidates.length === 0) return null;
    return candidates[Math.floor(Math.random() * candidates.length)];
  }, []);

  useEffect(() => {
    if (!config.active) {
      setPhase('idle');
      setMovingId(null);
      setTargetId(null);
      return;
    }

    let cancelled = false;
    const delay = (ms: number) => new Promise<void>(resolve => {
      const t = setTimeout(resolve, ms);
      // Allow early exit on cancel
      const id = setInterval(() => { if (cancelled) { clearTimeout(t); clearInterval(id); resolve(); } }, 50);
    });

    const waitUnpaused = async () => {
      while (pausedRef.current && !cancelled) await delay(150);
    };

    const loop = async () => {
      while (!cancelled && activeRef.current) {
        await waitUnpaused();
        if (cancelled) break;

        const t = TIMING[speedRef.current];

        setPhase('searching');
        setLastReasoning(null);
        const pair = findPairOnWorkspace();

        if (pair) {
          const [a, b] = pair;
          const origX = a.x;
          const origY = a.y;

          // Animate: move A toward B
          setPhase('moving');
          setMovingId(a.id);
          setTargetId(b.id);
          onMoveRef.current(a.id, b.x, b.y);

          await delay(t.move);
          if (cancelled) break;

          // Combine
          setPhase('combining');
          setMovingId(null);
          setTargetId(null);

          // Re-lookup from current state (may have shifted)
          const curWs = wsRef.current;
          const curA = curWs.find(e => e.id === a.id);
          const curB = curWs.find(e => e.id === b.id);
          if (curA && curB) {
            // In slow mode, show reasoning after combine
            const recipeKey = [curA.type, curB.type].sort().join('+');
            const result = await onCombineRef.current(curA, curB);
            if (!result) {
              // Combine failed — move A back to original position
              onMoveRef.current(a.id, origX, origY);
              await delay(300);
            } else if (speedRef.current === 'slow') {
              const reasoning = getRecipeReasoning(recipeKey);
              if (reasoning) {
                setLastReasoning(reasoning);
              }
            }
          }

          await delay(t.postCombine);
        } else {
          // Nothing combinable on board — spawn a frontier pair
          setPhase('spawning');
          const fp = findFrontierPair();
          if (!fp) {
            setPhase('done');
            break;
          }
          // Clear workspace if it's getting cluttered
          if (wsRef.current.length > 30) {
            // We can't clear from here — just spawn and let results pile up
            // The user can clear manually
          }
          // Preload the recipe bucket so hasRecipe() works for the spawned pair
          const fpKey = [fp[0], fp[1]].sort().join('+');
          await ensureRecipeBucketForKey(fpKey);
          if (cancelled) break;
          onSpawnRef.current(fp[0]);
          await delay(t.spawn);
          if (cancelled) break;
          onSpawnRef.current(fp[1]);
          await delay(t.spawn);
        }
      }
    };

    loop();
    return () => { cancelled = true; };
  }, [config.active, findPairOnWorkspace, findFrontierPair]);

  return { phase, movingId, targetId, lastReasoning };
}
