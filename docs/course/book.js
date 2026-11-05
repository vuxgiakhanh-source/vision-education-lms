(function () {
  'use strict';
  const data = JSON.parse(document.getElementById('book-data').textContent);
  const M = window.BookModels;
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));
  const fold = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
  const key = 'vision-lms-book-v1';
  let storageAvailable = true;
  let stored = {};
  try { stored = JSON.parse(localStorage.getItem(key) || '{}') || {}; }
  catch { storageAvailable = false; }
  if (typeof stored !== 'object' || Array.isArray(stored)) stored = {};
  const objectOrEmpty = value => value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  const state = {
    completed: objectOrEmpty(stored.completed), notes: objectOrEmpty(stored.notes),
    answers: objectOrEmpty(stored.answers), checked: objectOrEmpty(stored.checked),
    review: objectOrEmpty(stored.review), theme: stored.theme === 'dark' ? 'dark' : 'light',
    skills: objectOrEmpty(stored.skills), evidence: objectOrEmpty(stored.evidence),
    drafts: objectOrEmpty(stored.drafts), designs: objectOrEmpty(stored.designs), drills: objectOrEmpty(stored.drills),
    reading: objectOrEmpty(stored.reading), lastLesson: typeof stored.lastLesson === 'string' ? stored.lastLesson : '',
    font: Math.max(16, Math.min(22, Number(stored.font) || 18)),
  };
  let route = { type: 'home' };
  let reviewIndex = 0, reviewRevealed = false, reviewFilter = 'all';
  let knowledgeFilter = 'all';
  let modalOrigin = null, toastTimer = 0;
  let workedLine = 0;
  const syntaxExercises = [
    { name: '1 · Hiển thị một số', code: 'console.log(2);', task: 'Chỉ đổi số 2 thành số 9. Dự đoán rồi bấm thử.', expected: '9' },
    { name: '2 · Tính một phép cộng', code: 'console.log(2 + 3);', task: 'Tự đổi hai số để kết quả là 8.', expected: '8' },
    { name: '3 · Chữ nằm trong dấu nháy', code: "console.log('An');", task: "Đổi An thành Bình, giữ dấu nháy mở/đóng.", expected: 'Bình' },
    { name: '4 · Tạo và đọc biến', code: 'let soBai = 2;\nconsole.log(soBai);', task: 'Đổi giá trị ban đầu để hiển thị 5. Không đặt nháy quanh soBai.', expected: '5' },
    { name: '5 · Đổi giá trị qua từng dòng', code: 'let diem = 7;\ndiem = diem + 1;\nconsole.log(diem);', task: 'Đổi dòng cộng để kết quả là 9; đọc giá trị trước/sau ở bảng.', expected: '9' },
    { name: '6 · Tự viết từ ô trống', code: '', task: 'Tạo soBai bằng 2, tăng thêm 1, hiển thị số mới rồi hiển thị soBai === 3.', expected: '3\ntrue' },
  ];
  let syntaxExercise = 0, syntaxDraft = syntaxExercises[0].code;
  const cssState = { display: 'block', direction: 'row', padding: '16', gap: '12' };
  const labState = { loginScenario: 'success', loginStep: 0, codeLine: 2, memory: 'shallow', memoryChanged: false,
    count: 0, countTrace: null, join: 'left', transactionStep: 0, split: false, fail: true };
  const labs = [
    ['syntax', 'Gõ những dòng đầu'],
    ['css', 'Thử CSS từ đầu'],
    ['login', 'Luồng đăng nhập'], ['memory', 'Tham chiếu'], ['state', 'React state'], ['join', 'SQL JOIN'],
    ['transaction', 'Transaction'], ['deadline', 'Hạn nộp & retry'], ['permission', 'Phân quyền'],
    ['http', 'HTTP & dữ liệu'], ['oop', 'Ghép đối tượng'], ['grading', 'Điểm & mẫu số'], ['layout', 'Viewport'],
  ];
  const cards = data.lessons.flatMap(lesson => lesson.terms.map((term, index) => ({
    id: lesson.id + ':' + index, lesson: lesson.id, chapter: lesson.short, term: term[0], definition: term[1],
  })));
  const primaryLessons = data.lessons.filter(lesson => lesson.primary);
  const mainLessons = primaryLessons.length ? primaryLessons : data.lessons;
  const referenceLessons = data.lessons.filter(lesson => !lesson.primary);
  const courseStages = data.course?.stages || [{ name: 'Đường học chính', lessons: mainLessons.map(lesson => lesson.id), outcome: 'Hiểu, tự viết và thử lại bằng yêu cầu mới.' }];
  const startLesson = data.course?.start || mainLessons[0].id;
  const lessonById = id => data.lessons.find(lesson => lesson.id === id);
  const completedIn = lessons => lessons.filter(lesson => state.completed[lesson.id]).length;

  function save() {
    if (!storageAvailable) return;
    try { localStorage.setItem(key, JSON.stringify(state)); }
    catch { storageAvailable = false; warnStorage(); }
  }
  function warnStorage() {
    if (!storageAvailable) {
      $('storage-warning').hidden = false;
      $('storage-warning').textContent = 'Trình duyệt không cho lưu trên máy ở chế độ này. Nội dung vẫn dùng được; hãy xuất ghi chú trước khi đóng.';
    }
  }
  function toast(message) {
    $('toast').textContent = message; $('toast').hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(() => { $('toast').hidden = true; }, 3000);
  }
  function applyPreferences() {
    document.body.classList.toggle('dark', state.theme === 'dark');
    document.documentElement.style.setProperty('--reading', state.font + 'px');
    $('theme-toggle').textContent = state.theme === 'dark' ? 'Nền sáng' : 'Nền tối';
    $('theme-toggle').setAttribute('aria-pressed', String(state.theme === 'dark'));
  }
  function navigate(type, id = '', mode = '') {
    const target = type === 'home' ? '#home' : '#' + type + (id ? '/' + id : '') + (mode ? '/' + mode : '');
    if (location.hash === target) renderRoute(true);
    else location.hash = target;
    closeMenu();
  }
  function closeMenu() { $('sidebar').classList.remove('open'); document.body.classList.remove('nav-open'); $('menu-toggle').setAttribute('aria-expanded', 'false'); }
  function navButton(label, type, id = '', number = '') {
    const active = route.type === type && (type !== 'lesson' || route.id === id);
    return `<button type="button" class="chapter-link" data-route="${type}" data-id="${id}" ${active ? 'aria-current="page"' : ''}><span class="chapter-num">${esc(number)}</span><span>${esc(label)}</span>${type === 'lesson' && state.completed[id] ? '<span class="done-dot" aria-label="Đã tự làm">✓</span>' : ''}</button>`;
  }
  function renderNav() {
    let content = '<div class="nav-mobile-heading"><span>Mục lục học tập</span><button type="button" data-close-menu aria-label="Đóng mục lục">Đóng ×</button></div>';
    content += '<div class="nav-utilities">' + navButton('Bàn học của tôi', 'home', '', '⌂') + navButton('Kiến thức dùng trong dự án', 'knowledge', '', '◇') + navButton('Mốc thực hành', 'path', '', '◎') + '</div><div class="nav-section-title">ĐƯỜNG HỌC CHÍNH</div>';
    for (const stage of courseStages) {
      content += `<div class="nav-group-label">${esc(stage.name)}</div>`;
      content += stage.lessons.map(id => lessonById(id)).filter(Boolean).map(lesson => navButton(lesson.short, 'lesson', lesson.id, lesson.number)).join('');
    }
    content += `<details class="reference-nav" ${route.type === 'lesson' && referenceLessons.some(lesson => lesson.id === route.id) ? 'open' : ''}><summary><span>Thư viện chuyên đề</span><span class="nav-count">${referenceLessons.length}</span></summary><p>Tra đúng lúc cần; không phải đọc hết trước khi bắt đầu.</p>${referenceLessons.map(lesson => navButton(lesson.short, 'lesson', lesson.id, lesson.number)).join('')}</details>`;
    content += '<div class="nav-section-title">CÔNG CỤ HỌC</div>' + navButton('Phòng thực hành', 'lab', '', '↔') + navButton('Ôn bằng thẻ nhớ', 'review', '', '↻') + navButton('Ghi chú & bản sao', 'notes', '', '≡');
    $('navigation').innerHTML = content;
    const total = mainLessons.length;
    const done = completedIn(mainLessons);
    $('progress-label').textContent = `${done} / ${total} bài chính đã tự làm`;
    $('progress-fill').style.width = done / total * 100 + '%';
    $('progress-detail').textContent = 'Tự đánh dấu bằng bài đã làm. Lưu trên trình duyệt này.';
  }

  function renderHome() {
    const resume = lessonById(state.lastLesson);
    const next = resume || mainLessons.find(lesson => !state.completed[lesson.id]) || lessonById(startLesson);
    const done = completedIn(mainLessons);
    const percentage = Math.round(done / mainLessons.length * 100);
    const resumeStep = Math.max(0, Math.min(Number(state.reading[next.id]) || 0, next.sections.length - 1));
    const stageForNext = courseStages.findIndex(stage => stage.lessons.includes(next.id));
    return `<div class="page home-page">
      <div class="home-kicker"><span><span class="status-dot"></span> KHÔNG GIAN HỌC CỦA BẠN</span><span>Từ nền Python · Học theo sản phẩm</span></div>
      <section class="hero studio-hero">
        <div class="hero-copy"><div class="eyebrow">HIỂU TỪNG BƯỚC. TỰ VIẾT TỪ ĐẦU.</div><h1>Từ một dòng code<br>đến <span class="hero-highlight">cả hệ thống.</span></h1><p class="page-lead">Bắt đầu từ Python mày đã biết. Tự dựng một trang web, hiểu cách chia code, rồi mở rộng thành LMS qua từng lần thay yêu cầu.</p><div class="button-row"><button type="button" class="primary hero-start" data-route="lesson" data-id="${startLesson}">Bắt đầu đường học mới <span aria-hidden="true">↗</span></button><button type="button" class="text-button" data-route="knowledge">Kiến thức nào dự án bắt buộc dùng? →</button></div><div class="hero-assurance"><span>Không cần biết React trước</span><span>Cú pháp được giải nghĩa</span><span>Tự làm rồi nhận phản hồi</span></div></div>
        <aside class="continue-panel" aria-labelledby="continue-title"><div class="continue-top"><span class="eyebrow">${resume ? 'ĐANG HỌC GẦN ĐÂY' : 'BUỔI HỌC ĐẦU TIÊN'}</span><span class="lesson-badge">${esc(next.number)}</span></div><h2 id="continue-title">${esc(next.short)}</h2><p>${esc(next.goal)}</p><div class="continue-position"><span>${resume ? `Bài nhỏ ${resumeStep + 1} / ${next.sections.length}` : 'Mỗi lần một ý, tự tay làm lại'}</span><span>${percentage}% đường học</span></div><div class="progress-track"><div class="progress-fill" style="width:${percentage}%"></div></div><button type="button" class="primary continue-button" data-route="lesson" data-id="${next.id}" data-mode="learn/${resumeStep}">${resume ? 'Tiếp tục buổi học' : 'Mở bài đầu tiên'} <span aria-hidden="true">→</span></button><small>${done} / ${mainLessons.length} bài chính tự đánh dấu đã làm được</small></aside>
      </section>
      <section class="learning-overview" aria-label="Cách dùng giáo án"><div><strong>${mainLessons.length}</strong><span>bài trên đường chính</span></div><div><strong>${referenceLessons.length}</strong><span>chuyên đề để tra cứu</span></div><div><strong>${labs.length}</strong><span>mô phỏng để thử</span></div><p>Đọc một ý.<br><strong>Tự làm một việc.</strong></p></section>
      <section class="course-roadmap" aria-labelledby="roadmap-title"><div class="section-heading"><div><div class="eyebrow">ĐƯỜNG HỌC CHÍNH</div><h2 id="roadmap-title">Biết hôm nay học gì.<br>Thấy mình đang đi tới đâu.</h2></div><p>Mỗi chặng có sản phẩm cần tự viết. Mở từng chặng, làm bài và giữ lại bằng chứng trước khi đi tiếp.</p></div><div class="stage-list">${courseStages.map((stage, index) => {
        const lessons = stage.lessons.map(lessonById).filter(Boolean);
        const stageDone = completedIn(lessons);
        const isCurrent = index === (stageForNext < 0 ? 0 : stageForNext);
        return `<details class="course-stage ${stageDone === lessons.length ? 'stage-done' : ''} ${isCurrent ? 'stage-current' : ''}" ${isCurrent ? 'open' : ''}><summary><span class="stage-number">${String(index).padStart(2, '0')}</span><span class="stage-summary"><strong>${esc(stage.name.replace(/^\d+\s*·\s*/, ''))}</strong><span>${esc(stage.outcome)}</span></span><span class="stage-status">${stageDone === lessons.length ? '✓ Đã tự làm' : `${stageDone} / ${lessons.length} bài`}</span><span class="stage-chevron" aria-hidden="true">+</span></summary><div class="stage-lessons">${lessons.map(lesson => `<a class="stage-lesson" href="#lesson/${lesson.id}"><span class="lesson-badge">${esc(lesson.number)}</span><span><strong>${esc(lesson.short)}</strong><small>${esc(lesson.deliverable || lesson.goal)}</small></span><span class="lesson-arrow" aria-hidden="true">${state.completed[lesson.id] ? '✓' : '↗'}</span></a>`).join('')}</div></details>`;
      }).join('')}</div></section>
      <section class="study-toolbox"><div class="section-heading"><div><div class="eyebrow">ĐỪNG ĐỂ MỘT CHỖ VƯỚNG CHẶN CẢ BUỔI</div><h2>Công cụ ở ngay đây.</h2></div></div><div class="toolbox-grid"><section><span class="toolbox-symbol" aria-hidden="true">&lt;/&gt;</span><h3>Gặp hàm hay ký hiệu lạ</h3><p>Tra đầu vào, đầu ra và tác dụng; thử một ví dụ nhỏ rồi quay lại bài.</p><button type="button" class="text-button" data-route="lesson" data-id="api-reading">Học cách tự tra →</button></section><section><span class="toolbox-symbol" aria-hidden="true">↔</span><h3>Muốn nhìn cơ chế chạy</h3><p>Đổi một điều kiện trong mô phỏng, dự đoán rồi quan sát điều gì thay đổi.</p><button type="button" class="text-button" data-route="lab">Mở phòng thực hành →</button></section><section><span class="toolbox-symbol" aria-hidden="true">↗</span><h3>Đưa bài học ra máy mình</h3><p>Tải xưởng thực hành và đi theo README để chạy từng phiên bản của Sổ lớp.</p>${data.studio_archive ? '<button type="button" class="text-button" data-download-studio>Tải xưởng thực hành .zip ↓</button>' : '<button type="button" class="text-button" data-source="examples/README.md">Mở ví dụ chạy được →</button>'}</section></div></section>
      <details class="reference-directory"><summary><span><span class="eyebrow">THƯ VIỆN CHUYÊN ĐỀ</span><strong>Cần sâu hơn ở đâu, mở đúng chỗ đó.</strong></span><span>${referenceLessons.length} chuyên đề <span aria-hidden="true">+</span></span></summary><p class="muted">Các bài tham khảo bổ sung cho đường học chính. Không cần đọc hết trước khi tự bắt đầu.</p><div class="chapter-directory">${referenceLessons.map(lesson => `<a class="directory-row" href="#lesson/${lesson.id}"><span class="chapter-num">${esc(lesson.number)}</span><span><strong>${esc(lesson.short)}</strong><small>${esc(lesson.goal)}</small></span></a>`).join('')}</div></details>
      <footer class="home-footer"><p>Tiến độ là tự đánh giá sau khi làm bài. Sách không tự chấm project riêng của mày; G6 chỉ cách đưa code đi review và sửa.</p><div><button type="button" class="text-button" data-source="VALIDATION.md">Phần đã kiểm tra ↗</button><button type="button" class="text-button" data-route="notes">Sao lưu ghi chú ↗</button></div><span>Ấn bản ${esc(data.built_at)} · Dùng được offline</span></footer>
    </div>`;
  }

  function essence(lesson) {
    return `<div class="essence"><div class="eyebrow">Vấn đề trước, cú pháp sau</div><div class="question-callout">${esc(lesson.question)}</div><p class="core-copy">${esc(lesson.core)}</p><h2>Cách nghĩ từng bước</h2><ol class="steps">${lesson.steps.map(step => `<li>${esc(step)}</li>`).join('')}</ol><h2>Ba khái niệm cần giữ</h2><div class="term-grid">${lesson.terms.map(term => `<div class="term"><code>${esc(term[0])}</code><p>${esc(term[1])}</p></div>`).join('')}</div><div class="trap"><strong>Chỗ dễ hiểu nhầm</strong>${esc(lesson.trap)}</div><div class="button-row"><button type="button" class="primary" data-route="lab" data-id="${lesson.lab}">Nhìn cơ chế chạy →</button><button type="button" data-reader-mode="read">Đọc bài giảng đầy đủ</button></div><h2>Tự viết lại</h2><ol class="exercise-list">${lesson.practice.map(item => `<li>${esc(item)}</li>`).join('')}</ol></div>`;
  }
  function quizMarkup(lesson, print = false) {
    return `<div class="quiz"><p class="muted">Chọn và giải thích trong đầu trước khi kiểm tra. Mỗi đáp án đều đi kèm lý do; ghi lại điều bạn dự đoán khác thực tế.</p>${lesson.quiz.map((quiz, index) => {
      const qKey = lesson.id + ':' + index;
      const selected = state.answers[qKey];
      const checked = state.checked[qKey];
      return `<section class="quiz-item"><div class="eyebrow">Câu ${index + 1}</div><h3>${esc(quiz.q)}</h3><div class="choices">${quiz.choices.map((choice, choiceIndex) => `<label class="choice"><input type="radio" name="quiz-${lesson.id}-${index}" data-quiz="${qKey}" value="${choiceIndex}" ${selected === choiceIndex ? 'checked' : ''}><span>${esc(choice)}</span></label>`).join('')}</div><div class="button-row no-print"><button type="button" data-check-quiz="${qKey}">Kiểm tra & hiểu lý do</button></div>${checked ? `<div class="quiz-feedback ${selected === quiz.correct ? '' : 'wrong'}" role="status"><strong>${selected === quiz.correct ? 'Đúng — hãy tự kể lại lý do.' : 'Cần xem lại — đáp án: ' + esc(quiz.choices[quiz.correct])}</strong>${esc(quiz.why)}</div>` : ''}<div class="print-answer">Đáp án: ${esc(quiz.choices[quiz.correct])}. ${esc(quiz.why)}</div></section>`;
    }).join('')}</div>`;
  }
  function reflection(lesson) {
    return `<section class="reflection"><label for="reflection-${lesson.id}">Giải thích bằng lời của mình: dữ liệu đi đâu, điều gì thay đổi và vì sao?</label><textarea id="reflection-${lesson.id}" data-note="${lesson.id}" placeholder="Ví dụ: ban đầu tôi nghĩ… Sau khi thử, tôi thấy… Nếu thay điều kiện…">${esc(typeof state.notes[lesson.id] === 'string' ? state.notes[lesson.id] : '')}</textarea><div class="save-status" id="note-status">Ghi chú được lưu trên trình duyệt này. Có thể xuất ở mục Ghi chú.</div></section>`;
  }
  function workedExample(lesson) {
    const example = data.teaching.examples[lesson.id];
    if (!example) return '';
    const line = Math.max(0,Math.min(workedLine,example.lines.length-1));
    const explanation = example.lines[line];
    return `<details class="worked-example" open><summary><span class="lesson-tag">ĐỌC CÙNG NHAU</span><strong>${esc(example.title)}</strong><span class="summary-hint">Bấm một dòng để hiểu</span></summary><div class="worked-body"><p>${esc(example.intro)}</p><div class="worked-grid"><div class="worked-code"><div class="codebar"><span>${esc(example.language)} · ví dụ học tập</span><button type="button" data-open-syntax>Hiểu ký hiệu</button></div><div class="worked-lines">${example.highlighted_lines.map((html,index)=>`<button type="button" class="worked-line ${line===index?'active':''}" data-worked-line="${index}" aria-pressed="${line===index}" aria-label="Giải thích dòng ${index+1}"><span class="worked-number">${index+1}</span><code>${html || ' '}</code></button>`).join('')}</div></div><div class="line-explanation" id="line-explanation" role="status"><div class="eyebrow">DÒNG ${line+1} · HIỂU TỪNG Ý</div><h3>${esc(explanation.title)}</h3><p>${esc(explanation.explanation)}</p><div class="value-observation"><span>Giá trị / điều cần quan sát</span><strong>${esc(explanation.value)}</strong></div></div></div><details class="trace-disclosure"><summary>Xem bảng theo dõi dữ liệu</summary><div class="table-scroll"><table><thead><tr>${example.trace.headers.map(t=>`<th>${esc(t)}</th>`).join('')}</tr></thead><tbody>${example.trace.rows.map(row=>`<tr>${row.map(cell=>`<td>${esc(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></details><div class="prediction"><span class="lesson-tag">DỪNG LẠI VÀ DỰ ĐOÁN</span><p>${esc(example.predict.question)}</p><details><summary>Mở giải thích sau khi tự trả lời</summary><p>${esc(example.predict.answer)}</p></details></div><div class="guided-exercises"><h3>Từ hiểu sang tự viết</h3><ol>${example.practice.map(item=>`<li>${esc(item)}</li>`).join('')}</ol></div></div></details>`;
  }
  function renderKnowledge() {
    const labels = { all: 'Tất cả', build: 'Cốt lõi để xây', release: 'Trước khi có user', later: 'Khi có nhu cầu' };
    const topics = data.knowledge.filter(topic=>knowledgeFilter === 'all' || topic.level === knowledgeFilter);
    return `<div class="page knowledge-page"><header class="reader-header"><div class="eyebrow">VISION LMS / HỌC ĐỂ DÙNG VÀO ĐÂU?</div><h1>Biết phần nào phải nắm.<br>Biết nó dùng ở đâu.</h1><p class="page-lead">Bản đồ ${data.knowledge.length} nhóm kiến thức gắn với LMS của mày. Cốt lõi để tự xây; phần trước khi có user học ở chặng phát hành. Cả hai đều cần trong phạm vi sản phẩm tương ứng.</p></header><div class="knowledge-context"><strong>Đúng với dự án đang làm</strong><p>React · TypeScript · Vite · Tailwind → HTTP/Axios → FastAPI · SQLAlchemy → MySQL/Alembic. Repo hiện có auth/me/đổi mật khẩu; lớp, giao/nộp/chấm bài là phần tiếp tục tự xây. Dashboard đang dùng dữ liệu mẫu.</p></div><div class="knowledge-filters" aria-label="Lọc theo lúc cần học">${Object.entries(labels).map(([value,label])=>`<button type="button" data-knowledge-filter="${value}" aria-pressed="${knowledgeFilter===value}">${esc(label)}</button>`).join('')}</div><div class="knowledge-cards">${topics.map(topic=>`<section class="project-relevance relevance-${topic.level}"><div class="relevance-top"><span class="relevance-label">${esc(topic.label)}</span><span>DÙNG TRONG DỰ ÁN</span></div><h2>${esc(topic.name)}</h2><p><strong>Dùng ở đâu:</strong> ${esc(topic.use)}</p><p><strong>Vì sao phải hiểu:</strong> ${esc(topic.why)}</p><p class="relevance-proof"><strong>Tự làm được khi:</strong> ${esc(topic.proof)}</p><div class="knowledge-links">${topic.links.map(link=>{ const lesson=lessonById(link.lesson);return `<button type="button" data-route="lesson" data-id="${lesson.id}" data-mode="learn/${link.step}">${esc(lesson.number)} · ${esc(lesson.short)} ↗</button>`; }).join('')}</div></section>`).join('')}</div></div>`;
  }
  function knowledgeSummary(lesson) {
    const topics = data.knowledge.filter(topic=>lesson.knowledge.includes(topic.id));
    return `<details class="knowledge-summary"><summary><strong>${topics.length} nhóm kiến thức bài này dùng trong dự án</strong><span>Mở để biết học làm gì ↓</span></summary><ul>${topics.map(topic=>`<li><span class="mini-priority relevance-${topic.level}">${esc(topic.label)}</span><strong>${esc(topic.name)}</strong><p>${esc(topic.use)}</p></li>`).join('')}</ul><button type="button" class="text-button" data-route="knowledge">Xem bản đồ kiến thức toàn dự án →</button></details>`;
  }
  function studyPriorities(study, scope = 'SAU BÀI NÀY') {
    if (!study) return '';
    return `<section class="study-priorities" aria-label="Điều cần nhớ, cần làm và cách kiểm"><div class="priority-heading"><span class="eyebrow">${esc(scope)}</span><span>Đọc → tự viết → tự kiểm</span></div><div class="priority-grid"><div class="priority-key"><span class="priority-number">01</span><h3>Cần nhớ</h3><p>${esc(study.remember)}</p></div><div><span class="priority-number">02</span><h3>Phải tự làm</h3><p>${esc(study.do)}</p></div><div><span class="priority-number">03</span><h3>Cách kiểm</h3><p>${esc(study.proof)}</p></div></div></section>`;
  }
  function focusLesson(lesson, print = false) {
    const { syntax, architecture } = lesson.focus;
    const draft = typeof state.drafts[lesson.id] === 'string' ? state.drafts[lesson.id] : '';
    const design = typeof state.designs[lesson.id] === 'string' ? state.designs[lesson.id] : '';
    const markup = `<div class="focus-clinic"><section class="syntax-clinic"><div class="clinic-heading"><span class="clinic-icon" aria-hidden="true">{ }</span><div><span class="eyebrow">01 / HIỂU CÁCH VIẾT</span><h2>Mổ xẻ một cấu trúc.</h2></div></div><p class="clinic-intro">Đọc từng mảnh, ghép lại thành một câu. Mẫu nhỏ này để phân tích; bài tự viết nằm bên dưới.</p>${syntax.html}<dl class="syntax-parts">${syntax.parts.map(([token,meaning])=>`<div><dt><code>${esc(token)}</code></dt><dd>${esc(meaning)}</dd></div>`).join('')}</dl><aside class="teaching-callout callout-key"><strong class="callout-label">ĐIỀU CẦN GIỮ</strong><p>${esc(syntax.rule)}</p></aside><aside class="teaching-callout callout-warning"><strong class="callout-label">CHỖ DỄ SAI</strong><p>${esc(syntax.trap)}</p></aside></section><section class="architecture-clinic"><div class="clinic-heading"><span class="clinic-icon" aria-hidden="true">↳</span><div><span class="eyebrow">02 / HIỂU CÁCH CHIA HỆ THỐNG</span><h2>Theo trách nhiệm, tìm nơi sửa.</h2></div></div><ol class="architecture-flow" aria-label="Các bước hoặc trách nhiệm cần lần theo">${architecture.nodes.map((node,index)=>`<li><span>${String(index+1).padStart(2,'0')}</span><strong>${esc(node)}</strong></li>`).join('')}</ol><p>${esc(architecture.decision)}</p><div class="design-question"><span class="eyebrow">THAY YÊU CẦU THỬ XEM</span><p>${esc(architecture.question)}</p></div><label class="draft-label" for="design-${lesson.id}">Tự phân chia: nơi sửa → lý do → cách kiểm</label><textarea class="design-draft" id="design-${lesson.id}" data-design-draft="${lesson.id}" maxlength="20000" placeholder="Tự đề xuất trước khi mở source. Ghi tên trách nhiệm, chưa cần đoán hết tên file.">${esc(design)}</textarea></section><section class="self-write-panel"><div class="clinic-heading"><span class="clinic-icon" aria-hidden="true">✎</span><div><span class="eyebrow">03 / ĐÓNG MẪU, TỰ VIẾT</span><h2>Đến lượt mày chọn cách làm.</h2></div></div><p>${esc(syntax.task)}</p><label class="draft-label" for="draft-${lesson.id}">Bản nháp của mày · code, pseudocode hoặc bảng vết</label><textarea class="syntax-editor" id="draft-${lesson.id}" data-focus-draft="${lesson.id}" maxlength="20000" spellcheck="false" placeholder="Bắt đầu từ ô trống. Viết đầu vào/đầu ra, rồi tự chọn cú pháp.">${esc(draft)}</textarea><p class="draft-caption" id="focus-save-status">Bản nháp lưu trên trình duyệt này và có trong Xuất ghi chú. Ô này không chạy/chấm code; chạy trong môi trường của bài.</p><div class="self-check"><strong>Đối chiếu sau khi tự làm</strong><p>${esc(syntax.check)}</p><p>Đổi một input và giải thích lại từng dòng. Tự kiểm cả lỗi và nhánh biên.</p></div></section></div>`;
    if (!print) return markup;
    return markup.replace(/\s(?:id|for)="[^"]*"/g, '')
      .replace(/<textarea[^>]*>([\s\S]*?)<\/textarea>/g, '<pre class="printed-draft">$1</pre>');
  }
  function lessonDrill(lesson, index, drill) {
    if (!drill) return '';
    const key = lesson.id + ':' + index;
    const draft = typeof state.drills[key] === 'string' ? state.drills[key] : drill.starter;
    return `<section class="inline-drill" aria-labelledby="drill-title"><div class="eyebrow">THỬ NGAY / KHÔNG CẦN RỜI BÀI</div><h3 id="drill-title">Tự gõ để thấy mình hiểu đến đâu.</h3><p id="drill-task">${esc(drill.task)}</p><p class="drill-target">Output cần có: <code>${esc(drill.output.join(' · '))}</code></p><label class="draft-label" for="lesson-drill-code">Code mày tự viết</label><textarea class="syntax-editor" id="lesson-drill-code" data-drill-draft="${key}" maxlength="4000" spellcheck="false" aria-describedby="drill-task drill-limit">${esc(draft)}</textarea><div class="button-row"><button type="button" class="primary" data-run-drill>Chạy và xem từng bước →</button></div><details class="drill-hint"><summary>Kẹt một chỗ? Mở gợi ý</summary><p>${esc(drill.hint)}</p></details><p id="drill-limit" class="draft-caption">Bộ luyện giới hạn: let/const, gán, số/chuỗi/boolean, phép tính, so sánh, console.log một giá trị; cần dấu ;. Không chạy if/for/hàm, TS, DOM hay request.</p><div id="drill-feedback" class="drill-feedback" role="status" aria-live="polite">Chưa chạy. Dự đoán output trước.</div><div id="drill-trace"></div></section>`;
  }
  function activeDrill() {
    if (route.type !== 'lesson' || ['read', 'essence', 'quiz'].includes(route.mode)) return null;
    const lesson = lessonById(route.id);
    if (!lesson) return null;
    const index = state.reading[lesson.id] || 0;
    const drill = lesson.sections[index]?.study?.drill;
    return drill ? { drill, key: lesson.id + ':' + index } : null;
  }
  function runLessonDrill() {
    const active = activeDrill();
    if (!active) return;
    const source = $('lesson-drill-code').value;
    state.drills[active.key] = source; save();
    const result = window.SyntaxLab.run(source);
    const feedback = window.StudyCoach.assess(active.drill, result);
    $('drill-feedback').textContent = feedback.message + (result.ok ? '\nOutput: ' + (result.output.join(' · ') || '(trống)') : '\n' + result.error);
    $('drill-feedback').setAttribute('data-result', feedback.matches ? 'match' : 'retry');
    $('drill-trace').innerHTML = result.trace.length ? `<div class="table-scroll"><table><caption>Giá trị sau từng câu lệnh</caption><thead><tr><th>Dòng</th><th>Thao tác</th><th>Biến</th></tr></thead><tbody>${result.trace.map(step=>`<tr><td>${step.line}</td><td>${esc(step.action)}</td><td><code>${esc(JSON.stringify(step.variables))}</code></td></tr>`).join('')}</tbody></table></div>` : '';
  }
  function guidedLesson(lesson) {
    const sections = lesson.sections;
    const requested = route.step === '' || route.step === undefined ? state.reading[lesson.id] : Number(route.step);
    const index = Number.isInteger(requested) ? Math.max(0,Math.min(requested,sections.length-1)) : 0;
    const section = sections[index];
    const example = data.teaching.examples[lesson.id];
    const exampleStep = example ? sections.findIndex(s=>s.title.includes(example.section)) : -1;
    if (state.reading[lesson.id] !== index || state.lastLesson !== lesson.id) {
      state.reading[lesson.id] = index; state.lastLesson = lesson.id; save();
    }
    return `<div class="guided-layout"><div class="lesson-canvas"><div class="step-toolbar"><span class="step-position">BÀI NHỎ <strong>${String(index+1).padStart(2,'0')}</strong> / ${sections.length}</span><label class="section-selector"><span class="sr-only">Chọn bài nhỏ</span><select id="lesson-section" aria-label="Chọn bài nhỏ">${sections.map((s,i)=>`<option value="${i}" ${index===i?'selected':''}>${i+1}. ${esc(s.title)}</option>`).join('')}</select></label></div><div class="lesson-track" aria-label="Vị trí đang đọc trong bài"><span style="width:${(index+1)/sections.length*100}%"></span></div><section class="lesson-sheet"><div class="sheet-heading"><span class="lesson-tag">MỖI LẦN MỘT Ý</span><h2>${esc(section.title)}</h2></div>${index===0 ? `<div class="lesson-context"><strong>Câu hỏi dẫn đường</strong><p>${esc(lesson.question)}</p></div>${exampleStep > 0 ? `<button type="button" class="example-jump" data-learning-step="${exampleStep}">Ví dụ giải thích từng dòng · bài nhỏ ${exampleStep+1} ↗</button>` : ''}` : ''}${section.study ? studyPriorities(section.study, "VIỆC CỦA MỤC NÀY") : ''}${index===0 ? '<button type="button" class="focus-jump" data-reader-mode="essence">Mổ xẻ cú pháp & kiến trúc của bài này ↗</button>' : ''}${index===exampleStep ? workedExample(lesson) : ''}<article class="article guided-article">${section.html}</article>${lessonDrill(lesson,index,section.study?.drill)}<div class="step-reflection"><strong>Trước khi đi tiếp</strong><p>Tự kể lại ý chính bằng một câu. Với đoạn code, chỉ ra đầu vào, giá trị thay đổi và kết quả trước khi chạy.</p><button type="button" class="ghost small" data-scroll="reflection-${lesson.id}">Ghi lại cách mình hiểu ↓</button></div></section><div class="step-controls"><button type="button" data-learning-step="${index-1}" ${index===0?'disabled':''}>← Bài nhỏ trước</button><span>${index+1} / ${sections.length} · vị trí đọc</span>${index<sections.length-1 ? `<button type="button" class="primary" data-learning-step="${index+1}">Tiếp tục từng bước →</button>` : '<button type="button" class="primary" data-reader-mode="quiz">Tự kiểm tra bài này →</button>'}</div></div><aside class="lesson-rail" aria-label="Các bài nhỏ"><div class="eyebrow">ĐƯỜNG ĐI TRONG BÀI</div><p>Chọn một ý để đọc. Mở bài chưa có nghĩa đã làm được bài.</p><nav>${sections.map((s,i)=>`<button type="button" data-learning-step="${i}" ${index===i?'aria-current="step"':''}><span>${String(i+1).padStart(2,'0')}</span>${esc(s.title)}</button>`).join('')}</nav><button type="button" class="syntax-helper" data-open-syntax>Gặp ký hiệu lạ?<span>Mở sổ tra cú pháp ↗</span></button></aside></div>`;
  }
  function renderLesson(id, mode) {
    const lesson = lessonById(id) || lessonById(startLesson);
    const sequence = lesson.primary ? mainLessons : referenceLessons;
    const index = sequence.indexOf(lesson);
    const previous = sequence[index - 1], next = lesson.id === 'zero' ? lessonById('bridge') : sequence[index + 1];
    const stageIndex = courseStages.findIndex(stage => stage.lessons.includes(lesson.id));
    const selected = ['read', 'quiz', 'essence'].includes(mode) ? mode : 'learn';
    if (state.lastLesson !== lesson.id) { state.lastLesson = lesson.id; save(); }
    const contract = `<section class="learning-contract"><div><div class="eyebrow">HỌC TRƯỚC</div><div class="prerequisite-links">${(lesson.prerequisites || []).length ? lesson.prerequisites.map(id => {
      const dependency = lessonById(id);
      return dependency ? `<button type="button" data-route="lesson" data-id="${id}">${esc(dependency.short)} ↗</button>` : '';
    }).join('') : '<span class="small muted">Có thể bắt đầu ở bài này.</span>'}</div></div><div><div class="eyebrow">BẰNG CHỨNG SAU BÀI</div><p>${esc(lesson.deliverable || lesson.practice[0])}</p><button class="ghost small" type="button" data-route="path">Đối chiếu mốc thực hành →</button></div></section>`;
    let body;
    if (selected === 'read') {
      body = `<div class="reader-grid"><article class="article full-article">${lesson.html.replace(/<h1[^>]*>[\s\S]*?<\/h1>/, '')}</article><aside class="contents" aria-label="Nội dung bài"><strong>Trong bài này</strong>${lesson.contents.map(section => `<a href="#${section.id}" data-scroll="${section.id}">${esc(section.title)}</a>`).join('')}</aside></div>`;
    } else if (selected === 'learn') body = guidedLesson(lesson);
    else body = selected === 'quiz' ? quizMarkup(lesson) : focusLesson(lesson) + '<details class="essence-disclosure"><summary>Xem thêm bản đồ khái niệm và câu hỏi</summary>' + essence(lesson) + '</details>';
    body = `<details class="prerequisite-disclosure"><summary>Mục tiêu và kiến thức cần có trước bài</summary>${contract}</details>` + body;
    const references = (lesson.references || []).map(lessonById).filter(Boolean);
    if (!lesson.primary) body = `<section class="reference-orientation"><div><strong>Đây là chuyên đề để tra cứu.</strong><p>Đường học mới bắt đầu ở G0, dẫn từ nền Python đến tự viết và chia cấu trúc dự án.</p></div><button type="button" class="primary" data-route="lesson" data-id="${startLesson}">Bắt đầu từ G0 →</button></section>` + body;
    return `<div class="page lesson-page ${lesson.primary ? 'primary-lesson' : 'reference-lesson'}"><header class="reader-header"><div class="lesson-breadcrumb"><button type="button" class="text-button" data-route="home">Bàn học</button><span aria-hidden="true">/</span><span>${lesson.primary ? `Đường chính · chặng ${Math.max(0,stageIndex)}` : 'Thư viện chuyên đề'}</span><span class="lesson-badge">${esc(lesson.number)}</span></div><h1>${esc(lesson.title)}</h1><p class="page-lead">${esc(lesson.goal)}</p><div class="reader-meta"><span><span class="status-dot"></span> ${lesson.sections.length} bài nhỏ · đọc, tự viết và kiểm</span><button type="button" class="text-button" data-route="lab" data-id="${lesson.lab}">Thử bằng mô phỏng ↗</button></div></header><div class="reading-tabs" aria-label="Cách học chương"><button type="button" data-reader-mode="learn" aria-pressed="${selected === 'learn'}">Học từng bước</button><button type="button" data-reader-mode="essence" aria-pressed="${selected === 'essence'}">Cú pháp & kiến trúc</button><button type="button" data-reader-mode="read" aria-pressed="${selected === 'read'}">Toàn bộ bài</button><button type="button" data-reader-mode="quiz" aria-pressed="${selected === 'quiz'}">Tự kiểm tra</button></div>${studyPriorities(lesson.study)}${knowledgeSummary(lesson)}${body}${references.length ? `<section class="context-references" aria-label="Đọc sâu khi cần"><div><span class="eyebrow">ĐỌC SÂU KHI CẦN</span><p>Vướng phần nào, mở chuyên đề đó rồi quay lại bài đang làm.</p></div><div>${references.map(reference => `<button type="button" data-route="lesson" data-id="${reference.id}"><span>${esc(reference.number)}</span>${esc(reference.short)} ↗</button>`).join('')}</div></section>` : ''}${reflection(lesson)}<label class="completion"><input type="checkbox" data-complete="${lesson.id}" ${state.completed[lesson.id] ? 'checked' : ''}><span><strong>Tôi đã tự giải thích và làm lại được bài này.</strong><span>Đánh dấu sau khi tự viết và xử lý biến thể. Tiến độ này do bạn tự đánh giá.</span></span></label><nav class="pager" aria-label="Chuyển bài trong ${lesson.primary ? 'đường chính' : 'thư viện'}">${previous ? `<button type="button" data-route="lesson" data-id="${previous.id}"><small>← BÀI TRƯỚC</small><span>${esc(previous.short)}</span></button>` : '<button type="button" data-route="home"><small>← QUAY LẠI</small><span>Bàn học của tôi</span></button>'}${next ? `<button type="button" class="pager-next" data-route="lesson" data-id="${next.id}"><small>BÀI TIẾP THEO →</small><span>${esc(next.short)}</span></button>` : `<button type="button" class="pager-next" data-route="${lesson.primary ? 'path' : 'home'}"><small>${lesson.primary ? 'ĐỐI CHIẾU SẢN PHẨM' : 'TRỞ VỀ BÀN HỌC'} →</small><span>${lesson.primary ? 'Xem lại mốc thực hành' : 'Chọn chặng học tiếp'}</span></button>`}</nav></div>`;
  }

  const codeExplanation = [
    ['Khai báo hàm async và tham số', 'Data là đầu vào của lần gọi. LoginFormData là mô tả kiểu TypeScript. Khai báo hàm chưa tự chạy nghiệp vụ.', 'Hãy tìm handleSubmit(onSubmit) trong form.'],
    ['Mở phạm vi try', 'Các lỗi được ném trong quá trình này, kể cả tại await, có thể chuyển luồng đến catch tương ứng.', 'Phân biệt lỗi được catch với lỗi bị nuốt và báo thành công giả.'],
    ['Await giá trị hàm thực sự trả', 'AuthService.login gọi Axios rồi return res.data. Vì vậy res ở đây là LoginResponse, không phải response có status/header.', 'Nếu bỏ await, res là Promise; đọc access_token ngay không có ý nghĩa như mong muốn.'],
    ['Ghi token sau khi thành công', 'Dòng này chỉ chạy nếu await không ném lỗi. Đây là trạng thái ở trình duyệt, chưa phải bằng chứng quyền truy cập mọi dữ liệu.', 'Trong mô phỏng, token không được tạo hoặc ghi thật.'],
    ['Chọn nhánh theo cờ backend', 'Cờ must_change_password nói luồng tiếp theo. Backend vẫn phải có chính sách kiểm soát tài khoản cần đổi mật khẩu.', 'Đổi URL thủ công không được tự vượt quy tắc phía server.'],
    ['Đi tới trang đổi mật khẩu', 'Navigate điều khiển route frontend. Nó không thay thế thao tác đổi mật khẩu hoặc cấp quyền backend.', 'Tìm nơi repository đặt lại cờ sau khi đổi mật khẩu.'],
    ['Nhánh còn lại', 'Else chạy khi điều kiện if không đúng. Trong hợp đồng này cờ là boolean từ response hợp lệ.', 'Dữ liệu mạng sai kiểu không tự được TypeScript chữa lại.'],
    ['Đi tới dashboard', 'Trang hiện tại còn dùng dữ liệu mock. Đi tới được trang chưa chứng minh đã gọi /me và lấy lớp thật.', 'Đọc StudentDashboardPage để xem nguồn dữ liệu.'],
    ['Kết thúc nhánh', 'Dấu ngoặc đóng một khối, không phải ký hiệu trang trí. Thụt lề giúp nhìn quan hệ các nhánh.', 'Tự viết lại if/else với một điều kiện khác.'],
    ['Lỗi chuyển vào catch', 'Khi Promise reject tại await, các dòng còn lại trong try bị bỏ qua. Catch nhận lỗi để xử lý theo hợp đồng.', 'Không coi mọi lỗi mạng là mật khẩu sai hoặc hết phiên.'],
    ['Thu hẹp kiểu lỗi', 'Instanceof kiểm tra trước khi đọc message. Thông báo hiện tại chưa ánh xạ đầy đủ detail của backend.', 'Đề xuất mapping lỗi riêng; không trả 200 cho mọi thất bại.'],
    ['Đưa lỗi về form', 'SetError cập nhật trạng thái lỗi của form. { message } là shorthand cho { message: message }.', 'Tìm vị trí errors.root được render.'],
    ['Đóng catch', 'Kết thúc phạm vi xử lý lỗi. Hàm có thể kết thúc mà không điều hướng.', 'Mô tả trạng thái UI sau nhánh lỗi.'],
    ['Đóng hàm', 'Một lần gọi hoàn tất. Vì là async, bên gọi nhận Promise phản ánh kết quả.', 'Tự kể lại toàn bộ đường chạy không nhìn code.'],
  ];
  function labHeader(title, description) {
    return `<div class="lab-heading"><div><h2>${title}</h2><p>${description}</p></div></div>`;
  }
  const field = (label, id, choices, value) => `<label class="field">${label}<select id="${id}" aria-label="${esc(label)}">${choices.map(([v, text]) => `<option value="${v}" ${String(v) === String(value) ? 'selected' : ''}>${text}</option>`).join('')}</select></label>`;
  const checkbox = (label, id, checked) => `<label class="field check"><input type="checkbox" id="${id}" ${checked ? 'checked' : ''}>${label}</label>`;
  const listRows = (items, draft = false) => `<ul class="db-rows">${items.length ? items.map(item => `<li class="${draft ? 'draft' : ''}">${esc(item)}</li>`).join('') : '<li class="muted">Chưa có hàng</li>'}</ul>`;

  function loginLab() {
    const trace = M.loginTrace(labState.loginScenario);
    const step = trace[labState.loginStep];
    const explanation = codeExplanation[labState.codeLine];
    return labHeader('Một request đi đâu?', 'Chọn tình huống, đi từng bước rồi bấm từng dòng code để hiểu cú pháp. Đây là mô phỏng đường chạy, không gửi request hay ghi token thật.') + `<div class="lab-controls">${field('Tình huống', 'login-scenario', [['success','Đúng, không bắt đổi mật khẩu'],['change','Đúng, phải đổi mật khẩu'],['wrong','Sai mật khẩu'],['locked','Tài khoản bị khóa']], labState.loginScenario)}<button type="button" data-lab-action="login-prev" ${labState.loginStep === 0 ? 'disabled' : ''}>← Bước trước</button><button type="button" class="primary" data-lab-action="login-next" ${labState.loginStep === trace.length - 1 ? 'disabled' : ''}>Bước tiếp →</button><span class="trace-step">${labState.loginStep + 1} / ${trace.length}</span></div><div class="flow">${['TRÌNH DUYỆT','FASTAPI / SERVICE','REPOSITORY / MYSQL'].map((lane, index) => `<section class="flow-lane ${step.lane === index ? 'active' : ''}"><h3>${lane}</h3><div class="flow-box"><strong>${step.lane === index ? esc(step.title) : 'Chờ đến bước của lớp này'}</strong><div class="payload">${step.lane === index ? esc(step.payload) : index === 0 ? 'Form → client API → UI' : index === 1 ? 'Schema → router → quy tắc' : 'Session → query → User'}</div></div></section>`).join('')}</div><div class="trace-step">${esc(step.label)}</div><p class="trace-explanation">${esc(step.text)}</p><div class="code-explain-grid"><div class="codebox"><div class="codebar"><span>LoginForm · cấu trúc rút gọn</span><span>Bấm dòng để hiểu</span></div><div class="code-lines">${data.code_lines.map((line, index) => `<button type="button" class="trace-line ${labState.codeLine === index ? 'active' : ''}" data-code-line="${index}" aria-pressed="${labState.codeLine === index}"><span class="line-number">${index + 1}</span><span>${esc(line)}</span></button>`).join('')}</div></div><div class="lab-panel"><div class="eyebrow">DÒNG ${labState.codeLine + 1}</div><h3>${esc(explanation[0])}</h3><p>${esc(explanation[1])}</p><div class="trap"><strong>Tự hỏi thêm</strong>${esc(explanation[2])}</div><button type="button" data-route="lesson" data-id="first" data-mode="read">Đọc toàn bộ bài mẫu →</button></div></div>`;
  }
  function memoryLab() {
    const model = M.memory(labState.memory, labState.memoryChanged);
    const snippets = { alias: 'const b = a;\nb[0].status = \'submitted\';', shallow: 'const b = [...a];\nb[0].status = \'submitted\';', immutable: 'const b = a.map(item => ({ ...item }));\nb[0].status = \'submitted\';' };
    return labHeader('Container mới chưa chắc object mới', 'Ban đầu a = [{ id: 1, status: pending }]. Chọn cách tạo b, dự đoán a có đổi không, rồi thực hiện dòng thay đổi.') + `<div class="lab-controls">${field('Cách tạo b', 'memory-strategy', [['alias','b = a'],['shallow','b = [...a]'],['immutable','Array mới + object mới']],labState.memory)}<button type="button" class="primary" data-lab-action="memory-change">Chạy b[0].status = submitted</button><button type="button" data-lab-action="memory-reset">Đặt lại</button></div><div class="lab-two"><div class="lab-panel"><h3>Biến a · dữ liệu gốc</h3><div class="object-pointer">a → ${model.arrayA} → ${model.objectA}</div><div class="object-box">id: 1<br>status: <strong>${model.originalStatus}</strong></div></div><div class="lab-panel"><h3>Biến b · phần bạn đang sửa</h3><div class="object-pointer">b → ${model.arrayB} → ${model.objectB}</div><div class="object-box">id: 1<br>status: <strong>${model.copyStatus}</strong></div></div></div><div class="queue">${esc(snippets[labState.memory]).replace(/\n/g, '<br>')}</div><div class="outcome ${model.shared && labState.memoryChanged ? 'bad' : ''}"><strong>${!labState.memoryChanged ? 'Chưa chạy dòng thay đổi' : model.shared ? 'Bản gốc cũng thay đổi' : 'Bản gốc được giữ nguyên'}</strong><p>${model.shared ? 'Hai đường đi vẫn đến cùng Object 1. Const chỉ ngăn gán lại biến; spread array không tự sao chép object bên trong.' : 'Bây giờ b trỏ đến Object 2 mới. Với dữ liệu lồng sâu hơn, vẫn cần suy nghĩ nhánh nào đang chung tham chiếu.'}</p></div>`;
  }
  function stateLab() {
    return labHeader('Snapshot và hàng đợi cập nhật', 'Mô hình này minh họa hàng đợi setState; nó không chạy một React renderer trong sách. Hãy dự đoán trước khi bấm.') + `<div class="lab-two"><div class="lab-panel"><div class="eyebrow">COUNT HIỆN TẠI</div><div class="number-big">${labState.count}</div><p>Mỗi handler bắt đầu từ một snapshot của count.</p><div class="button-row"><button type="button" data-lab-action="state-replace">Hai lần setCount(count + 1)</button><button type="button" class="primary" data-lab-action="state-updater">Hai lần setCount(p ⇒ p + 1)</button><button type="button" data-lab-action="state-reset">Đặt về 0</button></div></div><div class="lab-panel"><h3>Đọc từng yêu cầu trong hàng đợi</h3>${labState.countTrace ? `<ol>${labState.countTrace.trace.map(line => `<li>${esc(line)}</li>`).join('')}</ol><p><strong>Kết quả: ${labState.countTrace.result}</strong></p>` : '<p class="muted">Chưa chạy. Bắt đầu từ 0, hãy dự đoán hai nút sẽ cho kết quả gì.</p>'}</div></div><div class="trap"><strong>Bản chất</strong>Biểu thức count + 1 dùng cùng giá trị count của handler hiện tại. Updater nhận giá trị trước nó trong hàng đợi, nên mô tả được hai lần cộng liên tiếp.</div>`;
  }
  function joinLab() {
    const result = M.join(labState.join);
    const tail = labState.join === 'missing' ? '\nWHERE s.id IS NULL' : '';
    return labHeader('Tìm người chưa nộp bằng LEFT JOIN', 'Fixture học tập: lớp có An, Bình, Chi; chỉ An có submission #11. Các quan hệ này được tính cục bộ, không chạy query MySQL.') + `<div class="lab-controls">${field('Phép ghép', 'join-mode', [['inner','INNER JOIN'],['left','LEFT JOIN'],['missing','LEFT JOIN + s.id IS NULL']],labState.join)}</div><div class="lab-two"><div class="lab-panel"><h3>Tập học sinh cần xét</h3><table><thead><tr><th>student_id</th><th>Học sinh</th></tr></thead><tbody><tr><td>1</td><td>An</td></tr><tr><td>2</td><td>Bình</td></tr><tr><td>3</td><td>Chi</td></tr></tbody></table><p class="small muted">Submission duy nhất: id 11, student_id 1.</p></div><div class="lab-panel"><h3>Kết quả ${esc(labState.join)}</h3><table><thead><tr><th>Học sinh</th><th>s.id</th></tr></thead><tbody>${result.rows.map(row => `<tr><td>${row.name}</td><td class="${row.submissionId === null ? 'null-cell' : ''}">${row.submissionId ?? 'NULL'}</td></tr>`).join('')}</tbody></table><div class="button-row"><span class="pill">COUNT(*) = ${result.countStar}</span><span class="pill rust">COUNT(s.id) = ${result.countSubmission}</span></div></div></div><div class="queue">${labState.join === 'inner' ? 'INNER' : 'LEFT'} JOIN submissions s<br>ON s.student_id = m.user_id AND s.assignment_id = :assignment_id${esc(tail).replace(/\n/g,'<br>')}</div><p class="trace-explanation">${labState.join === 'inner' ? 'INNER JOIN loại Bình và Chi vì không có bản nộp tương ứng. Vì thế bạn không tìm được người chưa nộp nếu bắt đầu chỉ từ các hàng đã khớp.' : labState.join === 'left' ? 'LEFT JOIN giữ đủ ba học sinh. NULL là dấu hiệu không có submission khớp; COUNT(s.id) bỏ các NULL nên cho 1 thay vì 3.' : 'Giữ hàng không khớp bằng s.id IS NULL. Tập này chính là người chưa có bài nộp trong phạm vi fixture đã chọn.'}</p>`;
  }
  function transactionLab() {
    const model = M.transaction(labState.transactionStep, labState.split, labState.fail);
    const descriptions = ['Chưa ghi: hai bước cần tạo lớp và thêm cô vào lớp.', labState.split ? 'Bước 1 đã commit riêng: lớp trở thành dữ liệu đã xác nhận.' : 'Bước 1 được flush: đã có id minh họa, nhưng chưa commit nghiệp vụ.', labState.fail ? 'Bước 2 lỗi. Rollback chỉ hủy phần chưa commit.' : 'Bước 2 thành công: đã có cả lớp và thành viên trong phạm vi đang xử lý.', model.failed ? 'Nghiệp vụ thất bại. Kiểm tra phần nào vẫn còn trong dữ liệu đã commit.' : 'Nghiệp vụ hoàn tất. Commit chung xác nhận các thay đổi cùng nhau.'];
    return labHeader('Flush, commit và nửa nghiệp vụ bị giữ lại', 'Đi từng bước tạo lớp rồi thêm cô vào lớp. Chọn lỗi ở bước 2 để nhìn giới hạn của rollback. Đây là mô hình dữ liệu trong bộ nhớ.') + `<div class="lab-controls">${field('Cách xác nhận', 'transaction-mode', [['single','Một transaction cho cả nghiệp vụ'],['split','Commit riêng sau từng bước']],labState.split ? 'split' : 'single')}${checkbox('Bước 2 bị lỗi','transaction-fail',labState.fail)}<button type="button" data-lab-action="transaction-next" class="primary" ${labState.transactionStep >= 3 ? 'disabled' : ''}>Chạy bước tiếp →</button><button type="button" data-lab-action="transaction-reset">Làm lại</button></div><p class="trace-explanation"><strong>Bước ${labState.transactionStep}/3.</strong> ${descriptions[labState.transactionStep]}</p><div class="lab-two"><div class="lab-panel"><h3>Đã commit</h3>${listRows(model.committed)}</div><div class="lab-panel"><h3>Chưa xác nhận trong transaction</h3>${listRows(model.pending,true)}</div></div>${model.failed ? `<div class="outcome ${model.orphan ? 'bad' : ''}"><strong>${model.orphan ? 'Còn lớp nhưng thiếu quan hệ thành viên' : 'Không giữ nửa nghiệp vụ'}</strong><p>${model.orphan ? 'Commit bước 1 đã chốt lớp. Rollback bước 2 không quay ngược được commit trước đó.' : 'Cả nhóm chưa commit đã được hủy. Id từng xuất hiện sau flush không phải bằng chứng dữ liệu đã được xác nhận.'}</p></div>` : ''}`;
  }
  function deadlineLab() {
    return labHeader('Hạn nộp và thử lại sau lỗi mạng', 'Theo hợp đồng bài học: deadline 13:00 inclusive; cùng nội dung đã lưu trả bản cũ, kể cả sau hạn. Danh tính/quyền vẫn được xét trước. Thay điều kiện rồi đọc đúng điểm dừng.') + `<div class="lab-controls">${field('Giờ server','deadline-time',[[-1,'12:59 · trước hạn'],[0,'13:00 · đúng hạn'],[1,'13:01 · sau hạn']],0)}${field('Bản nộp đã có','deadline-existing',[['none','Chưa có'],['same','Đã lưu cùng nội dung'],['different','Đã lưu nội dung khác']],'none')}${field('Bài tập','deadline-published',[['yes','Đã công bố'],['no','Nháp / đã đóng']],'yes')}</div><div class="lab-controls">${checkbox('Học sinh','deadline-student',true)}${checkbox('Tài khoản hoạt động','deadline-active',true)}${checkbox('Thuộc lớp','deadline-member',true)}<label class="field">Nội dung<input id="deadline-answer" value="A" maxlength="12000"></label></div><div id="deadline-result" aria-live="polite"></div>`;
  }
  function updateDeadline() {
    const result = M.deadline({ offset: Number($('deadline-time').value), existing: $('deadline-existing').value,
      published: $('deadline-published').value === 'yes', student: $('deadline-student').checked,
      active: $('deadline-active').checked, member: $('deadline-member').checked, answer: $('deadline-answer').value });
    $('deadline-result').innerHTML = `<ol class="checks">${result.checks.map(item => `<li class="${item.ok ? '' : 'failed'}"><span>${item.ok ? 'ĐẠT' : 'DỪNG'}</span><span>${esc(item.label)}</span></li>`).join('')}</ol><div class="outcome ${result.allowed ? '' : 'bad'}"><strong>${esc(result.title)}</strong><p>${result.retry ? 'Không tạo bản mới và không đổi thời điểm đã nhận. Đây là trả tác dụng đã có, không nhận bài mới sau hạn.' : result.allowed ? 'Chỉ sau các kiểm tra mới lưu bản nộp mới. MySQL thật còn cần ràng buộc UNIQUE và kiểm tra cạnh tranh.' : 'Không ghi thêm dữ liệu. Các bước sau điểm dừng không được dùng để biện minh cho một yêu cầu đã không đủ điều kiện.'}</p></div>`;
  }
  function permissionLab() {
    return labHeader('Token hợp lệ và phạm vi dữ liệu', 'Tài nguyên: bài nộp của An thuộc lớp 7. Policy đọc bài của mô hình dưới đây là giả định học tập, không tự thay đổi phân quyền sản phẩm.') + `<div class="lab-controls">${field('Người yêu cầu','permission-actor',[['own','An · chủ bài'],['other','Bình · học sinh khác'],['teacher','Cô phụ trách lớp 7'],['outsider','Cô thuộc lớp khác'],['assistant','Trợ giảng chỉ được điểm danh'],['admin','Admin chưa được cấp quyền đọc bài']],'own')}${checkbox('Token hợp lệ','permission-token',true)}${checkbox('Tài khoản hoạt động','permission-active',true)}</div><div id="permission-result" aria-live="polite"></div><div class="trap"><strong>Điều UI không thể bảo vệ thay server</strong>Ẩn nút hoặc không đưa link cho người dùng không chặn được request thủ công. Cùng quy tắc phải áp dụng với endpoint chi tiết, danh sách, tải file và export.</div>`;
  }
  function updatePermission() {
    const result = M.permission($('permission-actor').value,$('permission-token').checked,$('permission-active').checked);
    $('permission-result').innerHTML = `<div class="outcome ${result.allowed ? '' : 'bad'}"><strong>${result.code} · ${result.allowed ? 'Cho phép đọc' : 'Từ chối'}</strong><p>${esc(result.reason)}</p></div><div class="lab-two"><div class="lab-panel"><h3>Xác thực</h3><p>Ai gửi request? Token và trạng thái được backend xác minh theo policy.</p></div><div class="lab-panel"><h3>Phân quyền</h3><p>Người đó có quan hệ/capability nào với bài nộp và lớp này?</p></div></div>`;
  }
  function httpLab() {
    return labHeader('HTTP 200 chưa đủ để tin cấu trúc dữ liệu', 'Chọn kết quả, phân biệt transport, status và body theo hợp đồng. Các payload dưới đây là fixture cục bộ; không thực hiện request.') + `<div class="lab-controls">${field('Kết quả giả định','http-kind',[['good','200 · Task[] hợp lệ'],['empty','200 · []'],['bad','200 · body sai kiểu'],['401','401 · xác thực lỗi'],['network','Mất mạng / chưa có response']],'good')}</div><div id="http-result" aria-live="polite"></div>`;
  }
  function updateHttp() {
    const result = M.http($('http-kind').value);
    $('http-result').innerHTML = `<div class="lab-two"><div class="lab-panel"><h3>Điều phía client nhận</h3><pre>${esc(result.payload)}</pre></div><div class="lab-panel"><h3>Trạng thái nên biểu diễn</h3><div class="pill ${result.kind === 'error' ? 'rust' : ''}">${esc(result.state)}</div><p style="margin-top:16px">${esc(result.label)}</p></div></div><div class="trap"><strong>Tư duy ranh giới</strong>TypeScript giúp viết code theo kiểu; nó không sửa JSON sai từ mạng. Lỗi mạng không tự chứng minh hết phiên. Danh sách rỗng vẫn có thể là một lần tải thành công.</div>`;
  }
  function oopLab() {
    return labHeader('Service dùng một hợp đồng, adapter có thể đổi', 'Cả hai lựa chọn dưới đây đều là mô hình học tập. Adapter SQL chỉ hiển thị câu truy vấn minh họa, không kết nối database.') + `<div class="lab-controls">${field('Repository được truyền vào','oop-repo',[['memory','Kho nhớ mẫu'],['sql','Adapter SQL mô phỏng']],'memory')}${field('Id muốn tìm','oop-user',[['1','1 · có User'],['99','99 · không tìm thấy']],'1')}<button type="button" class="primary" data-lab-action="oop-run">Gọi service.find_user(id)</button></div><div class="lab-two"><div class="lab-panel"><h3>Composition</h3><div class="object-pointer">LoginService → repository → find_user(id)</div><p>Service cần thao tác tìm user. Bên lắp ráp quyết định adapter; nó không kế thừa repository.</p></div><div class="lab-panel"><h3>Kết quả và vết gọi</h3><pre id="oop-result">Chưa gọi. Hãy dự đoán kết quả với id 99.</pre></div></div><div class="queue">service = LoginService(repository)<br>user = service.find_user(user_id)</div>`;
  }
  function gradingLab() {
    return labHeader('Một kết quả, hai câu hỏi thống kê', 'Tỉ lệ đúng phụ thuộc mẫu số. Bộ so sánh số bên dưới dùng hợp đồng thập phân hẹp của bài học, không phải bộ giải toán hoặc quy tắc thi quốc gia.') + `<div class="lab-controls"><label class="field">Số câu đúng<input id="grade-correct" type="number" min="0" value="6"></label><label class="field">Số câu đã làm<input id="grade-attempted" type="number" min="0" value="8"></label><label class="field">Tổng câu được giao<input id="grade-total" type="number" min="1" value="10"></label></div><div id="grade-report" aria-live="polite"></div><h3>Chuẩn hóa đáp án số</h3><div class="lab-controls"><label class="field">Đáp án chuẩn<input id="numeric-expected" value="0.5" maxlength="110"></label><label class="field">Học sinh nhập<input id="numeric-answer" value="0.50" maxlength="110"></label></div><div id="numeric-result" aria-live="polite"></div>`;
  }
  function updateGrading() {
    const report = M.report(Number($('grade-correct').value),Number($('grade-attempted').value),Number($('grade-total').value));
    $('grade-report').innerHTML = report.valid ? `<div class="lab-two"><div class="lab-panel"><div class="eyebrow">TRÊN TOÀN BÀI</div><div class="number-big">${report.whole.toFixed(1)}%</div><p>Đúng / tổng câu được giao.</p></div><div class="lab-panel"><div class="eyebrow">TRONG PHẦN ĐÃ LÀM</div><div class="number-big">${report.attempted === null ? '—' : report.attempted.toFixed(1) + '%'}</div><p>${report.attempted === null ? 'Chưa làm câu nào, không chia cho 0.' : 'Đúng / số câu đã làm.'}</p></div></div>` : `<div class="outcome bad"><strong>Chưa tính</strong><p>${report.reason}</p></div>`;
    try {
      const expected = M.parseNumber($('numeric-expected').value), answer = M.parseNumber($('numeric-answer').value);
      $('numeric-result').innerHTML = `<div class="outcome ${expected === answer ? '' : 'bad'}"><strong>${expected === answer ? 'Cùng giá trị theo hợp đồng' : 'Khác giá trị'}</strong><p>Chuẩn: ${esc(expected)} · Nhập: ${esc(answer)}. Mô hình chuẩn hóa chuỗi để minh họa so sánh chính xác, không dùng eval hay coi dấu phẩy/phân số là hợp lệ mặc định.</p></div>`;
    } catch (error) { $('numeric-result').innerHTML = `<div class="outcome bad"><strong>Dữ liệu chưa hợp lệ</strong><p>${esc(error.message)} Dùng chữ số trước dấu chấm; không nhận 1/2, 0,5, NaN hoặc exponent trong bài này.</p></div>`; }
  }
  function layoutLab() {
    return labHeader('Inch, pixel vật lý và CSS viewport', 'Máy tính chỉ ước tính chiều rộng CSS từ các giả định. Bản bố cục bên dưới thu nhỏ để vừa khung và dùng breakpoint minh họa 900px; không phải screenshot dashboard thật.') + `<div class="lab-controls">${field('Rộng vật lý','layout-physical',[[1920,'1920 px'],[2560,'2560 px'],[3440,'3440 px'],[3840,'3840 px']],1920)}${field('Windows Scale','layout-scale',[[100,'100%'],[125,'125%'],[150,'150%'],[200,'200%']],125)}${field('Browser zoom','layout-zoom',[[100,'100%'],[125,'125%'],[150,'150%']],100)}</div><div id="layout-result"></div><label class="field" style="margin:24px 0">Thử riêng chiều rộng bố cục · CSS px<input id="layout-width" type="range" min="320" max="1600" value="1000" step="10"></label><div class="small muted" id="layout-meta"></div><div class="demo-stage" id="layout-stage"><div class="demo-fit" id="layout-fit"><div class="demo-nav">Bố cục học tập · một cột khi dưới 900 CSS px</div><div class="demo-grid" id="layout-grid"><section class="demo-item"><h3 style="margin-top:0">Nội dung chính</h3><p>Văn bản cần đủ chỗ để đọc và có thể xuống dòng.</p></section><aside class="demo-item">Lịch & tài liệu<br>Cột phụ 260px khi đủ rộng.</aside></div></div></div>`;
  }
  function updateLayout() {
    const width = M.viewport(Number($('layout-physical').value),Number($('layout-scale').value),Number($('layout-zoom').value));
    $('layout-result').innerHTML = `<div class="queue">${$('layout-physical').value} ÷ ${Number($('layout-scale').value)/100} ÷ ${Number($('layout-zoom').value)/100} ≈ <strong>${width} CSS px chiều rộng</strong></div>`;
    const demoWidth = Number($('layout-width').value), container = $('layout-stage'), demo = $('layout-fit');
    const scale = Math.min(1,(container.clientWidth - 28)/demoWidth);
    demo.style.width = demoWidth + 'px';
    demo.style.transform = `scale(${Math.max(.1,scale)})`;
    $('layout-grid').style.gridTemplateColumns = demoWidth >= 900 ? 'minmax(0,1fr) 260px' : 'minmax(0,1fr)';
    container.style.height = demo.offsetHeight * scale + 28 + 'px';
    $('layout-meta').textContent = `Khung giả định ${demoWidth}px · hiển thị ${Math.round(scale*100)}% để vừa sách.`;
  }
  function syntaxLab() {
    const exercise = syntaxExercises[syntaxExercise];
    return `<div class="page syntax-page"><div class="eyebrow">S0 / TỰ GÕ TỪ MỘT DÒNG</div><h1>Viết một chút.<br>Nhìn từng bước.</h1><p class="page-lead">Chỉ học số, chữ, biến và dấu gán trước. Đọc bài S0 song song; chưa cần biết React hay API.</p><div class="button-row"><button type="button" data-route="lesson" data-id="zero">Đọc giải thích từng ký hiệu →</button></div><label for="syntax-exercise">Chọn bài nhỏ</label><select id="syntax-exercise">${syntaxExercises.map((item, index) => `<option value="${index}" ${index === syntaxExercise ? 'selected' : ''}>${esc(item.name)}</option>`).join('')}</select><p id="syntax-task">${esc(exercise.task)}</p><p class="small">Kết quả mục tiêu: <code>${esc(exercise.expected).replace(/\n/g, ' · ')}</code>. Dự đoán trước khi chạy.</p><label for="syntax-code">Code mày tự gõ</label><textarea id="syntax-code" class="syntax-editor" spellcheck="false" autocapitalize="off" autocorrect="off" aria-describedby="syntax-limit syntax-task"></textarea><div class="button-row"><button class="primary" type="button" data-syntax-run>Chạy và xem từng dòng →</button><button type="button" data-syntax-reset>Khôi phục bài mẫu</button></div><p id="syntax-limit" class="small muted">Bộ luyện nhỏ chỉ hiểu let/const, gán, số/chuỗi/true/false, phép tính, so sánh và console.log một giá trị. Viết ; cuối từng câu. Chưa hỗ trợ if, vòng lặp, hàm, array/object; không phải máy chạy JavaScript đầy đủ. Bài gõ chỉ giữ trong tab này, hãy sao chép vào ghi chú/file nếu cần lưu.</p><section class="lab-panel"><h2>Kết quả hiển thị</h2><pre id="syntax-output" role="status" aria-live="polite">Chưa chạy. Đọc và dự đoán trước.</pre></section><section class="lab-panel"><h2>Máy đã làm gì qua từng dòng?</h2><div id="syntax-trace"><p>Tạo biến không tự hiển thị. Bảng này sẽ chỉ rõ giá trị đã thay đổi thế nào.</p></div></section><p class="small">Output khớp mục tiêu chưa tự chứng minh cách viết đã đúng ý. Hãy giải thích từng dấu rồi đóng mẫu và viết lại với số khác.</p></div>`;
  }
  function runSyntax() {
    syntaxDraft = $('syntax-code').value;
    const result = window.SyntaxLab.run(syntaxDraft);
    $('syntax-output').textContent = (result.output.length ? result.output.join('\n') : '(Chưa có câu lệnh hiển thị nào đã chạy.)')
      + (result.ok ? '\n\nĐã chạy xong trong phạm vi bộ luyện.' : `\n\nDòng ${result.line}: ${result.error}`);
    $('syntax-trace').innerHTML = result.trace.length ? `<div class="table-scroll"><table><thead><tr><th>Dòng</th><th>Việc vừa làm</th><th>Biến sau câu lệnh</th></tr></thead><tbody>${result.trace.map(step => `<tr><td>${step.line}</td><td>${esc(step.action)}</td><td>${Object.entries(step.variables).map(([name, value]) => `<code>${esc(name)} = ${esc(window.SyntaxLab.format(value))}</code>`).join('<br>') || 'Chưa có biến'}</td></tr>`).join('')}</tbody></table></div>` : '<p>Chưa có câu lệnh nào thực hiện được. Nếu có báo lỗi, sửa chỗ đó trước.</p>';
  }
  function cssLab() {
    return `<div class="page syntax-page"><div class="eyebrow">F1 / HTML CSS TỪ ĐẦU</div><h1>Đổi một thuộc tính.<br>Nhìn hộp thay đổi.</h1><p class="page-lead">HTML cố định có một hộp card và hai item. Chỉ đổi CSS bằng các lựa chọn dưới; chưa có React/Tailwind.</p><div class="button-row"><button type="button" data-route="lesson" data-id="markup">Đọc HTML/CSS từng bước →</button></div><div class="lab-controls">${field('display của card', 'css-display', [['block','block'],['flex','flex']], cssState.display)}${field('flex-direction', 'css-direction', [['row','row · hàng'],['column','column · cột']], cssState.direction)}${field('padding trong card', 'css-padding', [['0','0px'],['8','8px'],['16','16px'],['24','24px']], cssState.padding)}${field('gap giữa item', 'css-gap', [['0','0px'],['12','12px'],['24','24px']], cssState.gap)}</div><p id="css-explanation" role="status"></p><h2>HTML giữ nguyên</h2><pre class="css-example"><code>&lt;section class="card"&gt;\n  &lt;div class="item"&gt;An&lt;/div&gt;\n  &lt;div class="item"&gt;Bình&lt;/div&gt;\n&lt;/section&gt;</code></pre><h2>CSS đang áp dụng</h2><pre id="css-code" class="css-example"></pre><h2>Kết quả browser bố trí thật</h2><iframe id="css-preview" title="Màn thử HTML CSS" sandbox="" class="css-preview"></iframe><p class="small muted">Khung chỉ có HTML/CSS cố định và các giá trị được chọn sẵn, không chạy script/mạng. Padding/viền/màu của item được ghi trong CSS; lề body12px chỉ để khung dễ nhìn. Không có ô chạy CSS tùy ý.</p><p>Tự thử: display:block, tăng gap; sau đó display:flex và tăng gap lần nữa. Đổi padding để phân biệt đệm quanh nhóm với khoảng cách giữa hai item.</p></div>`;
  }
  function updateCssLab() {
    const choices = { display: ['block','flex'], direction: ['row','column'], padding: ['0','8','16','24'], gap: ['0','12','24'] };
    for (const [name, values] of Object.entries(choices)) {
      const candidate = $('css-' + name).value;
      if (values.includes(candidate)) cssState[name] = candidate;
    }
    const css = `.card {\n  box-sizing: border-box;\n  width: 100%;\n  border: 2px solid #78958a;\n  padding: ${cssState.padding}px;\n  display: ${cssState.display};\n  flex-direction: ${cssState.direction};\n  gap: ${cssState.gap}px;\n}\n.item { background: #dceadf; padding: 8px; min-width: 0; }`;
    $('css-code').textContent = css;
    $('css-explanation').textContent = cssState.display === 'block'
      ? 'Card dùng block: gap/flex-direction không tách/xếp các block thông thường trong ví dụ này. Padding vẫn tạo đệm phía trong viền.'
      : `Card dùng flex: hai con xếp theo ${cssState.direction === 'row' ? 'hàng' : 'cột'}, gap ${cssState.gap}px giữa chúng; padding ${cssState.padding}px quanh nhóm.`;
    const preview = `<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'"><style>body{margin:12px;font:16px/1.5 system-ui;color:#20332a}*{box-sizing:border-box}${css}</style></head><body><section class="card"><div class="item">An</div><div class="item">Bình</div></section></body></html>`;
    $('css-preview').setAttribute('srcdoc', preview);
  }
  function renderLab(id) {
    const selected = labs.some(lab => lab[0] === id) ? id : 'syntax'; route.id = selected;
    if (selected === 'syntax') return syntaxLab();
    if (selected === 'css') return cssLab();
    const content = { login: loginLab, memory: memoryLab, state: stateLab, join: joinLab, transaction: transactionLab,
      deadline: deadlineLab, permission: permissionLab, http: httpLab, oop: oopLab, grading: gradingLab, layout: layoutLab }[selected]();
    return `<div class="page lab-layout"><div class="eyebrow">PHÒNG THỰC HÀNH / CÁC MÔ HÌNH CỤC BỘ</div><div class="lab-picker" aria-label="Chọn cơ chế để thử">${labs.map(lab => `<button type="button" data-route="lab" data-id="${lab[0]}" aria-pressed="${selected === lab[0]}">${lab[1]}</button>`).join('')}</div>${content}<p class="lab-note">Đổi một điều kiện, dự đoán trước, rồi viết lại kết luận bằng lời của mình. Các mô hình không chạy code tùy ý, không gửi dữ liệu và không chứng minh hành vi DB/HTTP thật đã đúng.</p></div>`;
  }
  function afterLab() {
    if (route.id === 'syntax') { $('syntax-code').value = syntaxDraft; }
    if (route.id === 'css') {
      for (const [name, value] of Object.entries(cssState)) $('css-' + name).value = value;
      updateCssLab();
    }
    if (route.id === 'deadline') updateDeadline();
    if (route.id === 'permission') updatePermission();
    if (route.id === 'http') updateHttp();
    if (route.id === 'grading') updateGrading();
    if (route.id === 'layout') updateLayout();
  }

  function reviewDeck() { return cards.filter(card => reviewFilter === 'all' || state.review[card.id] !== 'remembered'); }
  function renderReview() {
    const deck = reviewDeck(); reviewIndex = Math.max(0,Math.min(reviewIndex,deck.length-1));
    const card = deck[reviewIndex];
    const remembered = cards.filter(item => state.review[item.id] === 'remembered').length;
    return `<div class="page review-shell"><div class="eyebrow">GỢI NHỚ CHỦ ĐỘNG</div><h1>Đóng lời giải.<br>Tự kể lại bản chất.</h1><p class="page-lead">Nhìn thuật ngữ, giải thích và lấy một ví dụ từ project trước khi lật thẻ. Bạn tự đánh giá mức nhớ, không chỉ mức quen mắt.</p><div class="lab-controls">${field('Bộ thẻ','review-filter',[['all','Tất cả thẻ'],['again','Chưa đánh dấu đã nhớ']],reviewFilter)}<span class="flash-progress">${remembered} / ${cards.length} thẻ tự đánh giá đã nhớ</span></div>${card ? `<section class="flashcard"><div class="eyebrow">${esc(card.chapter)} · ${reviewIndex+1}/${deck.length}</div><h2>${esc(card.term)}</h2>${reviewRevealed ? `<p class="definition">${esc(card.definition)}</p><p class="muted small">Tự nêu một ví dụ và một cách hiểu sai có thể gặp.</p>` : '<p class="muted">Đừng lật ngay. Hãy giải thích trước bằng một câu và một ví dụ.</p>'}<div class="button-row">${reviewRevealed ? '<button type="button" data-review-grade="again">Cần ôn lại</button><button type="button" class="primary" data-review-grade="remembered">Đã tự kể lại được</button>' : '<button type="button" class="primary" data-review-reveal>Hiện bản chất</button>'}</div></section><div class="button-row"><button type="button" data-review-step="-1">← Thẻ trước</button><button type="button" data-review-step="1">Thẻ tiếp →</button><button type="button" class="ghost" data-route="lesson" data-id="${card.lesson}">Đọc lại chương ↗</button></div>` : '<div class="outcome"><strong>Không còn thẻ trong bộ lọc này.</strong><p>Đổi sang tất cả để làm một vòng ôn mới. Tự đánh giá đã nhớ không có nghĩa sẽ không cần ôn lại.</p></div>'}</div>`;
  }
  function renderPath() {
    const milestones = data.path.milestones;
    const primaryIds = data.course?.primary_milestones || milestones.map(m => m.id);
    const primary = primaryIds.map(id => milestones.find(m => m.id === id)).filter(Boolean);
    const supplemental = milestones.filter(m => !primaryIds.includes(m.id));
    const checks = milestones.flatMap(m => m.checks.map((_, i) => m.id + ':' + i));
    const count = checks.filter(id => state.skills[id]).length;
    const milestoneMarkup = m => `<section class="path-card"><div class="eyebrow">SẢN PHẨM CÓ THỂ KIỂM</div><h2>${esc(m.name)}</h2><p>${esc(m.task)}</p><div class="prerequisite-links">${m.lessons.map(id => {
      const lesson = lessonById(id);
      return lesson ? `<button type="button" data-route="lesson" data-id="${id}">${esc(lesson.short)} ↗</button>` : '';
    }).join('')}</div><div class="skill-checks">${m.checks.map((check,i) => `<label><input type="checkbox" data-skill="${m.id}:${i}" ${state.skills[m.id+':'+i] ? 'checked' : ''}><span>${esc(check)}</span></label>`).join('')}</div><div class="trap"><strong>Biến thể phải tự xử lý</strong>${esc(m.change)}</div><p class="small"><strong>Nộp gì?</strong> ${esc(m.artifact)}</p><label class="evidence-label" for="evidence-${m.id}">Ghi bằng chứng và điểm chưa làm được</label><textarea id="evidence-${m.id}" data-evidence="${m.id}" placeholder="File tôi tự viết… Lệnh kiểm tra… Kết quả thật… Biến thể tôi đã xử lý…">${esc(typeof state.evidence[m.id] === 'string' ? state.evidence[m.id] : '')}</textarea></section>`;
    return `<div class="page path-page"><header class="reader-header"><div class="eyebrow">LÀM ĐƯỢC GÌ SAU MỖI CHẶNG?</div><h1>Tiến bộ nhìn thấy<br>qua việc tự làm.</h1><p class="page-lead">Đối chiếu code và kết quả thật với từng mốc. Đánh dấu sau khi tự làm được biến thể; sách chưa tự chạy hay chấm project riêng của bạn.</p></header><div class="path-summary"><strong id="skills-total">${count} / ${checks.length}</strong><span>tiêu chí tự đối chiếu trên toàn bộ mốc chính và mốc bổ sung.<br>Ghi điều đã thử, kết quả và phần còn cần sửa.</span></div><div class="section-heading"><div><div class="eyebrow">ĐI CÙNG ĐƯỜNG HỌC MỚI</div><h2>Mốc thực hành chính</h2></div><span class="small muted">${primary.length} mốc · mở bài để học, quay lại để đối chiếu</span></div><div class="path-grid">${primary.map(milestoneMarkup).join('')}</div>${supplemental.length ? `<details class="supplemental-milestones"><summary><strong>Mốc chuyên đề bổ sung</strong><span>${supplemental.length} mốc · giữ nguyên tiến độ cũ +</span></summary><p class="muted small">Dùng khi học sâu một chuyên đề hoặc cần củng cố. Các bằng chứng đã lưu vẫn ở đây.</p><div class="path-grid">${supplemental.map(milestoneMarkup).join('')}</div></details>` : ''}<p class="save-status" id="evidence-status">Ghi chú bằng chứng và tiêu chí lưu trên trình duyệt này. Xuất bản sao ở mục Ghi chú.</p><div class="button-row"><button type="button" data-export-notes>Xuất ghi chú & bằng chứng</button></div></div>`;
  }

  function renderNotes() {
    return `<div class="page"><div class="eyebrow">NHẬT KÝ CỦA RIÊNG BẠN</div><h1>Ghi cách mình hiểu,<br>và một bước tiếp theo.</h1><p class="page-lead">Ghi chú và tiến độ chỉ lưu ở trình duyệt/máy này khi được phép. Hãy xuất bản sao nếu cần chuyển máy hoặc giữ lâu dài. Không ghi mật khẩu hay token.</p><div class="button-row"><button type="button" class="primary" data-export-notes>Xuất ghi chú & tiến độ</button><button type="button" data-import-notes>Nhập bản sao</button><input type="file" id="notes-file" accept="application/json,.json" hidden></div><div class="notes-grid">${data.lessons.map(lesson => `<section class="note-row"><h3>${esc(lesson.number)} · ${esc(lesson.short)}</h3><textarea data-note="${lesson.id}" aria-label="Ghi chú ${esc(lesson.short)}" placeholder="Tôi đã hiểu… Tôi đã thử… Lần sau mở file…">${esc(typeof state.notes[lesson.id] === 'string' ? state.notes[lesson.id] : '')}</textarea><div class="button-row"><button type="button" class="ghost small" data-route="lesson" data-id="${lesson.id}">Quay lại bài →</button><span class="save-status">${state.completed[lesson.id] ? 'Đã tự đánh dấu hoàn thành' : 'Chưa tự đánh dấu hoàn thành'}</span></div></section>`).join('')}</div></div>`;
  }

  function renderRoute(scrollTop = false) {
    const bits = location.hash.slice(1).split('/');
    route = { type: bits[0] || 'home', id: bits[1] || '', mode: bits[2] || 'learn', step: bits[3] || '' };
    const renderers = { home: renderHome, knowledge: renderKnowledge, path: renderPath, lesson: () => renderLesson(route.id, route.mode), lab: () => renderLab(route.id), review: renderReview, notes: renderNotes };
    if (!renderers[route.type]) route = { type: 'home' };
    $('view').innerHTML = renderers[route.type]();
    renderNav();
    if (route.type === 'lab') afterLab();
    const drill = activeDrill();
    if (drill) $('lesson-drill-code').value = typeof state.drills[drill.key] === 'string' ? state.drills[drill.key] : drill.drill.starter;
    document.title = route.type === 'lesson' ? (data.lessons.find(item=>item.id===route.id)?.short || 'Bài học') + ' · Hiểu tận gốc' : 'Hiểu tận gốc · Giáo án Vision LMS';
    if (scrollTop) { window.scrollTo(0,0); $('main').focus({ preventScroll:true }); }
  }
  function refreshWithoutScroll() { const position = window.scrollY; renderRoute(); window.scrollTo(0,position); }
  function currentReviewCard() { return reviewDeck()[reviewIndex]; }

  function openModal(title, body, wide = false) {
    modalOrigin = document.activeElement;
    $('modal-title').textContent = title;
    $('modal-body').innerHTML = body;
    $('modal').classList.toggle('wide',wide);
    $('modal-overlay').hidden = false;
    document.body.style.overflow = 'hidden';
    ($('modal-body').querySelector('input,button,a,textarea') || $('modal-close')).focus();
  }
  function closeModal() {
    $('modal-overlay').hidden = true; document.body.style.overflow = '';
    if (modalOrigin?.isConnected) modalOrigin.focus();
  }
  function openSource(key) {
    const file = data.files[key];
    if (!file) { toast('Không có bản nhúng cho file này. Xem bản Markdown gốc.'); return; }
    openModal(file.name, `<div class="article">${file.html}</div>`,true);
  }
  function openSearch() {
    openModal('Tìm một khái niệm trong sách', '<input class="search-input" id="search-input" type="search" placeholder="Ví dụ: tham chiếu, deadline, self, rollback…" aria-label="Nội dung cần tìm"><div id="search-results"></div>');
    updateSearch('');
  }
  function openSyntax() {
    openModal('Đọc ký hiệu thành lời', '<p class="muted">Chọn đúng ngữ cảnh trước khi áp dụng một ký hiệu. Tìm bằng tên hoặc chính ký hiệu.</p><label class="sr-only" for="syntax-query">Tìm ký hiệu</label><input id="syntax-query" class="search-input" type="search" placeholder="Ví dụ: =>, return, self, await…"><div id="syntax-results"></div>', true);
    updateSyntax('');
  }
  function updateSyntax(query) {
    const normalized = fold(query.trim());
    const terms = data.teaching.syntax.filter(term=>fold([term.token,term.name,term.meaning,term.example].join(' ')).includes(normalized));
    $('syntax-results').innerHTML = terms.length ? `<div class="syntax-grid">${terms.map(term=>`<section class="syntax-entry"><code class="syntax-token">${esc(term.token)}</code><h3>${esc(term.name)}</h3><p>${esc(term.meaning)}</p><pre><code>${esc(term.example)}</code></pre><small>${esc(term.trap)}</small></section>`).join('')}</div>` : '<p class="empty">Chưa có ký hiệu này trong sổ tra nhanh. Xem bài Tra cứu để tìm tài liệu theo thư viện.</p>';
  }
  function openApiGuide() {
    openModal('Tra hàm/tool: nhận gì, trả gì, có tác dụng gì?', '<label for="api-query">Tên hàm/tool hoặc việc cần làm</label><input id="api-query" type="search" placeholder="Ví dụ: strip, map, Depends, padding…"><div id="api-results"></div>', true);
    updateApiGuide('');
    $('api-query').focus();
  }
  function updateApiGuide(query) {
    const normalized = fold(query.trim());
    const entries = data.api_guide.filter(entry => fold(Object.values(entry).join(' ')).includes(normalized));
    $('api-results').innerHTML = entries.length ? entries.map(entry => `<section class="api-entry"><div class="eyebrow">${esc(entry.kind)}</div><h3>${esc(entry.name)}</h3><p><strong>Khi dùng:</strong> ${esc(entry.when)}</p><pre><code>${esc(entry.signature)}</code></pre><dl><dt>Nhận gì?</dt><dd>${esc(entry.input)}</dd><dt>Trả gì?</dt><dd>${esc(entry.output)}</dd><dt>Tác dụng?</dt><dd>${esc(entry.effect)}</dd><dt>Dễ nhầm?</dt><dd>${esc(entry.pitfall)}</dd></dl><pre><code>${esc(entry.code)}</code></pre><a href="${esc(entry.docs)}" target="_blank" rel="noopener noreferrer">Mở tài liệu chính thức ↗</a></section>`).join('') : '<p>Chưa có tên này trong bộ tra chọn lọc. Mở F2 để tìm import/định nghĩa, đọc signature và điền phiếu API; không đoán từ tên.</p>';
  }
  function updateSearch(query) {
    const normalized = fold(query.trim());
    const results = data.lessons.map(lesson => {
      const index = fold(lesson.search).indexOf(normalized);
      return { lesson, index, titleMatch: fold(lesson.short + ' ' + lesson.title).includes(normalized) };
    }).filter(result => !normalized || result.index >= 0 || result.titleMatch).sort((a,b)=>Number(b.titleMatch)-Number(a.titleMatch)).slice(0,12);
    $('search-results').innerHTML = results.length ? results.map(({lesson,index}) => {
      const start = Math.max(0,index-55), snippet = lesson.search.slice(start,start+190).replace(/[#`*]/g,'');
      return `<button type="button" class="search-result" data-search-go="${lesson.id}"><strong>${esc(lesson.number)} · ${esc(lesson.short)}</strong><span>${esc(snippet)}…</span></button>`;
    }).join('') : '<p class="empty">Chưa tìm thấy. Thử tên khái niệm ngắn hơn.</p>';
  }

  function exportNotes() {
    const blob = new Blob([JSON.stringify({ format:'vision-lms-book-v1', exportedAt:new Date().toISOString(), ...state },null,2)],{type:'application/json'});
    const url = URL.createObjectURL(blob), anchor = document.createElement('a');
    anchor.href = url; anchor.download = 'vision-lms-ghi-chu.json'; anchor.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  async function importNotes(file) {
    if (!file) return;
    if (file.size > 2_000_000) { toast('Bản ghi chú quá lớn. Chọn file dưới 2 MB.'); return; }
    try {
      const incoming = JSON.parse(await file.text());
      if (incoming.format !== 'vision-lms-book-v1') throw new Error('Sai định dạng');
      for (const lesson of data.lessons) {
        if (typeof incoming.notes?.[lesson.id] === 'string') state.notes[lesson.id] = incoming.notes[lesson.id].slice(0,50000);
        if (typeof incoming.completed?.[lesson.id] === 'boolean') state.completed[lesson.id] = incoming.completed[lesson.id];
      }
      for (const card of cards) if (['again','remembered'].includes(incoming.review?.[card.id])) state.review[card.id] = incoming.review[card.id];
      for (const milestone of data.path.milestones) {
        if (typeof incoming.evidence?.[milestone.id] === 'string') state.evidence[milestone.id] = incoming.evidence[milestone.id].slice(0,50000);
        milestone.checks.forEach((_,i) => {
          const id = milestone.id + ':' + i;
          if (typeof incoming.skills?.[id] === 'boolean') state.skills[id] = incoming.skills[id];
        });
      }
      for (const lesson of data.lessons) {
        for (const field of ['drafts', 'designs']) {
          if (typeof incoming[field]?.[lesson.id] === 'string') state[field][lesson.id] = incoming[field][lesson.id].slice(0,20000);
        }
        lesson.sections.forEach((section, step) => {
          const drillKey = lesson.id + ':' + step;
          if (section.study?.drill && typeof incoming.drills?.[drillKey] === 'string') state.drills[drillKey] = incoming.drills[drillKey].slice(0,4000);
        });
        const index = incoming.reading?.[lesson.id];
        if (Number.isInteger(index) && index >= 0 && index < lesson.sections.length) state.reading[lesson.id] = index;
      }
      if (data.lessons.some(lesson=>lesson.id===incoming.lastLesson)) state.lastLesson = incoming.lastLesson;
      save(); renderRoute(); toast('Đã nhập ghi chú và tiến độ theo chương.');
    } catch { toast('Không đọc được bản sao hợp lệ. Dữ liệu hiện tại được giữ.'); }
  }
  function printBook() {
    $('print-content').innerHTML = '<header><div class="eyebrow">VISION EDUCATION / GIÁO ÁN TỰ HỌC</div><h1>Hiểu từng dòng.<br>Tự xây cả hệ thống.</h1><p>Bản đọc/in từ sách tương tác · '+data.built_at+'</p><p>Các mô phỏng nằm trong file HTML. Bản in gồm bài giảng, tự kiểm tra và ghi chú hiện có.</p></header>' + data.lessons.map(lesson=>`<section class="print-chapter"><div class="eyebrow">${esc(lesson.number)} / ${esc(lesson.short)}</div><h1>${esc(lesson.title)}</h1><p>${esc(lesson.goal)}</p><div class="question-callout">${esc(lesson.question)}</div><p>${esc(lesson.core)}</p>${studyPriorities(lesson.study)}${focusLesson(lesson,true)}<article class="article">${lesson.html}</article><h2>Tự kiểm tra</h2>${quizMarkup(lesson,true)}${state.notes[lesson.id]?'<h2>Ghi chú của tôi</h2><p>'+esc(state.notes[lesson.id]).replace(/\n/g,'<br>')+'</p>':''}</section>`).join('');
    $('print-content').querySelectorAll('details').forEach(detail=>detail.open=true);
    window.print();
  }

  document.addEventListener('click', async event => {
    const target = event.target.closest('button,a');
    if (!target) return;
    if (target.hasAttribute('data-close-menu')) { closeMenu(); $('menu-toggle').focus(); return; }
    if (target.hasAttribute('data-download-studio')) {
      const archive = data.studio_archive;
      if (!archive?.base64) { toast('Bản này chưa có gói xưởng thực hành.'); return; }
      try {
        const binary = atob(archive.base64);
        const bytes = Uint8Array.from(binary, character => character.charCodeAt(0));
        const url = URL.createObjectURL(new Blob([bytes], { type: 'application/zip' }));
        const anchor = document.createElement('a');
        anchor.href = url; anchor.download = archive.name; anchor.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        toast('Đã tải xưởng thực hành. Giải nén và mở README.md để bắt đầu.');
      } catch { toast('Chưa tải được gói thực hành. Hãy thử lại hoặc mở thư mục studio cạnh sách.'); }
      return;
    }
    if (target.hasAttribute('data-knowledge-filter')) { knowledgeFilter = ['all','build','release','later'].includes(target.dataset.knowledgeFilter) ? target.dataset.knowledgeFilter : 'all'; refreshWithoutScroll(); return; }
    if (target.hasAttribute('data-run-drill')) { runLessonDrill(); return; }
    if (target.hasAttribute('data-open-api')) { openApiGuide(); return; }
    if (target.hasAttribute('data-syntax-run')) { runSyntax(); return; }
    if (target.hasAttribute('data-syntax-reset')) {
      syntaxDraft = syntaxExercises[syntaxExercise].code;
      refreshWithoutScroll(); return;
    }
    if (target.hasAttribute('data-open-syntax')) { openSyntax(); return; }
    if (target.hasAttribute('data-learning-step')) {
      workedLine = 0;
      navigate('lesson',route.id,'learn/'+Math.max(0,Number(target.dataset.learningStep)));
      return;
    }
    if (target.hasAttribute('data-worked-line')) {
      const example = data.teaching.examples[route.id];
      if (!example) return;
      workedLine = Math.max(0,Math.min(Number(target.dataset.workedLine),example.lines.length-1));
      const line = example.lines[workedLine];
      $('line-explanation').innerHTML = `<div class="eyebrow">DÒNG ${workedLine+1} · HIỂU TỪNG Ý</div><h3>${esc(line.title)}</h3><p>${esc(line.explanation)}</p><div class="value-observation"><span>Giá trị / điều cần quan sát</span><strong>${esc(line.value)}</strong></div>`;
      $('view').querySelectorAll('.worked-line').forEach((button,index)=>{
        button.classList.toggle('active',index===workedLine);
        button.setAttribute('aria-pressed',String(index===workedLine));
      });
      return;
    }
    if (target.dataset.route) { event.preventDefault(); navigate(target.dataset.route,target.dataset.id || '',target.dataset.mode || ''); return; }
    if (target.dataset.go) {
      event.preventDefault(); const id=target.dataset.go;
      if (id==='code-map') openSource('../CODE_GUIDE.md'); else if (id==='examples') openSource('examples/README.md'); else navigate(id==='home'||id==='notes'?id:'lesson',id==='home'||id==='notes'?'':id,target.dataset.mode || 'read'); return;
    }
    if (target.dataset.source) { event.preventDefault(); openSource(target.dataset.source); return; }
    if (target.dataset.scroll) { event.preventDefault(); document.getElementById(target.dataset.scroll)?.scrollIntoView({block:'start'}); return; }
    if (target.dataset.readerMode) { navigate('lesson',route.id,target.dataset.readerMode); return; }
    if (target.dataset.checkQuiz) {
      const q=target.dataset.checkQuiz;
      if (!Number.isInteger(state.answers[q])) { toast('Chọn một đáp án trước khi kiểm tra.'); return; }
      state.checked[q]=true; save(); refreshWithoutScroll(); return;
    }
    if (target.dataset.codeLine) { labState.codeLine=Number(target.dataset.codeLine); refreshWithoutScroll(); return; }
    const action=target.dataset.labAction;
    if (action) {
      if (action==='login-prev') labState.loginStep=Math.max(0,labState.loginStep-1);
      if (action==='login-next') { labState.loginStep=Math.min(7,labState.loginStep+1); labState.codeLine=M.loginTrace(labState.loginScenario)[labState.loginStep].line; }
      if (action==='memory-change') labState.memoryChanged=true;
      if (action==='memory-reset') labState.memoryChanged=false;
      if (action==='state-reset') { labState.count=0; labState.countTrace=null; }
      if (action==='state-replace'||action==='state-updater') { labState.countTrace=M.stateQueue(labState.count,action==='state-updater'); labState.count=labState.countTrace.result; }
      if (action==='transaction-next') labState.transactionStep=Math.min(3,labState.transactionStep+1);
      if (action==='transaction-reset') labState.transactionStep=0;
      if (action==='oop-run') {
        const id=Number($('oop-user').value), adapter=$('oop-repo').value;
        const repository={ findUser(userId) { return userId===1?{id:1,full_name:'User mẫu'}:null; } };
        const service={findUser(userId){return repository.findUser(userId);}};
        const result=service.findUser(id);
        $('oop-result').textContent=(adapter==='sql'?'Adapter SQL mô phỏng:\nSELECT ... WHERE id = :id\n':'Kho nhớ mẫu:\nlookup theo id\n')+'Service nhận: '+JSON.stringify(result,null,2);
        return;
      }
      refreshWithoutScroll(); return;
    }
    if (target.hasAttribute('data-review-reveal')) { reviewRevealed=true; refreshWithoutScroll(); return; }
    if (target.dataset.reviewStep) { const deck=reviewDeck(); if (deck.length) reviewIndex=(reviewIndex+Number(target.dataset.reviewStep)+deck.length)%deck.length; reviewRevealed=false; refreshWithoutScroll(); return; }
    if (target.dataset.reviewGrade) {
      const card=currentReviewCard(); if (card) state.review[card.id]=target.dataset.reviewGrade;
      save(); if (reviewFilter==='all') reviewIndex=(reviewIndex+1)%cards.length; reviewRevealed=false; refreshWithoutScroll(); return;
    }
    if (target.hasAttribute('data-export-notes')) { exportNotes(); return; }
    if (target.hasAttribute('data-import-notes')) { $('notes-file').click(); return; }
    if (target.dataset.searchGo) { const id=target.dataset.searchGo; closeModal(); navigate('lesson',id,'read'); return; }
    if (target.dataset.font) { state.font=Math.max(16,Math.min(22,state.font+Number(target.dataset.font))); applyPreferences(); save(); }
  });

  document.addEventListener('change', event => {
    const target=event.target;
    if (target.id.startsWith('css-')) { updateCssLab(); return; }
    if (target.id === 'syntax-exercise') {
      syntaxExercise = Math.max(0, Math.min(syntaxExercises.length - 1, Number(target.value) || 0));
      syntaxDraft = syntaxExercises[syntaxExercise].code; refreshWithoutScroll(); return;
    }
    if (target.dataset.complete) { state.completed[target.dataset.complete]=target.checked; save(); renderNav(); }
    if (target.dataset.skill) {
      state.skills[target.dataset.skill] = target.checked; save();
      const all = data.path.milestones.flatMap(m => m.checks.map((_,i)=>m.id+':'+i));
      $('skills-total').textContent = all.filter(id=>state.skills[id]).length+' / '+all.length;
    }
    if (target.dataset.quiz) {
      state.answers[target.dataset.quiz]=Number(target.value);
      state.checked[target.dataset.quiz]=false;
      target.closest('.quiz-item').querySelector('.quiz-feedback')?.remove();
      save();
    }
    if (target.id==='login-scenario') { labState.loginScenario=target.value; labState.loginStep=0; labState.codeLine=0; refreshWithoutScroll(); }
    if (target.id==='memory-strategy') { labState.memory=target.value; labState.memoryChanged=false; refreshWithoutScroll(); }
    if (target.id==='join-mode') { labState.join=target.value; refreshWithoutScroll(); }
    if (target.id==='transaction-mode'||target.id==='transaction-fail') { labState.split=$('transaction-mode').value==='split'; labState.fail=$('transaction-fail').checked; labState.transactionStep=0; refreshWithoutScroll(); }
    if (target.id.startsWith('deadline-')) updateDeadline();
    if (target.id.startsWith('permission-')) updatePermission();
    if (target.id==='http-kind') updateHttp();
    if (target.id.startsWith('grade-')||target.id.startsWith('numeric-')) updateGrading();
    if (target.id.startsWith('layout-')) updateLayout();
    if (target.id==='review-filter') { reviewFilter=target.value; reviewIndex=0; reviewRevealed=false; refreshWithoutScroll(); }
    if (target.id==='lesson-section') { workedLine=0; navigate('lesson',route.id,'learn/'+Number(target.value)); }
    if (target.id==='notes-file') void importNotes(target.files[0]);
  });
  document.addEventListener('input', event => {
    const target=event.target;
    if (target.dataset.focusDraft || target.dataset.designDraft) {
      const id = target.dataset.focusDraft || target.dataset.designDraft;
      if (lessonById(id)) {
        state[target.dataset.focusDraft ? 'drafts' : 'designs'][id] = target.value.slice(0,20000); save();
        if ($('focus-save-status')) $('focus-save-status').textContent = storageAvailable ? 'Đã lưu bản nháp. Ô này không chạy/chấm code.' : 'Chưa lưu được. Xuất ghi chú trước khi đóng.';
      }
      return;
    }
    if (target.dataset.drillDraft) {
      const active = activeDrill();
      if (active && active.key === target.dataset.drillDraft) {
        state.drills[active.key] = target.value.slice(0,4000); save();
        $('drill-feedback').textContent = 'Code đã đổi. Dự đoán rồi chạy lại để kiểm phiên bản mới.';
        $('drill-feedback').setAttribute('data-result','stale');
        $('drill-trace').innerHTML = '';
      }
      return;
    }
    if (target.id === 'syntax-code') syntaxDraft = target.value;
    if (target.dataset.note) {
      state.notes[target.dataset.note]=target.value; save();
      if ($('note-status')) $('note-status').textContent=storageAvailable?'Đã lưu trên trình duyệt này.':'Chưa lưu được trên máy. Hãy xuất ghi chú trước khi đóng.';
    }
    if (target.dataset.evidence) {
      state.evidence[target.dataset.evidence] = target.value; save();
      $('evidence-status').textContent = storageAvailable ? 'Đã lưu bằng chứng trên trình duyệt này.' : 'Chưa lưu được. Xuất bản sao trước khi đóng.';
    }
    if (target.id==='search-input') updateSearch(target.value);
    if (target.id==='syntax-query') updateSyntax(target.value);
    if (target.id==='api-query') updateApiGuide(target.value);
    if (target.id==='deadline-answer') updateDeadline();
    if (target.id.startsWith('grade-')||target.id.startsWith('numeric-')) updateGrading();
    if (target.id==='layout-width') updateLayout();
  });

  $('menu-toggle').addEventListener('click',()=>{
    const open=$('sidebar').classList.toggle('open');
    document.body.classList.toggle('nav-open',open);
    $('menu-toggle').setAttribute('aria-expanded',String(open));
    if (open) $('navigation').querySelector('[data-close-menu]')?.focus();
  });
  $('search-trigger').addEventListener('click',openSearch);
  $('theme-toggle').addEventListener('click',()=>{state.theme=state.theme==='dark'?'light':'dark';applyPreferences();save();});
  $('focus-toggle').addEventListener('click',()=>{const focus=document.body.classList.toggle('focus-mode');$('focus-toggle').setAttribute('aria-pressed',String(focus));});
  $('print-book').addEventListener('click',printBook);
  $('modal-close').addEventListener('click',closeModal);
  $('modal-overlay').addEventListener('click',event=>{if(event.target===$('modal-overlay'))closeModal();});
  document.addEventListener('keydown',event=>{
    const typing=/^(INPUT|TEXTAREA|SELECT)$/.test(event.target.tagName);
    if (event.key==='Escape') { if (!$('modal-overlay').hidden) closeModal(); else if ($('sidebar').classList.contains('open')) { closeMenu(); $('menu-toggle').focus(); } }
    if (event.key==='/'&&!typing&&$('modal-overlay').hidden) { event.preventDefault();openSearch(); }
    if (event.key==='Tab'&&!$('modal-overlay').hidden) {
      const items=[...$('modal').querySelectorAll('button:not([disabled]),a[href],input,textarea,select')].filter(item=>item.getClientRects().length);
      const first=items[0],last=items[items.length-1];
      if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    }
    if (event.key==='Tab'&&$('modal-overlay').hidden&&$('sidebar').classList.contains('open')) {
      const items=[...$('sidebar').querySelectorAll('button:not([disabled]),a[href],summary')].filter(item=>item.getClientRects().length);
      const first=items[0],last=items[items.length-1];
      if(first&&event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
      if(last&&!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
    }
  });
  window.addEventListener('hashchange',()=>renderRoute(true));
  window.addEventListener('resize',()=>{
    if(window.innerWidth>960) closeMenu();
    if(route.type==='lab'&&route.id==='layout'&&$('layout-width'))updateLayout();
  });
  applyPreferences(); warnStorage(); renderRoute();
})();
