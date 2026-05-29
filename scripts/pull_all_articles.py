#!/usr/bin/env python3
"""Pull all YouTrack Knowledge Base articles to local markdown files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from youtrack_peristalsis.knowledge_base import KnowledgeBaseSync


def main() -> int:
    parser = argparse.ArgumentParser(
        description="YouTrack 기술 자료 문서를 전부 조회해 로컬 md 파일로 저장합니다.",
    )
    parser.add_argument(
        "-q",
        "--query",
        help="YouTrack query string (default: project: {YOUTRACK_ARTICLE_PREFIX})",
    )
    parser.add_argument(
        "-d",
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory (required)",
    )
    args = parser.parse_args()

    sync = KnowledgeBaseSync()
    paths = sync.pull_all(query=args.query, output_dir=args.output_dir)
    for path in paths:
        print(f"Saved: {path}")
    print(f"\n총 {len(paths)}개 문서 저장 완료")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
