"""Chạy thử: python -m app.modules.exams.imports.readers <tệp> [--json] [--verbose]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import read_exam
from .model import plain


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Đọc thử một tệp đề.")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true", help="in toàn bộ kết quả dạng JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="in cả đề và phương án")
    args = parser.parse_args()

    path = Path(args.path)
    doc = read_exam(path.read_bytes(), path.name)
    if args.json:
        print(json.dumps(doc.to_dict(), ensure_ascii=False, indent=2))
        return 0

    print(f"{doc.source_name}  [{doc.format}]  {doc.summary()}")
    for flag in doc.flags:
        print(f"  ! tài liệu [{flag.severity}] {flag.code}: {flag.message}")
    for section in doc.sections:
        declared = f"{section.declared_first}-{section.declared_last}" if section.declared_first else "?"
        print(f"\n== {section.title[:90]}  (loại={section.kind}, đề ghi={declared}, đọc được={len(section.questions)})")
        for flag in section.flags:
            print(f"   ! phần [{flag.severity}] {flag.code}: {flag.message}")
        for q in section.questions:
            ans = q.answer
            value = ans.value if not isinstance(ans.value, dict) else "".join(k if v else k.upper() + "✗" for k, v in ans.value.items())
            opts = "".join(q.options) or "-"
            where = f" tr{q.page}" if q.page else ""
            print(f"  Câu {q.number:>2}{where} {q.kind:15} opts={opts:4} đáp án={ans.status}:{value} ({'+'.join(ans.sources) or '-'})")
            if args.verbose:
                print(f"      đề: {plain(q.stem)[:110]}")
                for label, blocks in q.options.items():
                    print(f"      {label}: {plain(blocks)[:80]}")
            for flag in q.flags:
                if flag.severity == "error" or args.verbose:
                    print(f"      ! [{flag.severity}] {flag.code}: {flag.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
