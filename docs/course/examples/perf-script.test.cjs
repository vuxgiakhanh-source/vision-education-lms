/* Exercise business-check predicates with a fake k6 HTTP client. No load claim. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('../../../frontend/node_modules/typescript');
const source = fs.readFileSync(path.join(__dirname, '../workshop/perf/lms-load.js'), 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: {
  module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2023, esModuleInterop: true,
} }).outputText;

function run({ mode = 'read', body = [{ class_id: 1 }], status = 200, base, accounts } = {}) {
  const checks = [], calls = [], exports = {};
  const response = { status, json() { if (body === 'broken-json') throw new Error('invalid JSON'); return body; } };
  const http = { expectedStatuses: () => ({}), setResponseCallback() {},
    get(...args) { calls.push(args); return response; },
    post(...args) { calls.push(args); return response; } };
  const modules = {
    'k6/http': { __esModule: true, default: http },
    k6: { check(res, predicates) { checks.push(...Object.values(predicates).map(fn => fn(res))); } },
    'k6/data': { SharedArray: class { constructor(_name, produce) { return produce(); } } },
    'k6/execution': { __esModule: true, default: { scenario: { iterationInTest: 0 } } },
  };
  vm.runInNewContext(compiled, { exports, require: name => modules[name],
    __ENV: { MODE: mode, ...(base ? { BASE_URL: base } : {}) },
    open: () => JSON.stringify(accounts ?? [{ student_id: 2, token: 'fake-local-token' }]),
  });
  exports.default();
  return { checks, calls };
}

assert.deepEqual(run().checks, [true]);
for (const body of [[{ class_id: 99 }], [], 'broken-json', { detail: 'wrong shape' }]) {
  assert.deepEqual(run({ body }).checks, [false]);
}
assert.deepEqual(run({ status: 401 }).checks, [false]);
const valid = { student_id: 2, assignment_id: 1, answer: 'load-answer-2', score: null };
assert.deepEqual(run({ mode: 'submit', body: valid }).checks, [true]);
for (const bad of [{ ...valid, student_id: 3 }, { ...valid, score: 0 }, { ...valid, answer: 'wrong' }]) {
  assert.deepEqual(run({ mode: 'submit', body: bad }).checks, [false]);
}
assert.equal(JSON.parse(run({ mode: 'submit', body: valid }).calls[0][1]).answer, 'load-answer-2');
assert.throws(() => run({ base: 'https://example.com/api' }), /localhost/);
assert.throws(() => run({ accounts: [] }), /accounts/);
console.log('Load-script business checks reject bad status/JSON/scope/owner/answer/leaked grade; local target guard passed. Fake HTTP only, no k6 load executed.');
