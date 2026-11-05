(function (root) {
  'use strict';
  function assess(drill, result) {
    if (!result.ok) return { matches: false, message: 'Chưa chạy xong. Đọc lỗi và sửa một chỗ trước.' };
    if (JSON.stringify(result.output) !== JSON.stringify(drill.output)) {
      return { matches: false, message: 'Output chưa khớp. Theo bảng vết để tìm bước đầu tiên lệch dự đoán.' };
    }
    const final = result.trace.at(-1)?.variables || {};
    for (const [name, expected] of Object.entries(drill.variables || {})) {
      if (!Object.hasOwn(final, name) || !Object.is(final[name], expected)) {
        return { matches: false, message: 'Output khớp nhưng biến ' + name + ' chưa đúng yêu cầu. Tự tạo và cập nhật biến thay vì chỉ in đáp án.' };
      }
    }
    for (const [name, values] of Object.entries(drill.trace_values || {})) {
      let position = 0;
      for (const step of result.trace) {
        if (Object.hasOwn(step.variables, name) && Object.is(step.variables[name], values[position])) position++;
        if (position === values.length) break;
      }
      if (position < values.length) return { matches: false, message: 'Kết quả cuối đúng nhưng chưa thấy biến ' + name + ' đi qua các giá trị bài yêu cầu. Xem lại thứ tự tạo và cập nhật.' };
    }
    return { matches: true, message: 'Các điều kiện nhỏ đã khớp. Chưa kết luận mày đã hiểu: giải thích từng dấu, rồi tự đổi input và dự đoán lại.' };
  }
  const api = { assess };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.StudyCoach = api;
})(typeof window !== 'undefined' ? window : globalThis);
