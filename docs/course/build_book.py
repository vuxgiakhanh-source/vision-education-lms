"""Build one self-contained HTML book from the course sources.

Run with the system Python which already has mistune/pygments at authoring time:
    python docs/course/build_book.py
Only building needs these two packages; reading the generated file needs no server/network.
"""

from __future__ import annotations

import html
import hashlib
import base64
import io
import json
import posixpath
from pathlib import Path
import re
import unicodedata
import zipfile
from urllib.parse import unquote

import mistune
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

COURSE = Path(__file__).resolve().parent
REPO = COURSE.parents[1]
OUTPUT = COURSE / 'GIAO-AN-LMS.html'
PRACTICE_OUTPUT = COURSE / 'LMS-THUC-HANH.zip'
formatter = HtmlFormatter(nowrap=True)


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def codebox(source: str, language: str = 'text', label: str = '') -> str:
    try:
        code = highlight(source, get_lexer_by_name(language), formatter)
    except ClassNotFound:
        code = html.escape(source)
    return (
        '<div class="codebox"><div class="codebar"><span>' + escape(label or language)
        + '</span><div class="codebar-actions"><button type="button" data-open-syntax>Hiểu ký hiệu</button><button type="button" data-open-api>Tra hàm/tool</button></div></div>'
        '<pre><code>' + code + '</code></pre></div>'
    )


class BookRenderer(mistune.HTMLRenderer):
    def block_quote(self, text: str) -> str:
        marker = re.match(r'<p>\[!(KEY|TASK|CHECK|NOTE|WARNING)\]\s*', text)
        if not marker:
            return super().block_quote(text)
        kind = marker.group(1).lower()
        labels = {'key': 'CẦN NHỚ', 'task': 'TỰ VIẾT', 'check': 'TỰ KIỂM',
                  'note': 'HIỂU CƠ CHẾ', 'warning': 'CHỖ DỄ SAI'}
        content = '<p>' + text[marker.end():]
        return '<aside class="teaching-callout callout-' + kind + '"><strong class="callout-label">' + labels[kind] + '</strong>' + content + '</aside>'

    def paragraph(self, text: str) -> str:
        match = re.match(r'<strong>([^<]+)</strong>', text)
        labels = {'Cần nhớ:': 'key', 'Tự làm:': 'task', 'Tự viết:': 'task',
                  'Đầu ra:': 'check', 'Đích:': 'check', 'Tự kiểm:': 'check',
                  'Nếu kẹt:': 'note', 'Dễ sai:': 'warning'}
        kind = labels.get(html.unescape(match.group(1))) if match else None
        return '<p class="teaching-line line-' + kind + '">' + text + '</p>\n' if kind else super().paragraph(text)

    def block_code(self, code: str, info: str | None = None) -> str:
        language = (info or 'text').split()[0]
        if language == 'mermaid':
            rows = []
            for line in code.splitlines():
                match = re.match(r'\s*(\w+)\s+\S+--\S+\s+(\w+)\s*:\s*(.+)', line)
                if match:
                    left, right, relation = match.groups()
                    rows.append('<div class="relation"><code>' + escape(left)
                                + '</code><span>' + escape(relation)
                                + ' →</span><code>' + escape(right) + '</code></div>')
            if rows:
                return '<figure class="mermaid-figure"><figcaption class="eyebrow">Quan hệ dữ liệu</figcaption>' + ''.join(rows) + '</figure>'
        rendered = codebox(code, language)
        line_count = len(code.strip().splitlines())
        if line_count > 18 and language in {'javascript', 'typescript', 'tsx', 'jsx', 'python', 'html', 'css', 'sql'}:
            return ('<details class="reference-code"><summary><span>MÃ ĐỐI CHIẾU</span>'
                    + '<strong>' + str(line_count) + ' dòng · mở sau khi tự viết</strong></summary>'
                    + '<p>Trước khi mở, tự ghi đầu vào, đầu ra và cách làm. Khi đối chiếu, chỉ ra dòng khác dự đoán rồi đóng mẫu và viết lại một biến thể.</p>'
                    + rendered + '</details>')
        return rendered

    def table(self, text: str) -> str:
        return '<div class="table-scroll"><table>' + text + '</table></div>'


markdown = mistune.create_markdown(renderer=BookRenderer(escape=False), plugins=['table', 'strikethrough', 'task_lists'])


def slug(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', text).strip('-') or 'section'


def build() -> None:
    data = json.loads((COURSE / 'book-content.json').read_text(encoding='utf-8'))
    data['path'] = json.loads((COURSE / 'learning-path.json').read_text(encoding='utf-8'))
    advanced = json.loads((COURSE / 'advanced-content.json').read_text(encoding='utf-8'))
    beginner = json.loads((COURSE / 'beginner-content.json').read_text(encoding='utf-8'))
    frontend_path = json.loads((COURSE / 'frontend-path.json').read_text(encoding='utf-8'))
    course_path = json.loads((COURSE / 'course-path.json').read_text(encoding='utf-8'))
    study = json.loads((COURSE / 'study-guide.json').read_text(encoding='utf-8'))
    focus = json.loads((COURSE / 'study-focus.json').read_text(encoding='utf-8'))
    data['api_guide'] = json.loads((COURSE / 'api-guide.json').read_text(encoding='utf-8'))['entries']
    data['lessons'] = frontend_path['lessons'] + beginner['lessons'] + data['lessons']
    # Syntax before algorithm exercises; original lesson ids/quiz keys stay stable.
    thinking = next(lesson for lesson in data['lessons'] if lesson['id'] == 'thinking')
    data['lessons'].remove(thinking)
    data['lessons'].insert(next(i for i, lesson in enumerate(data['lessons']) if lesson['id'] == '01') + 1, thinking)
    thinking['prerequisites'] = ['01']
    next(lesson for lesson in data['lessons'] if lesson['id'] == '01')['prerequisites'] = ['bridge']
    next(lesson for lesson in data['lessons'] if lesson['id'] == '03')['prerequisites'] = ['markup']
    first = next(lesson for lesson in data['lessons'] if lesson['id'] == 'first')
    data['lessons'].remove(first)
    data['lessons'].insert(next(i for i, lesson in enumerate(data['lessons']) if lesson['id'] == '09') + 1, first)
    data['path']['milestones'] = frontend_path['milestones'] + data['path']['milestones'] + beginner['milestones']
    next(m for m in data['path']['milestones'] if m['id'] == 'language')['lessons'] = ['01', 'thinking', '02']
    data['lessons'].extend(advanced['lessons'])
    data['path']['milestones'].extend(advanced['milestones'])
    data['lessons'].extend(course_path['lessons'])
    data['path']['milestones'] = course_path['milestones'] + data['path']['milestones']
    data['path']['scope'] = course_path['scope']
    data['course'] = {key: course_path[key] for key in ['start', 'stages', 'primary_milestones']}
    primary_ids = [identifier for stage in course_path['stages'] for identifier in stage['lessons']]
    assert len(primary_ids) == len(set(primary_ids)), 'Duplicate primary course lesson'
    by_id = {lesson['id']: lesson for lesson in data['lessons']}
    assert set(study['lessons']) == set(by_id), 'Every lesson needs an explicit study contract'
    assert set(focus) == set(by_id), 'Every lesson needs a syntax and architecture clinic'
    for identifier, lesson in by_id.items():
        lesson['study'] = study['lessons'][identifier]
        assert all(lesson['study'].get(key) for key in ('remember', 'do', 'proof')), identifier
        lesson['focus'] = focus[identifier]
        clinic = lesson['focus']['syntax']
        assert all(clinic.get(key) for key in ('language', 'code', 'parts', 'rule', 'task', 'check')), identifier
        clinic['html'] = codebox(clinic['code'], clinic['language'], 'ĐỌC MỘT CẤU TRÚC')
        assert len(lesson['focus']['architecture']['nodes']) >= 2, identifier
    data['lessons'] = [by_id[identifier] for identifier in primary_ids] + [
        lesson for lesson in data['lessons'] if lesson['id'] not in primary_ids]
    for lesson in data['lessons']:
        lesson['primary'] = lesson['id'] in primary_ids
    # Core sessions introduce these concepts in context. Deep chapters remain references.
    references = {
        'studio-web': ['01', '03'], 'studio-react': ['02', '04'],
        'studio-python': ['thinking', 'python', '05'],
        'studio-feature': ['06', '07', '08', '09', 'workshop', 'clean'],
        'studio-modules': ['10', '11', '14', 'product'],
        'studio-transfer': ['13', 'delivery'],
        'performance': ['06', '08', '12'], 'release': ['delivery', '12'],
        'operations': ['09', 'debug'], 'capstone': ['clean'],
    }
    for identifier, ids in references.items():
        by_id[identifier]['references'] = ids
    for identifier, prerequisites in {
        'performance': ['studio-transfer'], 'release': ['performance'],
        'operations': ['release'], 'capstone': ['operations'],
    }.items():
        by_id[identifier]['prerequisites'] = prerequisites
    data['teaching'] = json.loads((COURSE / 'teaching-content.json').read_text(encoding='utf-8'))
    data['teaching']['examples'].update(beginner['worked'])
    for example in data['teaching']['examples'].values():
        example['highlighted_lines'] = [highlight(line, get_lexer_by_name(example['language']), formatter).rstrip('\n')
                                        for line in example['code'].splitlines()]
    lessons = data['lessons']
    source_ids = {lesson['source']: lesson['id'] for lesson in lessons}
    source_ids['README.md'] = 'home'
    source_ids['examples/README.md'] = 'examples'
    source_ids['../CODE_GUIDE.md'] = 'code-map'
    source_ids['../WORKLOG.md'] = 'notes'
    # Static source references for the independent workshop, never its DB/env/node_modules.
    workshop_paths = [COURSE / 'workshop' / 'README.md', COURSE / 'workshop' / 'requirements.txt']
    workshop_paths += sorted((COURSE / 'workshop').glob('test_*.py'))
    workshop_paths += sorted((COURSE / 'workshop' / 'lms_lab').glob('*.py'))
    workshop_paths += [p for p in sorted((COURSE / 'workshop' / 'frontend').iterdir())
                      if p.suffix in {'.ts', '.tsx', '.css', '.json', '.html'}]
    # Explicit names only: never recurse through backups, credentials, results or env.
    workshop_paths += [COURSE / 'workshop' / p for p in [
        'deploy/README.md', 'deploy/requirements.txt', 'deploy/Dockerfile.api',
        'deploy/Dockerfile.web', 'deploy/nginx.conf', 'deploy/compose.yaml',
        'deploy/alembic.ini', 'deploy/migrations/env.py',
        'deploy/migrations/versions/0001_baseline.py', 'deploy/seed_lab.py',
        'deploy/export_accounts.py', 'deploy/course-ci.yaml',
        'perf/lms-load.js', 'perf/REPORT.md', '.dockerignore', '.gitignore',
    ]]
    # The studio is an explicit allowlist: do not scan dependencies, DBs or user work.
    studio_paths = []
    for key in course_path['sources']:
        source_path = (COURSE / key).resolve()
        assert key.startswith('studio/') and source_path.is_relative_to(COURSE / 'studio'), key
        assert not any(part in {'node_modules', 'dist', '__pycache__', '.venv'} for part in source_path.parts)
        assert source_path.is_file(), key
        studio_paths.append(source_path)
    workshop_paths += studio_paths
    archive = io.BytesIO()
    archive_paths = set(workshop_paths) | {COURSE / lesson['source'] for lesson in data['lessons']}
    archive_paths |= {COURSE / 'README.md', COURSE / 'VALIDATION.md'}
    archive_paths |= {p for p in (COURSE / 'examples').iterdir() if p.suffix in {'.py', '.ts', '.md', '.json'}}
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for source_path in sorted(archive_paths):
            name = 'lms-practice/' + source_path.relative_to(COURSE).as_posix()
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 17, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, source_path.read_bytes())
    PRACTICE_OUTPUT.write_bytes(archive.getvalue())
    data['studio_archive'] = {'name': PRACTICE_OUTPUT.name, 'count': len(archive_paths),
                              'base64': base64.b64encode(archive.getvalue()).decode('ascii')}
    for lesson in lessons:
        source = (COURSE / lesson['source']).read_text(encoding='utf-8')
        body = markdown(source)
        contents = []
        used = set()

        def heading(match: re.Match) -> str:
            level, text = match.groups()
            plain = html.unescape(re.sub('<[^>]+>', '', text))
            identifier = lesson['id'] + '-' + slug(plain)
            while identifier in used:
                identifier += '-x'
            used.add(identifier)
            if level == '2':
                contents.append({'id': identifier, 'title': plain})
            return '<h' + level + ' id="' + identifier + '">' + text + '</h' + level + '>'

        body = re.sub(r'<h([1-4])>(.*?)</h\1>', heading, body, flags=re.S)
        lesson['html'] = body
        lesson['contents'] = contents
        lesson['search'] = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', body))).strip()

    files = {}
    for path in sorted((COURSE / 'examples').iterdir()):
        if path.suffix in {'.py', '.ts', '.md', '.json'}:
            key = 'examples/' + path.name
            text = path.read_text(encoding='utf-8')
            language = {'.py': 'python', '.ts': 'typescript', '.json': 'json'}.get(path.suffix, 'text')
            files[key] = {'name': key, 'html': markdown(text) if path.suffix == '.md' else codebox(text, language, key)}

    guide = (COURSE.parent / 'CODE_GUIDE.md').read_text(encoding='utf-8')
    files['../CODE_GUIDE.md'] = {'name': 'Bản đồ code hiện tại', 'html': markdown(guide)}
    files['VALIDATION.md'] = {'name': 'Báo cáo kiểm tra giáo án', 'html': markdown((COURSE / 'VALIDATION.md').read_text(encoding='utf-8'))}
    for source_path in workshop_paths:
        key = source_path.relative_to(COURSE).as_posix()
        content = source_path.read_text(encoding='utf-8')
        language = {'.py': 'python', '.ts': 'typescript', '.tsx': 'tsx', '.css': 'css',
                    '.json': 'json', '.html': 'html', '.js': 'javascript', '.yaml': 'yaml',
                    '.ini': 'ini', '.conf': 'nginx'}.get(source_path.suffix, 'text')
        files[key] = {'name': key, 'html': markdown(content) if source_path.suffix == '.md' else codebox(content, language, key)}
    # Embed only explicitly linked source code, never environment files or private data.
    for target in re.findall(r'\]\(([^)]+)\)', guide):
        if target.startswith(('http:', 'https:', '#')):
            continue
        source_path = (COURSE.parent / target.split('#', 1)[0]).resolve()
        if not source_path.is_relative_to(REPO) or source_path.suffix not in {'.py', '.ts', '.tsx', '.css'}:
            continue
        if source_path.exists():
            content = source_path.read_text(encoding='utf-8')
            key = '../' + target
            language = {'.py': 'python', '.ts': 'typescript', '.tsx': 'tsx', '.css': 'css'}[source_path.suffix]
            files[key] = {'name': str(source_path.relative_to(REPO)).replace('\\', '/'), 'html': codebox(content, language)}

    # Detect stale source snapshots without embedding private/environment files.
    for key, entry in files.items():
        source_path = (COURSE / key).resolve()
        entry['sha256'] = hashlib.sha256(source_path.read_bytes()).hexdigest()

    # Local Markdown links become in-book navigation or embedded source viewers.
    def rewrite_links(markup: str, base: str = '') -> str:
        def link(match: re.Match) -> str:
            target, caption = html.unescape(match.group(1)), match.group(2)
            if target.startswith(('https://', 'http://')):
                return '<a href="' + escape(target) + '" target="_blank" rel="noopener noreferrer">' + caption + '</a>'
            path = target.split('#', 1)[0]
            resolved = posixpath.normpath(base + path)
            if resolved in source_ids:
                destination = source_ids[resolved]
                mode = ''
                fragment = unquote(target.partition('#')[2])
                if fragment and destination in by_id:
                    reference = by_id[destination]
                    # Normalize punctuation and accents, including Bài14.5 vs bài145.
                    normalize_anchor = lambda value: re.sub('[^a-z0-9]', '', slug(value))
                    matches = [i for i, entry in enumerate(reference['contents'])
                               if normalize_anchor(entry['title']) == normalize_anchor(fragment)]
                    if len(matches) == 1:
                        without_title = re.sub(r'<h1[^>]*>[\s\S]*?</h1>', '', reference['html'], count=1).strip()
                        intro = re.split(r'<h2\b', without_title, maxsplit=1)[0].strip()
                        mode = 'learn/' + str(matches[0] + bool(intro))
                href = '#lesson/' + destination if destination in by_id else '#' + destination
                return '<a href="' + href + ('/' + mode if mode else '') + '" data-go="' + destination + '"' + (' data-mode="' + mode + '"' if mode else '') + '>' + caption + '</a>'
            if resolved in files:
                return '<a href="#source" data-source="' + escape(resolved) + '">' + caption + '</a>'
            if path.startswith('#') or not path:
                return match.group(0)
            return '<span>' + caption + ' <small class="muted">(đường dẫn nguồn: ' + escape(target) + ')</small></span>'
        return re.sub(r'<a href="([^"]+)">(.*?)</a>', link, markup, flags=re.S)

    for lesson in lessons:
        lesson['html'] = rewrite_links(lesson['html'])
        without_title = re.sub(r'<h1[^>]*>[\s\S]*?</h1>', '', lesson['html'], count=1).strip()
        sections = []
        for part in re.split(r'(?=<h2\b)', without_title):
            if not part.strip():
                continue
            match = re.match(r'<h2[^>]*>(.*?)</h2>', part, flags=re.S)
            title = html.unescape(re.sub(r'<[^>]+>', '', match.group(1))) if match else 'Trước khi bắt đầu'
            section_body = part[match.end():] if match else part
            section = {'title': title, 'html': section_body.strip()}
            guidance = study.get('sections', {}).get(lesson['id'], {}).get(str(len(sections)))
            if guidance:
                section['study'] = guidance
            sections.append(section)
        lesson['sections'] = sections
        for index in study.get('sections', {}).get(lesson['id'], {}):
            assert int(index) < len(sections), (lesson['id'], index)
    knowledge = json.loads((COURSE / 'project-knowledge.json').read_text(encoding='utf-8'))
    levels = {'build': 'CỐT LÕI ĐỂ XÂY', 'release': 'CẦN TRƯỚC KHI CÓ USER',
              'later': 'TRA KHI CÓ NHU CẦU'}
    for lesson in lessons:
        lesson['knowledge'] = []
    for topic in knowledge:
        assert topic['level'] in levels, topic['id']
        topic['label'] = levels[topic['level']]
        topic['links'] = []
        for target in topic.pop('targets'):
            lesson = by_id[target['lesson']]
            matches = [i for i, section in enumerate(lesson['sections'])
                       if target['match'] in section['title']] if target['match'] else [0]
            assert len(matches) == 1, (topic['id'], target, matches)
            index = matches[0]
            section = lesson['sections'][index]
            section.setdefault('knowledge', []).append(topic['id'])
            if topic['id'] not in lesson['knowledge']:
                lesson['knowledge'].append(topic['id'])
            topic['links'].append({'lesson': lesson['id'], 'step': index})
        markup = ('<aside class="project-relevance relevance-' + topic['level']
                  + '"><div class="relevance-top"><span class="relevance-label">'
                  + escape(topic['label']) + '</span><span>DÙNG TRONG DỰ ÁN</span></div>'
                  + '<h3>' + escape(topic['name']) + '</h3><p><strong>Dùng ở đâu:</strong> '
                  + escape(topic['use']) + '</p><p><strong>Vì sao phải hiểu:</strong> '
                  + escape(topic['why']) + '</p><p class="relevance-proof"><strong>Tự làm được khi:</strong> '
                  + escape(topic['proof']) + '</p></aside>')
        for link in topic['links']:
            lesson = by_id[link['lesson']]
            section = lesson['sections'][link['step']]
            section['html'] = markup + section['html']
            if link['step'] == 0 and section['title'] == 'Trước khi bắt đầu':
                lesson['html'] = re.sub(r'(</h1>)', lambda match: match.group(0) + markup, lesson['html'], count=1)
            else:
                heading_match = next((entry for entry in lesson['contents'] if entry['title'] == section['title']), None)
                assert heading_match, (lesson['id'], section['title'])
                lesson['html'] = re.sub(r'(<h2 id="' + re.escape(heading_match['id']) + r'">.*?</h2>)',
                                        lambda match: match.group(0) + markup, lesson['html'], count=1, flags=re.S)
            lesson['search'] += ' ' + ' '.join([topic['name'], topic['use'], topic['why']])
    assert all(lesson['knowledge'] for lesson in lessons), 'Every lesson needs project relevance'
    data['knowledge'] = knowledge
    for key in files:
        if key == '../CODE_GUIDE.md':
            files[key]['html'] = rewrite_links(files[key]['html'], '../')
        elif key.endswith('.md'):
            parent = posixpath.dirname(key)
            files[key]['html'] = rewrite_links(files[key]['html'], parent + '/' if parent else '')
    data['files'] = files
    data['built_at'] = '22/10/2026'
    data['code_lines'] = [
        'async function onSubmit(data: LoginFormData) {',
        '  try {',
        '    const res = await authService.login(data);',
        "    localStorage.setItem('access_token', res.access_token);",
        '    if (res.must_change_password) {',
        "      navigate('/change-password');",
        '    } else {',
        "      navigate('/dashboard');",
        '    }',
        '  } catch (error) {',
        "    const message = error instanceof Error ? error.message : 'Đăng nhập thất bại';",
        "    setError('root', { message });",
        '  }',
        '}',
    ]
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    css = (COURSE / 'book.css').read_text(encoding='utf-8')
    script = '\n'.join((COURSE / name).read_text(encoding='utf-8') for name in
                       ['book-models.js', 'syntax-lab.js', 'study-coach.js', 'book.js'])
    document = '''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Giáo án tương tác để tự xây Vision Education LMS: cú pháp, bản chất, mô phỏng và bài tập.">
<title>Hiểu tận gốc · Giáo án Vision LMS</title><style>''' + css + '''</style></head>
<body><a class="skip-link" href="#main">Đến nội dung học</a>
<aside class="sidebar" id="sidebar" aria-label="Mục lục giáo án">
 <div class="brand"><div class="eyebrow">VISION / LEARNING NOTES</div><strong>Hiểu tận gốc.</strong><span>Sổ tay tự xây hệ thống LMS</span></div>
 <nav class="nav-scroll" id="navigation"></nav>
 <div class="side-progress"><div class="small" id="progress-label">Tiến độ tự đánh giá</div><div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div><small id="progress-detail"></small></div>
</aside>
<div class="shell"><header class="topbar">
 <button type="button" class="mobile-menu" id="menu-toggle" aria-controls="sidebar" aria-expanded="false" aria-label="Mở mục lục">☰</button>
 <span class="topbar-label">MỘT ĐIỀU MỖI LẦN. HIỂU RỒI TỰ VIẾT.</span>
 <button type="button" class="search-trigger" id="search-trigger">Tìm trong sách <kbd>/</kbd></button>
 <div class="top-actions"><button type="button" class="font-control" data-font="-1" aria-label="Giảm cỡ chữ">A−</button><button type="button" class="font-control" data-font="1" aria-label="Tăng cỡ chữ">A+</button><button type="button" id="focus-toggle" class="hide-small" aria-pressed="false">Tập trung</button><button type="button" id="theme-toggle" aria-pressed="false">Nền tối</button><button type="button" id="print-book">In / PDF</button></div>
</header><main class="workspace" id="main" tabindex="-1"><div id="storage-warning" class="save-warning" hidden></div><div id="view"></div></main></div>
<div id="toast" class="toast" role="status" hidden></div>
<div id="modal-overlay" class="overlay" hidden><section class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div class="modal-header"><h2 id="modal-title"></h2><button type="button" id="modal-close" aria-label="Đóng hộp thoại">Đóng ×</button></div><div id="modal-body"></div></section></div>
<div class="print-book" id="print-content" hidden></div>
<noscript><div class="noscript"><h1>Giáo án Vision LMS</h1><p>Bật JavaScript để dùng mục lục, mô phỏng và câu hỏi. Bản Markdown gốc nằm cùng thư mục, bắt đầu tại README.md.</p></div></noscript>
<script type="application/json" id="book-data">''' + payload + '''</script><script>''' + script + '''</script></body></html>'''
    OUTPUT.write_text(document, encoding='utf-8')
    print(f'Built {OUTPUT}: {OUTPUT.stat().st_size:,} bytes; {len(lessons)} lessons, '
          f'{sum(len(item["quiz"]) for item in lessons)} questions, '
          f'{sum(len(item["terms"]) for item in lessons)} memory cards; all assets inline.')


if __name__ == '__main__':
    build()
