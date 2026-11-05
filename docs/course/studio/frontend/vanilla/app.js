import { findClasses, titleError } from './data.js';

const form = document.querySelector('#create-form');
const titleInput = document.querySelector('#class-title');
const queryInput = document.querySelector('#class-query');
const list = document.querySelector('#class-list');
const summary = document.querySelector('#summary');
const empty = document.querySelector('#empty-message');
const error = document.querySelector('#title-error');
const notice = document.querySelector('#notice');

if (!form || !titleInput || !queryInput || !list || !summary || !empty || !error || !notice) {
  throw new Error('Thiếu phần tử HTML. Kiểm tra id trong index.html.');
}

let classes = [];
let nextId = 1;

function render() {
  const visible = findClasses(classes, queryInput.value);
  list.replaceChildren();
  for (const classroom of visible) {
    const item = document.createElement('li');
    item.className = 'class-card';
    const title = document.createElement('h3');
    title.textContent = classroom.title;
    const description = document.createElement('p');
    description.textContent = `Mã lớp: ${classroom.id}`;
    item.append(title, description);
    list.append(item);
  }
  summary.textContent = `Hiện ${visible.length} / ${classes.length} lớp`;
  empty.textContent = classes.length === 0
    ? 'Chưa có lớp. Thêm lớp đầu tiên ở trên.'
    : visible.length === 0 ? 'Không có lớp khớp từ tìm kiếm.' : '';
}

function handleSubmit(event) {
  event.preventDefault();
  const title = titleInput.value.trim();
  const message = titleError(title);
  error.textContent = message;
  titleInput.setAttribute('aria-invalid', String(message !== ''));
  notice.textContent = '';
  if (message !== '') return;
  classes.push({ id: nextId, title });
  nextId = nextId + 1;
  titleInput.value = '';
  notice.textContent = `Đã thêm lớp ${title}. Nếu đang tìm kiếm, lớp có thể bị bộ lọc ẩn.`;
  render();
  titleInput.focus();
}

form.addEventListener('submit', handleSubmit);
queryInput.addEventListener('input', render);
render();
