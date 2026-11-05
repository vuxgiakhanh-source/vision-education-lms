/* Run: node docs/course/examples/book-models.test.cjs */
const assert = require('node:assert/strict');
const M = require('../book-models.js');
let passed = 0;
function test(name, fn) { fn(); passed++; console.log('PASS ' + name); }

test('Login success and error take separate paths', () => {
  assert.match(M.loginTrace('success')[7].payload, /dashboard/);
  assert.match(M.loginTrace('change')[7].payload, /change-password/);
  assert.match(M.loginTrace('wrong')[6].payload, /401/);
  assert.match(M.loginTrace('locked')[6].payload, /403/);
  assert.equal(M.loginTrace('success').length, 8);
});
test('Alias and shallow copy share nested object', () => {
  const alias = M.memory('alias', true), shallow = M.memory('shallow', true);
  assert.equal(alias.arrayA, alias.arrayB);
  assert.notEqual(shallow.arrayA, shallow.arrayB);
  assert.equal(shallow.objectA, shallow.objectB);
  assert.equal(shallow.originalStatus, 'submitted');
});
test('Immutable update leaves original unchanged', () => {
  const result = M.memory('immutable', true);
  assert.equal(result.originalStatus, 'pending');
  assert.equal(result.copyStatus, 'submitted');
  assert.notEqual(result.objectA, result.objectB);
});
test('State replacement uses snapshot; updaters compose', () => {
  assert.equal(M.stateQueue(3, false).result, 4);
  assert.equal(M.stateQueue(3, true).result, 5);
});
test('LEFT JOIN keeps missing submissions and COUNT skips NULL', () => {
  const left = M.join('left');
  assert.equal(left.rows.length, 3);
  assert.equal(left.countStar, 3);
  assert.equal(left.countSubmission, 1);
  assert.equal(M.join('inner').rows.length, 1);
  assert.equal(M.join('missing').rows.length, 2);
});
test('One transaction rollback leaves no orphan', () => {
  assert.equal(M.transaction(1, false, false).pending.length, 1);
  assert.equal(M.transaction(1, false, false).committed.length, 0);
  assert.deepEqual(M.transaction(2, false, true).committed, []);
  assert.deepEqual(M.transaction(2, false, true).pending, []);
  assert.equal(M.transaction(3, false, false).committed.length, 2);
});
test('Premature commit leaves orphan after later failure', () => {
  const result = M.transaction(3, true, true);
  assert.equal(result.orphan, true);
  assert.equal(result.committed.length, 1);
});
test('Permissions combine identity and scope', () => {
  assert.equal(M.permission('own', false).code, 401);
  assert.equal(M.permission('own', true, false).code, 403);
  assert.equal(M.permission('own').code, 200);
  assert.equal(M.permission('teacher').code, 200);
  for (const actor of ['other', 'outsider', 'assistant', 'admin', 'unknown']) {
    assert.equal(M.permission(actor).code, 403);
  }
});
const valid = {active:true, student:true, member:true, answer:'  Hàm số  ', existing:'none', published:true, offset:0};
test('New submission accepted at deadline, rejected afterwards', () => {
  assert.equal(M.deadline(valid).allowed, true);
  assert.equal(M.deadline({...valid, offset:1}).allowed, false);
  assert.equal(M.deadline({...valid, published:false}).allowed, false);
});
test('Same retry keeps old timestamp even after deadline or closure', () => {
  const retry = M.deadline({...valid, existing:'same', published:false, offset:99});
  assert.equal(retry.allowed, true);
  assert.equal(retry.retry, true);
  assert.match(retry.title, /12:00/);
  assert.match(M.deadline({...valid, existing:'different'}).title, /409/);
});
test('Retry still validates identity, membership and content', () => {
  for (const patch of [{active:false}, {student:false}, {member:false}, {answer:'   '}, {answer:'a'.repeat(10001)}]) {
    assert.equal(M.deadline({...valid, existing:'same', ...patch}).allowed, false);
  }
  assert.equal(M.deadline({...valid, answer:'😀'.repeat(10000)}).allowed, true);
});
test('Decimal comparison canonicalizes strings without float rounding', () => {
  for (const value of ['+001.500', '1.5', '01.50']) assert.equal(M.parseNumber(value), '1.5');
  assert.equal(M.parseNumber('-000.000'), '0');
  assert.equal(M.parseNumber('-010.050'), '-10.05');
  assert.notEqual(M.parseNumber('9007199254740992'), M.parseNumber('9007199254740993'));
  for (const value of ['', 'NaN', 'Infinity', '1e3', '.5', '1.', '1,5', '1+2', 'a'.repeat(101)]) assert.throws(() => M.parseNumber(value));
});
test('Reports use explicit denominators and validate invariants', () => {
  assert.deepEqual(M.report(6, 8, 10), {valid:true, whole:60, attempted:75});
  assert.equal(M.report(0, 0, 10).attempted, null);
  for (const args of [[1,0,2],[0,2,1],[0,0,0],[-1,0,1],[1.5,2,3],[NaN,2,3]]) assert.equal(M.report(...args).valid, false);
});
test('HTTP empty success differs from invalid body and network error', () => {
  assert.equal(M.http('empty').state, 'success: []');
  assert.equal(M.http('bad').state, 'validation error');
  assert.match(M.http('network').label, /chưa có HTTP/);
  assert.match(M.http('401').label, /401/);
});
test('Viewport estimate accounts for OS scale and browser zoom', () => {
  assert.equal(M.viewport(1920, 100, 100), 1920);
  assert.equal(M.viewport(1920, 125, 100), 1536);
  assert.equal(M.viewport(2560, 125, 125), 1638);
});
console.log(`${passed} teaching-model checks passed. No real API or SQL was executed.`);
