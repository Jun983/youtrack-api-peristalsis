"""Markdown file format with YAML frontmatter for article sync."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_KV_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


@dataclass(frozen=True)
class ArticleMarkdown:
    summary: str
    content: str
    id_readable: str | None = None
    article_id: str | None = None
    project: str | None = None
    parent_article: str | None = None

    def to_text(self) -> str:
        lines = ["---"]
        if self.id_readable:
            lines.append(f"id_readable: {self.id_readable}")
        if self.article_id:
            lines.append(f"article_id: {self.article_id}")
        if self.project:
            lines.append(f"project: {self.project}")
        if self.parent_article:
            lines.append(f"parent_article: {self.parent_article}")
        lines.append(f"summary: {self._escape_yaml(self.summary)}")
        lines.append("---")
        parts = ["\n".join(lines), "", self.content]
        return "\n".join(parts)

    @staticmethod
    def _escape_yaml(value: str) -> str:
        if any(c in value for c in ':"\\#\n'):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return value


def parse_article_markdown(text: str) -> ArticleMarkdown:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("Markdown file must start with YAML frontmatter (--- ... ---)")

    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line:
            continue
        kv = _KV_RE.match(line)
        if not kv:
            raise ValueError(f"Invalid frontmatter line: {line}")
        key, value = kv.group(1), kv.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        meta[key] = value

    summary = meta.get("summary")
    if not summary:
        raise ValueError("Frontmatter must include 'summary' (article title)")

    content = text[match.end() :]
    if content.startswith("\n"):
        content = content[1:]

    return ArticleMarkdown(
        summary=summary,
        content=content,
        id_readable=meta.get("id_readable"),
        article_id=meta.get("article_id"),
        project=meta.get("project"),
        parent_article=meta.get("parent_article"),
    )


def read_article_file(path: Path) -> ArticleMarkdown:
    return parse_article_markdown(path.read_text(encoding="utf-8"))


def write_article_file(path: Path, article: ArticleMarkdown) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(article.to_text(), encoding="utf-8")
    return path
