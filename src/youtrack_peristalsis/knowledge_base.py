"""Sync YouTrack Knowledge Base (기술 자료) articles with local markdown files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from youtrack_peristalsis.articles import resolve_article_id
from youtrack_peristalsis.client.articles import ArticlesClient
from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.config import Settings
from youtrack_peristalsis.md_format import ArticleMarkdown, read_article_file, write_article_file


def article_to_markdown(article: dict[str, Any]) -> ArticleMarkdown:
    project = article.get("project") or {}
    parent = article.get("parentArticle")
    return ArticleMarkdown(
        summary=article.get("summary") or "",
        content=article.get("content") or "",
        id_readable=article.get("idReadable"),
        article_id=article.get("id"),
        project=project.get("shortName"),
        parent_article=parent.get("idReadable") if parent else None,
    )


def resolve_output_path(
    docs_dir: Path,
    article: dict[str, Any],
    output: Path | None = None,
) -> Path:
    if output is not None:
        return output
    id_readable = article.get("idReadable") or article.get("id")
    if not id_readable:
        raise ValueError("Article has no idReadable or id for default filename")
    return docs_dir / f"{id_readable}.md"


class KnowledgeBaseSync:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    def resolve_article_id(self, article_id: str) -> str:
        return resolve_article_id(article_id, self._settings.article_prefix)

    def pull_article(
        self,
        article_id: str,
        *,
        output: Path | None = None,
    ) -> Path:
        """Fetch a YouTrack article and save it as a markdown file."""
        resolved_id = self.resolve_article_id(article_id)
        with YouTrackClient(self._settings) as http:
            articles = ArticlesClient(http)
            article = articles.get(resolved_id)

        md = article_to_markdown(article)
        path = resolve_output_path(self._settings.docs_dir, article, output)
        write_article_file(path, md)
        return path

    def push_article(
        self,
        file_path: Path,
        *,
        project_short_name: str | None = None,
        parent_article_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a YouTrack article from a local markdown file."""
        md = read_article_file(file_path)
        project = (
            project_short_name
            or md.project
            or self._settings.default_project
            or self._settings.article_prefix
        )
        if not project:
            raise ValueError(
                "Project short name is required. Set YOUTRACK_PROJECT or "
                "'project' in markdown frontmatter."
            )

        parent = parent_article_id or md.parent_article or self._settings.default_parent_article

        with YouTrackClient(self._settings) as http:
            articles = ArticlesClient(http)
            return articles.create(
                project_short_name=project,
                summary=md.summary,
                content=md.content,
                parent_article_id=parent,
            )

    def update_article(
        self,
        file_path: Path,
        *,
        article_id: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing YouTrack article from a local markdown file."""
        md = read_article_file(file_path)

        resolved_id = article_id or md.id_readable
        if not resolved_id:
            raise ValueError(
                "Article ID is required. Set 'id_readable' in markdown frontmatter "
                "or pass --article-id argument."
            )

        resolved_id = self.resolve_article_id(resolved_id)

        with YouTrackClient(self._settings) as http:
            articles = ArticlesClient(http)
            return articles.update(
                resolved_id,
                summary=md.summary,
                content=md.content,
            )
