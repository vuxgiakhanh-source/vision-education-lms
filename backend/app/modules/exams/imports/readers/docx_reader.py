"""Đọc đề Word (.docx) thành ParsedDocument.

Chỉ dùng thư viện chuẩn. Chữ chỉ để định vị câu, phương án và dấu đáp án; công thức MathType và hình
được giữ dưới dạng Block tham chiếu tệp ảnh, không dịch ra chữ.

Quy tắc an toàn: mọi điều không chắc thành Flag, đáp án không có bằng chứng thì là "missing".
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass

from .model import (
    Answer,
    Block,
    ParsedDocument,
    Question,
    QuestionKind,
    Section,
    plain,
)
from .mathtype import MAX_OBJECT_BYTES, Formula, formula_from_ole
from .safety import open_docx_parts
from .validators import validate

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
V = "{urn:schemas-microsoft-com:vml}"
O = "{urn:schemas-microsoft-com:office:office}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

FORMULA_CH = ""
IMAGE_CH = ""

BROWSER_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp", "svg"}

RE_SECTION = re.compile(r"^\s*PH[ẦA]N\s+([IVX]+|\d+)\b", re.IGNORECASE)
RE_DECLARED = re.compile(r"từ\s+câu\s*(\d+)\s*(?:đến|tới|-)\s*(?:câu\s*)?(\d+)", re.IGNORECASE)
RE_QUESTION = re.compile(r"^\s*C[âa]u\s*(\d+)\s*[.:)]", re.IGNORECASE)
RE_SOLUTION = re.compile(r"^\s*L[ờo]i\s*gi[ảa]i\b[\s:.\-]*", re.IGNORECASE)
RE_CHOSEN = re.compile(r"(?:Chọn|Đáp án)\s*[:.]?\s*([A-D])\b")
RE_SHORT_ANSWER = re.compile(r"^\s*(?:Đáp\s*số|ĐS|Đáp\s*án|Kết\s*quả)\s*[:.]\s*(.+)$", re.IGNORECASE)

OPTION_LABELS = "ABCD"
STATEMENT_LABELS = "abcd"


@dataclass
class _Cell:
    """Một ký tự của đoạn kèm cờ đánh dấu và (nếu là công thức hoặc hình) Block của nó."""

    ch: str
    marked: bool = False
    block: Block | None = None


class _Context:
    def __init__(self, rels: dict[str, str], zf: "zipfile.ZipFile | None" = None) -> None:
        self.rels = rels
        self.zf = zf
        self.assets: list[str] = []
        self._latex_cache: dict[str, Formula | None] = {}

    def formula_for(self, rid: str | None) -> Formula | None:
        """Công thức từ đối tượng nhúng (r:id của o:OLEObject): LaTeX MathType ghi sẵn, nếu không thì giải mã MTEF."""
        target = self.rels.get(rid or "", "")
        if not target or self.zf is None or not target.startswith("word/embeddings/"):
            return None
        if target not in self._latex_cache:
            formula = None
            try:
                info = self.zf.getinfo(target)
                if info.file_size <= MAX_OBJECT_BYTES:
                    formula = formula_from_ole(self.zf.read(target))
            except KeyError:
                pass
            self._latex_cache[target] = formula
        return self._latex_cache[target]

    def image_block(self, kind: str, rid: str | None) -> Block:
        target = self.rels.get(rid or "", "")
        ext = target.rsplit(".", 1)[-1].lower() if "." in target else ""
        return Block(
            kind=kind,  # type: ignore[arg-type]
            ref=target,
            needs_conversion=bool(target) and ext not in BROWSER_IMAGE_EXT,
        )


def _load_rels(rels_xml: bytes) -> dict[str, str]:
    if not rels_xml:
        return {}
    out: dict[str, str] = {}
    for rel in ET.fromstring(rels_xml).iter(REL + "Relationship"):
        target = rel.get("Target", "")
        if rel.get("TargetMode") == "External":
            continue
        out[rel.get("Id", "")] = target.lstrip("/") if target.startswith("/") else f"word/{target}"
    return out


def _run_marked(run: ET.Element) -> bool:
    rpr = run.find(W + "rPr")
    if rpr is None:
        return False
    hl = rpr.find(W + "highlight")
    if hl is not None and hl.get(W + "val") != "none":
        return True
    u = rpr.find(W + "u")
    return u is not None and u.get(W + "val") != "none"


def _object_block(obj: ET.Element, ctx: _Context) -> Block:
    rid = None
    for img in obj.iter(V + "imagedata"):
        rid = img.get(R + "id")
        break
    ole = obj.find(O + "OLEObject")
    prog = (ole.get("ProgID", "") if ole is not None else "").lower()
    is_formula = "equation" in prog or "mathtype" in prog or "dsmt" in prog
    block = ctx.image_block("formula" if is_formula else "image", rid)
    if is_formula and ole is not None:
        formula = ctx.formula_for(ole.get(R + "id"))
        if formula is not None:
            block.latex, block.latex_source = formula.latex, formula.source
            block.latex_unverified = list(formula.unverified)
    return block


def _walk(parent: ET.Element, cells: list[_Cell], ctx: _Context) -> None:
    for el in parent:
        tag = el.tag
        if tag == W + "r":
            marked = _run_marked(el)
            for child in el:
                ctag = child.tag
                if ctag == W + "t":
                    for ch in child.text or "":
                        cells.append(_Cell(ch, marked))
                elif ctag == W + "tab":
                    cells.append(_Cell("\t", False))
                elif ctag in (W + "br", W + "cr"):
                    cells.append(_Cell("\n", False))
                elif ctag == W + "object":
                    cells.append(_Cell(FORMULA_CH, marked, _object_block(child, ctx)))
                elif ctag == W + "pict":
                    rid = next((i.get(R + "id") for i in child.iter(V + "imagedata")), None)
                    cells.append(_Cell(IMAGE_CH, marked, ctx.image_block("image", rid)))
                elif ctag == W + "drawing":
                    rid = next((b.get(R + "embed") for b in child.iter(A + "blip")), None)
                    cells.append(_Cell(IMAGE_CH, marked, ctx.image_block("image", rid)))
        elif tag in (M + "oMath", M + "oMathPara"):
            cells.append(_Cell(FORMULA_CH, False, Block(kind="formula")))
        elif tag in (W + "hyperlink", W + "ins", W + "smartTag", W + "sdt", W + "sdtContent", W + "fldSimple"):
            _walk(el, cells, ctx)
        # w:del (chữ đã bị xóa khi theo dõi thay đổi) và các thẻ còn lại được bỏ qua


def _text(cells: list[_Cell]) -> str:
    return "".join(c.ch for c in cells)


def _blocks(cells: list[_Cell], start: int, end: int | None = None) -> list[Block]:
    out: list[Block] = []
    buf: list[str] = []
    for c in cells[start:end]:
        if c.block is None:
            buf.append(" " if c.ch in "\t\n" else c.ch)
        else:
            if buf:
                out.append(Block("text", "".join(buf)))
                buf = []
            out.append(c.block)
    if buf:
        out.append(Block("text", "".join(buf)))
    return [b for b in out if not (b.kind == "text" and not b.text.strip())]


def _is_marked(cells: list[_Cell], start: int, end: int) -> bool:
    return any(c.marked and not c.ch.isspace() for c in cells[start:end])


def _labelled_segments(text: str, expected: str, labels: str, closer: str):
    """Tách một dòng phương án/ý thành [(nhãn, bắt đầu nhãn, bắt đầu nội dung, kết thúc)].

    Dòng phải bắt đầu đúng nhãn kế tiếp mong đợi (đã bỏ khoảng trắng đầu). Các nhãn sau phải theo thứ tự
    và đứng sau khoảng trắng hoặc công thức. Nhờ vậy câu như "cho điểm C. Có bao nhiêu..." không bị nhầm.
    Trả None nếu dòng không phải dòng phương án.
    """
    lead = len(text) - len(text.lstrip())
    m = re.compile(rf"{re.escape(expected)}\s*{closer}").match(text, lead)
    if not m:
        return None
    starts = [(expected, lead, m.end())]
    idx = labels.index(expected)
    pos = m.end()
    for nxt in labels[idx + 1 :]:
        found = re.compile(rf"(?<=[\s{FORMULA_CH}{IMAGE_CH}]){re.escape(nxt)}\s*{closer}").search(text, pos)
        if not found:
            break
        starts.append((nxt, found.start(), found.end()))
        pos = found.end()
    segments = []
    for i, (label, start, content_start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        segments.append((label, start, content_start, end))
    return segments


def _section_kind(title: str) -> QuestionKind:
    low = title.lower()
    if "đúng sai" in low or "đúng/sai" in low or "đúng - sai" in low:
        return "true_false"
    if "trả lời ngắn" in low:
        return "short_answer"
    if "nhiều phương án" in low or "trắc nghiệm" in low:
        return "multiple_choice"
    return "unknown"


class _Builder:
    def __init__(self, doc: ParsedDocument) -> None:
        self.doc = doc
        self.section: Section | None = None
        self.q: Question | None = None
        self.mode = "stem"
        self.tables_skipped = 0

    # ----- cấu trúc -----
    def _implicit_section(self) -> Section:
        if self.section is None:
            self.section = Section(title="(không có tiêu đề phần)")
            self.doc.sections.append(self.section)
        return self.section

    def start_section(self, title: str) -> None:
        self.finish_question()
        declared = RE_DECLARED.search(title)
        self.section = Section(
            title=" ".join(title.split()),
            kind=_section_kind(title),
            declared_first=int(declared.group(1)) if declared else None,
            declared_last=int(declared.group(2)) if declared else None,
        )
        self.doc.sections.append(self.section)
        self.q = None

    def start_question(self, number: int, stem: list[Block]) -> None:
        self.finish_question()
        section = self._implicit_section()
        self.q = Question(number=number, kind=section.kind, stem=stem)
        section.questions.append(self.q)
        self.mode = "stem"

    # ----- nội dung -----
    def add_options(self, segments, cells: list[_Cell], kind: QuestionKind) -> None:
        q = self.q
        assert q is not None
        for label, start, content_start, end in segments:
            if label in q.options:
                q.add_flag("options_restart", f"Phương án {label} xuất hiện hai lần; có thể lẫn với lời giải.")
                continue
            q.options[label] = _blocks(cells, content_start, end)
            if _is_marked(cells, start, end):
                q.marked.append(label)
        if q.kind == "unknown":
            q.kind = kind
        self.mode = "stem"

    def _try_labelled(self, q: Question, text: str, cells: list[_Cell]) -> bool:
        """Nhận dòng phương án A–D hoặc ý a)–d) của câu hiện tại. True nếu đã xử lý dòng."""
        if q.kind == "short_answer":
            return False
        if q.kind == "multiple_choice":
            families = [(OPTION_LABELS, r"[.)]", "multiple_choice")]
        elif q.kind == "true_false":
            families = [(STATEMENT_LABELS, r"\)", "true_false")]
        else:
            families = [(OPTION_LABELS, r"[.)]", "multiple_choice"), (STATEMENT_LABELS, r"\)", "true_false")]
        have = list(q.options)
        for labels, closer, kind in families:
            if have and have[0] not in labels:
                continue
            n = len(have)
            if n < 4:
                segments = _labelled_segments(text, labels[n], labels, closer)
                if segments:
                    self.add_options(segments, cells, kind)  # type: ignore[arg-type]
                    return True
            if have and _labelled_segments(text, labels[0], labels, closer):
                q.add_flag("options_restart", "Có nhóm phương án thứ hai trong cùng câu; có thể lẫn với lời giải.")
                return True
        return False

    def handle_paragraph(self, cells: list[_Cell]) -> None:
        text = _text(cells)
        stripped = text.strip()
        if not stripped:
            return

        m = RE_SECTION.match(stripped)
        if m:
            self.start_section(stripped)
            return

        m = RE_QUESTION.match(text)
        if m:
            self.start_question(int(m.group(1)), _blocks(cells, m.end()))
            return

        q = self.q
        if q is None:
            return  # phần đầu đề (tên trường, mã đề, dặn dò)

        sol = RE_SOLUTION.match(text)
        if sol:
            self.mode = "solution"
            rest = text[sol.end() :]
            self._add_solution(rest)
            return

        # Dòng phương án luôn thuộc câu hiện tại, kể cả khi đang trong khối Lời giải
        if self._try_labelled(q, text, cells):
            return

        short = RE_SHORT_ANSWER.match(text)
        if short:
            if q.kind == "unknown":
                q.kind = "short_answer"
            q.answer = Answer("suggested", short.group(1).strip(), ["text"], "")
            return

        if self.mode == "solution":
            self._add_solution(text)
            return

        if q.options:
            q.add_flag("text_after_options", "Có nội dung nằm sau các phương án; đã gộp vào phần đề.", "info")
        q.stem.extend(_blocks(cells, 0))

    def _add_solution(self, text: str) -> None:
        q = self.q
        assert q is not None
        chunk = " ".join(text.replace(FORMULA_CH, "⟦công thức⟧").replace(IMAGE_CH, "⟦hình⟧").split())
        if chunk:
            q.solution_text = (q.solution_text + " " + chunk).strip()
        chosen = RE_CHOSEN.search(text)
        if chosen:
            if q.solution_choice and q.solution_choice != chosen.group(1):
                q.add_flag("solution_choice_twice", "Lời giải ghi hai đáp án khác nhau.")
            q.solution_choice = chosen.group(1)

    def note_table(self) -> None:
        self.tables_skipped += 1
        if self.q is not None:
            self.q.add_flag("table_skipped", "Có bảng trong câu này mà bộ đọc chưa đọc (phương án hoặc dữ kiện có thể nằm trong bảng).")

    # ----- chốt câu -----
    def finish_question(self) -> None:
        q = self.q
        if q is None:
            return
        self._finish_kind(q)
        self._decide_answer(q)
        for block in q.stem + [b for blocks in q.options.values() for b in blocks]:
            if block.ref and block.ref not in self.doc.assets:
                self.doc.assets.append(block.ref)
        if any(b.latex_unverified for b in q.stem + [b for blocks in q.options.values() for b in blocks]):
            q.add_flag(
                "formula_unverified",
                "Có công thức giải mã từ dữ liệu nhị phân, chứa cấu trúc chưa được đối chiếu với công thức thật; so với ảnh trước khi phát đề.",
            )
        self.q = None

    def _finish_kind(self, q: Question) -> None:
        if q.kind == "multiple_choice":
            if not q.options:
                q.add_flag("options_missing", "Phần trắc nghiệm nhưng không đọc được phương án nào.")
            elif len(q.options) < 4:
                q.add_flag("options_incomplete", f"Chỉ đọc được {len(q.options)} phương án ({''.join(q.options)}).")
        elif q.kind == "true_false":
            if len(q.options) < 4:
                # Tiêu đề phần ghi rõ "đúng sai" thì phải đủ 4 ý; loại chỉ suy ra thì có thể là câu ít ý hợp lệ.
                explicit = self.section is not None and self.section.kind == "true_false"
                q.add_flag(
                    "statements_incomplete",
                    f"Chỉ đọc được {len(q.options)}/4 ý ({''.join(q.options) or 'không có'}).",
                    "error" if explicit else "info",
                )
        elif q.kind == "short_answer":
            if q.options:
                q.add_flag("kind_mismatch", "Phần trả lời ngắn nhưng câu có phương án.")
        else:
            q.add_flag("kind_unknown", "Không xác định được loại câu.")

    def _decide_answer(self, q: Question) -> None:
        if q.kind == "multiple_choice":
            marked = [m for m in q.marked if m in q.options]
            if len(marked) > 1:
                q.answer = Answer("conflict", None, ["highlight"], f"Nhiều phương án được đánh dấu: {', '.join(marked)}.")
                q.add_flag("multiple_marked", "Nhiều phương án cùng được đánh dấu.")
            elif len(marked) == 1:
                value = marked[0]
                if q.solution_choice and q.solution_choice != value:
                    q.answer = Answer(
                        "conflict", value, ["highlight", "solution"],
                        f"Phương án được đánh dấu là {value} nhưng lời giải ghi Chọn {q.solution_choice}.",
                    )
                    q.add_flag("answer_sources_disagree", q.answer.note)
                elif q.solution_choice:
                    q.answer = Answer("suggested", value, ["highlight", "solution"], "Hai nguồn khớp.")
                else:
                    q.answer = Answer("suggested", value, ["highlight"], "Một nguồn (dấu đánh dấu).")
            elif q.solution_choice:
                q.answer = Answer("suggested", q.solution_choice, ["solution"], "Một nguồn (lời giải), không có dấu đánh dấu.")
            else:
                q.answer = Answer("missing", None, [], "Không thấy dấu đánh dấu hay lời giải.")
        elif q.kind == "true_false":
            if q.marked:
                values = {label: label in q.marked for label in q.options}
                q.answer = Answer("suggested", values, ["highlight"], "Quy ước: ý được đánh dấu là đúng, ý không đánh dấu là sai (chưa xác nhận với cô).")
                q.add_flag("convention_assumed", "Chưa xác nhận quy ước đánh dấu = đúng.", "info")
            else:
                q.answer = Answer("missing", None, [], "Không có ý nào được đánh dấu.")
        elif q.kind == "short_answer":
            if q.answer.status != "suggested":
                q.answer = Answer("missing", None, [], "Không có đáp số trong tệp.")
        # loại chưa rõ: giữ "missing" mặc định


def read_docx(data: bytes, source_name: str = "") -> ParsedDocument:
    document_xml, rels_xml, _names, zf = open_docx_parts(data)
    root = ET.fromstring(document_xml)
    body = root.find(W + "body")
    doc = ParsedDocument(source_name=source_name, format="docx")
    if body is None:
        doc.add_flag("empty_document", "Tệp Word không có nội dung.")
        return doc

    ctx = _Context(_load_rels(rels_xml), zf)
    builder = _Builder(doc)
    for el in body:
        if el.tag == W + "p":
            cells: list[_Cell] = []
            _walk(el, cells, ctx)
            builder.handle_paragraph(cells)
        elif el.tag == W + "tbl":
            builder.note_table()
    builder.finish_question()

    if not doc.questions:
        doc.add_flag("no_questions", "Không tìm thấy câu hỏi nào có dạng \"Câu n.\".")
    if builder.tables_skipped:
        doc.add_flag("tables_skipped", f"Có {builder.tables_skipped} bảng chưa được đọc (thường là tiêu đề hoặc bảng đáp án).", "info")
    if any(b.needs_conversion for q in doc.questions for blocks in [q.stem, *q.options.values()] for b in blocks):
        doc.add_flag("formula_needs_conversion", "Công thức/hình dạng WMF hoặc EMF cần đổi sang PNG trước khi hiển thị cho học sinh.", "info")
    formulas = [
        b for q in doc.questions for blocks in [q.stem, *q.options.values()] for b in blocks if b.kind == "formula"
    ]
    if formulas:
        with_latex = sum(1 for b in formulas if b.latex)
        if with_latex < len(formulas):
            doc.add_flag(
                "formulas_without_latex",
                f"{len(formulas) - with_latex}/{len(formulas)} công thức không mang LaTeX trong tệp; hiển thị bằng ảnh.",
                "info",
            )
    validate(doc)
    return doc
