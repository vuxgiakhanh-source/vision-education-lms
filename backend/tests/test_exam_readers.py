"""Test bộ đọc đề (DOCX, PDF). Tệp thử được dựng tại chỗ, không dùng đề thật của cô.

Nguyên tắc cần giữ: không có bằng chứng thì đáp án là "missing"; không chắc thì có Flag mức error;
không bao giờ đọc sai mà không báo.
"""

from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

import pytest

from app.modules.exams.imports.readers import (
    UnsafeFileError,
    UnsupportedFormatError,
    read_exam,
)
from app.modules.exams.imports.readers.docx_reader import read_docx
from app.modules.exams.imports.readers.model import plain

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:v="urn:schemas-microsoft-com:vml" '
    'xmlns:o="urn:schemas-microsoft-com:office:office" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)
RELS = (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="x" Target="media/image1.wmf"/>'
    '<Relationship Id="rId2" Type="x" Target="media/image2.png"/>'
    "</Relationships>"
)


# ----- dựng tệp Word thử -----
def run(text: str, mark: str = "", bold: bool = False) -> str:
    rpr = ""
    if bold:
        rpr += "<w:b/>"
    if "H" in mark:
        rpr += '<w:highlight w:val="yellow"/>'
    if "U" in mark:
        rpr += '<w:u w:val="single"/>'
    rpr = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def tab() -> str:
    return "<w:r><w:tab/></w:r>"


def eq(mark: str = "", rid: str = "rId1") -> str:
    rpr = '<w:rPr><w:highlight w:val="yellow"/></w:rPr>' if "H" in mark else ""
    return (
        f"<w:r>{rpr}<w:object><v:shape><v:imagedata r:id=\"{rid}\"/></v:shape>"
        '<o:OLEObject ProgID="Equation.DSMT4"/></w:object></w:r>'
    )


def p(*runs: str) -> str:
    return f"<w:p>{''.join(runs)}</w:p>"


def table() -> str:
    return "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>x</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"


def make_docx(*body: str, extra_files: dict[str, bytes] | None = None, document_xml: str | None = None) -> bytes:
    xml = document_xml or f'<?xml version="1.0" encoding="UTF-8"?><w:document {NS}><w:body>{"".join(body)}</w:body></w:document>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("word/document.xml", xml)
        zf.writestr("word/_rels/document.xml.rels", RELS)
        for name, content in (extra_files or {}).items():
            zf.writestr(name, content)
    return buf.getvalue()


def opts(a: str = "", b: str = "", c: str = "", d: str = "") -> str:
    """Một dòng 4 phương án, mỗi tham số là mark của phương án đó."""
    return p(
        tab(), run("A. "), run("một", a), tab(), run("B. "), run("hai", b),
        tab(), run("C. "), run("ba", c), tab(), run("D. "), run("bốn", d),
    )


def read(*body: str) -> object:
    return read_docx(make_docx(*body), "thu.docx")


def only_question(doc):
    assert len(doc.questions) == 1
    return doc.questions[0]


# ----- đáp án trắc nghiệm -----
def test_marked_option_is_suggested_from_highlight():
    q = only_question(read(p(run("Câu 1. Chọn đúng.")), opts(b="H")))
    assert q.kind == "multiple_choice"
    assert list(q.options) == ["A", "B", "C", "D"]
    assert q.answer.status == "suggested"
    assert q.answer.value == "B"
    assert q.answer.sources == ["highlight"]


def test_underline_also_counts_as_mark():
    q = only_question(read(p(run("Câu 1. x")), opts(c="U")))
    assert q.answer.value == "C"


def test_no_mark_is_missing_never_a_default():
    q = only_question(read(p(run("Câu 1. x")), opts()))
    assert q.answer.status == "missing"
    assert q.answer.value is None
    assert q.needs_review


def test_two_marked_options_is_conflict_with_no_value():
    q = only_question(read(p(run("Câu 1. x")), opts(a="H", c="H")))
    assert q.answer.status == "conflict"
    assert q.answer.value is None
    assert any(f.code == "multiple_marked" for f in q.flags)


def test_highlighted_whitespace_alone_is_not_a_mark():
    row = p(tab(), run("A. "), run("một"), run(" ", "H"), tab(), run("B. "), run("hai"),
            tab(), run("C. "), run("ba"), tab(), run("D. "), run("bốn"))
    q = only_question(read(p(run("Câu 1. x")), row))
    assert q.answer.status == "missing"


def test_mark_on_label_only_counts_for_that_option():
    row = p(tab(), run("A. "), run("một"), tab(), run("B. ", "H"), run("hai"),
            tab(), run("C. "), run("ba"), tab(), run("D. "), run("bốn"))
    q = only_question(read(p(run("Câu 1. x")), row))
    assert q.answer.value == "B"


def test_options_split_over_two_lines_are_read():
    two = [
        p(tab(), run("A. "), run("một"), tab(), run("B. "), run("hai", "H")),
        p(tab(), run("C. "), run("ba"), tab(), run("D. "), run("bốn")),
    ]
    q = only_question(read(p(run("Câu 1. x")), *two))
    assert list(q.options) == ["A", "B", "C", "D"]
    assert q.answer.value == "B"


def test_options_each_on_own_line_are_read():
    lines = [p(tab(), run(f"{label}. "), run(text, "H" if label == "D" else "")) for label, text in zip("ABCD", ["a", "b", "c", "d"])]
    q = only_question(read(p(run("Câu 1. x")), *lines))
    assert list(q.options) == ["A", "B", "C", "D"]
    assert q.answer.value == "D"


# ----- khối Lời giải nằm giữa đề và phương án -----
def test_solution_between_stem_and_options_keeps_options():
    doc = read(
        p(run("Câu 1. x")),
        p(run("Lời giải", bold=True)),
        p(run("Chọn B", "H")),
        p(run("Ta có kết quả.")),
        opts(b="H"),
    )
    q = only_question(doc)
    assert list(q.options) == ["A", "B", "C", "D"]
    assert q.solution_choice == "B"
    assert q.answer.status == "suggested"
    assert q.answer.sources == ["highlight", "solution"]
    assert "Ta có kết quả" in q.solution_text
    assert "Ta có kết quả" not in plain(q.stem)


def test_solution_disagreeing_with_mark_is_conflict_not_silent():
    doc = read(p(run("Câu 1. x")), p(run("Lời giải")), p(run("Chọn A")), opts(b="H"))
    q = only_question(doc)
    assert q.answer.status == "conflict"
    assert q.answer.value == "B"  # giữ dấu đánh dấu để cô thấy, nhưng không được coi là chắc
    assert any(f.code == "answer_sources_disagree" for f in q.flags)
    assert q.needs_review


def test_solution_only_answer_is_single_source():
    doc = read(p(run("Câu 1. x")), p(run("Lời giải")), p(run("Chọn C")), opts())
    q = only_question(doc)
    assert q.answer.status == "suggested"
    assert q.answer.value == "C"
    assert q.answer.sources == ["solution"]


def test_second_option_group_inside_solution_is_flagged():
    doc = read(p(run("Câu 1. x")), opts(a="H"), p(run("Lời giải")), opts())
    q = only_question(doc)
    assert any(f.code == "options_restart" for f in q.flags)


# ----- không nhầm nhãn trong đề với phương án -----
def test_label_inside_stem_sentence_is_not_an_option():
    doc = read(
        p(run("Câu 1. Cho điểm C. Có bao nhiêu điểm D thỏa mãn?")),
        p(run("C. là điểm đặc biệt của đoạn thẳng.")),
        opts(a="H"),
    )
    q = only_question(doc)
    assert list(q.options) == ["A", "B", "C", "D"]
    assert q.options["C"] and plain(q.options["C"]) == "ba"
    assert "điểm đặc biệt" in plain(q.stem)


def test_options_must_follow_in_order():
    row = p(tab(), run("B. "), run("hai"), tab(), run("A. "), run("một"))
    q = only_question(read(p(run("Câu 1. x")), row))
    assert q.options == {}
    assert any(f.code == "options_missing" for f in q.flags) or q.kind == "unknown"


def test_incomplete_options_are_flagged():
    row = p(tab(), run("A. "), run("một"), tab(), run("B. "), run("hai"))
    doc = read(
        p(run("PHẦN I. Câu trắc nghiệm nhiều phương án lựa chọn.")),
        p(run("Câu 1. x")),
        row,
    )
    q = only_question(doc)
    assert any(f.code == "options_incomplete" for f in q.flags)


# ----- đúng/sai -----
TF_SECTION = "PHẦN II. Câu trắc nghiệm đúng sai. Thí sinh trả lời từ câu 1 đến câu 1."


def tf_line(marks: str) -> str:
    """marks: 4 ký tự, mỗi ký tự là mark của ý a,b,c,d ('-' là không đánh dấu)."""
    parts = []
    for label, mark in zip("abcd", marks):
        parts += [tab(), run(f"{label}) "), run("nội dung", "" if mark == "-" else mark)]
    return p(*parts)


def test_true_false_on_one_line_reads_all_four():
    doc = read(p(run(TF_SECTION)), p(run("Câu 1. Khi đó:")), tf_line("HH-H"))
    q = only_question(doc)
    assert q.kind == "true_false"
    assert list(q.options) == ["a", "b", "c", "d"]
    assert q.answer.status == "suggested"
    assert q.answer.value == {"a": True, "b": True, "c": False, "d": True}
    assert any(f.code == "convention_assumed" for f in q.flags)


def test_true_false_without_marks_is_missing_not_all_false():
    doc = read(p(run(TF_SECTION)), p(run("Câu 1. Khi đó:")), tf_line("----"))
    q = only_question(doc)
    assert q.answer.status == "missing"
    assert q.answer.value is None


def test_true_false_with_too_few_statements_is_error_in_explicit_section():
    row = p(tab(), run("a) "), run("x", "H"), tab(), run("b) "), run("y"))
    doc = read(p(run(TF_SECTION)), p(run("Câu 1. Khi đó:")), row)
    q = only_question(doc)
    flag = next(f for f in q.flags if f.code == "statements_incomplete")
    assert flag.severity == "error"


def test_true_false_with_two_statements_without_section_is_info_only():
    row = p(tab(), run("a) "), run("x"), tab(), run("b) "), run("y"))
    doc = read(p(run("Câu 1. Khi đó:")), row)
    q = only_question(doc)
    assert q.kind == "true_false"
    flag = next(f for f in q.flags if f.code == "statements_incomplete")
    assert flag.severity == "info"


# ----- trả lời ngắn -----
def test_short_answer_without_key_is_missing():
    doc = read(p(run("PHẦN III. Câu trắc nghiệm trả lời ngắn. Thí sinh trả lời từ câu 1 đến câu 1.")), p(run("Câu 1. Tính.")))
    q = only_question(doc)
    assert q.kind == "short_answer"
    assert q.answer.status == "missing"


def test_short_answer_with_key_line_is_suggested():
    doc = read(
        p(run("PHẦN III. Câu trắc nghiệm trả lời ngắn. Thí sinh trả lời từ câu 1 đến câu 1.")),
        p(run("Câu 1. Tính.")),
        p(run("Đáp số: 3,5")),
    )
    q = only_question(doc)
    assert q.answer.status == "suggested"
    assert q.answer.value == "3,5"


def test_question_without_any_structure_is_unknown_and_flagged():
    q = only_question(read(p(run("Câu 1. Chứng minh rằng ..."))))
    assert q.kind == "unknown"
    assert any(f.code == "kind_unknown" for f in q.flags)
    assert q.answer.status == "missing"


# ----- số câu, đánh số -----
def make_section(n_declared: int, n_found: int) -> list[str]:
    body = [p(run(f"PHẦN III. Câu trắc nghiệm trả lời ngắn. Thí sinh trả lời từ câu 1 đến câu {n_declared}."))]
    body += [p(run(f"Câu {i}. Tính.")) for i in range(1, n_found + 1)]
    return body


def test_count_matches_declared_has_no_section_flag():
    doc = read(*make_section(3, 3))
    assert doc.sections[0].flags == []
    assert "section_problems" not in [f.code for f in doc.flags]


def test_missing_questions_are_reported_with_numbers():
    doc = read(*make_section(6, 4))
    flag = next(f for f in doc.sections[0].flags if f.code == "count_mismatch")
    assert "Thiếu: 5, 6" in flag.message
    assert any(f.code == "section_problems" for f in doc.flags)


def test_extra_questions_beyond_declared_are_reported():
    doc = read(*make_section(2, 3))
    flag = next(f for f in doc.sections[0].flags if f.code == "count_mismatch")
    assert "Ngoài khoảng" in flag.message


def test_duplicate_question_number_is_flagged():
    doc = read(p(run("Câu 1. a")), p(run("Câu 2. b")), p(run("Câu 1. c")))
    flagged = [q.number for q in doc.questions if any(f.code == "duplicate_number" for f in q.flags)]
    assert flagged == [1]


def test_numbering_gap_is_info():
    doc = read(p(run("Câu 1. a")), p(run("Câu 3. b")))
    gap = next(f for f in doc.questions[1].flags if f.code == "number_gap")
    assert gap.severity == "info"


def test_document_without_questions_is_flagged():
    doc = read(p(run("Chỉ có một dòng chữ bất kỳ.")))
    assert any(f.code == "no_questions" and f.severity == "error" for f in doc.flags)


# ----- nội dung đặc biệt -----
def test_table_inside_question_is_flagged_not_ignored_silently():
    doc = read(p(run("Câu 1. Cho bảng sau.")), table(), opts(a="H"))
    q = only_question(doc)
    assert any(f.code == "table_skipped" and f.severity == "error" for f in q.flags)


def test_wmf_formula_needs_conversion_and_png_does_not():
    doc = read(p(run("Câu 1. Tính "), eq(rid="rId1"), run(" và "), eq(rid="rId2")), opts(a="H"))
    q = only_question(doc)
    formulas = [b for b in q.stem if b.kind == "formula"]
    assert [b.ref for b in formulas] == ["word/media/image1.wmf", "word/media/image2.png"]
    assert [b.needs_conversion for b in formulas] == [True, False]
    assert any(f.code == "formula_needs_conversion" for f in doc.flags)
    assert "word/media/image1.wmf" in doc.assets


def test_formula_in_option_keeps_mark_and_block():
    row = p(tab(), run("A. "), eq(), tab(), run("B. "), eq("H"), tab(), run("C. "), run("ba"), tab(), run("D. "), run("bốn"))
    q = only_question(read(p(run("Câu 1. x")), row))
    assert q.answer.value == "B"
    assert [b.kind for b in q.options["B"]] == ["formula"]


def test_tracked_deletion_is_ignored_and_insertion_is_kept():
    body = p(run("Câu 1. Giữ "), '<w:del><w:r><w:delText>XÓA</w:delText></w:r></w:del>', "<w:ins>" + run("THÊM") + "</w:ins>")
    q = only_question(read(body))
    assert "XÓA" not in plain(q.stem)
    assert "THÊM" in plain(q.stem)


def test_question_label_variants():
    doc = read(p(run("Câu 1: a")), p(run("Câu 2) b")), p(run("Cau 3. c")))
    assert [q.number for q in doc.questions] == [1, 2, 3]


# ----- an toàn tệp -----
def test_doctype_in_document_is_rejected():
    xml = f'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><w:document {NS}><w:body/></w:document>'
    with pytest.raises(UnsafeFileError):
        read_docx(make_docx(document_xml=xml))


def test_not_a_zip_is_rejected():
    with pytest.raises(UnsafeFileError):
        read_docx(b"PK\x03\x04 broken")


def test_zip_bomb_by_compression_ratio_is_rejected():
    big = f'<?xml version="1.0"?><w:document {NS}><w:body>{"<w:p/>" * 4_000_000}</w:body></w:document>'
    with pytest.raises(UnsafeFileError):
        read_docx(make_docx(document_xml=big))


def test_missing_main_part_is_rejected():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("hello.txt", "x")
    with pytest.raises(UnsafeFileError):
        read_docx(buf.getvalue())


# ----- nhận dạng định dạng theo nội dung -----
def test_format_is_detected_by_content_not_name():
    data = make_docx(p(run("Câu 1. x")), opts(a="H"))
    assert read_exam(data, "doi-duoi.pdf").format == "docx"


def test_legacy_doc_and_unknown_are_reported_as_unsupported():
    with pytest.raises(UnsupportedFormatError):
        read_exam(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\0" * 100)
    with pytest.raises(UnsupportedFormatError):
        read_exam(b"MZ\x90\x00 executable")


def test_xlsx_is_reported_as_unsupported_for_now():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/workbook.xml", "<workbook/>")
    with pytest.raises(UnsupportedFormatError):
        read_exam(buf.getvalue())


# ----- PDF -----
def make_pdf(pages: list[list[str]]) -> bytes:
    """PDF tối thiểu, mỗi dòng ở một chỗ riêng cách nhau 30 điểm (chữ Helvetica, chỉ dùng ASCII/Latin-1)."""
    objects: list[bytes] = []

    def add(body: bytes) -> int:
        objects.append(body)
        return len(objects)

    catalog = add(b"")
    pages_obj = add(b"")
    font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    page_ids = []
    for lines in pages:
        ops = ["BT", "/F1 12 Tf"]
        y = 780
        for line in lines:
            safe = line.encode("cp1252").replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
            ops.append(f"1 0 0 1 72 {y} Tm".encode())
            ops.append(b"(" + safe + b") Tj")
            y -= 30
        ops.append("ET")
        stream = b"\n".join(o if isinstance(o, bytes) else o.encode() for o in ops)
        content = add(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_ids.append(add(f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 595 842] /Contents {content} 0 R /Resources << /Font << /F1 {font} 0 R >> >> >>".encode()))
    objects[catalog - 1] = f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode()
    kids = " ".join(f"{i} 0 R" for i in page_ids)
    objects[pages_obj - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return bytes(out)


def test_pdf_locates_questions_pages_and_positions():
    pdf = make_pdf([
        ["PHAN I. Trac nghiem", "Cau 1. Mot cau hoi", "Cau 2. Cau tiep theo"],
        ["Cau 3. Sang trang hai"],
    ])
    doc = read_exam(pdf, "de.pdf")
    assert doc.format == "pdf"
    assert doc.page_count == 2
    assert [(q.number, q.page) for q in doc.questions] == [(1, 1), (2, 1), (3, 2)]
    assert all(q.top is not None for q in doc.questions)
    assert doc.questions[0].top < doc.questions[1].top
    # PDF chưa đọc đáp án: phải là missing, không được đoán
    assert all(q.answer.status == "missing" for q in doc.questions)


def test_pdf_section_header_does_not_swallow_the_next_question():
    doc = read_exam(make_pdf([["PHAN II. Cau hoi", "Cau 1. Noi dung", "Cau 2. Noi dung"]]), "de.pdf")
    assert [q.number for q in doc.questions] == [1, 2]


def test_pdf_question_label_split_over_two_lines_is_joined():
    doc = read_exam(make_pdf([["Cau 1. Mot", "Cau", "2. Nhan bi ngat dong", "Cau 3. Cuoi"]]), "de.pdf")
    assert [q.number for q in doc.questions] == [1, 2, 3]


def test_pdf_without_text_is_flagged_as_scan():
    doc = read_exam(make_pdf([[""], [""]]), "quet.pdf")
    assert any(f.code == "no_text_layer" and f.severity == "error" for f in doc.flags)
    assert doc.questions == []


def test_pdf_numbering_problems_are_flagged():
    doc = read_exam(make_pdf([["Cau 1. a", "Cau 3. b", "Cau 3. c"]]), "de.pdf")
    codes = {f.code for q in doc.questions for f in q.flags}
    assert "duplicate_number" in codes


def test_pdf_truncated_file_is_rejected():
    with pytest.raises(UnsafeFileError):
        read_exam(b"%PDF-1.4\n1 0 obj << /Type /Catalog >> endobj\n")


def test_render_page_returns_png():
    from app.modules.exams.imports.readers.pdf_reader import render_page

    png = render_page(make_pdf([["Cau 1. Mot"]]), 0, scale=1.0)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    with pytest.raises(IndexError):
        render_page(make_pdf([["Cau 1. Mot"]]), 5)
