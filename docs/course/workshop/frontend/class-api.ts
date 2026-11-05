import axios from 'axios';
import { z } from 'zod';

const baseURL = import.meta.env.VITE_LAB_API_URL || 'http://127.0.0.1:8001';
const classroomSchema = z.object({
  id: z.number().int().positive(), title: z.string().min(1), teacher_id: z.number().int().positive(),
});
export type Classroom = z.infer<typeof classroomSchema>;
const authorization = (token: string) => ({ Authorization: `Bearer ${token}` });

export async function listClasses(token: string, signal: AbortSignal): Promise<Classroom[]> {
  const response = await axios.get<unknown>('/classes', { baseURL, headers: authorization(token), signal });
  return z.array(classroomSchema).parse(response.data);
}

export async function createClass(token: string, title: string): Promise<Classroom> {
  const response = await axios.post<unknown>('/classes', { title }, { baseURL, headers: authorization(token) });
  return classroomSchema.parse(response.data);
}

export function describeError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) return 'Không kết nối được API. Kiểm tra server và Network.';
    const messages: Record<number, string> = {
      401: 'Token không hợp lệ/hết hạn.', 403: 'Tài khoản không có quyền thực hiện.',
      404: 'Không thấy tài nguyên trong phạm vi được phép.', 422: 'Dữ liệu gửi không hợp lệ.',
      409: 'Bài đã có nội dung khác hoặc đã quá hạn. Tải lại để đối chiếu.',
    };
    return messages[error.response.status] ?? `API trả HTTP ${error.response.status}`;
  }
  return 'Response sai hợp đồng hoặc có lỗi chưa dự kiến. Xem công cụ phát triển.';
}
