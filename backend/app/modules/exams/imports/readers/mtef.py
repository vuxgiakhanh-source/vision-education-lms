"""Giải mã nhị phân MTEF v5 (công thức MathType) thành LaTeX.

Dùng khi đối tượng MathType không mang sẵn LaTeX (mathtype.py). Đây là bộ giải mã tự viết theo đặc tả MTEF, đối
chiếu với 73 công thức có LaTeX sẵn trong đề thật của cô (xem tests/test_exam_mtef.py).

NGUYÊN TẮC CHẶT: không đoán.
- Mọi điều lạ (mã bản ghi lạ, đệm chồng lấn, dữ liệu thừa, mẫu hay ký tự chưa hỗ trợ) ném MtefError hoặc
  UnsupportedFormula. Nơi gọi khi đó giữ ảnh công thức và gắn cờ, không bao giờ hiển thị công thức đoán.
- Chỉ hỗ trợ các cấu trúc đã kiểm chứng. Thêm cấu trúc mới chỉ khi có công thức thật để đối chiếu.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Loại bản ghi
END, LINE, CHAR, TMPL, PILE, MATRIX, EMBELL, RULER, FONT_STYLE_DEF, SIZE = range(10)
FULL, SUB, SUB2, SYM, SUBSYM, COLOR, COLOR_DEF, FONT_DEF, EQN_PREFS, ENCODING_DEF = range(10, 20)
FUTURE = 100

# Tùy chọn
OPT_NUDGE = 0x08
OPT_CHAR_EMBELL = 0x01
OPT_CHAR_ENC_CHAR8 = 0x04
OPT_CHAR_ENC_CHAR16 = 0x10
OPT_CHAR_ENC_NO_MTCODE = 0x20
OPT_LINE_NULL = 0x01
OPT_LINE_LSPACE = 0x04
OPT_RULER = 0x02
OPT_COLOR_CMYK = 0x01
OPT_COLOR_NAME = 0x04

# Kiểu chữ (typeface = 128 + số kiểu)
FN_TEXT, FN_FUNCTION, FN_VARIABLE, FN_LCGREEK, FN_UCGREEK, FN_SYMBOL, FN_VECTOR, FN_NUMBER = range(1, 9)
FN_MTEXTRA, FN_TEXT_FE, FN_EXPAND, FN_MARKER, FN_SPACE = 11, 12, 22, 23, 24

# Mẫu (selector)
TM_ANGLE, TM_PAREN, TM_BRACE, TM_BRACK, TM_BAR, TM_DBAR, TM_FLOOR, TM_CEILING = range(8)
TM_ROOT, TM_FRACT, TM_UBAR, TM_OBAR = 10, 11, 12, 13
TM_SUB, TM_SUP, TM_SUBSYM = 27, 28, 29
TM_VEC = 31

MAX_NODES = 5000
MAX_DEPTH = 40


class MtefError(ValueError):
    """Dữ liệu MTEF hỏng hoặc không đúng định dạng."""


class UnsupportedFormula(ValueError):
    """Công thức hợp lệ nhưng có cấu trúc chưa được kiểm chứng; phải dùng ảnh."""


@dataclass
class Node:
    kind: str  # "LINE" | "CHAR" | "TMPL" | "PILE" | "ROOT"
    typeface: int = 0
    code: int = 0
    selector: int = 0
    variation: int = 0
    null: bool = False
    embells: list[int] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)


@dataclass
class Header:
    version: int
    platform: int
    product: int
    app_key: str
    colored: bool = False


class _Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def u8(self) -> int:
        if self.pos >= len(self.data):
            raise MtefError("Dữ liệu MTEF bị cắt cụt.")
        v = self.data[self.pos]
        self.pos += 1
        return v

    def u16(self) -> int:
        return self.u8() | (self.u8() << 8)

    def cstring(self) -> bytes:
        out = bytearray()
        while True:
            c = self.u8()
            if c == 0:
                return bytes(out)
            out.append(c)
            if len(out) > 512:
                raise MtefError("Chuỗi quá dài.")

    def done(self) -> bool:
        return self.pos >= len(self.data)


def _read_dimensions(r: _Reader, count: int) -> None:
    """Mảng kích thước kiểu nibble (đơn vị rồi chữ số, 0xF kết thúc một giá trị). Chỉ cần bỏ qua đúng độ dài."""
    finished = 0
    while finished < count:
        byte = r.u8()
        for nib in (byte >> 4, byte & 15):
            if nib == 15:
                finished += 1
                if finished >= count:
                    break


def _read_prefs(r: _Reader) -> None:
    r.u8()  # options
    _read_dimensions(r, r.u8())  # kích thước
    _read_dimensions(r, r.u8())  # khoảng cách
    for _ in range(r.u8()):  # kiểu
        if r.u8() != 0:
            r.u8()


def parse(stream: bytes) -> tuple[Header, Node]:
    """Phân tích luồng "Equation Native" (28 byte tiêu đề OLE rồi MTEF). Ném MtefError nếu có điều lạ."""
    if len(stream) < 40:
        raise MtefError("Luồng quá ngắn.")
    r = _Reader(stream[28:])
    version, platform, product = r.u8(), r.u8(), r.u8()
    r.u8()  # phiên bản sản phẩm
    r.u8()  # phiên bản phụ
    if version != 5:
        raise MtefError(f"Chỉ hỗ trợ MTEF v5, gặp v{version}.")
    app_key = r.cstring().decode("ascii", "replace")
    r.u8()  # tùy chọn công thức
    header = Header(version, platform, product, app_key)

    root = Node("ROOT")
    stack: list[Node] = [root]
    nodes = 0
    color_defs: list[tuple[int, ...]] = []
    closed_root = False

    while not r.done():
        if closed_root:
            raise MtefError("Còn dữ liệu sau khi công thức kết thúc.")
        nodes += 1
        if nodes > MAX_NODES:
            raise MtefError("Công thức quá lớn.")
        tag = r.u8()

        if tag >= FUTURE:
            length = r.u8()
            if length == 255:
                length = r.u16()
            for _ in range(length):
                r.u8()
            continue
        if tag == END:
            node = stack.pop()
            if node is root:
                closed_root = True
            continue
        if tag == ENCODING_DEF:
            r.cstring()
            continue
        if tag == FONT_DEF:
            r.u8()
            r.cstring()
            continue
        if tag == EQN_PREFS:
            _read_prefs(r)
            continue
        if FULL <= tag <= SUBSYM:
            continue  # cỡ chữ: LaTeX tự lo
        if tag == SIZE:
            lsize = r.u8()
            if lsize == 101:
                r.u16()
            else:
                r.u8()
            continue
        if tag == COLOR:
            r.u8()
            continue
        if tag == COLOR_DEF:
            options = r.u8()
            values = tuple(r.u16() for _ in range(4 if options & OPT_COLOR_CMYK else 3))
            if options & OPT_COLOR_NAME:
                r.cstring()
            color_defs.append(values)
            continue

        parent = stack[-1]
        if len(stack) > MAX_DEPTH:
            raise MtefError("Công thức lồng quá sâu.")

        if tag == LINE:
            options = r.u8()
            if options & OPT_NUDGE:
                raise UnsupportedFormula("Có chỉnh vị trí tay (nudge).")
            if options & OPT_LINE_LSPACE:
                r.u8()
            if options & OPT_RULER:
                raise UnsupportedFormula("Có thước tab.")
            node = Node("LINE", null=bool(options & OPT_LINE_NULL))
            parent.children.append(node)
            if not node.null:
                stack.append(node)
        elif tag == CHAR:
            options = r.u8()
            if options & OPT_NUDGE:
                raise UnsupportedFormula("Có chỉnh vị trí tay (nudge).")
            typeface = r.u8()
            code = 0
            if not options & OPT_CHAR_ENC_NO_MTCODE:
                code = r.u16()
            if options & OPT_CHAR_ENC_CHAR8:
                r.u8()
            if options & OPT_CHAR_ENC_CHAR16:
                r.u16()
            if typeface < 128:
                raise MtefError(f"Kiểu chữ lạ: {typeface}.")
            node = Node("CHAR", typeface=typeface - 128, code=code)
            if options & OPT_CHAR_EMBELL:
                while True:
                    t = r.u8()
                    if t == END:
                        break
                    if t != EMBELL:
                        raise MtefError("Danh sách viền chữ không đúng.")
                    eopt = r.u8()
                    if eopt & OPT_NUDGE:
                        raise UnsupportedFormula("Có chỉnh vị trí tay (nudge).")
                    node.embells.append(r.u8())
            parent.children.append(node)
        elif tag == TMPL:
            options = r.u8()
            if options & OPT_NUDGE:
                raise UnsupportedFormula("Có chỉnh vị trí tay (nudge).")
            selector = r.u8()
            first = r.u8()
            variation = first
            if first & 0x80:
                variation = (first & 0x7F) | (r.u8() << 8)
            r.u8()  # tùy chọn của mẫu
            node = Node("TMPL", selector=selector, variation=variation)
            parent.children.append(node)
            stack.append(node)
        elif tag in (PILE, MATRIX, EMBELL, RULER, FONT_STYLE_DEF):
            raise UnsupportedFormula(f"Bản ghi {tag} chưa được hỗ trợ.")
        else:
            raise MtefError(f"Mã bản ghi lạ: {tag}.")

    if not closed_root or len(stack) != 0:
        raise MtefError("Cấu trúc không cân bằng (thiếu hoặc thừa bản ghi kết thúc).")
    header.colored = any(any(v) for v in color_defs)
    return header, root


