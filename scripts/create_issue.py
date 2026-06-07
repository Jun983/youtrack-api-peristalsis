"""로컬 마크다운 파일로부터 YouTrack 이슈를 생성한다."""

import argparse
import json
from pathlib import Path

from youtrack_peristalsis.issues_sync import IssueSync


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a YouTrack issue from a markdown file")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument(
        "--project",
        "-p",
        default=None,
        help="Project shortName (overrides frontmatter and YOUTRACK_ISSUE_PROJECT)",
    )
    args = parser.parse_args()

    sync = IssueSync()
    result = sync.create_issue(Path(args.file), project_short_name=args.project)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
