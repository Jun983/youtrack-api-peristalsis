from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from youtrack_peristalsis.knowledge_base import KnowledgeBaseSync, article_to_markdown
from youtrack_peristalsis.md_format import ArticleMarkdown, write_article_file

SAMPLE_ARTICLE = {
    "id": "226-0",
    "idReadable": "NP-A-1",
    "summary": "Getting Started",
    "content": "## Intro\n\nHello.",
    "project": {"shortName": "NP", "$type": "Project"},
    "parentArticle": {"idReadable": "NP-A-7", "$type": "Article"},
}


def test_article_to_markdown() -> None:
    md = article_to_markdown(SAMPLE_ARTICLE)
    assert md.summary == "Getting Started"
    assert md.id_readable == "NP-A-1"
    assert md.project == "NP"
    assert md.parent_article == "NP-A-7"


def test_pull_article(tmp_path: Path, sample_settings: None, monkeypatch) -> None:
    monkeypatch.setenv("YOUTRACK_DOCS_DIR", str(tmp_path))
    mock_get = MagicMock(return_value=SAMPLE_ARTICLE)

    with patch("youtrack_peristalsis.knowledge_base.ArticlesClient") as client_cls:
        client_cls.return_value.get = mock_get
        with patch("youtrack_peristalsis.knowledge_base.YouTrackClient"):
            path = KnowledgeBaseSync().pull_article("NP-A-1")

    assert path == tmp_path / "NP-A-1.md"
    assert path.read_text(encoding="utf-8").startswith("---")
    mock_get.assert_called_once_with("NP-A-1")


def test_push_article_requires_project(tmp_path: Path, sample_settings: None) -> None:
    file_path = tmp_path / "new.md"
    write_article_file(
        file_path,
        ArticleMarkdown(summary="New Doc", content="Content only."),
    )
    with pytest.raises(ValueError, match="Project"):
        KnowledgeBaseSync().push_article(file_path)


def test_push_article_creates(tmp_path: Path, sample_settings: None, monkeypatch) -> None:
    monkeypatch.setenv("YOUTRACK_PROJECT", "NP")
    file_path = tmp_path / "new.md"
    write_article_file(
        file_path,
        ArticleMarkdown(summary="New Doc", content="Body."),
    )
    created = {
        "id": "226-99",
        "idReadable": "NP-A-99",
        "summary": "New Doc",
        "content": "Body.",
    }
    mock_create = MagicMock(return_value=created)

    with patch("youtrack_peristalsis.knowledge_base.ArticlesClient") as client_cls:
        client_cls.return_value.create = mock_create
        with patch("youtrack_peristalsis.knowledge_base.YouTrackClient"):
            result = KnowledgeBaseSync().push_article(file_path)

    assert result["idReadable"] == "NP-A-99"
    mock_create.assert_called_once_with(
        project_short_name="NP",
        summary="New Doc",
        content="Body.",
        parent_article_id=None,
    )
