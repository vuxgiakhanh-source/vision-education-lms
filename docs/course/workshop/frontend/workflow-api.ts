import axios from 'axios';
import { z } from 'zod';

const api = axios.create({ baseURL: import.meta.env.VITE_LAB_API_URL || 'http://127.0.0.1:8001', timeout: 10000 });
const actor = z.object({ id: z.number().int(), name: z.string(), role: z.enum(['teacher', 'student']) });
const assignment = z.object({ id: z.number().int(), class_id: z.number().int(), title: z.string(), due_at: z.string().nullable() });
const submission = z.object({ id: z.number().int(), assignment_id: z.number().int(), student_id: z.number().int(),
  answer: z.string(), submitted_at: z.string(), score: z.number().int().min(0).max(10).nullable(), grade_published: z.boolean() });
export type Actor = z.infer<typeof actor>;
export type Assignment = z.infer<typeof assignment>;
export type Submission = z.infer<typeof submission>;

export async function readIdentity(token: string, signal?: AbortSignal) {
  return actor.parse((await api.get('/me', { signal, headers: { Authorization: `Bearer ${token}` } })).data);
}
export async function readAssignments(token: string, classId: number, signal?: AbortSignal) {
  return assignment.array().parse((await api.get(`/classes/${classId}/assignments`, { signal, headers: { Authorization: `Bearer ${token}` } })).data);
}
export async function createAssignment(token: string, classId: number, title: string, dueAt: string | null) {
  return assignment.parse((await api.post(`/classes/${classId}/assignments`, { title, due_at: dueAt }, { headers: { Authorization: `Bearer ${token}` } })).data);
}
export async function readSubmissions(token: string, id: number, teacher: boolean, signal?: AbortSignal) {
  const suffix = teacher ? 'submissions' : 'my-submission';
  const data: unknown = (await api.get(`/assignments/${id}/${suffix}`, { signal, headers: { Authorization: `Bearer ${token}` } })).data;
  if (teacher) return submission.array().parse(data);
  const row = submission.nullable().parse(data);
  return row ? [row] : [];
}
export async function submitAnswer(token: string, id: number, answer: string) {
  return submission.parse((await api.post(`/assignments/${id}/submissions`, { answer }, { headers: { Authorization: `Bearer ${token}` } })).data);
}
export async function saveGrade(token: string, id: number, score: number, publish: boolean) {
  return submission.parse((await api.put(`/submissions/${id}/grade`, { score, publish }, { headers: { Authorization: `Bearer ${token}` } })).data);
}
