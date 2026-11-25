"""Lấy công thức từ đối tượng MathType nhúng trong DOCX (word/embeddings/oleObjectN.bin).

Mỗi đối tượng là một tệp OLE (CFB) có luồng "Equation Native": 28 byte đầu là tiêu đề, phần sau là dữ liệu MTEF.
Khi tác giả bật tùy chọn chèn TeX, MathType ghi kèm bản LaTeX của công thức, đứng sau chuỗi
"TeX Input Language" và kết thúc bằng byte 0. Đó là LaTeX CHÍNH XÁC do chính MathType sinh ra, không phải đoán.

Đo trên tệp thật của cô: mã 102 có 25/113 đối tượng mang LaTeX, s03 có 48/97, s04 và s05 là 0. Đối tượng không
mang LaTeX phải hiển thị bằng ảnh (hoặc cần bộ giải mã nhị phân MTEF, chưa làm). Không có LaTeX thì trả None,
không bao giờ suy đoán.

An toàn: đối tượng nhúng là dữ liệu không tin cậy. Giới hạn kích thước, chỉ đọc đúng một luồng, mọi lỗi thành None.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

MAX_OBJECT_BYTES = 256 * 1024
MAX_TEX_CHARS = 4000
STREAM_NAME = "Equation Native"
TEX_MARKER = b"TeX Input Language\x00"
MTEF_HEADER_BYTES = 28
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def tex_from_equation_stream(data: bytes) -> str | None:
    """LaTeX nằm trong luồng "Equation Native", hoặc None nếu công thức không mang LaTeX."""
    start = data.find(TEX_MARKER, MTEF_HEADER_BYTES)
    if start < 0:
        return None
    start += len(TEX_MARKER)
    end = data.find(b"\x00", start)
    if end < 0:
        return None
    raw = data[start:end]
    if not raw or len(raw) > MAX_TEX_CHARS * 4:
        return None
    try:
        tex = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    tex = tex.strip()
    # MathType bọc cả công thức trong một cặp {}; bỏ cặp ngoài cùng khi nó bao trọn nội dung.
    if tex.startswith("{") and tex.endswith("}") and _outer_braces_match(tex):
        tex = tex[1:-1].strip()
    return tex[:MAX_TEX_CHARS] or None


def _outer_braces_match(tex: str) -> bool:
    depth = 0
    for i, ch in enumerate(tex):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and i != len(tex) - 1:
                return False
    return depth == 0


def tex_from_ole(data: bytes) -> str | None:
    """Mở tệp OLE của một đối tượng MathType và lấy LaTeX nếu có. Mọi lỗi (hỏng, thiếu luồng) trả None."""
    if not data or len(data) > MAX_OBJECT_BYTES or data[:8] != OLE_MAGIC:
        return None
    try:
        import olefile

        with olefile.OleFileIO(io.BytesIO(data)) as ole:
            if not ole.exists(STREAM_NAME) or ole.get_size(STREAM_NAME) > MAX_OBJECT_BYTES:
                return None
            return tex_from_equation_stream(ole.openstream(STREAM_NAME).read())
    except Exception:  # noqa: BLE001 - dữ liệu không tin cậy: mọi lỗi đều là "không có"
        return None


@dataclass(frozen=True)
class Formula:
    """Công thức lấy từ một đối tượng MathType.

    source = "mathtype_tex": LaTeX do chính MathType ghi sẵn (chính xác).
    source = "mtef_decoded": giải mã nhị phân MTEF. `unverified` liệt kê các cấu trúc chưa có công thức thật để
    đối chiếu; khác rỗng nghĩa là cô phải so với ảnh trước khi phát đề.
    """

    latex: str
    source: str
    unverified: tuple[str, ...] = ()


def formula_from_equation_stream(data: bytes) -> Formula | None:
    tex = tex_from_equation_stream(data)
    if tex:
        return Formula(tex, "mathtype_tex")
    from .mtef import MtefError, UnsupportedFormula
    from .mtef_latex import decode

    try:
        decoded = decode(data)
    except (MtefError, UnsupportedFormula):
        return None
    return Formula(decoded.latex, "mtef_decoded", tuple(sorted(decoded.unverified)))


def formula_from_ole(data: bytes) -> Formula | None:
    """Như tex_from_ole nhưng thử cả giải mã nhị phân khi tệp không mang LaTeX. Mọi lỗi trả None."""
    if not data or len(data) > MAX_OBJECT_BYTES or data[:8] != OLE_MAGIC:
        return None
    try:
        import olefile

        with olefile.OleFileIO(io.BytesIO(data)) as ole:
            if not ole.exists(STREAM_NAME) or ole.get_size(STREAM_NAME) > MAX_OBJECT_BYTES:
                return None
            return formula_from_equation_stream(ole.openstream(STREAM_NAME).read())
    except Exception:  # noqa: BLE001 - dữ liệu không tin cậy: mọi lỗi đều là "không có"
        return None
