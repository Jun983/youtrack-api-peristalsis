#!/usr/bin/env python3
"""Create a YouTrack Knowledge Base article from a local markdown file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from youtrack_peristalsis.knowledge_base import KnowledgeBaseSync


def main() -> int:
    parser = argparse.ArgumentParser(
        description="로컬 md 파일 내용으로 YouTrack 기술 자료 문서를 작성합니다.",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Markdown file path (with YAML frontmatter)",
    )
    parser.add_argument(
        "-p",
        "--project",
        help="Project shortName (overrides frontmatter / YOUTRACK_PROJECT)",
    )
    parser.add_argument(
        "--parent",
        help="Parent article idReadable (overrides frontmatter / YOUTRACK_PARENT_ARTICLE)",
    )
    args = parser.parse_args()

    if not args.file.is_file():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    sync = KnowledgeBaseSync()
    created = sync.push_article(
        args.file,
        project_short_name=args.project,
        parent_article_id=args.parent,
    )
    print(json.dumps(created, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
