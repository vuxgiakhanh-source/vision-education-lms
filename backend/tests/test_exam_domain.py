"""Test logic thuần của phòng thi: hạn nộp, biên nhận, đáp án, chấm điểm, tráo đề."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.exams.domain.answer_key import missing_questions
from app.modules.exams.domain.deadline import (
    can_enter,
    compute_deadline,
    grace_floor,
    is_within_grace,
)
from app.modules.exams.domain.grading import DEFAULT_SCORING, grade, normalize_short
from app.modules.exams.domain.receipt import (
    RECEIPT_ALPHABET,
    RECEIPT_LENGTH,
    content_digest,
    new_receipt_code,
)
from app.modules.exams.domain.shuffle import (
    ShuffleItem,
    display_labels,
    options_are_shufflable,
    order_section,
)


def at(hh: int, mm: int, ss: int = 0) -> datetime:
    return datetime(2026, 12, 1, hh, mm, ss)


# ----- hạn nộp -----
def test_on_time_entry_gets_full_duration():
    assert compute_deadline(at(8, 0), at(10, 0), 90) == at(9, 30)


def test_late_entry_is_cut_at_close_not_extended():
    # phòng 08:00-10:00, bài 90 phút, vào 08:45: hạn là 10:00, không phải 10:15
    assert compute_deadline(at(8, 45), at(10, 0), 90) == at(10, 0)


def test_can_enter_window_is_half_open():
    assert not can_enter(at(7, 59, 59), at(8, 0), at(10, 0))
    assert can_enter(at(8, 0), at(8, 0), at(10, 0))
    assert can_enter(at(9, 59, 59), at(8, 0), at(10, 0))
    assert not can_enter(at(10, 0), at(8, 0), at(10, 0))


def test_grace_accepts_up_to_deadline_plus_grace():
    deadline = at(9, 30)
    assert is_within_grace(at(9, 30, 30), deadline, 30)
    assert not is_within_grace(at(9, 30, 31), deadline, 30)


def test_grace_floor_matches_is_within_grace():
    deadline = at(9, 30)
    for now in (at(9, 30), at(9, 30, 30), at(9, 30, 31), at(9, 29)):
        assert (deadline >= grace_floor(now, 30)) == is_within_grace(now, deadline, 30)


# ----- biên nhận -----
def test_receipt_code_shape_and_alphabet():
    code = new_receipt_code()
    assert len(code) == RECEIPT_LENGTH
    assert set(code) <= set(RECEIPT_ALPHABET)
    assert not set("0O1ILU") & set(RECEIPT_ALPHABET)


def test_receipt_codes_do_not_repeat_in_practice():
    assert len({new_receipt_code() for _ in range(5000)}) == 5000


def test_digest_ignores_key_order_and_detects_change():
    a = {"q1": "A", "q2": {"a": True, "b": False}}
    b = {"q2": {"b": False, "a": True}, "q1": "A"}
    assert content_digest(a) == content_digest(b)
    assert content_digest(a) != content_digest({**a, "q1": "B"})
    assert len(content_digest(a)) == 64


def test_digest_keeps_vietnamese_text_stable():
    assert content_digest({"q": "căn bậc hai"}) == content_digest({"q": "căn bậc hai"})


# ----- khóa đáp án -----
QUESTIONS = [
    {"id": "q1", "type": "multiple_choice", "options": ["A", "B", "C", "D"]},
    {"id": "q2", "type": "true_false", "statements": ["a", "b", "c", "d"]},
    {"id": "q3", "type": "short_answer"},
]
GOOD_KEY = {
    "q1": {"type": "multiple_choice", "correct": "B"},
    "q2": {"type": "true_false", "correct": {"a": True, "b": False, "c": True, "d": False}},
    "q3": {"type": "short_answer", "correct": "3,5"},
}


def test_complete_key_has_nothing_missing():
    assert missing_questions(QUESTIONS, GOOD_KEY) == []


def test_missing_entry_is_reported_in_exam_order():
    key = {k: v for k, v in GOOD_KEY.items() if k != "q2"}
    assert missing_questions(QUESTIONS, key) == ["q2"]


@pytest.mark.parametrize(
    "q, entry",
    [
        ("q1", {"type": "multiple_choice", "correct": "E"}),  # không có phương án E
        ("q1", {"type": "multiple_choice", "correct": None}),
        ("q1", {"type": "true_false", "correct": "B"}),  # sai loại
        ("q2", {"type": "true_false", "correct": {"a": True}}),  # thiếu ý
        ("q2", {"type": "true_false", "correct": {"a": 1, "b": 0, "c": 1, "d": 0}}),  # không phải bool
        ("q3", {"type": "short_answer", "correct": "  "}),
        ("q3", {"type": "short_answer", "correct": []}),
    ],
)
def test_invalid_entries_count_as_missing(q, entry):
    assert missing_questions(QUESTIONS, {**GOOD_KEY, q: entry}) == [q]


def test_short_answer_accepts_list_of_spellings():
    key = {**GOOD_KEY, "q3": {"type": "short_answer", "correct": ["3,5", "7/2"]}}
    assert missing_questions(QUESTIONS, key) == []


# ----- chấm điểm -----
def test_all_correct_gets_max_score():
    answers = {"q1": "B", "q2": {"a": True, "b": False, "c": True, "d": False}, "q3": "3.5"}
    result = grade(GOOD_KEY, DEFAULT_SCORING, answers)
    assert result.score == result.max_score == Decimal("1.75")  # 0.25 + 1 + 0.5


def test_blank_and_wrong_get_zero_without_error():
    assert grade(GOOD_KEY, DEFAULT_SCORING, {}).score == 0
    wrong = grade(GOOD_KEY, DEFAULT_SCORING, {"q1": "A", "q3": "9"})
    assert wrong.score == 0


@pytest.mark.parametrize("right, points", [(0, "0"), (1, "0.1"), (2, "0.25"), (3, "0.5"), (4, "1")])
def test_true_false_scale_by_number_of_correct_statements(right, points):
    truth = ["a", "b", "c", "d"]
    given = {k: (GOOD_KEY["q2"]["correct"][k] if i < right else not GOOD_KEY["q2"]["correct"][k]) for i, k in enumerate(truth)}
    result = grade({"q2": GOOD_KEY["q2"]}, DEFAULT_SCORING, {"q2": given})
    assert result.score == Decimal(points)


def test_unanswered_statement_counts_as_wrong():
    result = grade({"q2": GOOD_KEY["q2"]}, DEFAULT_SCORING, {"q2": {"a": True, "b": False}})
    assert result.score == Decimal("0.25")  # 2 ý đúng


def test_unknown_question_ids_in_answers_are_ignored():
    result = grade(GOOD_KEY, DEFAULT_SCORING, {"zzz": "A", "q1": "B"})
    assert result.score == Decimal("0.25")


def test_score_is_exact_decimal():
    key = {f"q{i}": {"type": "multiple_choice", "correct": "A"} for i in range(40)}
    answers = {f"q{i}": "A" for i in range(40)}
    assert grade(key, DEFAULT_SCORING, answers).score == Decimal("10.00")


@pytest.mark.parametrize(
    "given, correct, ok",
    [
        ("3,5", "3.5", True),
        (" 3.50 ", "3,5", True),
        ("-0", "0", True),
        ("2", "2.0", True),
        ("7/2", "3.5", False),  # không tự tính phân số: cô liệt kê cách viết chấp nhận
        ("", "3.5", False),
        (None, "3.5", False),
        ("Căn  Hai", "căn hai", True),
    ],
)
def test_short_answer_normalization(given, correct, ok):
    key = {"q": {"type": "short_answer", "correct": correct}}
    result = grade(key, DEFAULT_SCORING, {"q": given})
    assert (result.score > 0) is ok


def test_normalize_short_examples():
    assert normalize_short("3,50") == "3.5"
    assert normalize_short("0,0") == "0"
    assert normalize_short("  Abc   Def ") == "abc def"


def test_unsupported_question_type_raises():
    with pytest.raises(ValueError):
        grade({"q": {"type": "essay", "correct": "x"}}, DEFAULT_SCORING, {})


# ----- tráo đề -----
def items(n: int = 8, **pins) -> list[ShuffleItem]:
    return [ShuffleItem(f"q{i}", ("A", "B", "C", "D"), **pins.get(f"q{i}", {})) for i in range(1, n + 1)]


def test_same_seed_gives_same_order():
    a = order_section(12345, "s1", items())
    b = order_section(12345, "s1", items())
    assert a == b


def test_different_seeds_give_different_orders():
    orders = {tuple(order_section(seed, "s1", items()).question_ids) for seed in range(50)}
    assert len(orders) > 40


def test_order_is_a_permutation_with_nothing_lost():
    order = order_section(7, "s1", items())
    assert sorted(order.question_ids) == sorted(i.id for i in items())
    for qid, opts in order.option_ids.items():
        assert sorted(opts) == ["A", "B", "C", "D"]


def test_pinned_question_keeps_its_position():
    its = [ShuffleItem("q1", ("A", "B")), ShuffleItem("q2", ("A", "B"), pin_position=True), ShuffleItem("q3", ("A", "B")), ShuffleItem("q4", ("A", "B"))]
    for seed in range(30):
        assert order_section(seed, "s1", its).question_ids[1] == "q2"


def test_pinned_options_keep_original_order():
    its = [ShuffleItem("q1", ("A", "B", "C", "D"), pin_options=True), ShuffleItem("q2", ("A", "B", "C", "D"))]
    for seed in range(30):
        assert order_section(seed, "s1", its).option_ids["q1"] == ["A", "B", "C", "D"]


def test_sections_are_shuffled_independently():
    one = order_section(5, "s1", items(4)).question_ids
    two = order_section(5, "s2", items(4)).question_ids
    assert sorted(one) == sorted(two)  # cùng tập câu, quyết định thứ tự riêng theo phần


def test_duplicate_ids_are_rejected():
    with pytest.raises(ValueError):
        order_section(1, "s1", [ShuffleItem("q1"), ShuffleItem("q1")])


def test_order_does_not_depend_on_input_order():
    its = items()
    a = order_section(99, "s1", its)
    b = order_section(99, "s1", list(reversed(its)))
    assert a.question_ids == b.question_ids
    assert a.option_ids == b.option_ids


def test_order_is_stable_across_runs_golden():
    """Kết quả cố định. Nếu test này đổi, mọi em đang thi sẽ thấy đề bị đổi thứ tự: không được đổi thuật toán."""
    order = order_section(2026, "s1", items(5))
    assert order.question_ids == ["q5", "q1", "q3", "q2", "q4"]
    assert order.option_ids["q1"] == ["C", "B", "D", "A"]
    assert order.option_ids["q2"] == ["B", "A", "C", "D"]


def test_shuffle_never_changes_which_option_is_correct():
    """Đáp án gắn với mã phương án gốc nên chấm không đổi dù hiển thị bị tráo."""
    key = {"q1": {"type": "multiple_choice", "correct": "C"}}
    order = order_section(31, "s1", [ShuffleItem("q1", ("A", "B", "C", "D"))])
    labels = display_labels(order.option_ids["q1"])
    shown_correct = labels["C"]  # em thấy đáp án đúng ở chữ này
    assert shown_correct in "ABCD"
    # em chọn đúng phương án (mã gốc C) bất kể nó hiện ở chữ nào
    assert grade(key, DEFAULT_SCORING, {"q1": "C"}).score == Decimal("0.25")
    assert grade(key, DEFAULT_SCORING, {"q1": "A"}).score == 0


def test_display_labels_follow_shuffled_order():
    assert display_labels(["C", "A", "D", "B"]) == {"C": "A", "A": "B", "D": "C", "B": "D"}


@pytest.mark.parametrize(
    "texts, ok",
    [
        (["1", "2", "3", "4"], True),
        (["x = 1", "x = 2", "Cả A và B đều đúng", "Không có đáp án nào"], False),
        (["Tất cả các phương án trên"], False),
        (["Cả ba đều sai"], False),
        (["Chỉ B và C"], False),
        (["vectơ AB", "vectơ AC"], True),
    ],
)
def test_options_referring_to_each_other_are_not_shufflable(texts, ok):
    assert options_are_shufflable(texts) is ok
