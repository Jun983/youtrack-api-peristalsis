#!/usr/bin/env python3
"""Pull a YouTrack Knowledge Base article to a local markdown file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from youtrack_peristalsis.knowledge_base import KnowledgeBaseSync


def main() -> int:
    parser = argparse.ArgumentParser(
        description="YouTrack 기술 자료 문서를 조회해 로컬 md 파일로 저장합니다.",
    )
    parser.add_argument(
        "article_id",
        help="Article ID or number (e.g. 13 → XAC-A-13, XAC-13 → XAC-A-13, or full XAC-A-13)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: {YOUTRACK_DOCS_DIR}/{idReadable}.md)",
    )
    args = parser.parse_args()

    sync = KnowledgeBaseSync()
    path = sync.pull_article(args.article_id, output=args.output)
    print(f"Saved: {path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
