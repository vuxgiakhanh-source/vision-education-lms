import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { createClass, describeError, listClasses } from './class-api';
import type { Classroom } from './class-api';

type State = { kind: 'loading' } | { kind: 'error'; message: string }
  | { kind: 'success'; items: Classroom[] };
const formSchema = z.object({ title: z.string().trim().min(1, 'Nhập tên lớp')
  .refine(value => [...value].length <= 200, 'Tối đa 200 Unicode code point') });
type Values = z.infer<typeof formSchema>;

export function ClassroomPractice({ token }: { token: string }) {
  const [state, setState] = useState<State>({ kind: 'loading' });
  const [reload, setReload] = useState(0);
  const [query, setQuery] = useState('');
  const { register, handleSubmit, reset, setError, formState: { errors, isSubmitting } } =
    useForm<Values>({ resolver: zodResolver(formSchema), defaultValues: { title: '' } });
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    setState({ kind: 'loading' });
    listClasses(token, controller.signal).then(
      items => { if (active) setState({ kind: 'success', items }); },
      error => { if (active) setState({ kind: 'error', message: describeError(error) }); },
    );
    return () => { active = false; controller.abort(); };
  }, [token, reload]);

  async function submit(values: Values) {
    try {
      await createClass(token, values.title);
      reset();
      setReload(previous => previous + 1);
    } catch (error) {
      setError('root', { message: describeError(error) });
    }
  }

  const items = state.kind === 'success' ? state.items : [];
  const visible = items.filter(item => item.title.toLowerCase().includes(query.trim().toLowerCase()));
  return <section>
    <h2>Lớp trong phạm vi tài khoản</h2>
    <form onSubmit={handleSubmit(submit)}>
      <label htmlFor="title">Tên lớp mới</label>
      <input id="title" {...register('title')} aria-invalid={!!errors.title} />
      {errors.title && <p role="alert">{errors.title.message}</p>}
      {errors.root && <p role="alert">{errors.root.message}</p>}
      <button disabled={isSubmitting} type="submit">{isSubmitting ? 'Đang lưu…' : 'Tạo lớp (quyền cô)'}</button>
    </form>
    <label htmlFor="class-query">Tìm trong trang kết quả</label>
    <input id="class-query" value={query} onChange={event => setQuery(event.target.value)} />
    {state.kind === 'loading' && <p role="status">Đang tải…</p>}
    {state.kind === 'error' && <div><p role="alert">{state.message}</p>
      <button onClick={() => setReload(value => value + 1)}>Thử lại</button></div>}
    {state.kind === 'success' && <>
      <p>{visible.length} lớp trên trang đã tải.</p>
      {visible.length === 0 ? <p>Chưa có lớp khớp. Kiểm tra bộ lọc và quyền lớp.</p> :
        <ul>{visible.map(item => <li key={item.id}><strong>{item.title}</strong> · #{item.id}</li>)}</ul>}
    </>}
  </section>;
}
