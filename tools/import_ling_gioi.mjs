// Re-run with --fetch to refresh the authorized upstream snapshot and images.
import { readFile, writeFile, mkdir, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const base = 'https://eyanhuahu.github.io/lingjie/';
const root = new URL('../', import.meta.url);
const file = p => new URL(p, root);
await mkdir(file('app/data/ling-gioi/'), { recursive: true });
const snapshot = file('app/data/ling-gioi/source.json');
if (process.argv.includes('--fetch')) {
  const response = await fetch(base + 'data.json');
  if (!response.ok) throw new Error(`Source: ${response.status}`);
  await writeFile(snapshot, await response.text());
}
const raw = await readFile(snapshot, 'utf8');
const source = JSON.parse(raw);
const paths = [...new Set(raw.match(/images\/[\w./-]+\.(?:png|jpg|jpeg|gif|webp|svg)/g) || [])];
const assets = [];
for (const path of paths) {
  if (path.split('/').includes('..')) throw new Error(`Unsafe image path: ${path}`);
  const target = file('public/ling-gioi/' + path);
  let download = process.argv.includes('--fetch');
  try { await access(target); } catch { download = true; }
  if (download) {
    const response = await fetch(base + path);
    if (!response.ok) throw new Error(`Asset ${path}: ${response.status}`);
    await mkdir(new URL('.', target), { recursive: true });
    await writeFile(target, Buffer.from(await response.arrayBuffer()));
  }
  const bytes = await readFile(target);
  assets.push({ path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
}
await writeFile(file('app/data/ling-gioi/source-manifest.json'), JSON.stringify({
  url: base, importedAt: new Date().toISOString(), sourceSha256: createHash('sha256').update(raw).digest('hex'),
  permission: 'User confirmed author permission to republish and translate in this task.',
  sections: source.sections.length, items: source.items.length, assets,
}, null, 2) + '\n');
console.log(`Imported ${source.items.length} entries, ${source.sections.length} sections and ${assets.length} local assets.`);
