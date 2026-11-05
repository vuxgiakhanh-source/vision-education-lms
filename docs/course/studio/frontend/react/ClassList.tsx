import type { Classroom } from './data';

export function ClassList({ items }: { items: Classroom[] }) {
  return <ul className="class-list">
    {items.map(classroom => <li className="class-card" key={classroom.id}>
      <h3>{classroom.title}</h3>
      <p>Mã lớp: {classroom.id}</p>
    </li>)}
  </ul>;
}
