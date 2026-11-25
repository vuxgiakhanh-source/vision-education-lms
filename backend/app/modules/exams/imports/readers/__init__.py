"""Bộ đọc đề: nhận dạng định dạng theo nội dung rồi đọc ra ParsedDocument."""

from __future__ import annotations

from .model import ParsedDocument
from .safety import UnsafeFileError, UnsupportedFormatError, detect_format

__all__ = ["read_exam", "ParsedDocument", "UnsafeFileError", "UnsupportedFormatError"]


def read_exam(data: bytes, source_name: str = "") -> ParsedDocument:
    """Đọc tệp đề theo nội dung (không tin đuôi tệp). Ném UnsafeFileError hoặc UnsupportedFormatError."""
    kind = detect_format(data)
    if kind == "docx":
        from .docx_reader import read_docx

        return read_docx(data, source_name)
    if kind == "pdf":
        from .pdf_reader import read_pdf

        return read_pdf(data, source_name)
    if kind in ("doc", "xlsx"):
        raise UnsupportedFormatError(f"Định dạng .{kind} chưa có bộ đọc.")
    raise UnsupportedFormatError("Không nhận dạng được định dạng tệp.")
