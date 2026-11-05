const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const lab = require('../syntax-lab.js');
const coach = require('../study-coach.js');
const guide = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../study-guide.json'), 'utf8'));
let count = 0;
for (const sections of Object.values(guide.sections)) {
  for (const section of Object.values(sections)) {
    const drill = section.drill;
    if (!drill) continue;
    const result = lab.run(drill.solution);
    assert.equal(result.ok, true, result.error);
    assert.equal(coach.assess(drill, result).matches, true, drill.task);
    assert.equal(coach.assess(drill, lab.run('')).matches, false);
    assert.equal(coach.assess(drill, lab.run('console.log(2;')).matches, false);
    if (drill.variables) {
      const outputOnly = drill.output.map(value => 'console.log(' + JSON.stringify(value) + ');').join('\n');
      assert.equal(coach.assess(drill, lab.run(outputOnly)).matches, false, 'output-only shortcut');
    }
    count++;
  }
}
const traceDrill = { output:['6'], variables:{diem:6}, trace_values:{diem:[4,6]} };
assert.equal(coach.assess(traceDrill, lab.run('let diem = 6; console.log(diem);')).matches, false);
assert.equal(coach.assess(traceDrill, lab.run('let diem = 4; diem = 6; console.log(diem);')).matches, true);
console.log(`${count} inline drills checked: solutions, syntax errors, empty attempts, output shortcuts and trace constraints. No mastery claim.`);
