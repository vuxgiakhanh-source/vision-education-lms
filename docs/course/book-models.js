/* Pure teaching models. They do not call APIs, run SQL, or modify the LMS. */
(function (root) {
  'use strict';
  function loginTrace(scenario) {
    const error = scenario === 'wrong' || scenario === 'locked';
    const mustChange = scenario === 'change';
    const code = scenario === 'locked' ? 403 : 401;
    return [
      { lane: 0, label: 'Chưa bấm nút', title: 'Form giữ dữ liệu', text: 'Dữ liệu trên form chưa tự đi vào database. Hành động submit mới bắt đầu luồng.', payload: 'phoneNumber: chuỗi\npassword: không hiển thị', line: 0 },
      { lane: 0, label: '01 / Event', title: 'handleSubmit → onSubmit', text: 'Form xử lý validation trước. Nếu hợp lệ, onSubmit nhận dữ liệu. Đây là lúc hàm được gọi, khác với lúc khai báo hàm.', payload: 'onSubmit(data)\nKiểu: LoginFormData', line: 0 },
      { lane: 0, label: '02 / Client API', title: 'authService.login(data)', text: 'Lớp gọi API đổi phoneNumber thành phone_number theo hợp đồng. Await chưa trả kết quả cho form khi request còn đang xử lý.', payload: 'POST /login\n{ phone_number, password }\nDữ liệu nhạy cảm được ẩn', line: 2 },
      { lane: 1, label: '03 / Router', title: 'FastAPI nhận LoginRequest', text: 'Backend đọc body và kiểm tra schema. Router gọi service; dữ liệu đã qua form vẫn phải được kiểm tra ở server.', payload: 'LoginRequest\n→ LoginService.login(request)', line: 2 },
      { lane: 2, label: '04 / Repository', title: 'Tìm User trong MySQL', text: 'Repository dùng Session để truy vấn theo số điện thoại. Kết quả là User hoặc None; repository không điều hướng trình duyệt.', payload: 'SELECT user theo phone_number\nKết quả giả định: có User', line: 2 },
      error
        ? { lane: 1, label: '05 / Kiểm tra', title: scenario === 'wrong' ? 'Mật khẩu không đúng' : 'Tài khoản bị khóa', text: `Service ném lỗi, router chuyển thành HTTP ${code}. Không tạo token thành công cho tình huống này.`, payload: `HTTP ${code}\nAxios: Promise reject`, line: 9 }
        : { lane: 1, label: '05 / Kiểm tra', title: 'Hợp lệ → tạo response', text: 'Service kiểm tra mật khẩu và trạng thái. Token được tạo ở backend. Cờ bắt đổi mật khẩu quyết định nhánh tiếp theo của form.', payload: `HTTP 200\naccess_token: [ẩn]\nmust_change_password: ${mustChange}`, line: 2 },
      error
        ? { lane: 0, label: '06 / Promise', title: 'Await ném lỗi vào catch', text: 'Luồng bỏ qua các dòng lưu token và điều hướng trong try. Form xử lý lỗi ở catch; không phải request nào cũng có response thành công.', payload: `catch(error)\nHTTP ${code}`, line: 9 }
        : { lane: 0, label: '06 / Promise', title: 'Service frontend trả res.data', text: 'Res trong hàm gọi Axios là response. Nhưng hàm đó return res.data, nên res ở form là body LoginResponse. Hai biến nằm ở hai scope.', payload: 'Form nhận LoginResponse\nKhông nhận nguyên AxiosResponse', line: 2 },
      error
        ? { lane: 0, label: '07 / UI', title: 'setError ở form', text: 'Form hiển thị lỗi theo cách hiện có. Trong repo, lỗi Axios chưa được ánh xạ đầy đủ từ detail backend. Đây là chỗ có thể cải thiện sau khi chốt hợp đồng lỗi.', payload: "setError('root', { message })\nKhông lưu token mới", line: 11 }
        : { lane: 0, label: '07 / UI', title: mustChange ? 'Đi tới đổi mật khẩu' : 'Đi tới dashboard', text: 'Form lưu token và điều hướng. Route frontend không tự cấp quyền API; dashboard hiện dùng mock nên đến được trang chưa chứng minh đã lấy hồ sơ thật.', payload: `localStorage.setItem(...)\nnavigate('${mustChange ? '/change-password' : '/dashboard'}')`, line: mustChange ? 5 : 7 },
    ];
  }
  function memory(strategy, changed) {
    const shared = strategy !== 'immutable';
    return { arrayA: 'Array A', arrayB: strategy === 'alias' ? 'Array A' : 'Array B',
      objectA: 'Object 1', objectB: shared ? 'Object 1' : 'Object 2',
      originalStatus: changed && shared ? 'submitted' : 'pending',
      copyStatus: changed ? 'submitted' : 'pending', shared };
  }
  function stateQueue(start, functional) {
    const requested = start + 1;
    return functional
      ? { result: start + 2, trace: [`Bắt đầu: ${start}`, `updater 1: ${start} + 1 = ${start + 1}`, `updater 2: ${start + 1} + 1 = ${start + 2}`] }
      : { result: requested, trace: [`Snapshot của handler: count = ${start}`, `Lệnh 1: thay bằng ${requested}`, `Lệnh 2: thay bằng ${requested} (vẫn đọc cùng snapshot)`] };
  }
  function join(mode) {
    const members = [{ id: 1, name: 'An' }, { id: 2, name: 'Bình' }, { id: 3, name: 'Chi' }];
    let rows = members.map(member => ({ ...member, submissionId: member.id === 1 ? 11 : null }));
    if (mode === 'inner') rows = rows.filter(row => row.submissionId !== null);
    if (mode === 'missing') rows = rows.filter(row => row.submissionId === null);
    return { rows, countStar: rows.length, countSubmission: rows.filter(row => row.submissionId !== null).length };
  }
  function transaction(step, split, fail) {
    const committed = [], pending = [];
    if (step >= 1) (split ? committed : pending).push('classes: Lớp A');
    if (step >= 2) {
      if (fail) pending.length = 0;
      else (split ? committed : pending).push('memberships: cô → Lớp A');
    }
    if (step >= 3 && !fail) committed.push(...pending.splice(0));
    return { committed, pending, failed: step >= 2 && fail, orphan: step >= 2 && fail && split };
  }
  function permission(actor, authenticated = true, active = true) {
    if (!authenticated) return { code: 401, allowed: false, reason: 'Chưa xác thực danh tính hợp lệ.' };
    if (!active) return { code: 403, allowed: false, reason: 'Tài khoản không hoạt động theo policy của ví dụ.' };
    const choices = {
      own: [true, 'Học sinh là chủ bài nộp.'], other: [false, 'Học sinh khác chủ bài; token hợp lệ không cấp quyền đọc chéo.'],
      teacher: [true, 'Cô được phân công lớp và có quyền đọc bài nộp.'], outsider: [false, 'Cô không thuộc phạm vi lớp của bài.'],
      assistant: [false, 'Trợ giảng chỉ được điểm danh trong policy bài học, chưa được đọc bài.'],
      admin: [false, 'Policy bài học không mặc định cấp quyền đọc nội dung học tập cho mọi admin.'],
    };
    const [allowed, reason] = choices[actor] || [false, 'Không có quyền rõ ràng.'];
    return { code: allowed ? 200 : 403, allowed, reason };
  }
  function deadline(options) {
    const checks = [];
    function check(label, ok, failure) {
      checks.push({ label, ok });
      return ok ? null : { allowed: false, title: failure, checks };
    }
    let fail = check('Học sinh đang hoạt động', options.active && options.student, 'Từ chối: danh tính/trạng thái không phù hợp');
    if (fail) return fail;
    fail = check('Đúng thành viên lớp', options.member, 'Từ chối: không thuộc lớp');
    if (fail) return fail;
    const answer = String(options.answer).trim();
    fail = check('Nội dung 1–10000 ký tự', [...answer].length >= 1 && [...answer].length <= 10000, 'Từ chối: nội dung không hợp lệ');
    if (fail) return fail;
    if (options.existing !== 'none') {
      fail = check('Khớp bản nộp cũ', options.existing === 'same', '409: đã nộp nội dung khác');
      if (fail) return fail;
      return { allowed: true, retry: true, title: 'Trả bản cũ · giữ timestamp 12:00', checks };
    }
    fail = check('Bài đã công bố', options.published, 'Từ chối: bài nháp hoặc đã đóng');
    if (fail) return fail;
    fail = check('Giờ server ≤ 13:00', options.offset <= 0, 'Từ chối: quá hạn cho bản nộp mới');
    if (fail) return fail;
    return { allowed: true, retry: false, title: 'Nhận bản nộp mới', checks };
  }
  function parseNumber(text) {
    const value = String(text).trim();
    if (value.length > 100 || !/^[+-]?[0-9]+(?:\.[0-9]+)?$/.test(value)) throw new Error('Định dạng không thuộc hợp đồng số thập phân của bài học.');
    const negative = value.startsWith('-');
    const parts = value.replace(/^[+-]/, '').split('.');
    const whole = parts[0].replace(/^0+(?=\d)/, '');
    const fraction = (parts[1] || '').replace(/0+$/, '');
    const normalized = whole + (fraction ? '.' + fraction : '');
    return (negative && normalized !== '0' ? '-' : '') + normalized;
  }
  function report(correct, attempted, total) {
    if (![correct, attempted, total].every(Number.isInteger) || total <= 0 || correct < 0 || attempted < correct || total < attempted) {
      return { valid: false, reason: 'Cần số nguyên: 0 ≤ đúng ≤ đã làm ≤ tổng; tổng > 0.' };
    }
    return { valid: true, whole: correct / total * 100, attempted: attempted ? correct / attempted * 100 : null };
  }
  function http(kind) {
    if (kind === 'network') return { kind: 'error', label: 'Lỗi mạng · chưa có HTTP response', payload: 'Không suy ra đã hết phiên từ lỗi mạng.', state: 'error' };
    if (kind === '401') return { kind: 'error', label: 'HTTP 401 · xử lý phiên', payload: '{ detail: "Xác thực không hợp lệ" }', state: 'error' };
    if (kind === 'bad') return { kind: 'error', label: 'HTTP 200 nhưng body sai hợp đồng', payload: '[{ id: "một", title: null }]', state: 'validation error' };
    if (kind === 'empty') return { kind: 'success', label: 'HTTP 200 · thành công rỗng', payload: '[]', state: 'success: []' };
    return { kind: 'success', label: 'HTTP 200 · thành công có dữ liệu', payload: '[{ id: 1, title: "Hàm số", status: "pending", score: null }]', state: 'success: [Task]' };
  }
  function viewport(physical, scale, zoom) {
    return Math.floor(physical / (scale / 100) / (zoom / 100));
  }
  const models = { loginTrace, memory, stateQueue, join, transaction, permission, deadline, parseNumber, report, http, viewport };
  if (typeof module !== 'undefined' && module.exports) module.exports = models;
  else root.BookModels = models;
})(typeof window !== 'undefined' ? window : globalThis);
