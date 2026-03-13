/**
 * Tests for element normalization
 * RED phase - these tests should fail until implementation is added
 */

const { normalizeElement, normalizeUnicode, emojiToCodepoint } = require('../src/utils');

describe('normalizeElement', () => {
  test('converts to lowercase', () => {
    expect(normalizeElement('FIRE')).toBe('fire');
    expect(normalizeElement('Fire')).toBe('fire');
    expect(normalizeElement('fIrE')).toBe('fire');
  });

  test('trims whitespace', () => {
    expect(normalizeElement('  fire')).toBe('fire');
    expect(normalizeElement('fire  ')).toBe('fire');
    expect(normalizeElement('  fire  ')).toBe('fire');
  });

  test('removes special characters', () => {
    expect(normalizeElement('fire!')).toBe('fire');
    expect(normalizeElement('fire@')).toBe('fire');
    expect(normalizeElement('fire#')).toBe('fire');
    expect(normalizeElement('f.i.r.e')).toBe('fire');
    expect(normalizeElement('fire-')).toBe('fire');
    expect(normalizeElement('fire_')).toBe('fire');
  });

  test('handles multiple special characters', () => {
    expect(normalizeElement('  Fire!@#  ')).toBe('fire');
    expect(normalizeElement('f-i-r-e!')).toBe('fire');
  });

  test('handles empty or whitespace-only input', () => {
    expect(normalizeElement('')).toBe('');
    expect(normalizeElement('   ')).toBe('');
  });

  test('preserves valid alphanumeric strings', () => {
    expect(normalizeElement('robot2')).toBe('robot2');
    expect(normalizeElement('level5')).toBe('level5');
  });
});

describe('normalizeUnicode', () => {
  test('applies NFC normalization', () => {
    // Test with accented characters
    expect(normalizeUnicode('café')).toBe('café');
    // Test with composed vs decomposed forms
    expect(normalizeUnicode('e\u0301')).toBe('\u00e9');
  });

  test('handles emoji characters', () => {
    expect(normalizeUnicode('🔥')).toBe('🔥');
    expect(normalizeUnicode('💧')).toBe('💧');
  });
});

describe('emojiToCodepoint', () => {
  test('converts single emoji to hex codepoint', () => {
    expect(emojiToCodepoint('🔥')).toBe('1F525');
    expect(emojiToCodepoint('💧')).toBe('1F4A7');
    expect(emojiToCodepoint('🌍')).toBe('1F30D');
  });

  test('converts multiple codepoints for ZWJ sequences', () => {
    // Family emoji
    expect(emojiToCodepoint('👨‍👩‍👧‍👦')).toContain('1F468');
  });

  test('returns undefined for non-emoji', () => {
    expect(emojiToCodepoint('a')).toBeUndefined();
    expect(emojiToCodepoint('!')).toBeUndefined();
  });
});
