"""Kiểm tra tệp tải lên trước khi đọc. Tệp đề là dữ liệu không tin cậy."""

from __future__ import annotations

import io
import zipfile

MAX_FILE_BYTES = 50 * 1024 * 1024
MAX_ZIP_ENTRIES = 5000
MAX_XML_BYTES = 50 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED = 500 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200


class UnsafeFileError(ValueError):
    """Tệp không an toàn hoặc hỏng. Thông điệp dành cho người dùng."""


class UnsupportedFormatError(ValueError):
    """Định dạng chưa có bộ đọc."""


def detect_format(data: bytes) -> str:
    """Nhận dạng theo nội dung (không tin đuôi tệp): pdf, docx, xlsx, doc hoặc unknown."""
    if data[:5] == b"%PDF-":
        return "pdf"
    if data[:4] == b"PK\x03\x04":
        try:
            names = set(zipfile.ZipFile(io.BytesIO(data)).namelist())
        except zipfile.BadZipFile:
            return "unknown"
        if "word/document.xml" in names:
            return "docx"
        if "xl/workbook.xml" in names:
            return "xlsx"
        return "unknown"
    if data[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
        return "doc"
    return "unknown"


def open_docx_parts(data: bytes) -> tuple[bytes, bytes, list[str], "zipfile.ZipFile"]:
    """Trả (document.xml, document.xml.rels, tên mọi phần, tệp zip đang mở) sau khi kiểm giới hạn.

    Chặn: tệp quá lớn, quá nhiều phần, tỷ lệ nén bất thường (zip bomb), XML có DOCTYPE/ENTITY.
    """
    if len(data) > MAX_FILE_BYTES:
        raise UnsafeFileError("Tệp quá lớn.")
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise UnsafeFileError("Tệp Word bị hỏng hoặc không phải .docx.") from exc

    infos = zf.infolist()
    if len(infos) > MAX_ZIP_ENTRIES:
        raise UnsafeFileError("Tệp có quá nhiều thành phần.")
    if sum(i.file_size for i in infos) > MAX_TOTAL_UNCOMPRESSED:
        raise UnsafeFileError("Tệp giải nén quá lớn.")

    def read_part(name: str, required: bool) -> bytes:
        try:
            info = zf.getinfo(name)
        except KeyError:
            if required:
                raise UnsafeFileError("Tệp Word thiếu nội dung chính.") from None
            return b""
        if info.file_size > MAX_XML_BYTES:
            raise UnsafeFileError("Nội dung Word quá lớn.")
        if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
            raise UnsafeFileError("Tệp có tỷ lệ nén bất thường.")
        content = zf.read(name)
        head = content[:4096].upper()
        if b"<!DOCTYPE" in head or b"<!ENTITY" in content.upper():
            raise UnsafeFileError("Tệp chứa khai báo XML không được phép.")
        return content

    document = read_part("word/document.xml", required=True)
    rels = read_part("word/_rels/document.xml.rels", required=False)
    return document, rels, zf.namelist(), zf
