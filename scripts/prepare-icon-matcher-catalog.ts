import fs from 'node:fs';
import path from 'node:path';

interface ElementsIndex {
  buckets: Record<string, string>;
}

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function loadElementIds(dataDir: string): string[] {
  const groupedElementsIndexPath = path.join(dataDir, 'data', 'elements', 'index.json');
  if (fs.existsSync(groupedElementsIndexPath)) {
    const index = readJson<ElementsIndex>(groupedElementsIndexPath);
    const elementIds = new Set<string>();

    for (const bucketFile of Object.values(index.buckets)) {
      const bucketPath = path.join(dataDir, 'data', 'elements', 'by-group', bucketFile);
      if (!fs.existsSync(bucketPath)) continue;
      const bucket = readJson<Record<string, unknown>>(bucketPath);
      for (const key of Object.keys(bucket)) {
        elementIds.add(key);
      }
    }

    return Array.from(elementIds).sort();
  }

  const elementsIndexPath = path.join(dataDir, 'data', 'elements-index.json');
  if (fs.existsSync(elementsIndexPath)) {
    const index = readJson<ElementsIndex>(elementsIndexPath);
    const elementIds = new Set<string>();

    for (const bucketFile of Object.values(index.buckets)) {
      const bucketPath = path.join(dataDir, 'data', bucketFile);
      if (!fs.existsSync(bucketPath)) continue;
      const bucket = readJson<Record<string, unknown>>(bucketPath);
      for (const key of Object.keys(bucket)) {
        elementIds.add(key);
      }
    }

    return Array.from(elementIds).sort();
  }

  const elementsPath = path.join(dataDir, 'elements.json');
  const elements = readJson<Record<string, unknown>>(elementsPath);
  return Object.keys(elements).sort();
}

function main(): void {
  const dataDir = path.resolve(import.meta.dirname, '..', 'public');
  const matcherRoot = path.resolve(import.meta.dirname, '..', 'icon-matcher');
  const catalogDir = path.join(matcherRoot, 'elementalSrc');

  const elementIds = loadElementIds(dataDir);

  fs.mkdirSync(catalogDir, { recursive: true });

  const elementKeysPath = path.join(catalogDir, 'elementKeys.json');
  fs.writeFileSync(elementKeysPath, JSON.stringify(elementIds, null, 2) + '\n', 'utf8');

  console.log(`Wrote ${elementIds.length} element ids to ${elementKeysPath}`);
}

main();
