import { useEffect, useState } from 'react';
import { describeError } from './class-api';
import { createAssignment, readAssignments, readIdentity, readSubmissions, saveGrade, submitAnswer } from './workflow-api';
import type { Actor, Assignment, Submission } from './workflow-api';

function GradeForm({ token, row, changed }: { token: string; row: Submission; changed: () => void }) {
  const [score, setScore] = useState(String(row.score ?? ''));
  const [publish, setPublish] = useState(row.grade_published);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  return <form onSubmit={async event => {
    event.preventDefault(); setBusy(true); setError('');
    try { await saveGrade(token, row.id, Number(score), publish); changed(); }
    catch (cause) { setError(describeError(cause)); }
    finally { setBusy(false); }
  }}>
    <label>Điểm nguyên 0–10 cho bài #{row.id}<input required type="number" min="0" max="10" step="1" value={score} onChange={event => setScore(event.target.value)} /></label>
    <label><input type="checkbox" checked={publish} onChange={event => setPublish(event.target.checked)} /> Công bố cho học sinh</label>
    <button disabled={busy}>{busy ? 'Đang lưu…' : 'Lưu điểm'}</button>
    {error && <p role="alert">{error}</p>}
  </form>;
}

function AssignmentPanel({ token, item, teacher }: { token: string; item: Assignment; teacher: boolean }) {
  const [rows, setRows] = useState<Submission[]>([]);
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); let active = true;
    setLoading(true); setError('');
    readSubmissions(token, item.id, teacher, controller.signal).then(
      result => { if (active) { setRows(result); setLoading(false); } },
      cause => { if (active) { setError(describeError(cause)); setLoading(false); } },
    );
    return () => { active = false; controller.abort(); };
  }, [token, item.id, teacher, revision]);
  return <article>
    <h4>{item.title} · #{item.id}</h4>
    <p>Hạn: {item.due_at ? new Date(item.due_at).toLocaleString() : 'Không đặt'}</p>
    {loading && <p role="status">Đang tải bài nộp…</p>}
    {error && <p role="alert">{error}</p>}
    <button onClick={() => setRevision(value => value + 1)}>Tải lại bài và điểm</button>
    {!teacher && <form onSubmit={async event => {
      event.preventDefault(); setBusy(true); setError('');
      try { await submitAnswer(token, item.id, answer); setRevision(value => value + 1); }
      catch (cause) { setError(describeError(cause)); }
      finally { setBusy(false); }
    }}>
      <label>Nội dung bài nộp<textarea required value={answer} onChange={event => setAnswer(event.target.value)} /></label>
      <button disabled={busy}>{busy ? 'Đang gửi…' : 'Nộp / gửi lại cùng nội dung'}</button>
      <p>Đổi nội dung sau lần nộp đầu sẽ nhận 409. Lỗi gửi vẫn giữ nội dung để đối chiếu.</p>
    </form>}
    {!loading && rows.length === 0 && <p>Chưa có bài nộp trong trang kết quả này.</p>}
    {rows.map(row => <section key={row.id}>
      <p>Học sinh #{row.student_id}: {row.answer}</p>
      <p>Nộp lúc {new Date(row.submitted_at).toLocaleString()} · Điểm: {row.score === null ? 'Chưa công bố / chưa chấm' : row.score}</p>
      {teacher && <GradeForm key={`${row.id}:${row.score}:${row.grade_published}:${revision}`} token={token} row={row} changed={() => setRevision(value => value + 1)} />}
    </section>)}
  </article>;
}

export function WorkflowPractice({ token }: { token: string }) {
  const [actor, setActor] = useState<Actor | null>(null);
  const [classDraft, setClassDraft] = useState('1');
  const [classId, setClassId] = useState(1);
  const [items, setItems] = useState<Assignment[]>([]);
  const [title, setTitle] = useState('');
  const [deadline, setDeadline] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); let active = true;
    setLoading(true); setError(''); setItems([]);
    Promise.all([readIdentity(token, controller.signal), readAssignments(token, classId, controller.signal)]).then(
      ([identity, rows]) => { if (active) { setActor(identity); setItems(rows); setLoading(false); } },
      cause => { if (active) { setError(describeError(cause)); setLoading(false); } },
    );
    return () => { active = false; controller.abort(); };
  }, [token, classId, revision]);
  return <section>
    <h2>Giao → nộp → chấm → xem điểm</h2>
    <form onSubmit={event => { event.preventDefault(); setClassId(Number(classDraft)); setRevision(value => value + 1); }}>
      <label>ID lớp<input required type="number" min="1" step="1" value={classDraft} onChange={event => setClassDraft(event.target.value)} /></label>
      <button>Tải lớp</button>
    </form>
    {actor && <p>Tài khoản: {actor.name} · {actor.role}</p>}
    {loading && <p role="status">Đang tải…</p>}
    {error && <p role="alert">{error}</p>}
    {actor?.role === 'teacher' && !loading && <form onSubmit={async event => {
      event.preventDefault(); setBusy(true); setError('');
      try {
        await createAssignment(token, classId, title, deadline ? new Date(deadline).toISOString() : null);
        setTitle(''); setDeadline(''); setRevision(value => value + 1);
      } catch (cause) { setError(describeError(cause)); }
      finally { setBusy(false); }
    }}>
      <label>Tên bài<input required value={title} onChange={event => setTitle(event.target.value)} /></label>
      <label>Hạn theo giờ máy hiện tại (có thể bỏ trống)<input type="datetime-local" value={deadline} onChange={event => setDeadline(event.target.value)} /></label>
      <button disabled={busy}>{busy ? 'Đang giao…' : 'Giao bài ngay'}</button>
    </form>}
    {!loading && !error && items.length === 0 && <p>Chưa có bài tập.</p>}
    <p>Lab tải 20 bài/trang và 20 bài nộp/trang. Bài mở rộng: thêm điều khiển phân trang; không coi đây là toàn bộ dữ liệu.</p>
    {items.map(item => <AssignmentPanel key={`${classId}:${item.id}`} token={token} item={item} teacher={actor?.role === 'teacher'} />)}
  </section>;
}
