"""단일 YouTrack 이슈를 조회해 로컬 마크다운 파일로 저장한다."""

import argparse
from pathlib import Path

from youtrack_peristalsis.issues_sync import IssueSync


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull a single YouTrack issue")
    parser.add_argument("issue_id", help="Issue id (e.g. XAC-42, 42)")
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output file or directory (default: current directory)",
    )
    parser.add_argument(
        "--with-comments",
        action="store_true",
        help="Include issue comments in the output",
    )
    args = parser.parse_args()

    sync = IssueSync()
    path = sync.pull_issue(args.issue_id, output=Path(args.output), with_comments=args.with_comments)
    print(f"Saved: {path}")


if __name__ == "__main__":
    main()
