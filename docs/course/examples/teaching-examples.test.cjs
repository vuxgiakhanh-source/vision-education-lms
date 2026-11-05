const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ts = require('../../../frontend/node_modules/typescript');
const examples = JSON.parse(fs.readFileSync(path.join(__dirname, '../teaching-content.json'), 'utf8')).examples;

async function main() {
  const tasks = [{title:'Hàm số',status:'pending'}, {title:'Tích phân',status:'graded'}, {title:'Hình học',status:'pending'}];
  assert.equal(vm.runInNewContext(examples.thinking.code + '; countPending(input)', {input:tasks}), 2);
  assert.equal(vm.runInNewContext(examples.thinking.code + '; countPending(input)', {input:[]}), 0);
  const result = vm.runInNewContext(examples['01'].code + '; ({pending,titles})', {tasks});
  assert.equal(result.pending.length, 2);
  assert.equal(result.pending[0], tasks[0]);
  assert.equal(JSON.stringify(result.titles), JSON.stringify(['Hàm số','Hình học']));
  assert.equal(tasks.length, 3);
  const code = ts.transpileModule(examples['02'].code, {compilerOptions:{target:ts.ScriptTarget.ES2023}}).outputText;
  const title = await vm.runInNewContext(code + '; loadTitle(client)', {client:{get:async()=>({data:{title:'Đại số'}})}});
  assert.equal(title,'Đại số');
  await assert.rejects(vm.runInNewContext(code+'; loadTitle(client)', {client:{get:async()=>{throw new Error('network');}}}), /network/);
  console.log('Worked JS/TS examples passed: loop boundary, callback output/reference and await success/rejection. No real HTTP or React renderer.');
}
main().catch(error=>{ console.error(error); process.exitCode=1; });
