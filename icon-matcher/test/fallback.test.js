/**
 * Tests for fallback dictionary functionality
 * RED phase - these tests should fail until implementation is added
 */

const { getFallbackMatch, hasFallbackEntry } = require('../src/matchIcons');

describe('getFallbackMatch', () => {
  test('returns match for common game elements', () => {
    expect(getFallbackMatch('fire')).toBe('1F525');
    expect(getFallbackMatch('water')).toBe('1F4A7');
    expect(getFallbackMatch('earth')).toBe('1F30D');
    expect(getFallbackMatch('air')).toBe('1F32C');
  });

  test('returns match for technology elements', () => {
    expect(getFallbackMatch('robot')).toBe('1F916');
    expect(getFallbackMatch('ai')).toBe('1F916');
  });

  test('returns null for unknown elements', () => {
    expect(getFallbackMatch('xyzunknown')).toBeNull();
    expect(getFallbackMatch('randomword')).toBeNull();
  });

  test('handles case insensitive fallback', () => {
    expect(getFallbackMatch('FIRE')).toBe('1F525');
    expect(getFallbackMatch('Water')).toBe('1F4A7');
  });
});

describe('hasFallbackEntry', () => {
  test('returns true for fallback entries', () => {
    expect(hasFallbackEntry('fire')).toBe(true);
    expect(hasFallbackEntry('water')).toBe(true);
    expect(hasFallbackEntry('robot')).toBe(true);
  });

  test('returns false for non-fallback entries', () => {
    expect(hasFallbackEntry('random')).toBe(false);
    expect(hasFallbackEntry('xyz')).toBe(false);
  });
});

describe('fallback priority', () => {
  test('fallback is used when keyword match fails', () => {
    const { matchElement } = require('../src/matchIcons');
    const emojiIndex = {};
    const fallback = { fire: '1F525' };
    
    const result = matchElement('fire', emojiIndex, fallback);
    expect(result).toBeDefined();
    expect(result.code).toBe('1F525');
  });

  test('exact/keyword match takes priority over fallback', () => {
    const { matchElement } = require('../src/matchIcons');
    const emojiIndex = { fire: { emoji: '🔥', code: '1F525', keywords: ['flame'] } };
    const fallback = { fire: '1F3BE' };
    
    const result = matchElement('fire', emojiIndex, fallback);
    expect(result.code).toBe('1F525');
  });

  test('uses provided fallback dictionary argument', () => {
    const { matchElement } = require('../src/matchIcons');
    const result = matchElement('mycustom', {}, { mycustom: '1F600' });
    expect(result).toEqual({ code: '1F600' });
  });
});
