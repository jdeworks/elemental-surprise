import fs from 'node:fs';
import path from 'node:path';

interface MatchReport {
  bySource?: Record<string, string[]>;
}

interface MasterIndex {
  groups: Record<string, { elementCount: number; bucketCount: number }>;
}

interface GroupIndex {
  buckets: Record<string, string>;
  elementToBucket: Record<string, string>;
}

interface ElementDef {
  id: string;
  group?: string;
}

function copyFileIfExists(from: string, to: string): void {
  if (!fs.existsSync(from)) return;
  fs.mkdirSync(path.dirname(to), { recursive: true });
  fs.copyFileSync(from, to);
}

function copyDirIfExists(fromDir: string, toDir: string): void {
  if (!fs.existsSync(fromDir)) return;
  fs.mkdirSync(toDir, { recursive: true });
  for (const entry of fs.readdirSync(fromDir, { withFileTypes: true })) {
    const from = path.join(fromDir, entry.name);
    const to = path.join(toDir, entry.name);
    if (entry.isDirectory()) {
      copyDirIfExists(from, to);
    } else {
      fs.copyFileSync(from, to);
    }
  }
}

function expectedSvgFilesFromReport(sourceDir: string): Set<string> | null {
  const reportPath = path.join(sourceDir, '_report.json');
  if (!fs.existsSync(reportPath)) return null;

  const report = JSON.parse(fs.readFileSync(reportPath, 'utf8')) as MatchReport;
  const ids = new Set<string>();
  for (const sourceIds of Object.values(report.bySource ?? {})) {
    for (const id of sourceIds) {
      ids.add(`${id}.svg`);
    }
  }

  return ids.size > 0 ? ids : null;
}

/** Build a map of element ID → group slug by reading the hierarchical data. */
function loadElementGroups(dataDir: string): Map<string, string> {
  const map = new Map<string, string>();
  const masterPath = path.join(dataDir, 'data', 'elements', 'index.json');
  if (!fs.existsSync(masterPath)) return map;

  const master = JSON.parse(fs.readFileSync(masterPath, 'utf8')) as MasterIndex;
  for (const groupSlug of Object.keys(master.groups)) {
    const groupDir = path.join(dataDir, 'data', 'elements', 'by-group', groupSlug);
    const groupIndexPath = path.join(groupDir, 'index.json');
    if (!fs.existsSync(groupIndexPath)) continue;
    const groupIndex = JSON.parse(fs.readFileSync(groupIndexPath, 'utf8')) as GroupIndex;

    for (const bucketFile of Object.values(groupIndex.buckets)) {
      const bucketPath = path.join(groupDir, bucketFile);
      if (!fs.existsSync(bucketPath)) continue;
      const bucket = JSON.parse(fs.readFileSync(bucketPath, 'utf8')) as Record<string, ElementDef>;
      for (const [id, el] of Object.entries(bucket)) {
        const slug = (el.group || groupSlug).toLowerCase().replace(/\s+/g, '-');
        map.set(id, slug);
      }
    }
  }
  return map;
}

function copyMatchedIcons(
  sourceDir: string,
  targetDir: string,
  elementGroups: Map<string, string>,
): { copied: number; groupCopied: number } {
  if (!fs.existsSync(sourceDir)) {
    throw new Error(`Matched icons directory not found: ${sourceDir}`);
  }

  fs.mkdirSync(targetDir, { recursive: true });

  const expectedFromReport = expectedSvgFilesFromReport(sourceDir);
  const sourceFiles = fs
    .readdirSync(sourceDir)
    .filter((name) => name.endsWith('.svg'))
    .filter((name) => (expectedFromReport ? expectedFromReport.has(name) : true));

  let groupCopied = 0;

  for (const fileName of sourceFiles) {
    const from = path.join(sourceDir, fileName);
    const elementId = fileName.replace('.svg', '');

    // Copy to group subdirectory (primary — this is what elements reference)
    const groupSlug = elementGroups.get(elementId);
    if (groupSlug) {
      const groupDir = path.join(targetDir, groupSlug);
      fs.mkdirSync(groupDir, { recursive: true });
      fs.copyFileSync(from, path.join(groupDir, fileName));
      groupCopied++;
    }
  }

  return { copied: sourceFiles.length, groupCopied };
}

function main(): void {
  const repoRoot = path.resolve(import.meta.dirname, '..');
  const sourceDir = path.join(repoRoot, 'icon-matcher', 'output', 'matched-icons');
  const targetDir = path.join(repoRoot, 'public', 'icons');
  const dataDir = path.join(repoRoot, 'public');
  const attributionDir = path.join(repoRoot, 'public', 'attribution');

  const elementGroups = loadElementGroups(dataDir);
  console.log(`Loaded group info for ${elementGroups.size} elements`);

  const result = copyMatchedIcons(sourceDir, targetDir, elementGroups);

  fs.mkdirSync(attributionDir, { recursive: true });
  copyFileIfExists(path.join(sourceDir, '_NOTICE.txt'), path.join(attributionDir, 'NOTICE.txt'));
  copyFileIfExists(path.join(sourceDir, '_attribution.json'), path.join(attributionDir, 'attribution.json'));
  copyFileIfExists(path.join(sourceDir, '_attribution-full.json'), path.join(attributionDir, 'attribution-full.json'));
  copyDirIfExists(path.join(sourceDir, '_licenses'), path.join(attributionDir, 'licenses'));

  console.log(`Synced ${result.groupCopied} icons to group subdirectories in ${targetDir}`);
  console.log(`Updated attribution artifacts in ${attributionDir}`);
}

main();
