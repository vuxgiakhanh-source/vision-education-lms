const assert = require('node:assert/strict');
const vm = require('node:vm');
const lab = require('../syntax-lab.js');

const programs = [
  'console.log(2 + 3);',
  'let diem = 7; diem = diem + 1; console.log(diem);',
  'const ten = "An"; console.log(ten);',
  'console.log("2" + 1); console.log(2 + 1);',
  'console.log(2 + 3 * 4); console.log((2 + 3) * 4);',
  'let diem = 7; console.log(diem === 7); console.log(diem === "7");',
  'console.log(-2 + 1); console.log(0 / 0); console.log(1 / 0);',
  'let __proto__ = 2; console.log(__proto__ + 1);',
  'console.log(";"); console.log("==="); // symbols inside strings are data',
];
for (const source of programs) {
  const expected = [];
  vm.runInNewContext(source, { console: { log: value => expected.push(String(value)) } }, { timeout: 200 });
  const actual = lab.run(source);
  assert.equal(actual.ok, true, actual.error);
  assert.deepEqual(actual.output, expected);
}
const trace = lab.run('let diem = 7;\ndiem = diem + 1;\nconsole.log(diem);').trace;
assert.deepEqual(trace.map(step => step.variables.diem), [7, 8, 8]);
assert.deepEqual(trace.map(step => step.line), [1, 2, 3]);
assert.match(lab.run('const diem = 7; diem = 8;').error, /const/);
assert.match(lab.run('console.log(diem);').error, /Chưa khai báo/);
assert.match(lab.run('let diem = 7; let diem = 8;').error, /đã được khai báo/);
assert.deepEqual(lab.run('console.log(1); let a = 1; let a = 2;').output, []);
assert.match(lab.run('console.log("An);').error, /nháy/);
const syntaxError = lab.run('console.log(1); console.log(2;');
assert.equal(syntaxError.ok, false);
assert.deepEqual(syntaxError.output, []); // parse whole program before effects
assert.match(lab.run('while (true) {}').error, /chưa hỗ trợ/);
assert.match(lab.run('console.log(1)\nconsole.log(2);').error, /Cần ;/);
assert.match(lab.run(' '.repeat(4001)).error, /4000/);
assert.deepEqual(lab.run('let a = 1;').output, []);
assert.equal(lab.format(Infinity), 'Infinity');
assert.equal(lab.format(NaN), 'NaN');
assert.equal(lab.run('console.log(a);').ok, false); // each run has fresh variables
console.log('Beginner syntax lab: supported programs match real JS; traces, errors, limits and fresh runs passed. No eval in the browser model.');
