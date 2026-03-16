import fs from 'node:fs';
import path from 'node:path';

interface MasterIndex {
  groups: Record<string, { elementCount: number; bucketCount: number }>;
}

interface GroupIndex {
  buckets: Record<string, string>;
  elementToBucket: Record<string, string>;
}

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function loadElementIds(dataDir: string): string[] {
  const masterIndexPath = path.join(dataDir, 'data', 'elements', 'index.json');
  if (fs.existsSync(masterIndexPath)) {
    const master = readJson<MasterIndex>(masterIndexPath);
    const elementIds = new Set<string>();

    for (const groupSlug of Object.keys(master.groups)) {
      const groupDir = path.join(dataDir, 'data', 'elements', 'by-group', groupSlug);
      const groupIndexPath = path.join(groupDir, 'index.json');
      if (!fs.existsSync(groupIndexPath)) continue;
      const groupIndex = readJson<GroupIndex>(groupIndexPath);

      for (const bucketFile of Object.values(groupIndex.buckets)) {
        const bucketPath = path.join(groupDir, bucketFile);
        if (!fs.existsSync(bucketPath)) continue;
        const bucket = readJson<Record<string, unknown>>(bucketPath);
        for (const key of Object.keys(bucket)) {
          elementIds.add(key);
        }
      }
    }

    return Array.from(elementIds).sort();
  }

  // Fallback: flat elements.json
  const elementsPath = path.join(dataDir, 'elements.json');
  if (fs.existsSync(elementsPath)) {
    const elements = readJson<Record<string, unknown>>(elementsPath);
    return Object.keys(elements).sort();
  }

  return [];
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
