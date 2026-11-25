"""Kiểm tra chéo sau khi đọc. Mục tiêu: không để lỗi đọc sai hoặc sót câu trôi qua mà không báo."""

from __future__ import annotations

from .model import ParsedDocument, Section


def _check_declared_count(section: Section) -> None:
    if section.declared_first is None or section.declared_last is None:
        return
    first, last = section.declared_first, section.declared_last
    declared = list(range(first, last + 1))
    found = [q.number for q in section.questions]
    missing = sorted(set(declared) - set(found))
    extra = sorted(set(found) - set(declared))
    if missing or extra:
        parts = [f"Đề ghi câu {first}–{last} ({len(declared)} câu), đọc được {len(found)} câu."]
        if missing:
            parts.append("Thiếu: " + ", ".join(str(n) for n in missing) + ".")
        if extra:
            parts.append("Ngoài khoảng đề ghi: " + ", ".join(str(n) for n in extra) + ".")
        parts.append("Kiểm tra xem tệp có bị rút gọn hay bộ đọc bỏ sót.")
        section.add_flag("count_mismatch", " ".join(parts))


def _check_numbering(section: Section) -> None:
    seen: set[int] = set()
    previous = 0
    for q in section.questions:
        if q.number in seen:
            q.add_flag("duplicate_number", f"Số câu {q.number} xuất hiện hai lần trong phần.")
        elif q.number < previous:
            q.add_flag("out_of_order", f"Câu {q.number} nằm sau câu {previous}.")
        elif previous and q.number != previous + 1:
            q.add_flag("number_gap", f"Câu {q.number} đứng ngay sau câu {previous} (nhảy số).", "info")
        seen.add(q.number)
        previous = max(previous, q.number)


def _check_content(section: Section) -> None:
    for q in section.questions:
        if not q.stem and not q.options:
            q.add_flag("empty_question", "Câu không có nội dung nào được đọc.")


def validate(doc: ParsedDocument) -> None:
    """Gắn cờ lên tài liệu. Không đổi nội dung đã đọc."""
    for section in doc.sections:
        _check_declared_count(section)
        _check_numbering(section)
        _check_content(section)
    if doc.sections and any(s.flags for s in doc.sections):
        doc.add_flag("section_problems", "Có phần bị lệch so với khai báo trong đề; xem cờ của từng phần.")
