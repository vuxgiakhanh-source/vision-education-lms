"""Mã biên nhận và băm nội dung bài nộp."""

from __future__ import annotations

import hashlib
import json
import secrets

# Bỏ 0/O, 1/I/L, U để học sinh đọc mã qua điện thoại hoặc viết tay không nhầm.
RECEIPT_ALPHABET = "ABCDEFGHJKMNPQRSTVWXYZ23456789"
RECEIPT_LENGTH = 10


def new_receipt_code() -> str:
    """Sinh mã bằng `secrets` (không đoán trước được). Tính duy nhất do UNIQUE(receipt_code) bảo đảm."""
    return "".join(secrets.choice(RECEIPT_ALPHABET) for _ in range(RECEIPT_LENGTH))


def content_digest(answers: dict) -> str:
    """SHA-256 của đáp án ở dạng chuẩn hóa (không phụ thuộc thứ tự khóa), để em chứng minh mình đã nộp gì."""
    canonical = json.dumps(answers, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
