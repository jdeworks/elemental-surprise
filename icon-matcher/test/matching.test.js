/**
 * Tests for element matching functionality
 * RED phase - these tests should fail until implementation is added
 */

const { findExactMatch, findKeywordMatch, matchElement } = require('../src/matchIcons');
const emojiIndex = require('../data/emoji-index.json');

describe('findExactMatch', () => {
  test('matches exact element name', () => {
    const result = findExactMatch('fire', emojiIndex);
    expect(result).toBeDefined();
    expect(result.emoji).toBe('🔥');
  });

  test('returns null for non-existent element', () => {
    const result = findExactMatch('nonexistentxyz', emojiIndex);
    expect(result).toBeNull();
  });

  test('is case insensitive', () => {
    const result1 = findExactMatch('fire', emojiIndex);
    const result2 = findExactMatch('FIRE', emojiIndex);
    const result3 = findExactMatch('Fire', emojiIndex);
    expect(result1).toEqual(result2);
    expect(result2).toEqual(result3);
  });
});

describe('findKeywordMatch', () => {
  test('finds match by keyword', () => {
    const result = findKeywordMatch('flame', emojiIndex);
    expect(result).toBeDefined();
    expect(result.emoji).toBe('🔥');
  });

  test('returns null when no keyword matches', () => {
    const result = findKeywordMatch('xyznotfound', emojiIndex);
    expect(result).toBeNull();
  });

  test('matches partial keywords', () => {
    const result = findKeywordMatch('wat', emojiIndex);
    expect(result).toBeDefined();
    // "wat" prefix-matches "water"; any water-related emoji is acceptable
    expect(result.keywords).toBeDefined();
    expect(result.keywords.some(k => k === 'water')).toBe(true);
  });
});

describe('matchElement', () => {
  test('uses exact match first', () => {
    const result = matchElement('fire', emojiIndex, {});
    expect(result).toBeDefined();
    expect(result.emoji).toBe('🔥');
  });

  test('falls back to keyword match', () => {
    const result = matchElement('flame', emojiIndex, {});
    expect(result).toBeDefined();
    expect(result.emoji).toBe('🔥');
  });

  test('returns null when no match found', () => {
    const result = matchElement('xyznotmatching', emojiIndex, {});
    expect(result).toBeNull();
  });

  test('handles normalized input', () => {
    const result1 = matchElement('  fire  ', emojiIndex, {});
    const result2 = matchElement('fire', emojiIndex, {});
    expect(result1).toEqual(result2);
  });
});
