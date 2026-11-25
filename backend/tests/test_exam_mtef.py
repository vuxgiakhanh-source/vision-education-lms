"""Bộ giải mã nhị phân MTEF (công thức MathType).

Dữ liệu cố định là byte công thức THẬT lấy từ đề của cô, kèm đáp án chuẩn do chính MathType ghi sẵn. Ngày 24/11/2026
bộ giải mã đã khớp 98/98 công thức có đáp án chuẩn; test này khóa hành vi đó lại.

Nguyên tắc: không đoán. Công thức lạ bị từ chối để dùng ảnh; công thức giải mã bằng cấu trúc chưa có công thức
thật để đối chiếu thì bị đánh dấu `unverified`.
"""

from __future__ import annotations

import random
import re
import time

import pytest
from mtef_fixtures import FIXTURES

from app.modules.exams.imports.readers.mathtype import formula_from_equation_stream, tex_from_equation_stream
from app.modules.exams.imports.readers.mtef import MtefError, UnsupportedFormula, parse
from app.modules.exams.imports.readers.mtef_latex import VERIFIED_FEATURES, decode


def stream(name: str) -> bytes:
    return bytes.fromhex(FIXTURES[name][1])


def truth(name: str) -> str:
    return FIXTURES[name][2]


def canon(s: str) -> str:
    """Chuẩn hóa các cách viết hiển thị giống hệt nhau (x^{2} = x^2, \\mathrm = \\text, khoảng trắng)."""
    s = s.replace(r"\right.", "").replace(r"\left.", "")
    s = re.sub(r"\\left|\\right|\\,|\\ |\\;|\\!|~|\\quad", "", s)
    s = s.replace(r"\rightarrow", r"\to").replace("−", "-").replace(r"\mathrm", r"\text")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"([\^_])\{(.)\}", r"\1\2", s)
    s = re.sub(r"\\text\{([^{}]*)\}", lambda m: "\x01" + m.group(1) + "\x02", s)
    return s.replace("\x02\x01", "")


VERIFIED = ["abc", "vector_eq", "embell_arrow", "frac_sqrt_sup", "limit", "bar_over_char", "percent", "text_units"]


# ----- khớp với đáp án chuẩn của MathType -----
@pytest.mark.parametrize("name", VERIFIED)
def test_decoder_matches_the_latex_mathtype_wrote_itself(name):
    expected = tex_from_equation_stream(stream(name))
    assert expected is not None
    decoded = decode(stream(name))
    assert canon(decoded.latex) == canon(expected)
    assert decoded.unverified == set()  # chỉ dùng cấu trúc đã được kiểm chứng


def test_exact_output_is_locked_for_the_common_cases():
    assert decode(stream("abc")).latex == "A,B,C"
    assert decode(stream("vector_eq")).latex == r"\overrightarrow{AB}=\overrightarrow{CA}+\overrightarrow{BC}"
    assert decode(stream("limit")).latex == r"\lim_{x\rightarrow+\infty}f(x)=2"
    assert decode(stream("bar_over_char")).latex == r"\bar{C}(x)"
    assert decode(stream("percent")).latex == r"p\%"


def test_verified_features_are_exactly_those_with_real_evidence():
    seen: set[str] = set()
    for name in VERIFIED:
        seen |= decode(stream(name)).features
    # mọi tính năng được tin cậy phải xuất hiện trong ít nhất một công thức thật đã khớp
    assert VERIFIED_FEATURES <= seen


# ----- cấu trúc chưa có công thức thật để đối chiếu -----
@pytest.mark.parametrize(
    "name, feature",
    [("unverified_paren", "fence:paren"), ("unverified_bar", "fence:bar"), ("unverified_hat", "hat")],
)
def test_unverified_structures_are_decoded_but_marked(name, feature):
    decoded = decode(stream(name))
    assert feature in decoded.unverified
    formula = formula_from_equation_stream(stream(name))
    assert formula is not None and formula.source == "mtef_decoded" and feature in formula.unverified


def test_latex_written_by_mathtype_is_preferred_over_decoding():
    formula = formula_from_equation_stream(stream("vector_eq"))
    assert formula.source == "mathtype_tex" and formula.unverified == ()


# ----- từ chối thay vì đoán -----
def test_old_equation_editor_format_is_an_error_not_a_guess():
    with pytest.raises(MtefError):
        decode(stream("v3"))
    assert formula_from_equation_stream(stream("v3")) is None


def test_ruler_objects_are_unsupported():
    with pytest.raises(UnsupportedFormula):
        decode(stream("ruler"))
    assert formula_from_equation_stream(stream("ruler")) is None


def test_colored_formula_is_refused_because_color_would_be_lost():
    data = bytearray(stream("abc"))
    # đổi giá trị màu của COLOR_DEF (tag 0x10, options 0, 3 giá trị 16 bit) thành màu đỏ
    at = data.find(bytes([0x10, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    assert at > 0
    data[at + 2] = 0xFF
    with pytest.raises(UnsupportedFormula):
        decode(bytes(data))


# ----- toàn vẹn cấu trúc -----
@pytest.mark.parametrize("name", VERIFIED)
def test_trailing_data_and_missing_terminator_are_rejected(name):
    good = stream(name)
    with pytest.raises(MtefError):
        parse(good + b"\x00")
    with pytest.raises(MtefError):
        parse(good[:-1])


def test_truncating_a_real_formula_anywhere_never_gives_a_wrong_answer():
    """Cắt cụt ở MỌI vị trí: hoặc báo lỗi, hoặc (chỉ khi cắt đúng chỗ kết thúc hợp lệ) ra đúng công thức."""
    good = stream("vector_eq")
    full = decode(good).latex
    for cut in range(len(good)):
        try:
            result = decode(good[:cut]).latex
        except (MtefError, UnsupportedFormula):
            continue
        assert result == full


def test_random_corruption_only_ever_raises_the_two_expected_errors():
    rng = random.Random(20261124)
    names = VERIFIED + ["unverified_paren", "unverified_bar", "unverified_hat", "ruler", "v3"]
    started = time.perf_counter()
    for _ in range(4000):
        data = bytearray(stream(rng.choice(names)))
        for _ in range(rng.randint(1, 4)):
            data[rng.randrange(28, len(data))] = rng.randrange(256)  # chỉ phá phần MTEF, giữ nguyên tiêu đề OLE
        try:
            decode(bytes(data))
        except (MtefError, UnsupportedFormula):
            pass
    assert time.perf_counter() - started < 20


def test_deep_nesting_is_rejected_quickly():
    good = stream("abc")
    body_start = good.index(bytes([0x0A, 0x01, 0x00]))
    bomb = good[:body_start] + bytes([0x0A, 0x01, 0x00]) + bytes([0x03, 0x00, 0x0B, 0x00, 0x00, 0x01, 0x00]) * 500
    started = time.perf_counter()
    with pytest.raises(MtefError):
        parse(bomb + b"\x00" * 1200)
    assert time.perf_counter() - started < 1


def test_huge_record_count_is_rejected():
    good = stream("abc")
    body_start = good.index(bytes([0x0A, 0x01, 0x00]))
    char = bytes([0x02, 0x00, 0x83, 0x41, 0x00])
    bomb = good[:body_start] + bytes([0x0A, 0x01, 0x00]) + char * 6000 + b"\x00\x00"
    with pytest.raises(MtefError):
        parse(bomb)


def test_too_short_stream_is_rejected():
    with pytest.raises(MtefError):
        parse(b"")
    with pytest.raises(MtefError):
        parse(bytes(30))


def test_unknown_record_tag_is_rejected_not_skipped():
    good = bytearray(stream("abc"))
    body_start = bytes(good).index(bytes([0x0A, 0x01, 0x00]))
    good[body_start + 3] = 0x63  # tag 99: nằm trong khoảng "không dùng", phải từ chối
    with pytest.raises((MtefError, UnsupportedFormula)):
        parse(bytes(good))
