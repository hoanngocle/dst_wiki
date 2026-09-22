const test = require('node:test');
const assert = require('node:assert/strict');

const Catalog = require('./data.js');

test('ships all 71 current affixes from the runtime catalog', () => {
  const current = Catalog.rows.filter((row) => row.status === 'Đang có');
  assert.equal(current.length, 71);
});

test('gives every row a unique key and the fields required by the workbench', () => {
  const keys = new Set();
  for (const row of Catalog.rows) {
    assert.equal(typeof row.key, 'string');
    assert.ok(row.key.length > 0);
    assert.ok(!keys.has(row.key), `duplicate key: ${row.key}`);
    keys.add(row.key);
    for (const field of ['name', 'family', 'code', 'effectKey', 'tier', 'category', 'status', 'current', 'proposed']) {
      assert.equal(typeof row[field], 'string', `${row.key}.${field}`);
    }
  }
});

test('defines all five tiers for every tiered proposal family', () => {
  const proposals = Catalog.rows.filter((row) => row.status.startsWith('Đề xuất') && row.tier !== 'UTILITY');
  const byFamily = new Map();
  for (const row of proposals) {
    if (!byFamily.has(row.family)) byFamily.set(row.family, []);
    byFamily.get(row.family).push(row.tier);
  }
  assert.ok(byFamily.size >= 20);
  for (const [family, tiers] of byFamily) {
    assert.deepEqual([...tiers].sort(), ['I', 'II', 'III', 'IV', 'V'], family);
  }
});

test('keeps utility proposals in the gradient tier', () => {
  const utilities = Catalog.rows.filter((row) => row.status.startsWith('Đề xuất') && row.category === 'Tiện ích');
  assert.ok(utilities.length >= 7);
  assert.ok(utilities.every((row) => row.tier === 'UTILITY'));
});

test('contains no forbidden long dash in visible catalog copy', () => {
  const visible = JSON.stringify(Catalog.rows);
  assert.equal(visible.includes('—'), false);
  assert.equal(visible.includes('–'), false);
});
