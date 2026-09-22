const test = require('node:test');
const assert = require('node:assert/strict');

const View = require('./view.js');

test('maps tiers to semantic classes including utility gradient', () => {
  assert.equal(View.tierClass('I'), 'tier-i');
  assert.equal(View.tierClass('V'), 'tier-v');
  assert.equal(View.tierClass('UTILITY'), 'tier-utility');
  assert.equal(View.tierClass('unknown'), 'tier-none');
});

test('escapes catalog copy before rendering editable table rows', () => {
  const html = View.renderRow({
    key: 'unsafe',
    numericId: '1',
    name: '<img src=x onerror=alert(1)>',
    family: 'Test',
    code: 'test_code',
    effectKey: 'testEffect',
    tier: 'I',
    category: 'Tấn công',
    slot: 'Vũ khí',
    status: 'Đề xuất - adapter',
    current: 'Chưa có',
    proposed: '5%',
    cap: '10%',
    exclusiveGroup: '',
    source: 'source.lua',
    decision: 'Đánh giá',
    note: 'Ghi chú',
  });

  assert.ok(!html.includes('<img'));
  assert.ok(html.includes('&lt;img'));
  assert.ok(html.includes('data-key="unsafe"'));
  assert.ok(html.includes('data-field="proposed"'));
});

test('renders Bỏ as the selected decision for rejected rows', () => {
  const html = View.renderRow({
    key: 'removed',
    name: 'Nhanh Nhẹn',
    family: 'Nhanh Nhẹn',
    code: 'equip_speed_i',
    effectKey: 'addSpeedPercent',
    tier: 'I',
    category: 'Cơ động',
    slot: 'Vũ khí',
    status: 'Đề xuất - adapter',
    current: 'Chưa có',
    proposed: '1-5%',
    cap: '',
    source: 'data.js',
    decision: 'Bỏ',
    note: 'Đã loại khỏi thiết kế đá cường hóa.',
  });

  assert.ok(html.includes('<option value="Bỏ" selected>Bỏ</option>'));
});

test('summarizes visible and edited rows for the header', () => {
  const summary = View.summarize(
    [
      { status: 'Đang có', tier: 'I' },
      { status: 'Đề xuất - adapter', tier: 'V' },
      { status: 'Đề xuất - adapter', tier: 'UTILITY' },
    ],
    { edited: { proposed: '9%' } },
  );

  assert.deepEqual(summary, { visible: 3, current: 1, proposals: 2, utility: 1, edited: 1 });
});
