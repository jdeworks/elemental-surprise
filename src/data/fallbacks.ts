// Funny fallback results for impossible combinations.
// These are cosmetic — they don't count as real discoveries.

export interface FallbackResult {
  name: string;
  reasoning: string;
}

const FALLBACK_ELEMENTS = [
  { name: 'Chaos', icon: 'chaos' },
  { name: 'Nothing Useful', icon: 'nothing' },
  { name: 'Confusion', icon: 'confusion' },
  { name: 'Bad Idea', icon: 'bad-idea' },
  { name: 'Mystery Goo', icon: 'goo' },
  { name: 'Awkward Silence', icon: 'silence' },
  { name: 'Oops', icon: 'oops' },
  { name: 'A Mess', icon: 'mess' },
  { name: 'Disappointment', icon: 'disappointment' },
  { name: 'Nope', icon: 'nope' },
] as const;

const REASONING_TEMPLATES = [
  'You combined {a} with {b}. The universe is confused.',
  '{a} and {b} stared at each other awkwardly. Nothing happened.',
  'The laws of physics politely declined this combination of {a} and {b}.',
  '{a} + {b} = ??? Even nature doesn\'t know what to do with this.',
  'Somewhere, a scientist just felt a chill. {a} and {b} don\'t mix.',
  '{a} looked at {b} and said "I don\'t think so."',
  'You tried to combine {a} with {b}. Reality said no.',
  'The combination of {a} and {b} produced only existential dread.',
  '{a} and {b} briefly formed something, then it vanished in a puff of logic.',
  'Nice try! But {a} and {b} are just not compatible.',
];

/** Simple deterministic hash for a pair of strings. */
function hashPair(a: string, b: string): number {
  const key = [a, b].sort().join('+');
  let hash = 0;
  for (let i = 0; i < key.length; i++) {
    hash = ((hash << 5) - hash + key.charCodeAt(i)) | 0;
  }
  return Math.abs(hash);
}

/** Get a funny fallback result for an impossible combination. */
export function getFallbackResult(aId: string, bId: string, aName: string, bName: string): FallbackResult {
  const hash = hashPair(aId, bId);
  const element = FALLBACK_ELEMENTS[hash % FALLBACK_ELEMENTS.length];
  const template = REASONING_TEMPLATES[hash % REASONING_TEMPLATES.length];
  return {
    name: element.name,
    reasoning: template.replace(/\{a\}/g, aName).replace(/\{b\}/g, bName),
  };
}
