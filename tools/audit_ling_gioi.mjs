import { readFile, writeFile } from 'node:fs/promises';
const root = new URL('../app/data/ling-gioi/', import.meta.url);
const read = async path => JSON.parse(await readFile(new URL(path, root), 'utf8'));
const source = await read('source.json');
const translations = (await Promise.all(['part-a.json', 'part-b.json', 'part-c.json'].map(read))).flat();
const findings = [];
const numbers = text => {
  const clean = text.replace(/\[\[(?:图片|image):[^\]]+\]\]|\[images\/[^\]]+\]/g, '');
  const counts = new Map();
  for (const match of clean.matchAll(/\d+(?:\.\d+)?/g)) counts.set(match[0], (counts.get(match[0]) || 0) + 1);
  return counts;
};
for (const entry of source.items) {
  const vi = translations.find(item => item.id === entry.id);
  if (!vi) { findings.push({ id: entry.id, issue: 'missing translation' }); continue; }
  for (const [original, translated] of [['简介', 'summary'], ['制作配方', 'recipe'], ['详情', 'details']]) {
    const expected = numbers(entry[original]);
    const actual = numbers(vi[translated]);
    const missing = [...expected].filter(([value, count]) => count > (actual.get(value) || 0));
    if (missing.length) findings.push({ id: entry.id, field: translated, missingNumericOccurrences: missing.map(([value, count]) => ({ value, source: count, translation: actual.get(value) || 0 })) });
  }
}
const report = { entries: translations.length, sourceEntries: source.items.length, findings };
await writeFile(new URL('../../../docs/ling-gioi-numeric-audit.json', root), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
if (translations.length !== source.items.length) process.exitCode = 1;
