#!/usr/bin/env python3
"""Update a YouTrack Knowledge Base article from a local markdown file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from youtrack_peristalsis.knowledge_base import KnowledgeBaseSync


def main() -> int:
    parser = argparse.ArgumentParser(
        description="로컬 md 파일 내용으로 YouTrack 기술 자료 문서를 수정합니다.",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Markdown file path (with YAML frontmatter containing id_readable)",
    )
    parser.add_argument(
        "--article-id",
        help="Article idReadable (e.g. XAC-A-171). Overrides frontmatter id_readable.",
    )
    args = parser.parse_args()

    if not args.file.is_file():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    sync = KnowledgeBaseSync()
    updated = sync.update_article(
        args.file,
        article_id=args.article_id,
    )
    print(json.dumps(updated, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
