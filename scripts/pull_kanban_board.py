"""칸반보드 이슈(미완료 상태)를 코멘트 포함해 로컬 마크다운 파일로 저장한다."""

import argparse
from pathlib import Path

from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.client.issues import IssuesClient
from youtrack_peristalsis.config import Settings
from youtrack_peristalsis.issues_sync import issue_to_markdown, resolve_output_path
from youtrack_peristalsis.issue_format import write_issue_file

KANBAN_QUERY = "project: XAC #Unresolved"


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull kanban board issues with comments")
    parser.add_argument(
        "--query",
        "-q",
        default=KANBAN_QUERY,
        help=f"YouTrack query (default: {KANBAN_QUERY!r})",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default=".",
        help="Output directory (default: current directory)",
    )
    args = parser.parse_args()

    settings = Settings()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with YouTrackClient(settings) as http:
        issues_client = IssuesClient(http)
        all_issues = issues_client.list(query=args.query)
        print(f"Found {len(all_issues)} issue(s). Fetching comments...")

        paths: list[Path] = []
        for issue in all_issues:
            issue_id = issue.get("idReadable") or issue.get("id")
            try:
                comments = issues_client.list_comments(issue_id)
            except Exception as e:
                print(f"  Warning: failed to fetch comments for {issue_id}: {e}")
                comments = []

            md = issue_to_markdown(issue, comments=comments)
            path = resolve_output_path(issue=issue, output=output_dir)
            write_issue_file(path, md)
            paths.append(path)
            print(f"  Saved: {path} ({len(comments)} comment(s))")

    print(f"\nDone. Saved {len(paths)} issue(s) to {output_dir}")


if __name__ == "__main__":
    main()
