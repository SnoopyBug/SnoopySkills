#!/usr/bin/env python3
"""
Read text from a PDF file and print plain text to stdout.

Usage:
  python .\skills\paper-survey\scripts\read_pdf_text.py --pdf "D:\path\paper.pdf"
"""

from __future__ import annotations

import argparse
import os
import sys


def _load_reader(pdf_path: str):
    try:
        from pypdf import PdfReader  # type: ignore

        return PdfReader(pdf_path), "pypdf"
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore

            return PdfReader(pdf_path), "PyPDF2"
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency: install one of these packages first:\n"
                "  pip install pypdf\n"
                "or\n"
                "  pip install PyPDF2"
            ) from exc


def extract_text(pdf_path: str, max_chars: int) -> str:
    reader, backend = _load_reader(pdf_path)
    chunks: list[str] = []

    for idx, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            page_text = f"\n[WARN] Failed to extract page {idx}: {exc}\n"
        chunks.append(f"\n\n===== PAGE {idx} =====\n{page_text}")

        if max_chars > 0 and sum(len(c) for c in chunks) >= max_chars:
            break

    text = "".join(chunks)
    if max_chars > 0:
        text = text[:max_chars]

    header = (
        f"[INFO] backend={backend}\n"
        f"[INFO] file={pdf_path}\n"
        f"[INFO] pages_read={min(len(reader.pages), len(chunks))}/{len(reader.pages)}\n"
    )
    return header + text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text from a PDF file.")
    parser.add_argument("--pdf", required=True, help="Absolute or relative PDF path.")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=300000,
        help="Maximum number of characters in output (default: 300000, <=0 means unlimited).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = os.path.abspath(args.pdf)

    if not os.path.isfile(pdf_path):
        print(f"[ERROR] PDF not found: {pdf_path}", file=sys.stderr)
        return 1
    if not pdf_path.lower().endswith(".pdf"):
        print(f"[ERROR] Input is not a .pdf file: {pdf_path}", file=sys.stderr)
        return 1

    try:
        text = extract_text(pdf_path, args.max_chars)
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[ERROR] Failed to read PDF: {exc}", file=sys.stderr)
        return 3

    if len(text.strip()) < 200:
        print(
            "[WARN] Extracted text is very short. The PDF may be scanned/image-based. "
            "Consider OCR before analysis.",
            file=sys.stderr,
        )

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
