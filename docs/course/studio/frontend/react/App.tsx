import { useState } from 'react';
import type { FormEvent } from 'react';
import type { Classroom } from './data';
import { findClasses, titleError } from './data';
import { ClassList } from './ClassList';

export function App() {
  const [classes, setClasses] = useState<Classroom[]>([]);
  const [nextId, setNextId] = useState(1);
  const [title, setTitle] = useState('');
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const visible = findClasses(classes, query);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalized = title.trim();
    const message = titleError(normalized);
    setError(message);
    setNotice('');
    if (message !== '') return;
    const classroom = { id: nextId, title: normalized };
    setClasses(previous => [...previous, classroom]);
    setNextId(previous => previous + 1);
    setTitle('');
    setNotice(`Đã thêm lớp ${normalized}. Nếu đang tìm kiếm, lớp có thể bị bộ lọc ẩn.`);
  }

  return <main className="page">
    <header>
      <p className="eyebrow">Xưởng tự viết · React + TypeScript</p>
      <h1>Sổ lớp học</h1>
      <p>Dữ liệu ở bộ nhớ của tab. Tải lại trang sẽ bắt đầu lại.</p>
    </header>
    <section className="panel" aria-labelledby="create-heading">
      <h2 id="create-heading">Thêm lớp</h2>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="class-title">Tên lớp</label>
        <div className="toolbar">
          <input id="class-title" name="title" value={title}
            onChange={event => setTitle(event.target.value)}
            aria-invalid={error !== ''} aria-describedby="title-help title-error" />
          <button type="submit">Thêm lớp</button>
        </div>
        <p id="title-help" className="help">Tên sau khi bỏ khoảng trắng hai đầu phải có 1–100 ký tự JS.</p>
        <p id="title-error" className="error" role="alert">{error}</p>
      </form>
      <p role="status">{notice}</p>
    </section>
    <section className="panel" aria-labelledby="list-heading">
      <h2 id="list-heading">Các lớp của mình</h2>
      <label htmlFor="class-query">Tìm theo tên lớp</label>
      <input id="class-query" type="search" name="query" value={query}
        onChange={event => setQuery(event.target.value)} />
      <p role="status">Hiện {visible.length} / {classes.length} lớp</p>
      <ClassList items={visible} />
      {classes.length === 0 && <p>Chưa có lớp. Thêm lớp đầu tiên ở trên.</p>}
      {classes.length > 0 && visible.length === 0 && <p>Không có lớp khớp từ tìm kiếm.</p>}
    </section>
  </main>;
}
