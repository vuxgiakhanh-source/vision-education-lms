"""Khóa đáp án: kiểm tra đủ trước khi phát hành.

Định dạng khóa (JSON): {"<mã câu>": {"type": "multiple_choice" | "true_false" | "short_answer", "correct": ...}}
- multiple_choice: correct là mã phương án gốc ("A"). Mã phương án KHÔNG đổi khi tráo; chữ A–D hiển thị mới đổi.
- true_false: correct là {"a": true, "b": false, "c": ..., "d": ...}, phải đủ mọi ý của câu.
- short_answer: correct là chuỗi, hoặc danh sách chuỗi nếu chấp nhận nhiều cách viết.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def _is_complete(question: Mapping[str, Any], entry: Mapping[str, Any] | None) -> bool:
    if not entry or entry.get("type") != question["type"]:
        return False
    correct = entry.get("correct")
    kind = question["type"]
    if kind == "multiple_choice":
        return isinstance(correct, str) and correct in set(question.get("options") or [])
    if kind == "true_false":
        statements = list(question.get("statements") or [])
        return (
            isinstance(correct, dict)
            and bool(statements)
            and set(correct) == set(statements)
            and all(isinstance(v, bool) for v in correct.values())
        )
    if kind == "short_answer":
        values = correct if isinstance(correct, list) else [correct]
        return bool(values) and all(isinstance(v, str) and v.strip() for v in values)
    return False


def missing_questions(questions: Iterable[Mapping[str, Any]], key: Mapping[str, Any]) -> list[str]:
    """Mã các câu chưa có đáp án hợp lệ, theo thứ tự đề. Rỗng nghĩa là đủ, được phép phát hành."""
    return [q["id"] for q in questions if not _is_complete(q, key.get(q["id"]))]
