"""Chuyển cây MTEF (mtef.parse) thành LaTeX, kèm danh sách cấu trúc đã dùng.

Hai mức tin cậy:
- VERIFIED_FEATURES: cấu trúc đã có công thức thật mà LaTeX giải ra khớp với LaTeX do chính MathType ghi sẵn
  (đối chiếu trên đề thật của cô ngày 24/11/2026). Dùng thẳng.
- Cấu trúc còn lại được giải theo đặc tả nhưng CHƯA có công thức thật để đối chiếu. Vẫn trả LaTeX nhưng
  `unverified` khác rỗng, nơi gọi phải gắn cờ để cô so với ảnh gốc trước khi phát đề.
Cấu trúc không có trong bảng nào ném UnsupportedFormula: nơi gọi giữ ảnh.

Chỉ thêm một cấu trúc vào VERIFIED_FEATURES khi test đối chiếu (tests/test_exam_mtef.py) có công thức thật cho nó.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .mtef import (
    FN_EXPAND,
    FN_FUNCTION,
    FN_LCGREEK,
    FN_MTEXTRA,
    FN_NUMBER,
    FN_SPACE,
    FN_SYMBOL,
    FN_TEXT,
    FN_UCGREEK,
    FN_VARIABLE,
    MtefError,
    Node,
    UnsupportedFormula,
    parse,
)

# Mẫu (selector)
TM_ANGLE, TM_PAREN, TM_BRACE, TM_BRACK, TM_BAR, TM_DBAR, TM_FLOOR, TM_CEILING = range(8)
TM_INTERVAL, TM_ROOT, TM_FRACT, TM_UBAR, TM_OBAR = 9, 10, 11, 12, 13
TM_LIM, TM_SUB, TM_SUP, TM_VEC, TM_HAT = 23, 27, 28, 31, 33

# Chỉ những cấu trúc đã có công thức thật khớp với LaTeX do MathType ghi sẵn (98/98 công thức có đáp án,
# đề thật ngày 24/11/2026). Chữ Hy Lạp, hàm (sin, cos), chỉ số dưới, ngoặc, mũ chưa có công thức thật để đối
# chiếu nên KHÔNG nằm ở đây: công thức dùng chúng bị gắn cờ cần cô xem.
VERIFIED_FEATURES = frozenset(
    {"char", "text", "symbol", "space", "vec", "frac", "sqrt", "sup", "lim", "embell:rarrow", "embell:bar"}
)

GREEK = {
    0x3B1: r"\alpha", 0x3B2: r"\beta", 0x3B3: r"\gamma", 0x3B4: r"\delta", 0x3B5: r"\epsilon", 0x3B6: r"\zeta",
    0x3B7: r"\eta", 0x3B8: r"\theta", 0x3B9: r"\iota", 0x3BA: r"\kappa", 0x3BB: r"\lambda", 0x3BC: r"\mu",
    0x3BD: r"\nu", 0x3BE: r"\xi", 0x3C0: r"\pi", 0x3C1: r"\rho", 0x3C3: r"\sigma", 0x3C4: r"\tau",
    0x3C5: r"\upsilon", 0x3C6: r"\varphi", 0x3C7: r"\chi", 0x3C8: r"\psi", 0x3C9: r"\omega",
    0x3D5: r"\phi", 0x3F5: r"\epsilon", 0x3D1: r"\vartheta",
    0x393: r"\Gamma", 0x394: r"\Delta", 0x398: r"\Theta", 0x39B: r"\Lambda", 0x39E: r"\Xi", 0x3A0: r"\Pi",
    0x3A3: r"\Sigma", 0x3A6: r"\Phi", 0x3A8: r"\Psi", 0x3A9: r"\Omega",
}
SYMBOLS = {
    0x2212: "-", 0xB1: r"\pm", 0xD7: r"\times", 0xF7: r"\div", 0x22C5: r"\cdot", 0xB7: r"\cdot",
    0x2260: r"\neq", 0x2264: r"\leq", 0x2265: r"\geq", 0x2248: r"\approx", 0x2261: r"\equiv",
    0x221E: r"\infty", 0x2192: r"\rightarrow", 0x2190: r"\leftarrow", 0x2194: r"\leftrightarrow",
    0x21D2: r"\Rightarrow", 0x21D0: r"\Leftarrow", 0x21D4: r"\Leftrightarrow",
    0x2208: r"\in", 0x2209: r"\notin", 0x2282: r"\subset", 0x2283: r"\supset", 0x2286: r"\subseteq",
    0x2287: r"\supseteq", 0x222A: r"\cup", 0x2229: r"\cap", 0x2205: r"\emptyset",
    0x2220: r"\angle", 0x22A5: r"\perp", 0x2225: r"\parallel", 0x2200: r"\forall", 0x2203: r"\exists",
    0x2026: r"\ldots", 0x22EF: r"\cdots", 0x2202: r"\partial", 0x2234: r"\therefore", 0x25B3: r"\triangle",
    0x0025: r"\%", 0x2032: "'",
}
ASCII_OK = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=<>()[]|,.;:!?/'")
FUNCTIONS = {
    "sin", "cos", "tan", "cot", "sec", "csc", "log", "ln", "lg", "exp", "max", "min", "sup", "inf", "arcsin",
    "arccos", "arctan", "sinh", "cosh", "tanh", "det", "gcd", "lim", "dim", "ker", "deg", "arg",
}
# Dấu cách thường và các dấu cách riêng của MathType (vùng U+EF00).
SPACES = {0x20: r"\ ", 0xA0: r"\ ", 0x2009: r"\,", 0x200A: r"\,", 0x2002: r"\ ", 0x2003: r"\quad "}
SPACES.update({code: r"\," for code in range(0xEF00, 0xEF09)})
VEC_BY_VARIATION = {1: r"\overleftarrow", 2: r"\overrightarrow", 3: r"\overleftrightarrow"}
# Viền chữ (embellishment) trên MỘT ký tự: mã -> (lệnh, tên tính năng)
EMBELLS = {
    11: (r"\overrightarrow", "embell:rarrow"),
    17: (r"\bar", "embell:bar"),
    12: (r"\overleftarrow", "embell:larrow"),
    9: (r"\hat", "embell:hat"),
    8: (r"\tilde", "embell:tilde"),
    2: (r"\dot", "embell:dot"),
    3: (r"\ddot", "embell:ddot"),
}
PRIMES = {5: "'", 6: "''", 18: "'''"}
# Ký tự ngoặc thật trong mẫu ngoặc (kiểu EXPAND). U+EC07/EC08 là thanh dọc riêng của MathType.
FENCE_GLYPHS = {
    0x28: "(", 0x29: ")", 0x5B: "[", 0x5D: "]", 0x7B: r"\{", 0x7D: r"\}", 0x7C: "|",
    0xEC07: "|", 0xEC08: "|", 0x2016: r"\|", 0x2329: r"\langle", 0x232A: r"\rangle",
    0x27E8: r"\langle", 0x27E9: r"\rangle", 0x230A: r"\lfloor", 0x230B: r"\rfloor", 0x2308: r"\lceil", 0x2309: r"\rceil",
}
FENCE_FEATURE = {TM_PAREN: "fence:paren", TM_BRACK: "fence:brack", TM_BRACE: "fence:brace", TM_BAR: "fence:bar",
                 TM_DBAR: "fence:dbar", TM_ANGLE: "fence:angle", TM_FLOOR: "fence:floor", TM_CEILING: "fence:ceil",
                 TM_INTERVAL: "fence:interval"}


@dataclass
class Decoded:
    latex: str
    features: set[str] = field(default_factory=set)

    @property
    def unverified(self) -> set[str]:
        return self.features - VERIFIED_FEATURES


class _Translator:
    def __init__(self) -> None:
        self.features: set[str] = set()

    # ----- ký tự -----
    def char(self, node: Node) -> str:
        tf, code = node.typeface, node.code
        if code in SPACES and tf in (FN_SPACE, FN_TEXT, FN_MTEXTRA, FN_VARIABLE, FN_FUNCTION, FN_SYMBOL, FN_NUMBER):
            self.features.add("space")
            return SPACES[code]
        if tf in (FN_LCGREEK, FN_UCGREEK) and code in SYMBOLS:
            self.features.add("symbol")  # MathType đôi khi đặt ∞ trong kiểu chữ Hy Lạp
            return SYMBOLS[code]
        if tf in (FN_LCGREEK, FN_UCGREEK):
            if code not in GREEK:
                raise UnsupportedFormula(f"Chữ Hy Lạp chưa hỗ trợ: U+{code:04X}.")
            self.features.add("greek")
            return GREEK[code]
        if code in SYMBOLS and tf in (FN_SYMBOL, FN_VARIABLE, FN_FUNCTION, FN_NUMBER, FN_MTEXTRA, FN_TEXT):
            self.features.add("symbol")
            return SYMBOLS[code]
        if code < 128 and chr(code) in ASCII_OK and tf in (FN_TEXT, FN_FUNCTION, FN_VARIABLE, FN_SYMBOL, FN_NUMBER):
            self.features.add("char")
            return chr(code)
        raise UnsupportedFormula(f"Ký tự chưa hỗ trợ: kiểu {tf}, mã U+{code:04X}.")

    def embellished(self, node: Node) -> str:
        base = self.char(node)
        for embell in node.embells:
            if embell in EMBELLS:
                macro, feature = EMBELLS[embell]
                self.features.add(feature)
                base = f"{macro}{{{base}}}"
            elif embell in PRIMES:
                self.features.add("embell:prime")
                base = base + PRIMES[embell]
            else:
                raise UnsupportedFormula(f"Viền chữ chưa hỗ trợ: {embell}.")
        return base

    # ----- dòng -----
    def items(self, children: list[Node]) -> str:
        parts: list[str] = []
        i = 0
        while i < len(children):
            node = children[i]
            if self._is_text(node):
                j, text = i, ""
                while j < len(children) and self._is_text(children[j]):
                    text += chr(children[j].code)
                    j += 1
                self.features.add("text")
                parts.append(r"\text{" + text + "}")
                i = j
                continue
            if self._is_function_letter(node):
                j, word = i, ""
                while j < len(children) and self._is_function_letter(children[j]):
                    word += chr(children[j].code)
                    j += 1
                self.features.add("function")
                parts.append("\\" + word if word in FUNCTIONS else r"\mathrm{" + word + "}")
                i = j
                continue
            parts.append(self.node(node))
            i += 1
        return _join(parts)

    @staticmethod
    def _is_text(node: Node) -> bool:
        return (
            node.kind == "CHAR" and node.typeface == FN_TEXT and node.code < 128 and not node.embells
            and chr(node.code) not in "\\{}$&#^_%~" and node.code >= 0x21
        )

    @staticmethod
    def _is_function_letter(node: Node) -> bool:
        return node.kind == "CHAR" and node.typeface == FN_FUNCTION and node.code < 128 and chr(node.code).isalpha() and not node.embells

    def line(self, node: Node) -> str:
        if node.kind != "LINE":
            raise MtefError("Ngăn của mẫu không phải một dòng.")
        return self.items(node.children)

    def node(self, node: Node) -> str:
        if node.kind == "CHAR":
            return self.embellished(node)
        if node.kind == "LINE":
            return self.line(node)
        if node.kind == "TMPL":
            return self.template(node)
        raise UnsupportedFormula(f"Nút {node.kind} chưa hỗ trợ.")

    # ----- mẫu -----
    def template(self, node: Node) -> str:
        sel, var, kids = node.selector, node.variation, node.children
        if sel == TM_VEC:
            macro = VEC_BY_VARIATION.get(var)
            if macro is None or not kids or kids[0].kind != "LINE":
                raise UnsupportedFormula(f"Mẫu vectơ chưa hỗ trợ (biến thể {var}).")
            self.features.add("vec")
            return f"{macro}{{{self.line(kids[0])}}}"
        if sel == TM_HAT:
            if var != 0 or not kids or kids[0].kind != "LINE":
                raise UnsupportedFormula(f"Mũ chưa hỗ trợ (biến thể {var}).")
            inner = kids[0]
            self.features.add("hat")
            macro = r"\hat" if len(inner.children) == 1 else r"\widehat"
            return f"{macro}{{{self.line(inner)}}}"
        if sel == TM_FRACT:
            if var != 0 or len(kids) != 2 or any(k.kind != "LINE" for k in kids):
                raise UnsupportedFormula(f"Phân số chưa hỗ trợ (biến thể {var}).")
            self.features.add("frac")
            return rf"\frac{{{self.line(kids[0])}}}{{{self.line(kids[1])}}}"
        if sel == TM_ROOT:
            if var == 0 and kids and kids[0].kind == "LINE" and (len(kids) == 1 or (len(kids) == 2 and kids[1].kind == "LINE" and kids[1].null)):
                self.features.add("sqrt")
                return rf"\sqrt{{{self.line(kids[0])}}}"
            if var == 1 and len(kids) == 2 and all(k.kind == "LINE" and not k.null for k in kids):
                self.features.add("nthroot")
                return rf"\sqrt[{self.line(kids[1])}]{{{self.line(kids[0])}}}"
            raise UnsupportedFormula(f"Căn chưa hỗ trợ (biến thể {var}).")
        if sel in (TM_SUB, TM_SUP):
            if any(k.kind != "LINE" for k in kids):
                raise UnsupportedFormula("Chỉ số có thành phần lạ.")
            live = [k for k in kids if not k.null]
            if len(live) != 1:
                raise UnsupportedFormula("Chỉ số không đúng một ngăn.")
            self.features.add("sub" if sel == TM_SUB else "sup")
            return ("_" if sel == TM_SUB else "^") + "{" + self.line(live[0]) + "}"
        if sel == TM_LIM:
            # đã kiểm chứng: biến thể 16 = "lim" có cận dưới, không có cận trên
            if var != 16 or len(kids) != 3 or any(k.kind != "LINE" for k in kids) or not kids[2].null:
                raise UnsupportedFormula(f"Giới hạn chưa hỗ trợ (biến thể {var}).")
            word = "".join(chr(c.code) for c in kids[0].children if c.kind == "CHAR")
            if word not in FUNCTIONS or len(word) != len(kids[0].children):
                raise UnsupportedFormula(f"Toán tử giới hạn lạ: {word!r}.")
            self.features.add("lim")
            return "\\" + word + "_{" + self.line(kids[1]) + "}"
        if sel in FENCE_FEATURE:
            return self.fence(node)
        if sel in (TM_OBAR, TM_UBAR) and var == 0 and kids and kids[0].kind == "LINE":
            self.features.add("overbar" if sel == TM_OBAR else "underbar")
            return (r"\overline" if sel == TM_OBAR else r"\underline") + "{" + self.line(kids[0]) + "}"
        raise UnsupportedFormula(f"Mẫu chưa hỗ trợ: loại {node.selector}, biến thể {var}.")

    def fence(self, node: Node) -> str:
        """Ngoặc lấy từ chính ký tự ngoặc trong mẫu, không suy từ loại mẫu."""
        kids = node.children
        if not kids or kids[0].kind != "LINE" or kids[0].null:
            raise UnsupportedFormula("Ngoặc không có nội dung.")
        glyphs = []
        for k in kids[1:]:
            if k.kind != "CHAR" or k.typeface != FN_EXPAND or k.code not in FENCE_GLYPHS or k.embells:
                raise UnsupportedFormula(f"Ký tự ngoặc lạ trong mẫu {node.selector}.")
            glyphs.append(FENCE_GLYPHS[k.code])
        side = node.variation & 0x03
        if len(glyphs) == 2:
            left, right = glyphs
        elif len(glyphs) == 1 and side == 1:
            left, right = glyphs[0], "."
        elif len(glyphs) == 1 and side == 2:
            left, right = ".", glyphs[0]
        else:
            raise UnsupportedFormula(f"Ngoặc chưa hỗ trợ (biến thể {node.variation}).")
        self.features.add(FENCE_FEATURE[node.selector])
        return rf"\left{left} {self.line(kids[0])} \right{right}"


def _join(parts: list[str]) -> str:
    """Nối các mảnh LaTeX, thêm dấu cách sau lệnh chữ cái khi mảnh kế tiếp bắt đầu bằng chữ cái."""
    out = ""
    for part in parts:
        if not part:
            continue
        if out and re.search(r"\\[A-Za-z]+$", out) and re.match(r"[A-Za-z]", part):
            out += " "
        out += part
    return out


def decode(stream: bytes) -> Decoded:
    """Giải luồng "Equation Native" thành LaTeX. Ném MtefError (hỏng) hoặc UnsupportedFormula (chưa hỗ trợ)."""
    header, root = parse(stream)
    if header.colored:
        raise UnsupportedFormula("Công thức có màu; màu sẽ mất nếu đổi sang LaTeX.")
    if len(root.children) != 1 or root.children[0].kind != "LINE":
        raise UnsupportedFormula("Thân công thức không phải một dòng duy nhất.")
    t = _Translator()
    latex = t.line(root.children[0]).strip()
    if not latex or latex.count("{") - latex.count(r"\{") != latex.count("}") - latex.count(r"\}"):
        raise MtefError("LaTeX sinh ra không cân bằng.")
    return Decoded(latex=latex, features=t.features)
