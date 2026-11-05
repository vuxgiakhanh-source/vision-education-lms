/* Template/state unit checks with a minimal DOM double; not browser or layout QA. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const course = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(course, 'GIAO-AN-LMS.html'), 'utf8');
const payload = html.match(/<script type="application\/json" id="book-data">([\s\S]*?)<\/script>/)[1];
const data = JSON.parse(payload);
const criteria = data.path.milestones.reduce((total, milestone) => total + milestone.checks.length, 0);
const storage = new Map([['vision-lms-book-v1', JSON.stringify({
  notes: { '01': 'Existing learner note' }, completed: { '01': true },
})]]);

function setup(hash, blocked = false) {
  const nodes = new Map();
  const events = {}, windowEvents = {};
  const downloads = [], blobs = [];
  const node = id => {
    if (nodes.has(id)) return nodes.get(id);
    const classes = new Set(), attributes = {};
    const element = { id, innerHTML: '', textContent: '', hidden: true, style: {},
      classList: { toggle(name, force) {
        const on = force === undefined ? !classes.has(name) : !!force;
        if (on) classes.add(name); else classes.delete(name);
        return on;
      }, remove(name) { classes.delete(name); }, contains(name) { return classes.has(name); } },
      setAttribute(name, value) { attributes[name] = value; },
      getAttribute(name) { return attributes[name]; },
      addEventListener() {}, focus() {}, querySelector() { return null; }, querySelectorAll() { return []; },
    };
    nodes.set(id, element); return element;
  };
  node('book-data').textContent = payload;
  const sandbox = { console, setTimeout: () => 1, clearTimeout() {}, Blob,
    atob: value => Buffer.from(value, 'base64').toString('binary'),
    URL: { createObjectURL(blob) { blobs.push(blob); return 'blob:local-course'; }, revokeObjectURL() {} },
    document: { getElementById: node, body: node('body'),
      createElement: () => ({ click() { downloads.push(this); } }),
      documentElement: { style: { setProperty() {} } },
      addEventListener(type, fn) { events[type] = fn; } },
    localStorage: { getItem(key) { if (blocked) throw new Error('storage denied'); return storage.get(key) ?? null; },
      setItem(key, value) { if (blocked) throw new Error('storage denied'); storage.set(key, value); } },
    location: { hash }, scrollY: 0, scrollTo() {},
    addEventListener(type, fn) { windowEvents[type] = fn; },
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(path.join(course, 'book-models.js'), 'utf8'), sandbox);
  vm.runInContext(fs.readFileSync(path.join(course, 'syntax-lab.js'), 'utf8'), sandbox);
  vm.runInContext(fs.readFileSync(path.join(course, 'study-coach.js'), 'utf8'), sandbox);
  vm.runInContext(fs.readFileSync(path.join(course, 'book.js'), 'utf8'), sandbox);
  return { node, events, downloads, blobs, get hash() { return sandbox.location.hash; },
    resize(width) { sandbox.innerWidth = width; windowEvents.resize(); },
    navigate(hash) { sandbox.location.hash = hash; windowEvents.hashchange(); } };
}

const runtime = setup('#path');
assert.equal((runtime.node('view').innerHTML.match(/data-skill=/g) || []).length, criteria);
assert.match(runtime.node('view').innerHTML, /M11/);
runtime.events.change({ target: { dataset: { skill: 'environment:0' }, checked: true, id: '' } });
assert.equal(runtime.node('skills-total').textContent, `1 / ${criteria}`);
assert.match(runtime.node('view').innerHTML, /M17/);
runtime.events.input({ target: { dataset: { evidence: 'environment' }, value: '<script>not code</script>', id: '' } });
let saved = JSON.parse(storage.get('vision-lms-book-v1'));
assert.equal(saved.notes['01'], 'Existing learner note');
assert.equal(saved.completed['01'], true);
assert.equal(saved.skills['environment:0'], true);
assert.equal(saved.evidence.environment, '<script>not code</script>');
const reloaded = setup('#path');
assert.match(reloaded.node('view').innerHTML, /data-skill="environment:0" checked/);
assert.match(reloaded.node('view').innerHTML, /&lt;script&gt;not code&lt;\/script&gt;/);
assert.doesNotMatch(reloaded.node('view').innerHTML, /<script>not code/);

let views = 0;
for (const lesson of data.lessons) {
  for (const mode of ['learn', 'essence', 'read', 'quiz']) {
    runtime.navigate(`#lesson/${lesson.id}/${mode}`);
    assert.match(runtime.node('view').innerHTML, /learning-contract/);
    assert.ok(runtime.node('view').innerHTML.length > 1000, `${lesson.id}/${mode}`);
    if (mode === 'quiz') assert.equal((runtime.node('view').innerHTML.match(/class="quiz-item"/g) || []).length, lesson.quiz.length);
    if (mode === 'learn') assert.match(runtime.node('view').innerHTML, /lesson-section/);
    views++;
  }
}
runtime.navigate('#lesson/01/learn/2');
assert.equal(JSON.parse(storage.get('vision-lms-book-v1')).reading['01'], 2);
assert.equal(JSON.parse(storage.get('vision-lms-book-v1')).lastLesson, '01');
const resumed = setup('#lesson/01');
assert.match(resumed.node('view').innerHTML, /<option value="2" selected/);
const exampleStep = data.lessons.find(l=>l.id==='01').sections.findIndex(s=>s.title.includes(data.teaching.examples['01'].section));
runtime.navigate('#lesson/01/learn/'+exampleStep);
assert.equal((runtime.node('view').innerHTML.match(/data-worked-line=/g) || []).length, 5);
const lineButton = { dataset: { workedLine: '3' }, hasAttribute: name=>name==='data-worked-line' };
lineButton.closest = () => lineButton;
runtime.events.click({ target: lineButton });
assert.match(runtime.node('line-explanation').innerHTML, /Truyền hàm, để filter gọi/);
runtime.navigate('#lesson/01/learn/999');
assert.equal(JSON.parse(storage.get('vision-lms-book-v1')).reading['01'], data.lessons.find(l=>l.id==='01').sections.length-1);
runtime.navigate('#home');
assert.ok(runtime.node('view').innerHTML.includes(`<strong>${data.lessons.filter(l => l.primary).length}</strong><span>bài trên đường chính`));
assert.match(runtime.node('view').innerHTML, /data-id="studio-start">Bắt đầu đường học mới/);
assert.equal((runtime.node('view').innerHTML.match(/class="course-stage /g) || []).length, data.course.stages.length);
assert.match(runtime.node('navigation').innerHTML, /reference-nav/);
const primary = data.lessons.filter(lesson => lesson.primary);
for (let index = 0; index < primary.length - 1; index++) {
  runtime.navigate('#lesson/' + primary[index].id);
  assert.ok(runtime.node('view').innerHTML.includes(`class="pager-next" data-route="lesson" data-id="${primary[index + 1].id}"`));
}
runtime.navigate('#lesson/capstone');
assert.match(runtime.node('view').innerHTML, /class="pager-next" data-route="path"/);
runtime.navigate('#lesson/product');
assert.match(runtime.node('view').innerHTML, /reference-orientation/);
for (const lesson of data.lessons.filter(item => item.id.startsWith('studio-'))) {
  lesson.sections.forEach((section, step) => {
    runtime.navigate(`#lesson/${lesson.id}/learn/${step}`);
    assert.ok(runtime.node('view').innerHTML.includes(section.html), `${lesson.id}/${step}`);
  });
}
const sectionLink = { dataset: { go: '14', mode: 'learn/3' }, hasAttribute: () => false, closest() { return this; } };
runtime.events.click({ target: sectionLink, preventDefault() {} });
assert.equal(runtime.hash, '#lesson/14/learn/3');
runtime.node('sidebar').classList.toggle('open', true);
runtime.events.keydown({ key: 'Escape', target: { tagName: 'BUTTON' } });
assert.equal(runtime.node('sidebar').classList.contains('open'), false);
assert.equal(runtime.node('menu-toggle').getAttribute('aria-expanded'), 'false');
runtime.node('sidebar').classList.toggle('open', true);
runtime.resize(1280);
assert.equal(runtime.node('sidebar').classList.contains('open'), false);
const downloadButton = { dataset: {}, hasAttribute: name => name === 'data-download-studio', closest() { return this; } };
runtime.events.click({ target: downloadButton });
assert.equal(runtime.downloads.length, 1);
assert.equal(runtime.downloads[0].download, data.studio_archive.name);
assert.equal(runtime.blobs[0].type, 'application/zip');
runtime.navigate('#lab/syntax');
assert.equal(runtime.node('syntax-code').value, 'console.log(2);');
runtime.node('syntax-code').value = 'let diem = 7;\ndiem = diem + 1;\nconsole.log(diem);';
const runButton = { hasAttribute: name => name === 'data-syntax-run', closest() { return this; } };
runtime.events.click({ target: runButton });
assert.match(runtime.node('syntax-output').textContent, /^8/);
assert.match(runtime.node('syntax-trace').innerHTML, /diem = 7/);
assert.match(runtime.node('syntax-trace').innerHTML, /diem = 8/);
runtime.node('syntax-code').value = 'console.log("<img src=x onerror=alert(1)>");';
runtime.events.click({ target: runButton });
assert.match(runtime.node('syntax-trace').innerHTML, /&lt;img/);
assert.doesNotMatch(runtime.node('syntax-trace').innerHTML, /<img/);
runtime.navigate('#lab/css');
assert.match(runtime.node('css-code').textContent, /display: block/);
runtime.node('css-display').value = 'flex';
runtime.node('css-direction').value = 'column';
runtime.events.change({ target: { id: 'css-display', dataset: {} } });
assert.match(runtime.node('css-code').textContent, /display: flex/);
assert.match(runtime.node('css-code').textContent, /flex-direction: column/);
runtime.node('css-gap').value = 'url(https://example.com)';
runtime.events.change({ target: { id: 'css-gap', dataset: {} } });
assert.doesNotMatch(runtime.node('css-code').textContent, /url\(/);
const apiButton = { hasAttribute: name => name === 'data-open-api', closest() { return this; } };
runtime.events.click({ target: apiButton });
assert.match(runtime.node('api-results').innerHTML, /str.strip/);
runtime.events.input({ target: { id: 'api-query', value: 'strip', dataset: {} } });
assert.match(runtime.node('api-results').innerHTML, /String mới/);
assert.doesNotMatch(runtime.node('api-results').innerHTML, /<h3>React.useState/);
runtime.navigate('#review');
assert.ok(runtime.node('view').innerHTML.includes(`${data.lessons.reduce((count, lesson) => count + lesson.terms.length, 0)} thẻ`));
assert.equal(setup('#home', true).node('storage-warning').hidden, false);

// Project relevance is visible in both reading modes; atlas links land at actual sections.
for (const lesson of data.lessons) {
  assert.ok(lesson.knowledge.length > 0, lesson.id);
  runtime.navigate(`#lesson/${lesson.id}/essence`);
  assert.match(runtime.node('view').innerHTML, /syntax-parts/);
  assert.match(runtime.node('view').innerHTML, /architecture-flow/);
  assert.match(runtime.node('view').innerHTML, /data-focus-draft=/);
  assert.match(runtime.node('view').innerHTML, /Phải tự làm/);
}
for (const topic of data.knowledge) {
  for (const link of topic.links) {
    const lesson = data.lessons.find(l => l.id === link.lesson);
    assert.ok(lesson.sections[link.step].html.includes(topic.name));
    assert.ok(lesson.html.includes(topic.name));
  }
}
runtime.navigate('#knowledge');
assert.equal((runtime.node('view').innerHTML.match(/DÙNG TRONG DỰ ÁN/g) || []).length, data.knowledge.length);
const filterButton = { dataset: { knowledgeFilter: 'later' }, hasAttribute: name=>name==='data-knowledge-filter', closest() { return this; } };
runtime.events.click({ target: filterButton });
assert.equal((runtime.node('view').innerHTML.match(/DÙNG TRONG DỰ ÁN/g) || []).length, data.knowledge.filter(t=>t.level==='later').length);
assert.match(runtime.node('view').innerHTML, /Cache, queue/);
// Drafts persist, are escaped, and never mark the lesson completed.
runtime.navigate('#lesson/bridge/essence');
runtime.events.input({ target: { id:'draft-bridge', dataset:{focusDraft:'bridge'}, value:'</textarea><img src=x onerror=alert(1)>' } });
runtime.events.input({ target: { id:'design-bridge', dataset:{designDraft:'bridge'}, value:'Use case owns policy' } });
let draftReload = setup('#lesson/bridge/essence');
assert.match(draftReload.node('view').innerHTML, /&lt;\/textarea&gt;&lt;img/);
assert.doesNotMatch(draftReload.node('view').innerHTML, /<img src=x/);
assert.match(draftReload.node('view').innerHTML, /Use case owns policy/);
assert.notEqual(JSON.parse(storage.get('vision-lms-book-v1')).completed.bridge, true);
// Inline drill: output alone does not satisfy required variable/trace constraints.
runtime.navigate('#lesson/zero/learn/7');
assert.match(runtime.node('view').innerHTML, /data-run-drill/);
const drillButton = { dataset:{}, hasAttribute: name=>name==='data-run-drill', closest() { return this; } };
runtime.node('lesson-drill-code').value = 'console.log(6);';
runtime.events.click({ target: drillButton });
assert.equal(runtime.node('drill-feedback').getAttribute('data-result'), 'retry');
runtime.node('lesson-drill-code').value = 'let diem = 4; diem = diem + 2; console.log(diem);';
runtime.events.click({ target: drillButton });
assert.equal(runtime.node('drill-feedback').getAttribute('data-result'), 'match');
assert.match(runtime.node('drill-trace').innerHTML, /diem/);
assert.notEqual(JSON.parse(storage.get('vision-lms-book-v1')).completed.zero, true);
const changedCode = 'let diem = 4; console.log(diem;';
runtime.events.input({ target:{ id:'lesson-drill-code',dataset:{drillDraft:'zero:7'},value:changedCode } });
assert.equal(runtime.node('drill-feedback').getAttribute('data-result'), 'stale');
assert.equal(runtime.node('drill-trace').innerHTML, '');
const drillReload = setup('#lesson/zero/learn/7');
assert.equal(drillReload.node('lesson-drill-code').value, changedCode);
drillReload.events.click({ target: drillButton });
assert.equal(drillReload.node('drill-feedback').getAttribute('data-result'), 'retry');
assert.match(drillReload.node('drill-feedback').textContent, /Chưa chạy xong/);
// Unsupported syntax is rejected with feedback, never evaluated as arbitrary JS.
drillReload.node('lesson-drill-code').value = 'while (true) {}';
drillReload.events.click({ target: drillButton });
assert.match(drillReload.node('drill-feedback').textContent, /chưa hỗ trợ/);
console.log(`${views} lesson views + path/home/review templates checked; ${criteria} criteria, persistence, legacy notes and escaping passed. DOM double only, no layout claim.`);

(async () => {
  // Export/import carries authored drafts, accepts only known keys, bounds text.
  const imported = { format:'vision-lms-book-v1', drafts:{bridge:'new code',unknown:'ignore'},
    designs:{bridge:'new design'}, drills:{'zero:7':'let diem = 4;','unknown:7':'ignore'},
    reading:{zero:7}, notes:{'01':'Existing learner note'} };
  runtime.events.change({target:{id:'notes-file',dataset:{},files:[{size:1000,text:async()=>JSON.stringify(imported)}]}});
  await new Promise(resolve=>setImmediate(resolve));
  const importedState=JSON.parse(storage.get('vision-lms-book-v1'));
  assert.equal(importedState.drafts.bridge,'new code');
  assert.equal(importedState.designs.bridge,'new design');
  assert.equal(importedState.drills['zero:7'],'let diem = 4;');
  assert.equal(importedState.drafts.unknown,undefined);
  assert.equal(importedState.drills['unknown:7'],undefined);
  const exportButton = {dataset:{},hasAttribute:name=>name==='data-export-notes',closest(){return this;}};
  await runtime.events.click({target:exportButton});
  const exported=JSON.parse(await runtime.blobs.at(-1).text());
  assert.equal(exported.drafts.bridge,'new code');
  assert.equal(exported.designs.bridge,'new design');
  assert.equal(exported.drills['zero:7'],'let diem = 4;');
  assert.equal(exported.notes['01'],'Existing learner note');
  console.log('Draft export/import preserved known fields and rejected unknown keys.');
})().catch(error=>{console.error(error);process.exitCode=1;});
