import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';
import exec from 'k6/execution';

const base = (__ENV.BASE_URL || 'http://127.0.0.1:8088/api').replace(/\/$/, '');
if (!/^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?\/api$/.test(base)) {
  throw new Error('Lab này chỉ gửi tải đến localhost /api. Tự review script khi chuyển sang staging riêng.');
}
const accounts = new SharedArray('accounts', () => JSON.parse(open(__ENV.ACCOUNTS_FILE || './accounts.json')));
if (!accounts.length || accounts.some(account => !account.token || !Number.isInteger(account.student_id))) {
  throw new Error('Cần accounts.json fixture hợp lệ');
}
const rate = Number(__ENV.RATE || '5');
const duration = __ENV.DURATION || '30s';
const mode = __ENV.MODE || 'read';
if (!Number.isInteger(rate) || rate < 1 || !['read', 'submit'].includes(mode)) throw new Error('RATE nguyên dương; MODE read/submit');
export const options = {
  scenarios: { workload: { executor: 'constant-arrival-rate', rate, timeUnit: '1s', duration,
    preAllocatedVUs: 10, maxVUs: Number(__ENV.MAX_VUS || '100'), gracefulStop: '10s' } },
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'], checks: ['rate>0.99'], dropped_iterations: ['count==0'],
  },
  discardResponseBodies: false,
};
http.setResponseCallback(http.expectedStatuses(200));

export default function () {
  const account = accounts[exec.scenario.iterationInTest % accounts.length];
  const params = { headers: { Authorization: `Bearer ${account.token}`, 'Content-Type': 'application/json' },
    timeout: '10s', tags: { name: mode === 'read' ? 'assignment-list' : 'submit-or-retry' } };
  if (mode === 'read') {
    const response = http.get(`${base}/classes/1/assignments?page_size=20`, params);
    check(response, { 'đúng lớp và đủ trang': r => {
      if (r.status !== 200) return false;
      try { const rows = r.json(); return Array.isArray(rows) && rows.length > 0 && rows.length <= 20 && rows.every(row => row.class_id === 1); }
      catch { return false; }
    } });
  } else {
    const response = http.post(`${base}/assignments/1/submissions`, JSON.stringify({ answer: `load-answer-${account.student_id}` }), params);
    check(response, { 'đúng chủ, nội dung và chưa lộ điểm': r => {
      if (r.status !== 200) return false;
      try { const row = r.json(); return row.student_id === account.student_id && row.assignment_id === 1 && row.answer === `load-answer-${account.student_id}` && row.score === null; }
      catch { return false; }
    } });
  }
}
