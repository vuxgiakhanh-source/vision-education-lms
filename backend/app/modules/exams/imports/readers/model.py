"""Dạng trung gian (IR) mà mọi bộ đọc đề đều trả về.

Nguyên tắc: không có bằng chứng thì trạng thái là "missing", không bao giờ là một giá trị mặc định.
Mọi điều bộ đọc không chắc đều thành một Flag để cô duyệt, không được đoán lặng lẽ.

Module này thuần dữ liệu: không import DB, FastAPI hay service, để chạy được trong tiến trình con
có giới hạn tài nguyên và test không cần MySQL.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

QuestionKind = Literal["multiple_choice", "true_false", "short_answer", "unknown"]
AnswerStatus = Literal["suggested", "conflict", "missing"]
Severity = Literal["error", "info"]

FORMULA_PLACEHOLDER = "⟦công thức⟧"
IMAGE_PLACEHOLDER = "⟦hình⟧"


@dataclass
class Block:
    """Một mảnh nội dung hiển thị: chữ, công thức hoặc hình.

    `ref` là tên phần trong tệp nguồn (ví dụ word/media/image1.wmf). `needs_conversion` bật khi
    định dạng trình duyệt không hiển thị được (WMF, EMF) và phải đổi sang PNG trước khi phát cho học sinh.
    """

    kind: Literal["text", "formula", "image"]
    text: str = ""
    ref: str = ""
    needs_conversion: bool = False
    # LaTeX do chính MathType ghi trong tệp (chính xác, không phải đoán). Rỗng nghĩa là chỉ có ảnh.
    latex: str = ""
    latex_source: str = ""  # "mathtype_tex" (chính xác) hoặc "mtef_decoded" (giải mã nhị phân)
    latex_unverified: list[str] = field(default_factory=list)  # cấu trúc chưa có công thức thật để đối chiếu


@dataclass
class Flag:
    code: str
    message: str
    severity: Severity = "error"


@dataclass
class Answer:
    status: AnswerStatus = "missing"
    # trắc nghiệm: "B"; đúng/sai: {"a": True, ...}; trả lời ngắn: chuỗi
    value: str | dict[str, bool] | None = None
    sources: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class Question:
    number: int
    kind: QuestionKind = "unknown"
    stem: list[Block] = field(default_factory=list)
    options: dict[str, list[Block]] = field(default_factory=dict)
    marked: list[str] = field(default_factory=list)
    solution_text: str = ""
    solution_choice: str | None = None
    answer: Answer = field(default_factory=Answer)
    flags: list[Flag] = field(default_factory=list)
    # PDF: vị trí để cắt ảnh câu hỏi. DOCX: None.
    page: int | None = None
    top: float | None = None

    def add_flag(self, code: str, message: str, severity: Severity = "error") -> None:
        if not any(f.code == code for f in self.flags):
            self.flags.append(Flag(code, message, severity))

    @property
    def needs_review(self) -> bool:
        return (
            self.answer.status != "suggested"
            or any(f.severity == "error" for f in self.flags)
        )


@dataclass
class Section:
    title: str
    kind: QuestionKind = "unknown"
    declared_first: int | None = None
    declared_last: int | None = None
    questions: list[Question] = field(default_factory=list)
    flags: list[Flag] = field(default_factory=list)

    def add_flag(self, code: str, message: str, severity: Severity = "error") -> None:
        if not any(f.code == code for f in self.flags):
            self.flags.append(Flag(code, message, severity))


@dataclass
class ParsedDocument:
    source_name: str
    format: Literal["docx", "pdf"]
    sections: list[Section] = field(default_factory=list)
    flags: list[Flag] = field(default_factory=list)
    page_count: int | None = None
    # tên phần ảnh/công thức đã dùng trong tệp (docx) để worker đổi sang PNG
    assets: list[str] = field(default_factory=list)

    def add_flag(self, code: str, message: str, severity: Severity = "error") -> None:
        if not any(f.code == code for f in self.flags):
            self.flags.append(Flag(code, message, severity))

    @property
    def questions(self) -> list[Question]:
        return [q for s in self.sections for q in s.questions]

    def summary(self) -> dict:
        qs = self.questions
        by_status = {"suggested": 0, "conflict": 0, "missing": 0}
        for q in qs:
            by_status[q.answer.status] += 1
        return {
            "questions": len(qs),
            "answers": by_status,
            "needs_review": sum(1 for q in qs if q.needs_review),
            "document_flags": [f.code for f in self.flags if f.severity == "error"],
        }

    def to_dict(self) -> dict:
        return asdict(self)


def plain(blocks: list[Block]) -> str:
    """Chữ thường của một danh sách Block, công thức và hình thành ký hiệu giữ chỗ."""
    parts: list[str] = []
    for b in blocks:
        if b.kind == "text":
            parts.append(b.text)
        elif b.kind == "formula":
            parts.append(FORMULA_PLACEHOLDER)
        else:
            parts.append(IMAGE_PLACEHOLDER)
    return " ".join("".join(parts).split())
