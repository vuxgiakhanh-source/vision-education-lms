export function titleError(title) {
  if (title.length === 0) return 'Nhập tên lớp.';
  if (title.length > 100) return 'Tên lớp tối đa 100 ký tự JS.';
  return '';
}

export function findClasses(classes, query) {
  const normalized = query.trim().toLowerCase();
  const result = [];
  for (const classroom of classes) {
    if (classroom.title.toLowerCase().includes(normalized)) {
      result.push(classroom);
    }
  }
  return result;
}
