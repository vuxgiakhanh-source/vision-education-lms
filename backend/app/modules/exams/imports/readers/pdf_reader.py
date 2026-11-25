"""Đọc đề PDF thành ParsedDocument.

Chữ trích từ PDF dễ sai ký hiệu toán và thứ tự, nên chữ chỉ dùng để ĐỊNH VỊ: tìm "Câu n", tiêu đề phần
và số câu đề tự khai. Nội dung hiển thị cho học sinh phải là ảnh cắt từ trang (render_page).
Đáp án trong PDF chưa được đọc tự động: mọi câu để "missing" cho cô nhập.

Dùng pdfminer.six (định vị) và pypdfium2 (đếm trang, dựng ảnh), không dùng PyMuPDF vì giấy phép AGPL.
"""

from __future__ import annotations

import io
import re
import unicodedata

from .model import Answer, Block, ParsedDocument, Question, Section
from .safety import MAX_FILE_BYTES, UnsafeFileError
from .validators import validate

MAX_PAGES = 200
MIN_CHARS_FOR_TEXT_PAGE = 30

RE_SECTION = re.compile(r"^\s*PH[ẦA]N\s+([IVX]+|\d+)\b", re.IGNORECASE)
RE_DECLARED = re.compile(r"từ\s+câu\s*(\d+)\s*(?:đến|tới|-)\s*(?:câu\s*)?(\d+)", re.IGNORECASE)
RE_QUESTION = re.compile(r"^\s*C[âa]u\s*(\d+)\s*[.:)]", re.IGNORECASE)


def _norm(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _section_kind(title: str):
    low = title.lower()
    if "đúng sai" in low or "đúng/sai" in low or "đúng - sai" in low:
        return "true_false"
    if "trả lời ngắn" in low:
        return "short_answer"
    if "nhiều phương án" in low or "trắc nghiệm" in low:
        return "multiple_choice"
    return "unknown"


def _page_count(data: bytes) -> int:
    import pypdfium2 as pdfium

    try:
        pdf = pdfium.PdfDocument(data)
    except Exception as exc:  # pypdfium2 ném PdfiumError với nhiều loại lỗi
        message = str(exc).lower()
        if "password" in message:
            raise UnsafeFileError("PDF có mật khẩu, không đọc được.") from exc
        raise UnsafeFileError("PDF bị hỏng hoặc không đọc được.") from exc
    try:
        return len(pdf)
    finally:
        pdf.close()


def read_pdf(data: bytes, source_name: str = "") -> ParsedDocument:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LAParams, LTTextContainer, LTTextLine

    if len(data) > MAX_FILE_BYTES:
        raise UnsafeFileError("Tệp quá lớn.")
    if data[:5] != b"%PDF-":
        raise UnsafeFileError("Tệp không phải PDF.")

    pages = _page_count(data)
    doc = ParsedDocument(source_name=source_name, format="pdf", page_count=pages)
    if pages > MAX_PAGES:
        raise UnsafeFileError(f"PDF có {pages} trang, vượt giới hạn {MAX_PAGES} trang.")

    section: Section | None = None
    question: Question | None = None
    text_pages = 0
    blank_pages: list[int] = []
    # Nhãn "Câu" đứng riêng một dòng, số câu nằm dòng sau: (nhãn, trang, vị trí trên trang)
    pending_label: tuple[str, int, float] | None = None

    try:
        layouts = list(extract_pages(io.BytesIO(data), laparams=LAParams()))
    except Exception as exc:
        raise UnsafeFileError("Không đọc được nội dung PDF.") from exc

    for page_no, layout in enumerate(layouts, start=1):
        height = layout.height
        chars = 0
        for container in layout:
            if not isinstance(container, LTTextContainer):
                continue
            container_text = _norm(container.get_text())
            chars += len(container_text.strip())

            lines = [container] if isinstance(container, LTTextLine) else [
                obj for obj in container if isinstance(obj, LTTextLine)
            ]
            i = 0
            while i < len(lines):
                line_text = _norm(lines[i].get_text())
                if RE_SECTION.match(line_text.strip()):
                    # Tiêu đề phần có thể trải qua vài dòng; dừng khi gặp "Câu n." hoặc phần kế để không nuốt câu hỏi.
                    parts = [line_text]
                    j = i + 1
                    while j < len(lines):
                        nxt = _norm(lines[j].get_text())
                        if RE_QUESTION.match(nxt) or RE_SECTION.match(nxt.strip()):
                            break
                        parts.append(nxt)
                        j += 1
                    title = " ".join(" ".join(parts).split())
                    declared = RE_DECLARED.search(title)
                    section = Section(
                        title=title,
                        kind=_section_kind(title),
                        declared_first=int(declared.group(1)) if declared else None,
                        declared_last=int(declared.group(2)) if declared else None,
                    )
                    doc.sections.append(section)
                    question = None
                    i = j
                    continue
                m = RE_QUESTION.match(line_text)
                at_page, at_top = page_no, round(height - lines[i].y1, 1)
                if m is None and pending_label is not None:
                    joined = pending_label[0].strip() + " " + line_text.lstrip()
                    m = RE_QUESTION.match(joined)
                    if m:
                        line_text = joined
                        at_page, at_top = pending_label[1], pending_label[2]
                pending_label = None
                if m is None and re.fullmatch(r"\s*C[âa]u\s*", line_text):
                    pending_label = (line_text, page_no, round(height - lines[i].y1, 1))
                    i += 1
                    continue
                if m:
                    if section is None:
                        section = Section(title="(không có tiêu đề phần)")
                        doc.sections.append(section)
                    question = Question(
                        number=int(m.group(1)),
                        kind=section.kind,
                        stem=[Block("text", " ".join(line_text[m.end():].split()))],
                        page=at_page,
                        top=at_top,
                    )
                    question.answer = Answer("missing", None, [], "PDF: đáp án chưa đọc tự động.")
                    question.add_flag(
                        "pdf_text_locating_only",
                        "Chữ trích từ PDF chỉ dùng để định vị; hiển thị bằng ảnh trang.",
                        "info",
                    )
                    section.questions.append(question)
                i += 1
        if chars >= MIN_CHARS_FOR_TEXT_PAGE:
            text_pages += 1
        else:
            blank_pages.append(page_no)

    if pages and text_pages == 0:
        doc.add_flag("no_text_layer", "PDF dạng quét hoặc ảnh, không có lớp chữ. Cần OCR hoặc cô nhập cấu trúc và đáp án tay.")
    elif blank_pages:
        doc.add_flag("pages_without_text", "Trang không có chữ (có thể là ảnh): " + ", ".join(map(str, blank_pages)) + ".", "info")
    if not doc.questions and text_pages:
        doc.add_flag("no_questions", "Không tìm thấy câu hỏi nào có dạng \"Câu n.\".")
    doc.add_flag("answers_not_read", "Đáp án trong PDF chưa được đọc tự động; cô nhập ở màn duyệt.", "info")
    validate(doc)
    return doc


def render_page(data: bytes, page_index: int, scale: float = 2.0) -> bytes:
    """Dựng một trang PDF thành ảnh PNG (page_index tính từ 0)."""
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(data)
    try:
        if not 0 <= page_index < len(pdf):
            raise IndexError("Trang không tồn tại.")
        bitmap = pdf[page_index].render(scale=scale)
        out = io.BytesIO()
        bitmap.to_pil().save(out, format="PNG")
        return out.getvalue()
    finally:
        pdf.close()
