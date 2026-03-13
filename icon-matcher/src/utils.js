/**
 * Utility functions for emoji matching
 */

/**
 * Normalize an element name: lowercase, trim, remove special characters
 * @param {string} element - The element string to normalize
 * @returns {string} - Normalized string
 */
function normalizeElement(element) {
  if (!element) return '';
  
  return element
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s]/g, '');
}

/**
 * Normalize Unicode string using NFC normalization
 * @param {string} codepoint - The Unicode string to normalize
 * @returns {string} - NFC normalized string
 */
function normalizeUnicode(codepoint) {
  if (!codepoint) return '';
  
  // Use Unicode NFC normalization
  return codepoint.normalize('NFC');
}

/**
 * Convert emoji to uppercase hex codepoint(s)
 * @param {string} emoji - The emoji character(s)
 * @returns {string|undefined} - Uppercase hex codepoint(s) or undefined if not emoji
 */
function emojiToCodepoint(emoji) {
  if (!emoji) return undefined;
  
  // Get codepoints from the string
  const codepoints = [...emoji];
  
  // Check if it's actually an emoji by checking if any codepoint is in emoji range
  // Emojis are typically in ranges above U+2000 or are specific emoji characters
  const hasEmoji = codepoints.some(cp => {
    const code = cp.codePointAt(0);
    // Check for emoji ranges or specific emoji characters
    return (
      code >= 0x2000 || // Miscellaneous symbols
      code >= 0xFE00 && code <= 0xFE0F || // Variation selectors
      (code >= 0x1F300 && code <= 0x1F9FF) || // Emoticons, Misc Symbols, Transport/Map, Flags, Emoji
      (code >= 0x1F600 && code <= 0x1F64F) || // Emoticons
      (code >= 0x1F680 && code <= 0x1F6FF) || // Transport
      (code >= 0x2600 && code <= 0x26FF) || // Misc symbols
      (code >= 0x2700 && code <= 0x27BF) || // Dingbats
      cp === '️' // Variation selector-16
    );
  });
  
  if (!hasEmoji) return undefined;
  
  // Convert to uppercase hex codepoints
  return codepoints
    .map(cp => cp.codePointAt(0).toString(16).toUpperCase())
    .join('-');
}

module.exports = {
  normalizeElement,
  normalizeUnicode,
  emojiToCodepoint
};
