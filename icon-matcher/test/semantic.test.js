/**
 * Tests for semantic matching functionality
 * RED phase - these tests should fail until implementation is added
 * Note: Semantic matching is opt-in via --semantic flag
 */

const { findBestMatch, isSemanticEnabled } = require('../src/semanticMatcher');

describe('findBestMatch', () => {
  test('returns best match from candidates', () => {
    const candidates = [
      { key: 'fire', emoji: '🔥', keywords: ['flame', 'hot'] },
      { key: 'water', emoji: '💧', keywords: ['liquid', 'wet'] },
      { key: 'earth', emoji: '🌍', keywords: ['planet', 'ground'] }
    ];
    
    const result = findBestMatch('flame', candidates);
    expect(result).toBeDefined();
    expect(result.key).toBe('fire');
  });

  test('returns null for empty candidates', () => {
    const result = findBestMatch('test', []);
    expect(result).toBeNull();
  });

  test('handles similar concepts', () => {
    const candidates = [
      { key: 'magic', emoji: '✨', keywords: ['sparkle', 'magic'] },
      { key: 'star', emoji: '⭐', keywords: ['star', 'night'] }
    ];
    
    const result = findBestMatch('spell', candidates);
    expect(result).toBeDefined();
    expect(result.key).toBe('magic');
  });

  test('returns null when no reasonable match exists', () => {
    const candidates = [
      { key: 'fire', emoji: '🔥', keywords: ['flame'] },
      { key: 'water', emoji: '💧', keywords: ['liquid'] }
    ];
    
    const result = findBestMatch('zzzznonexistent', candidates);
    expect(result).toBeNull();
  });
});

describe('isSemanticEnabled', () => {
  test('returns false by default', () => {
    expect(isSemanticEnabled()).toBe(false);
  });

  test('returns true when enabled', () => {
    const { enableSemantic } = require('../src/semanticMatcher');
    enableSemantic();
    expect(isSemanticEnabled()).toBe(true);
  });
});

describe('semantic matching threshold', () => {
  test('respects similarity threshold', () => {
    const candidates = [
      { key: 'fire', emoji: '🔥', keywords: ['hot'] },
      { key: 'cold', emoji: '❄️', keywords: ['ice'] }
    ];
    
    const result = findBestMatch('hot', candidates, 0.8);
    expect(result).toBeDefined();
    expect(result.key).toBe('fire');
  });

  test('returns null below threshold', () => {
    const candidates = [
      { key: 'fire', emoji: '🔥', keywords: ['hot'] },
      { key: 'cold', emoji: '❄️', keywords: ['ice'] }
    ];
    
    const result = findBestMatch('unrelatedword', candidates, 0.5);
    expect(result).toBeNull();
  });
});
