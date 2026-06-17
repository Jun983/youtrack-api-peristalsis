"""Issue local file format — YAML frontmatter + Markdown body."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class IssueMarkdown:
    summary: str
    description: str
    id_readable: str | None = None
    issue_id: str | None = None
    project: str | None = None
    state: str | None = None
    assignee: str | None = None
    priority: str | None = None
    issue_type: str | None = None
    comments: tuple[dict[str, Any], ...] = field(default_factory=tuple)

    def to_markdown(self) -> str:
        """Serialize to YAML frontmatter + Markdown body string."""
        meta: dict = {"summary": self.summary}
        if self.id_readable is not None:
            meta["id_readable"] = self.id_readable
        if self.issue_id is not None:
            meta["issue_id"] = self.issue_id
        if self.project is not None:
            meta["project"] = self.project
        if self.state is not None:
            meta["state"] = self.state
        if self.assignee is not None:
            meta["assignee"] = self.assignee
        if self.priority is not None:
            meta["priority"] = self.priority
        if self.issue_type is not None:
            meta["type"] = self.issue_type
        frontmatter = yaml.dump(meta, allow_unicode=True, sort_keys=False).rstrip()
        body = f"---\n{frontmatter}\n---\n\n{self.description}"
        if self.comments:
            body += "\n\n---\n\n## 코멘트\n\n"
            for comment in self.comments:
                author = (comment.get("author") or {}).get("name", "알 수 없음")
                created_ms = comment.get("created")
                if created_ms:
                    dt = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                else:
                    dt = ""
                text = comment.get("text") or ""
                body += f"**{author}** · {dt}\n\n{text}\n\n---\n\n"
        return body

    @classmethod
    def from_markdown(cls, text: str) -> "IssueMarkdown":
        """Parse YAML frontmatter + Markdown body into IssueMarkdown."""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                meta = yaml.safe_load(parts[1]) or {}
                description = parts[2].lstrip("\n")
                return cls(
                    summary=meta.get("summary", ""),
                    description=description,
                    id_readable=meta.get("id_readable"),
                    issue_id=meta.get("issue_id"),
                    project=meta.get("project"),
                    state=meta.get("state"),
                    assignee=meta.get("assignee"),
                    priority=meta.get("priority"),
                    issue_type=meta.get("type"),
                )
        return cls(summary="", description=text)


def read_issue_file(path: Path) -> IssueMarkdown:
    return IssueMarkdown.from_markdown(path.read_text(encoding="utf-8"))


def write_issue_file(path: Path, issue: IssueMarkdown) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(issue.to_markdown(), encoding="utf-8")
