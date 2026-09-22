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
  for (const family of byFamily.keys()) {
    const tiers = Catalog.rows
      .filter((row) => row.family === family && row.tier !== 'UTILITY')
      .map((row) => row.tier);
    assert.deepEqual([...new Set(tiers)].sort(), ['I', 'II', 'III', 'IV', 'V'], family);
  }
});

test('keeps utility proposals in the gradient tier', () => {
  const utilities = Catalog.rows.filter((row) => row.status.startsWith('Đề xuất') && row.category === 'Tiện ích');
  assert.ok(utilities.length >= 7);
  assert.ok(utilities.every((row) => row.tier === 'UTILITY'));
});

test('adds durability tiers III to V with the requested ranges', () => {
  const rows = Catalog.rows.filter((row) => row.family === 'Bền Bỉ');
  assert.deepEqual(
    rows.map((row) => [row.tier, row.proposed]),
    [
      ['I', '+20-80 độ bền'],
      ['II', '+40-160 độ bền'],
      ['III', '+120-280 độ bền'],
      ['IV', '+240-400 độ bền'],
      ['V', '+360-640 độ bền'],
    ],
  );
  assert.deepEqual(rows.slice(2).map((row) => row.status), [
    'Đề xuất - dùng ngay',
    'Đề xuất - dùng ngay',
    'Đề xuất - dùng ngay',
  ]);
});

test('splits critical rate and critical damage into five requested tiers', () => {
  const rate = Catalog.rows.filter((row) => row.family === 'Tỷ Lệ Bạo Kích');
  const damage = Catalog.rows.filter((row) => row.family === 'Sát Thương Bạo Kích');

  assert.deepEqual(rate.map((row) => row.proposed), ['1-5%', '3-10%', '5-15%', '10-20%', '15-30%']);
  assert.ok(rate.every((row) => row.effectKey === 'criticalHitRate' && row.cap === 'Tổng 100%'));
  assert.deepEqual(damage.map((row) => row.proposed), ['2-10%', '6-20%', '10-30%', '20-40%', '30-60%']);
  assert.ok(damage.every((row) => row.effectKey === 'criticalHitEffect' && row.cap === 'Không cap'));
});

test('contains no forbidden long dash in visible catalog copy', () => {
  const visible = JSON.stringify(Catalog.rows);
  assert.equal(visible.includes('—'), false);
  assert.equal(visible.includes('–'), false);
});
