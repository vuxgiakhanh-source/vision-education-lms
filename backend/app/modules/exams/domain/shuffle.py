"""Tráo câu và phương án, cố định theo hạt giống của từng lượt thi.

Ba nguyên tắc:
1. Thứ tự là hàm của (hạt giống, mã). Cùng hạt giống thì luôn ra cùng thứ tự, nên em F5 hay đổi máy
   vẫn thấy đúng bản của mình. Dùng băm SHA-256 thay vì `random.shuffle` để kết quả không phụ thuộc phiên
   bản Python.
2. Đáp án gắn với MÃ phương án gốc, không gắn với chữ A–D hiển thị. Tráo không bao giờ làm đổi đáp án đúng.
3. Câu không an toàn để tráo thì giữ nguyên chỗ: phương án kiểu "cả A và B đều đúng", câu dùng chung dữ
   kiện, hoặc cô đánh dấu cố định. Chỉ tráo trong từng phần, không trộn trắc nghiệm với đúng/sai.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

DISPLAY_LABELS = "ABCD"

# Phương án nhắc tới phương án khác: không được tráo.
_REFERS_TO_OTHER_OPTION = re.compile(
    r"(?:\b(?:cả|tất\s*cả|các)\s+(?:ba|bốn|hai|\d)\b"
    r"|\btất\s*cả\s+các\s+(?:phương\s+án|đáp\s+án|ý)\b"
    r"|\bcác\s+(?:phương\s+án|đáp\s+án)\s+(?:trên|còn\s+lại|đều)\b"
    r"|\b(?:cả|và|hoặc)\s+[A-D]\b"
    r"|\b[A-D]\s+(?:và|hoặc)\s+[A-D]\b"
    r"|\bđều\s+(?:đúng|sai)\b"
    r"|\bkhông\s+có\s+(?:phương\s+án|đáp\s+án)\b"
    r"|\bphương\s+án\s+[A-D]\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ShuffleItem:
    id: str
    option_ids: tuple[str, ...] = ()
    # Cô hoặc bộ đọc đánh dấu không tráo vị trí câu này (câu chùm, tham chiếu câu trước...).
    pin_position: bool = False
    # Không tráo thứ tự phương án của câu này.
    pin_options: bool = False


@dataclass
class SectionOrder:
    question_ids: list[str]
    option_ids: dict[str, list[str]] = field(default_factory=dict)


def options_are_shufflable(option_texts: Sequence[str]) -> bool:
    """False nếu có phương án nhắc tới phương án khác ("cả A và B đều đúng")."""
    return not any(_REFERS_TO_OTHER_OPTION.search(text or "") for text in option_texts)


def _rank(seed: int, scope: str, item_id: str) -> str:
    return hashlib.sha256(f"{seed}|{scope}|{item_id}".encode()).hexdigest()


def _permute(seed: int, scope: str, ids: Sequence[str]) -> list[str]:
    return sorted(ids, key=lambda i: (_rank(seed, scope, i), i))


def order_section(seed: int, section_id: str, items: Sequence[ShuffleItem]) -> SectionOrder:
    """Thứ tự câu và phương án của một phần. Câu `pin_position` giữ nguyên chỗ, các câu còn lại tráo vào
    những chỗ trống."""
    ids = [item.id for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError("Mã câu bị trùng trong cùng một phần.")

    free_ids = [item.id for item in items if not item.pin_position]
    shuffled_free = iter(_permute(seed, f"q:{section_id}", free_ids))
    question_ids = [item.id if item.pin_position else next(shuffled_free) for item in items]

    by_id: Mapping[str, ShuffleItem] = {item.id: item for item in items}
    option_ids: dict[str, list[str]] = {}
    for qid in question_ids:
        item = by_id[qid]
        if item.option_ids:
            option_ids[qid] = (
                list(item.option_ids)
                if item.pin_options
                else _permute(seed, f"o:{section_id}:{qid}", item.option_ids)
            )
    return SectionOrder(question_ids=question_ids, option_ids=option_ids)


def display_labels(ordered_option_ids: Sequence[str]) -> dict[str, str]:
    """Chữ A–D hiển thị cho từng mã phương án theo thứ tự đã tráo: {"C": "A", "A": "B", ...}."""
    return {option_id: DISPLAY_LABELS[i] for i, option_id in enumerate(ordered_option_ids)}
