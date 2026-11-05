/* Syntax checks for teaching snippets; strict types for the independent FE reference. */
const fs = require('node:fs');
const path = require('node:path');
const ts = require('../../frontend/node_modules/typescript');
const course = __dirname;
const frontend = path.resolve(course, '../../frontend');
const catalog = JSON.parse(fs.readFileSync(path.join(course, 'book-content.json'), 'utf8'));
catalog.lessons.push(...JSON.parse(fs.readFileSync(path.join(course, 'advanced-content.json'), 'utf8')).lessons);
catalog.lessons.push(...JSON.parse(fs.readFileSync(path.join(course, 'beginner-content.json'), 'utf8')).lessons);
catalog.lessons.push(...JSON.parse(fs.readFileSync(path.join(course, 'frontend-path.json'), 'utf8')).lessons);
catalog.lessons.push(...JSON.parse(fs.readFileSync(path.join(course, 'course-path.json'), 'utf8')).lessons);
let snippets = 0;
let errors = [];
for (const [id, focus] of Object.entries(JSON.parse(fs.readFileSync(path.join(course, 'study-focus.json'), 'utf8')))) {
  const example = focus.syntax;
  if (!['javascript', 'typescript', 'tsx', 'jsx'].includes(example.language)) continue;
  snippets++;
  const result = ts.transpileModule(example.code, {
    fileName: `focus-${id}.${['tsx','jsx'].includes(example.language) ? 'tsx' : 'ts'}`,
    reportDiagnostics: true,
    compilerOptions: { target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX },
  });
  errors.push(...(result.diagnostics || []).filter(d=>d.category === ts.DiagnosticCategory.Error));
}
for (const lesson of catalog.lessons) {
  const source = fs.readFileSync(path.join(course, lesson.source), 'utf8');
  const fences = /^```(javascript|typescript|tsx|jsx)\s*\r?\n([\s\S]*?)^```/gm;
  let match;
  while ((match = fences.exec(source))) {
    snippets++;
    const filename = `${lesson.id}-${snippets}.${['tsx', 'jsx'].includes(match[1]) ? 'tsx' : 'ts'}`;
    const result = ts.transpileModule(match[2], {
      fileName: filename, reportDiagnostics: true,
      compilerOptions: { target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX },
    });
    errors.push(...(result.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error));
  }
}
const folders = [path.join(course, 'workshop/frontend'), path.join(course, 'studio/frontend/react')];
const options = { target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext,
  moduleResolution: ts.ModuleResolutionKind.Bundler, jsx: ts.JsxEmit.ReactJSX,
  strict: true, skipLibCheck: true, noEmit: true, esModuleInterop: true };
const host = ts.createCompilerHost(options);
host.resolveModuleNames = (names, containingFile) => names.map(name => {
  const base = name.startsWith('.') ? containingFile : path.join(frontend, 'src/__course_check__.tsx');
  return ts.resolveModuleName(name, base, options, ts.sys).resolvedModule;
});
const files = folders.flatMap(folder => fs.readdirSync(folder).filter(name => /\.(ts|tsx)$/.test(name)).map(name => path.join(folder, name)));
const program = ts.createProgram(files, options, host);
errors.push(...ts.getPreEmitDiagnostics(program).filter(d => d.category === ts.DiagnosticCategory.Error));
const teaching = JSON.parse(fs.readFileSync(path.join(course, 'teaching-content.json'), 'utf8'));
Object.assign(teaching.examples, JSON.parse(fs.readFileSync(path.join(course, 'beginner-content.json'), 'utf8')).worked);
for (const [id, example] of Object.entries(teaching.examples)) {
  if (!['javascript', 'typescript', 'tsx'].includes(example.language)) continue;
  snippets++;
  const result = ts.transpileModule(example.code, { fileName: `${id}.${example.language === 'tsx' ? 'tsx' : 'ts'}`,
    reportDiagnostics: true, compilerOptions: { target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX } });
  errors.push(...(result.diagnostics || []).filter(d=>d.category===ts.DiagnosticCategory.Error));
}
for (const entry of JSON.parse(fs.readFileSync(path.join(course, 'api-guide.json'), 'utf8')).entries) {
  if (!['javascript', 'typescript', 'tsx'].includes(entry.language)) continue;
  snippets++;
  const result = ts.transpileModule(entry.code, { fileName: `api-${snippets}.${entry.language === 'tsx' ? 'tsx' : 'ts'}`,
    reportDiagnostics: true, compilerOptions: { target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX } });
  errors.push(...(result.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error));
}
if (errors.length) {
  console.error(ts.formatDiagnosticsWithColorAndContext(errors, {
    getCurrentDirectory: () => process.cwd(), getCanonicalFileName: file => file, getNewLine: () => '\n',
  }));
  process.exitCode = 1;
} else console.log(`${snippets} JS/TS/TSX snippets parsed; ${files.length} workshop/studio frontend files passed strict type checking. No browser/runtime claim.`);
