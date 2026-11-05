import { averageScore, countPending, markSubmitted, parseTask, searchTasks } from './tasks.ts';
import type { Task } from './tasks.ts';

let checks = 0;
function check(condition: boolean, message: string): void {
  checks += 1;
  if (!condition) throw new Error(message);
}
function throws(action: () => unknown, message: string): void {
  let failed = false;
  try { action(); } catch { failed = true; }
  check(failed, message);
}

const tasks: Task[] = [
  { id: 1, title: 'Hàm số', status: 'pending', score: null },
  { id: 2, title: 'Tích phân', status: 'graded', score: 0 },
  { id: 3, title: 'Hình học', status: 'graded', score: 10 },
];

check(countPending([]) === 0, 'Mảng rỗng');
check(countPending(tasks) === 1, 'Đếm đúng pending');
check(searchTasks(tasks, ' HÀM ').length === 1, 'Trim và hoa/thường');
check(searchTasks(tasks, 'Không tồn tại').length === 0, 'Không có kết quả');
check(searchTasks(tasks, '').length === 3, 'Query rỗng');
check(averageScore(tasks) === 5, 'Giữ điểm 0');
check(averageScore([]) === null, 'Chưa có điểm');
check(averageScore([tasks[0]]) === null, 'Chưa chấm khác 0');

const updated = markSubmitted(tasks, 1);
check(updated !== tasks, 'Tạo array mới');
check(updated[0] !== tasks[0], 'Tạo object thay đổi mới');
check(updated[1] === tasks[1], 'Giữ tham chiếu object không đổi');
check(tasks[0].status === 'pending', 'Không sửa gốc');
check(updated[0].status === 'submitted', 'Cập nhật pending');
check(markSubmitted(tasks, 2)[1].status === 'graded', 'Không lùi trạng thái graded');
check(parseTask({ id: 1, title: ' X ', status: 'graded', score: 0 }).title === 'X', 'Parse và trim');

for (const value of [
  null, {}, { id: '1', title: 'X', status: 'pending', score: null },
  { id: 1, title: ' ', status: 'pending', score: null },
  { id: 1, title: 'X', status: 'graded', score: null },
  { id: 1, title: 'X', status: 'graded', score: NaN },
  { id: 1, title: 'X', status: 'graded', score: 11 },
  { id: 1, title: 'X', status: 'pending', score: 0 },
  { id: 1, title: 'X', status: 'unknown', score: null },
]) {
  throws(() => parseTask(value), 'Từ chối dữ liệu sai');
}

console.log(`${checks} kiểm tra TypeScript đã qua.`);
