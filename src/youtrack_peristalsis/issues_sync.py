"""Sync YouTrack issues with local markdown files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.client.issues import IssuesClient
from youtrack_peristalsis.config import Settings
from youtrack_peristalsis.issue_format import IssueMarkdown, read_issue_file, write_issue_file
from youtrack_peristalsis.issues import resolve_issue_id


def issue_to_markdown(issue: dict[str, Any]) -> IssueMarkdown:
    project = issue.get("project") or {}
    state = issue.get("state") or {}
    assignee = issue.get("assignee") or {}
    priority = issue.get("priority") or {}
    issue_type = issue.get("type") or {}
    return IssueMarkdown(
        summary=issue.get("summary") or "",
        description=issue.get("description") or "",
        id_readable=issue.get("idReadable"),
        issue_id=issue.get("id"),
        project=project.get("shortName"),
        state=state.get("name"),
        assignee=assignee.get("name"),
        priority=priority.get("name"),
        issue_type=issue_type.get("name"),
    )


def resolve_output_path(issue: dict[str, Any], output: Path) -> Path:
    if output.is_dir():
        id_readable = issue.get("idReadable") or issue.get("id")
        if not id_readable:
            raise ValueError("Issue has no idReadable or id for default filename")
        return output / f"{id_readable}.md"
    return output


class IssueSync:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def resolve_issue_id(self, issue_id: str) -> str:
        return resolve_issue_id(issue_id, self._settings.issue_prefix)

    def pull_issue(self, issue_id: str, *, output: Path) -> Path:
        """Fetch a YouTrack issue and save it as a markdown file."""
        resolved_id = self.resolve_issue_id(issue_id)
        with YouTrackClient(self._settings) as http:
            issues = IssuesClient(http)
            issue = issues.get(resolved_id)

        md = issue_to_markdown(issue)
        path = resolve_output_path(issue=issue, output=output)
        write_issue_file(path, md)
        return path

    def pull_all(self, *, query: str | None = None, output_dir: Path) -> list[Path]:
        """Fetch all YouTrack issues matching the query and save as markdown files."""
        if query is None and self._settings.issue_prefix:
            query = f"project: {self._settings.issue_prefix}"

        with YouTrackClient(self._settings) as http:
            issues = IssuesClient(http)
            all_issues = issues.list(query=query)

        paths: list[Path] = []
        for issue in all_issues:
            md = issue_to_markdown(issue)
            path = resolve_output_path(issue=issue, output=output_dir)
            write_issue_file(path, md)
            paths.append(path)
        return paths

    def create_issue(
        self,
        file_path: Path,
        *,
        project_short_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a YouTrack issue from a local markdown file."""
        md = read_issue_file(file_path)
        project = project_short_name or md.project or self._settings.default_issue_project
        if not project:
            raise ValueError(
                "Project short name is required. Set YOUTRACK_ISSUE_PROJECT or "
                "'project' in markdown frontmatter."
            )

        with YouTrackClient(self._settings) as http:
            issues = IssuesClient(http)
            return issues.create(
                project_short_name=project,
                summary=md.summary,
                description=md.description,
            )

    def update_issue(
        self,
        file_path: Path,
        *,
        issue_id: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing YouTrack issue from a local markdown file."""
        md = read_issue_file(file_path)

        resolved_id = issue_id or md.id_readable
        if not resolved_id:
            raise ValueError(
                "Issue ID is required. Set 'id_readable' in markdown frontmatter "
                "or pass --issue-id argument."
            )

        resolved_id = self.resolve_issue_id(resolved_id)

        with YouTrackClient(self._settings) as http:
            issues = IssuesClient(http)
            return issues.update(
                resolved_id,
                summary=md.summary,
                description=md.description,
            )
