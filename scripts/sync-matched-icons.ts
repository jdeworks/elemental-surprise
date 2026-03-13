import fs from 'node:fs';
import path from 'node:path';

interface MatchReport {
  bySource?: Record<string, string[]>;
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

function copyMatchedIcons(sourceDir: string, targetDir: string): { copied: number; removed: number } {
  if (!fs.existsSync(sourceDir)) {
    throw new Error(`Matched icons directory not found: ${sourceDir}`);
  }

  fs.mkdirSync(targetDir, { recursive: true });

  const expectedFromReport = expectedSvgFilesFromReport(sourceDir);
  const sourceFiles = fs
    .readdirSync(sourceDir)
    .filter((name) => name.endsWith('.svg'))
    .filter((name) => (expectedFromReport ? expectedFromReport.has(name) : true));
  const sourceSet = new Set(sourceFiles);

  for (const fileName of sourceFiles) {
    const from = path.join(sourceDir, fileName);
    const to = path.join(targetDir, fileName);
    fs.copyFileSync(from, to);
  }

  let removed = 0;
  const targetFiles = fs.readdirSync(targetDir).filter((name) => name.endsWith('.svg'));
  for (const fileName of targetFiles) {
    if (!sourceSet.has(fileName)) {
      fs.unlinkSync(path.join(targetDir, fileName));
      removed += 1;
    }
  }

  return { copied: sourceFiles.length, removed };
}

function main(): void {
  const repoRoot = path.resolve(import.meta.dirname, '..');
  const sourceDir = path.join(repoRoot, 'icon-matcher', 'output', 'matched-icons');
  const targetDir = path.join(repoRoot, 'public', 'icons');
  const attributionDir = path.join(repoRoot, 'public', 'attribution');

  const result = copyMatchedIcons(sourceDir, targetDir);

  fs.mkdirSync(attributionDir, { recursive: true });
  copyFileIfExists(path.join(sourceDir, '_NOTICE.txt'), path.join(attributionDir, 'NOTICE.txt'));
  copyFileIfExists(path.join(sourceDir, '_attribution.json'), path.join(attributionDir, 'attribution.json'));
  copyFileIfExists(path.join(sourceDir, '_attribution-full.json'), path.join(attributionDir, 'attribution-full.json'));
  copyDirIfExists(path.join(sourceDir, '_licenses'), path.join(attributionDir, 'licenses'));

  console.log(`Copied ${result.copied} matched icons to ${targetDir}`);
  if (result.removed > 0) {
    console.log(`Removed ${result.removed} stale icons from ${targetDir}`);
  }
  console.log(`Updated attribution artifacts in ${attributionDir}`);
}

main();
