"""Lấy LaTeX chính xác từ đối tượng MathType nhúng trong DOCX.

Không có LaTeX thì phải là "không có": không bao giờ suy đoán công thức.
"""

from __future__ import annotations

import io
import zipfile

import pytest
from test_exam_readers import NS, RELS, eq, opts, p, run  # noqa: F401  (trợ giúp dựng tệp Word thử)

from app.modules.exams.imports.readers import docx_reader
from app.modules.exams.imports.readers.docx_reader import read_docx
from app.modules.exams.imports.readers.mathtype import (
    MAX_OBJECT_BYTES,
    Formula,
    tex_from_equation_stream,
    tex_from_ole,
)

HEADER = bytes(28)  # tiêu đề 28 byte của luồng "Equation Native"


def stream(tex: bytes | None, extra: bytes = b"") -> bytes:
    body = b"\x05\x01\x00\x06\x09DSMT6\x00\x01f\x1bTeX Input Language\x00" + tex + b"\x00" if tex is not None else b"\x05\x01\x00"
    return HEADER + body + extra


# ----- giải LaTeX từ luồng -----
def test_extracts_tex_and_strips_the_outer_braces_mathtype_adds():
    assert tex_from_equation_stream(stream(b"{A,B,C}")) == "A,B,C"
    assert tex_from_equation_stream(stream(rb"{\overrightarrow{AB}=\overrightarrow{CA}+\overrightarrow{BC}}")) == (
        r"\overrightarrow{AB}=\overrightarrow{CA}+\overrightarrow{BC}"
    )


def test_keeps_braces_that_do_not_wrap_the_whole_formula():
    assert tex_from_equation_stream(stream(rb"{a}+{b}")) == "{a}+{b}"
    assert tex_from_equation_stream(stream(rb"\frac{1}{2}")) == r"\frac{1}{2}"


def test_formula_without_tex_annotation_is_none_not_a_guess():
    assert tex_from_equation_stream(stream(None)) is None


@pytest.mark.parametrize(
    "data",
    [
        b"",
        HEADER,
        HEADER + b"TeX Input Language\x00",  # có nhãn nhưng không có nội dung
        HEADER + b"TeX Input Language\x00{x^2}",  # thiếu byte kết thúc
        HEADER + b"TeX Input Language\x00\xff\xfe\x00",  # không phải UTF-8
        b"TeX Input Language\x00{x}\x00",  # nằm trong 28 byte tiêu đề: không phải dữ liệu thật
    ],
)
def test_malformed_streams_return_none(data):
    assert tex_from_equation_stream(data) is None


def test_non_ascii_tex_is_decoded():
    assert tex_from_equation_stream(stream("{α+β}".encode("utf-8"))) == "α+β"


# ----- tệp OLE không tin cậy -----
@pytest.mark.parametrize(
    "data",
    [b"", b"not ole", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 200, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\xff" * 512],
)
def test_corrupt_ole_returns_none_without_raising(data):
    assert tex_from_ole(data) is None


def test_oversized_object_is_refused():
    assert tex_from_ole(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * MAX_OBJECT_BYTES) is None


# ----- nối vào bộ đọc DOCX -----
def docx_with_formula(embedding: bytes | None, ole_attrs: str = 'r:id="rId5"') -> bytes:
    formula = (
        '<w:r><w:object><v:shape><v:imagedata r:id="rId1"/></v:shape>'
        f'<o:OLEObject ProgID="Equation.DSMT4" {ole_attrs}/></w:object></w:r>'
    )
    body = p(run("Câu 1. Tính "), formula) + opts(b="H")
    document = f'<?xml version="1.0"?><w:document {NS}><w:body>{body}</w:body></w:document>'
    rels = RELS.replace("</Relationships>", '<Relationship Id="rId5" Type="x" Target="embeddings/oleObject1.bin"/></Relationships>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", document)
        zf.writestr("word/_rels/document.xml.rels", rels)
        if embedding is not None:
            zf.writestr("word/embeddings/oleObject1.bin", embedding)
    return buf.getvalue()


def stem_formulas(doc):
    return [b for b in doc.questions[0].stem if b.kind == "formula"]


def test_latex_from_the_embedded_object_is_attached_to_the_formula_block(monkeypatch):
    seen = []
    monkeypatch.setattr(
        docx_reader, "formula_from_ole", lambda data: (seen.append(data), Formula(r"\frac{1}{2}", "mathtype_tex"))[1]
    )
    doc = read_docx(docx_with_formula(b"du-lieu-nhung"))
    (formula,) = stem_formulas(doc)
    assert formula.latex == r"\frac{1}{2}"
    assert formula.latex_source == "mathtype_tex" and formula.latex_unverified == []
    assert formula.ref == "word/media/image1.wmf"  # ảnh vẫn còn để dự phòng
    assert seen == [b"du-lieu-nhung"]
    assert not any(f.code == "formulas_without_latex" for f in doc.flags)


def test_formula_without_latex_keeps_the_image_and_is_flagged():
    doc = read_docx(docx_with_formula(b"khong phai ole"))
    (formula,) = stem_formulas(doc)
    assert formula.latex == ""
    assert formula.needs_conversion is True
    flag = next(f for f in doc.flags if f.code == "formulas_without_latex")
    assert "1/1" in flag.message and flag.severity == "info"


def test_missing_embedding_part_is_not_an_error():
    doc = read_docx(docx_with_formula(None))
    assert stem_formulas(doc)[0].latex == ""


def test_ole_object_without_relationship_id_is_not_an_error():
    doc = read_docx(docx_with_formula(b"x", ole_attrs=""))
    assert stem_formulas(doc)[0].latex == ""


def test_same_embedding_is_parsed_once(monkeypatch):
    calls = []
    monkeypatch.setattr(docx_reader, "formula_from_ole", lambda data: (calls.append(1), Formula("x", "mathtype_tex"))[1])
    formula = (
        '<w:r><w:object><v:shape><v:imagedata r:id="rId1"/></v:shape>'
        '<o:OLEObject ProgID="Equation.DSMT4" r:id="rId5"/></w:object></w:r>'
    )
    body = p(run("Câu 1. "), formula, formula, formula)
    document = f'<?xml version="1.0"?><w:document {NS}><w:body>{body}</w:body></w:document>'
    rels = RELS.replace("</Relationships>", '<Relationship Id="rId5" Type="x" Target="embeddings/oleObject1.bin"/></Relationships>')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", document)
        zf.writestr("word/_rels/document.xml.rels", rels)
        zf.writestr("word/embeddings/oleObject1.bin", b"x")
    doc = read_docx(buf.getvalue())
    assert [b.latex for b in stem_formulas(doc)] == ["x", "x", "x"]
    assert len(calls) == 1
