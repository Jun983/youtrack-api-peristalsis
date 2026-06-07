"""YouTrack 이슈 목록을 조회해 로컬 마크다운 파일로 저장한다."""

import argparse
from pathlib import Path

from youtrack_peristalsis.issues_sync import IssueSync


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull all YouTrack issues")
    parser.add_argument(
        "--query",
        "-q",
        default=None,
        help="YouTrack issue query (default: project filter from YOUTRACK_ISSUE_PREFIX)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Output directory (default: current directory)",
    )
    args = parser.parse_args()

    sync = IssueSync()
    paths = sync.pull_all(query=args.query, output_dir=Path(args.output_dir))
    print(f"Saved {len(paths)} issue(s):")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
