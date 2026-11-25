"""Chấm bài. Hàm thuần, dùng Decimal để điểm không lệch do số thực.

Thang mặc định theo đề THPT: trắc nghiệm 0,25 điểm/câu; đúng/sai chấm theo số ý đúng
(1 ý 0,1; 2 ý 0,25; 3 ý 0,5; 4 ý 1,0); trả lời ngắn 0,5 điểm/câu. Cô có thể thay thang trong `scoring`.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any

DEFAULT_SCORING: dict[str, Any] = {
    "multiple_choice": "0.25",
    "true_false": ["0", "0.1", "0.25", "0.5", "1"],
    "short_answer": "0.5",
}

_NUMBER = re.compile(r"^[+-]?\d+(?:[.,]\d+)?$")


@dataclass
class GradeResult:
    score: Decimal
    max_score: Decimal
    per_question: dict[str, Decimal] = field(default_factory=dict)


def _dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Thang điểm không hợp lệ: {value!r}") from exc


def normalize_short(value: str) -> str:
    """Chuẩn hóa đáp số: bỏ khoảng trắng thừa, dấu phẩy thập phân thành dấu chấm, bỏ số 0 thừa ở cuối."""
    text = unicodedata.normalize("NFC", value).strip()
    compact = text.replace(" ", "")
    if _NUMBER.match(compact):
        number = _dec(compact.replace(",", "."))
        normalized = format(number.normalize(), "f")
        return "0" if normalized in ("-0", "") else normalized
    return " ".join(text.casefold().split())


def _short_matches(given: Any, correct: Any) -> bool:
    if not isinstance(given, str) or not given.strip():
        return False
    accepted = correct if isinstance(correct, list) else [correct]
    return normalize_short(given) in {normalize_short(str(c)) for c in accepted}


def _true_false_points(given: Any, correct: Mapping[str, bool], table: list[Any]) -> Decimal:
    if not isinstance(given, dict):
        return Decimal(0)
    right = sum(1 for k, v in correct.items() if k in given and given[k] is v)
    return _dec(table[right])


def grade(key: Mapping[str, Any], scoring: Mapping[str, Any], answers: Mapping[str, Any]) -> GradeResult:
    """Chấm `answers` theo `key`. Câu không trả lời được 0 điểm; mã câu lạ trong `answers` bị bỏ qua."""
    mc_points = _dec(scoring["multiple_choice"])
    tf_table = list(scoring["true_false"])
    short_points = _dec(scoring["short_answer"])

    total = Decimal(0)
    maximum = Decimal(0)
    per_question: dict[str, Decimal] = {}
    for qid, entry in key.items():
        kind, correct = entry["type"], entry["correct"]
        given = answers.get(qid)
        if kind == "multiple_choice":
            maximum += mc_points
            earned = mc_points if isinstance(given, str) and given == correct else Decimal(0)
        elif kind == "true_false":
            maximum += _dec(tf_table[len(correct)])
            earned = _true_false_points(given, correct, tf_table)
        elif kind == "short_answer":
            maximum += short_points
            earned = short_points if _short_matches(given, correct) else Decimal(0)
        else:
            raise ValueError(f"Loại câu không hỗ trợ: {kind!r}")
        per_question[qid] = earned
        total += earned
    return GradeResult(score=total, max_score=maximum, per_question=per_question)
