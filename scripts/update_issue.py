"""로컬 마크다운 파일로부터 YouTrack 이슈를 수정한다."""

import argparse
import json
from pathlib import Path

from youtrack_peristalsis.issues_sync import IssueSync


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a YouTrack issue from a markdown file")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument(
        "--issue-id",
        default=None,
        help="Issue id (overrides frontmatter id_readable)",
    )
    args = parser.parse_args()

    sync = IssueSync()
    result = sync.update_issue(Path(args.file), issue_id=args.issue_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
