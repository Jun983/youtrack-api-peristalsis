import pytest

from youtrack_peristalsis.articles import resolve_article_id


@pytest.mark.parametrize(
    ("article_id", "prefix", "expected"),
    [
        ("13", "XAC", "XAC-A-13"),
        ("XAC-13", "XAC", "XAC-A-13"),
        ("xac-13", "XAC", "XAC-A-13"),
        ("NP-A-1", None, "NP-A-1"),
        ("226-0", "XAC", "226-0"),
        ("NP-A-1", "XAC", "NP-A-1"),
    ],
)
def test_resolve_article_id(article_id: str, prefix: str | None, expected: str) -> None:
    assert resolve_article_id(article_id, prefix) == expected


def test_pull_resolves_prefix(tmp_path, sample_settings: None, monkeypatch) -> None:
    monkeypatch.setenv("YOUTRACK_ARTICLE_PREFIX", "XAC")
    from unittest.mock import MagicMock, patch

    from youtrack_peristalsis.knowledge_base import KnowledgeBaseSync

    mock_get = MagicMock(return_value={"idReadable": "XAC-13", "summary": "T", "content": ""})
    with patch("youtrack_peristalsis.knowledge_base.ArticlesClient") as client_cls:
        client_cls.return_value.get = mock_get
        with patch("youtrack_peristalsis.knowledge_base.YouTrackClient"):
            KnowledgeBaseSync().pull_article("13", output=tmp_path / "XAC-13.md")

    mock_get.assert_called_once_with("XAC-A-13")
