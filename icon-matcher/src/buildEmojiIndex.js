const fs = require('fs');
const path = require('path');
const { normalizeElement, emojiToCodepoint } = require('./utils');

function loadEmojiData() {
  try {
    const emojisData = require('emojilib');
    const unicodeEmojiData = require('unicode-emoji-json');
    return { emojisData, unicodeEmojiData, source: 'npm-packages' };
  } catch (_) {
    const emojisPath = path.join(__dirname, '../data/emojis.json');
    const unicodeEmojiPath = path.join(__dirname, '../data/unicode-emoji.json');
    const emojisData = JSON.parse(fs.readFileSync(emojisPath, 'utf8'));
    const unicodeEmojiData = JSON.parse(fs.readFileSync(unicodeEmojiPath, 'utf8'));
    return { emojisData, unicodeEmojiData, source: 'data-files' };
  }
}

function buildEmojiIndex(preloaded) {
  const { emojisData, unicodeEmojiData } = preloaded || loadEmojiData();
  const index = {};
  const emojiDataList = [];
  
  for (const [emoji, keywords] of Object.entries(emojisData)) {
    const codepoint = emojiToCodepoint(emoji);
    if (!codepoint) continue;
    
    const unicodeInfo = unicodeEmojiData[emoji];
    const name = unicodeInfo ? unicodeInfo.slug : keywords[0];
    
    emojiDataList.push({
      emoji,
      code: codepoint,
      keywords: [...new Set([name, ...keywords])],
      name,
      nameLen: name.length,
      isSingleWord: !name.includes('_')
    });
  }
  
  emojiDataList.sort((a, b) => {
    if (a.isSingleWord !== b.isSingleWord) return b.isSingleWord - a.isSingleWord;
    return a.nameLen - b.nameLen;
  });
  
  const seenKeys = new Set();
  
  for (const data of emojiDataList) {
    const primaryName = normalizeElement(data.name);
    
    if (primaryName && !seenKeys.has(primaryName)) {
      index[primaryName] = {
        emoji: data.emoji,
        code: data.code,
        keywords: data.keywords.map(k => normalizeElement(k)).filter(k => k),
        name: data.name
      };
      seenKeys.add(primaryName);
    }
    
    for (const keyword of data.keywords) {
      const normalizedKeyword = normalizeElement(keyword);
      if (normalizedKeyword && !seenKeys.has(normalizedKeyword)) {
        index[normalizedKeyword] = {
          emoji: data.emoji,
          code: data.code,
          keywords: data.keywords.map(k => normalizeElement(k)).filter(k => k),
          name: data.name
        };
        seenKeys.add(normalizedKeyword);
      }
    }
  }
  
  return index;
}

/**
 * Save index to file
 */
function saveIndex() {
  const { emojisData, unicodeEmojiData, source } = loadEmojiData();
  const index = buildEmojiIndex({ emojisData, unicodeEmojiData });
  const dataDir = path.join(__dirname, '../data');
  if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

  const emojisPath = path.join(dataDir, 'emojis.json');
  const unicodeEmojiPath = path.join(dataDir, 'unicode-emoji.json');
  const outputPath = path.join(__dirname, '../data/emoji-index.json');

  fs.writeFileSync(emojisPath, JSON.stringify(emojisData, null, 2));
  fs.writeFileSync(unicodeEmojiPath, JSON.stringify(unicodeEmojiData, null, 2));
  fs.writeFileSync(outputPath, JSON.stringify(index, null, 2));

  console.log(`Emoji source: ${source}`);
  console.log(`Wrote ${emojisPath}`);
  console.log(`Wrote ${unicodeEmojiPath}`);
  console.log(`Emoji index saved to ${outputPath}`);
  console.log(`Total entries: ${Object.keys(index).length}`);
}

// Run if executed directly
if (require.main === module) {
  saveIndex();
}

module.exports = {
  buildEmojiIndex,
  loadEmojiData
};
