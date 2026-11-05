import { StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ClassroomPractice } from './ClassroomPractice';
import { WorkflowPractice } from './WorkflowPractice';
import './style.css';

function App() {
  const [draft, setDraft] = useState('');
  const [token, setToken] = useState('');
  return <main>
    <h1>Xưởng lớp học</h1>
    <p>Dùng token fixture của lab cục bộ. Đây là công cụ học, chưa phải màn đăng nhập sản phẩm.</p>
    <form onSubmit={event => { event.preventDefault(); setToken(draft.trim()); }}>
      <label htmlFor="token">Token tài khoản mẫu</label>
      <input id="token" type="password" value={draft} onChange={event => setDraft(event.target.value)} />
      <button type="submit">Áp dụng tài khoản</button>
      <button type="button" onClick={() => { setToken(''); setDraft(''); }}>Xóa phiên mẫu</button>
    </form>
    {token && <div key={token}><ClassroomPractice token={token} /><WorkflowPractice token={token} /></div>}
  </main>;
}

const root = document.getElementById('root');
if (!root) throw new Error('Không có root');
createRoot(root).render(<StrictMode><App /></StrictMode>);
