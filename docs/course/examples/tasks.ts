// Lời giải học tập thuần TypeScript, không gọi API hoặc sửa dashboard.
export type Task =
  | { id: number; title: string; status: 'pending' | 'submitted'; score: null }
  | { id: number; title: string; status: 'graded'; score: number };

export function countPending(tasks: readonly Task[]): number {
  return tasks.filter(task => task.status === 'pending').length;
}

export function searchTasks(tasks: readonly Task[], query: string): Task[] {
  const normalized = query.trim().toLowerCase();
  return tasks.filter(task => task.title.toLowerCase().includes(normalized));
}

export function markSubmitted(tasks: readonly Task[], taskId: number): Task[] {
  return tasks.map(task => task.id === taskId && task.status === 'pending'
    ? { ...task, status: 'submitted' }
    : task);
}

export function averageScore(tasks: readonly Task[]): number | null {
  const scores = tasks.filter(task => task.status === 'graded').map(task => task.score);
  if (scores.length === 0) return null;
  if (scores.some(score => !Number.isFinite(score) || score < 0 || score > 10)) {
    throw new Error('Điểm không hợp lệ');
  }
  return scores.reduce((total, score) => total + score, 0) / scores.length;
}

export function parseTask(value: unknown): Task {
  if (typeof value !== 'object' || value === null ||
      !('id' in value) || !('title' in value) ||
      !('status' in value) || !('score' in value)) {
    throw new Error('Thiếu dữ liệu task');
  }
  const { id, title, status, score } = value;
  if (typeof id !== 'number' || !Number.isInteger(id) || id <= 0 ||
      typeof title !== 'string' || title.trim() === '') {
    throw new Error('Id hoặc title không hợp lệ');
  }
  if (status === 'graded') {
    if (typeof score !== 'number' || !Number.isFinite(score) || score < 0 || score > 10) {
      throw new Error('Điểm không hợp lệ');
    }
    return { id, title: title.trim(), status, score };
  }
  if ((status === 'pending' || status === 'submitted') && score === null) {
    return { id, title: title.trim(), status, score };
  }
  throw new Error('Trạng thái hoặc điểm không hợp lệ');
}
