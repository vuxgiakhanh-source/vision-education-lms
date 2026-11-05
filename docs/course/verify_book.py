"""Check packaging and navigation of the offline artifact; no browser/DB needed."""
from collections import Counter
from html.parser import HTMLParser
import ast
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.ids = []
        self.containers = []
        self.table_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self.table_count += 1
        if tag in {'details', 'summary', 'pre', 'code', 'table'}:
            self.containers.append(tag)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in {'script', 'img', 'iframe', 'audio', 'video', 'source'} and attrs.get('src'):
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.assets.append(attrs.get('href'))

    def handle_endtag(self, tag):
        if tag in {'details', 'summary', 'pre', 'code', 'table'}:
            assert self.containers and self.containers[-1] == tag, (tag, self.containers)
            self.containers.pop()


def check_markdown_tables(source: str, filename: str, rendered_count: int) -> int:
    """Catch malformed pipe rows and tables silently rendered as paragraphs."""
    fence = None
    columns = None
    previous = ''
    count = 0
    for number, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        marker = re.match(r'^(`{3,}|~{3,})(.*)$', stripped)
        if marker:
            token, suffix = marker.groups()
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not suffix.strip():
                fence = None
            columns = None
            previous = ''
            continue
        if fence:
            continue
        if re.fullmatch(r'\|[\s:|\-]+\|', stripped) and '-' in stripped:
            assert previous.startswith('|'), f'{filename}:{number}: table has no header'
            columns = len(re.split(r'(?<!\\)\|', stripped[1:-1]))
            header_columns = len(re.split(r'(?<!\\)\|', previous[1:-1]))
            assert columns == header_columns, f'{filename}:{number}: header column mismatch'
            count += 1
        elif columns is not None and stripped.startswith('|'):
            assert stripped.endswith('|'), f'{filename}:{number}: table row missing trailing pipe'
            actual = len(re.split(r'(?<!\\)\|', stripped[1:-1]))
            assert actual == columns, (f'{filename}:{number}: table expects {columns} columns, got {actual}; '
                                       'escape literal pipes inside cells, including inline code')
        else:
            columns = None
        previous = stripped
    assert rendered_count == count, (f'{filename}: {count} Markdown tables but {rendered_count} rendered; '
                                     'a table may have become raw text')
    return count


book = Path(__file__).with_name('GIAO-AN-LMS.html').read_text(encoding='utf-8')
doc = Document()
doc.feed(book)
assert not doc.assets, f'Unexpected external assets: {doc.assets}'
assert not re.search(r'@import\b|url\(\s*[\'"]?https?://', book)
assert len(doc.ids) == len(set(doc.ids)), Counter(doc.ids)
payload = re.search(r'<script type="application/json" id="book-data">(.*?)</script>', book, re.S).group(1)
data = json.loads(payload)
catalog = json.loads(Path(__file__).with_name('book-content.json').read_text(encoding='utf-8'))
advanced = json.loads(Path(__file__).with_name('advanced-content.json').read_text(encoding='utf-8'))
beginner = json.loads(Path(__file__).with_name('beginner-content.json').read_text(encoding='utf-8'))
frontend_path = json.loads(Path(__file__).with_name('frontend-path.json').read_text(encoding='utf-8'))
course_path = json.loads(Path(__file__).with_name('course-path.json').read_text(encoding='utf-8'))
catalog['lessons'] = frontend_path['lessons'] + beginner['lessons'] + catalog['lessons']
catalog['lessons'].extend(advanced['lessons'])
catalog['lessons'].extend(course_path['lessons'])
assert len(data['lessons']) == len(catalog['lessons'])
questions = sum(len(x['quiz']) for x in data['lessons'])
cards = sum(len(x['terms']) for x in data['lessons'])
assert questions == sum(len(x['quiz']) for x in catalog['lessons'])
assert cards == sum(len(x['terms']) for x in catalog['lessons'])
assert data['lessons'][0]['id'] == data['course']['start'] == 'studio-start'
primary_ids = [id for stage in data['course']['stages'] for id in stage['lessons']]
assert len(primary_ids) == len(set(primary_ids))
assert primary_ids == [lesson['id'] for lesson in data['lessons'] if lesson['primary']]
assert all(lesson['primary'] == (lesson['id'] in primary_ids) for lesson in data['lessons'])
assert next(l for l in data['lessons'] if l['id'] == 'thinking')['prerequisites'] == ['01']
assert next(l for l in data['lessons'] if l['id'] == '01')['prerequisites'] == ['bridge']
assert next(l for l in data['lessons'] if l['id'] == '03')['prerequisites'] == ['markup']
assert len({x['id'] for x in data['lessons']}) == len(data['lessons'])
assert len(data['code_lines']) == 14
known = {x['id'] for x in data['lessons']} | {'home', 'notes', 'examples', 'code-map'}
table_count = 0
for lesson in data['lessons']:
    article = Document()
    article.feed(lesson['html'])
    assert len(article.ids) == len(set(article.ids)), lesson['id']
    assert all(entry['id'] in article.ids for entry in lesson['contents'])
    assert (Path(__file__).parent / lesson['source']).is_file()
    if lesson['id'].startswith('studio-'):
        assert '(đường dẫn nguồn:' not in lesson['html'], f'Unpackaged link in {lesson["id"]}'
    raw = (Path(__file__).parent / lesson['source']).read_text(encoding='utf-8')
    table_count += check_markdown_tables(raw, lesson['source'], article.table_count)
    for index, snippet in enumerate(re.findall(r'^```python\s*\n(.*?)^```', raw, re.S | re.M)):
        ast.parse(snippet, filename=f'{lesson["source"]}:{index}')
    for quiz in lesson['quiz']:
        assert 0 <= quiz['correct'] < len(quiz['choices']) and quiz['why']
    for destination in re.findall(r'data-go="([^"]+)"', lesson['html']):
        assert destination in known, destination
    for source in re.findall(r'data-source="([^"]+)"', lesson['html']):
        assert source in data['files'], source
assert not any('.env' in key.lower() for key in data['files'])
for key, entry in data['files'].items():
    source_path = (Path(__file__).parent / key).resolve()
    assert source_path.is_relative_to(Path(__file__).resolve().parents[2])
    assert entry['sha256'] == hashlib.sha256(source_path.read_bytes()).hexdigest(), f'Stale embedded source: {key}'
    if key.endswith('.md'):
        rendered = Document()
        rendered.feed(entry['html'])
        table_count += check_markdown_tables(source_path.read_text(encoding='utf-8'), key, rendered.table_count)
assert len(data['files']) > 5
assert len(data['path']['milestones']) == 21 + len(course_path['milestones'])
milestone_ids = [milestone['id'] for milestone in data['path']['milestones']]
assert len(milestone_ids) == len(set(milestone_ids))
assert set(data['course']['primary_milestones']) <= set(milestone_ids)
assert len(data['api_guide']) == 12
assert data['api_guide'] == json.loads(Path(__file__).with_name('api-guide.json').read_text(encoding='utf-8'))['entries']
for entry in data['api_guide']:
    assert all(entry.get(field) for field in ['name', 'kind', 'when', 'signature', 'input', 'output', 'effect', 'pitfall', 'language', 'code', 'docs'])
    assert entry['docs'].startswith('https://')
    if entry['language'] == 'python':
        ast.parse(entry['code'])
for milestone in data['path']['milestones']:
    assert len(milestone['checks']) >= 3 and milestone['artifact'] and milestone['change']
    assert all(id in known for id in milestone['lessons'])
for lesson in data['lessons']:
    assert all(id in known for id in lesson.get('prerequisites', []))
    assert all(id in known for id in lesson.get('references', []))
    assert len({q['q'] for q in lesson['quiz']}) == len(lesson['quiz'])
    assert lesson['sections'] and all(section['title'] and section['html'] for section in lesson['sections'])
    assert all(lesson['study'].get(key) for key in ['remember', 'do', 'proof'])
    assert lesson['focus']['syntax']['parts'] and lesson['focus']['architecture']['question']
    assert len(lesson['focus']['architecture']['nodes']) >= 2
    clinic = Document()
    clinic.feed(lesson['focus']['syntax']['html'])
    assert not clinic.containers
    assert 'data-copy-code' not in lesson['html'] + lesson['focus']['syntax']['html']
    if lesson['focus']['syntax']['language'] == 'python':
        ast.parse(lesson['focus']['syntax']['code'])
    assert lesson['knowledge']
    for section in lesson['sections']:
        boundaries = Document()
        boundaries.feed(section['html'])
        assert not boundaries.containers, (lesson['id'], section['title'], boundaries.containers)
topic_ids = [topic['id'] for topic in data['knowledge']]
assert len(topic_ids) == len(set(topic_ids))
assert set(topic_ids) == {topic['id'] for topic in json.loads(Path(__file__).with_name('project-knowledge.json').read_text(encoding='utf-8'))}
for topic in data['knowledge']:
    assert topic['level'] in {'build', 'release', 'later'}
    assert topic['use'] and topic['why'] and topic['proof'] and topic['links']
    for link in topic['links']:
        target = next(lesson for lesson in data['lessons'] if lesson['id'] == link['lesson'])
        assert topic['id'] in target['knowledge']
        assert topic['id'] in target['sections'][link['step']]['knowledge']
        assert topic['name'] in target['sections'][link['step']]['html']
        assert topic['name'] in target['html']
assert len(data['teaching']['examples']) == 9
assert len(data['teaching']['syntax']) == 20
for lesson_id, example in data['teaching']['examples'].items():
    assert lesson_id in known
    assert any(example['section'] in s['title'] for s in next(l for l in data['lessons'] if l['id'] == lesson_id)['sections'])
    assert len(example['code'].splitlines()) == len(example['lines']) == len(example['highlighted_lines'])
    assert all(line['title'] and line['explanation'] and line['value'] for line in example['lines'])
    assert all(len(row) == len(example['trace']['headers']) for row in example['trace']['rows'])
    assert example['predict']['answer'] and len(example['practice']) == 3
    if example['language'] == 'python':
        ast.parse(example['code'])
assert 'workshop/lms_lab/app.py' in data['files']
assert 'workshop/frontend/ClassroomPractice.tsx' in data['files']
assert 'workshop/frontend/WorkflowPractice.tsx' in data['files']
assert 'workshop/perf/lms-load.js' in data['files']
assert 'workshop/deploy/compose.yaml' in data['files']
assert not any(key.endswith('accounts.json') or '/backups/' in key or '/results/' in key for key in data['files'])
assert '</script' not in payload.lower()
assert course_path['sources'], 'Missing studio source allowlist'
assert set(course_path['sources']) <= set(data['files'])
assert base64.b64decode(data['studio_archive']['base64'], validate=True) == Path(__file__).with_name('LMS-THUC-HANH.zip').read_bytes()
with zipfile.ZipFile(io.BytesIO(base64.b64decode(data['studio_archive']['base64'], validate=True))) as bundle:
    assert len(bundle.namelist()) == data['studio_archive']['count']
    assert bundle.testzip() is None
    assert len(bundle.namelist()) == len(set(bundle.namelist()))
    for name in bundle.namelist():
        assert name.startswith('lms-practice/') and '..' not in Path(name).parts
        key = name.removeprefix('lms-practice/')
        assert not any(part in {'node_modules', 'dist', '__pycache__', '.venv', 'results', 'backups'} for part in Path(key).parts)
        assert '.env' not in key.lower() and not key.endswith(('.db', '.sqlite', 'accounts.json'))
        assert bundle.read(name) == (Path(__file__).parent / key).read_bytes(), name
    for key in course_path['sources']:
        assert 'lms-practice/' + key in bundle.namelist()
        if key.endswith('.py'):
            ast.parse((Path(__file__).parent / key).read_text(encoding='utf-8'), filename=key)
for source in (Path(__file__).parent / 'workshop').rglob('*.py'):
    if '__pycache__' not in source.parts:
        ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
print(f'Offline artifact verified: {len(data["lessons"])} lessons, {questions} quizzes, {cards} cards, '
      f'{len(data["files"])} embedded source documents, {table_count} rendered tables; no external asset URLs.')
