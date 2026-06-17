from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from youtrack_peristalsis.config import Settings
from youtrack_peristalsis.issue_format import IssueMarkdown, write_issue_file
from youtrack_peristalsis.issues_sync import IssueSync, issue_to_markdown

SAMPLE_COMMENTS = [
    {
        "id": "4-1",
        "text": "This is a comment.",
        "created": 1700000000000,
        "updated": 1700000000000,
        "author": {"id": "1-1", "name": "Alice"},
    },
]

SAMPLE_ISSUE = {
    "id": "2-42",
    "idReadable": "XAC-42",
    "summary": "Fix login bug",
    "description": "Login fails when password contains special chars.",
    "project": {"shortName": "XAC", "$type": "Project"},
    "state": {"name": "Open"},
    "assignee": {"name": "Alice"},
    "priority": {"name": "Normal"},
    "type": {"name": "Bug"},
}

SAMPLE_ISSUE_2 = {
    "id": "2-43",
    "idReadable": "XAC-43",
    "summary": "Add dark mode",
    "description": "Support dark mode in UI.",
    "project": {"shortName": "XAC", "$type": "Project"},
    "state": {"name": "Open"},
    "assignee": None,
    "priority": {"name": "Normal"},
    "type": {"name": "Feature"},
}


def _make_settings(**kwargs) -> Settings:
    return Settings(
        youtrack_base_url="https://example.youtrack.cloud",
        youtrack_token="perm:test-token",
        _env_file=None,
        **kwargs,
    )


def test_issue_to_markdown() -> None:
    md = issue_to_markdown(SAMPLE_ISSUE)
    assert md.summary == "Fix login bug"
    assert md.id_readable == "XAC-42"
    assert md.project == "XAC"
    assert md.state == "Open"
    assert md.assignee == "Alice"
    assert md.priority == "Normal"
    assert md.issue_type == "Bug"


def test_pull_issue(tmp_path: Path, sample_settings: None) -> None:
    mock_get = MagicMock(return_value=SAMPLE_ISSUE)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.get = mock_get
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            path = IssueSync().pull_issue("XAC-42", output=tmp_path / "issue.md")

    assert path == tmp_path / "issue.md"
    assert path.read_text(encoding="utf-8").startswith("---")
    mock_get.assert_called_once_with("XAC-42")


def test_pull_issue_saves_to_dir(tmp_path: Path, sample_settings: None) -> None:
    mock_get = MagicMock(return_value=SAMPLE_ISSUE)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.get = mock_get
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            path = IssueSync().pull_issue("XAC-42", output=tmp_path)

    assert path == tmp_path / "XAC-42.md"
    assert path.exists()


def test_pull_all(tmp_path: Path, sample_settings: None) -> None:
    mock_list = MagicMock(return_value=[SAMPLE_ISSUE, SAMPLE_ISSUE_2])

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.list = mock_list
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            paths = IssueSync().pull_all(output_dir=tmp_path)

    assert len(paths) == 2
    assert tmp_path / "XAC-42.md" in paths
    assert tmp_path / "XAC-43.md" in paths
    mock_list.assert_called_once_with(query=None)


def test_pull_all_with_query(tmp_path: Path, sample_settings: None) -> None:
    mock_list = MagicMock(return_value=[SAMPLE_ISSUE])

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.list = mock_list
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            IssueSync().pull_all(query="project: XAC", output_dir=tmp_path)

    mock_list.assert_called_once_with(query="project: XAC")


def test_create_issue(tmp_path: Path, sample_settings: None, monkeypatch) -> None:
    monkeypatch.setenv("YOUTRACK_ISSUE_PROJECT", "XAC")
    file_path = tmp_path / "new_issue.md"
    write_issue_file(
        file_path,
        IssueMarkdown(summary="Fix login bug", description="Login fails."),
    )
    created = {
        "id": "2-99",
        "idReadable": "XAC-99",
        "summary": "Fix login bug",
        "description": "Login fails.",
    }
    mock_create = MagicMock(return_value=created)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.create = mock_create
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            result = IssueSync().create_issue(file_path)

    assert result["idReadable"] == "XAC-99"
    mock_create.assert_called_once_with(
        project_short_name="XAC",
        summary="Fix login bug",
        description="Login fails.",
    )


def test_create_issue_with_project_arg(tmp_path: Path, sample_settings: None) -> None:
    file_path = tmp_path / "new_issue.md"
    write_issue_file(
        file_path,
        IssueMarkdown(summary="New feature", description="Description here."),
    )
    created = {"id": "2-100", "idReadable": "XAC-100", "summary": "New feature"}
    mock_create = MagicMock(return_value=created)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.create = mock_create
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            result = IssueSync().create_issue(file_path, project_short_name="XAC")

    assert result["idReadable"] == "XAC-100"
    mock_create.assert_called_once_with(
        project_short_name="XAC",
        summary="New feature",
        description="Description here.",
    )


def test_create_issue_requires_project(tmp_path: Path) -> None:
    settings = _make_settings()
    file_path = tmp_path / "new_issue.md"
    write_issue_file(
        file_path,
        IssueMarkdown(summary="Fix bug", description="Body."),
    )
    with pytest.raises(ValueError, match="Project"):
        IssueSync(settings=settings).create_issue(file_path)


def test_update_issue(tmp_path: Path, sample_settings: None) -> None:
    file_path = tmp_path / "existing_issue.md"
    write_issue_file(
        file_path,
        IssueMarkdown(
            summary="Updated summary",
            description="Updated description.",
            id_readable="XAC-42",
        ),
    )
    updated = {**SAMPLE_ISSUE, "summary": "Updated summary"}
    mock_update = MagicMock(return_value=updated)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.update = mock_update
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            result = IssueSync().update_issue(file_path)

    assert result["summary"] == "Updated summary"
    mock_update.assert_called_once_with(
        "XAC-42",
        summary="Updated summary",
        description="Updated description.",
    )


def test_update_issue_with_id_arg(tmp_path: Path, sample_settings: None) -> None:
    file_path = tmp_path / "existing_issue.md"
    write_issue_file(
        file_path,
        IssueMarkdown(summary="Updated summary", description="Updated description."),
    )
    updated = {**SAMPLE_ISSUE, "summary": "Updated summary"}
    mock_update = MagicMock(return_value=updated)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.update = mock_update
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            result = IssueSync().update_issue(file_path, issue_id="XAC-42")

    mock_update.assert_called_once_with(
        "XAC-42",
        summary="Updated summary",
        description="Updated description.",
    )


def test_pull_issue_with_comments(tmp_path: Path, sample_settings: None) -> None:
    mock_get = MagicMock(return_value=SAMPLE_ISSUE)
    mock_list_comments = MagicMock(return_value=SAMPLE_COMMENTS)

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.get = mock_get
        client_cls.return_value.list_comments = mock_list_comments
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            path = IssueSync().pull_issue("XAC-42", output=tmp_path, with_comments=True)

    assert path == tmp_path / "XAC-42.md"
    content = path.read_text(encoding="utf-8")
    assert "## 코멘트" in content
    assert "Alice" in content
    assert "This is a comment." in content
    mock_list_comments.assert_called_once_with("XAC-42")


def test_pull_issue_without_comments_by_default(tmp_path: Path, sample_settings: None) -> None:
    mock_get = MagicMock(return_value=SAMPLE_ISSUE)
    mock_list_comments = MagicMock()

    with patch("youtrack_peristalsis.issues_sync.IssuesClient") as client_cls:
        client_cls.return_value.get = mock_get
        client_cls.return_value.list_comments = mock_list_comments
        with patch("youtrack_peristalsis.issues_sync.YouTrackClient"):
            path = IssueSync().pull_issue("XAC-42", output=tmp_path)

    content = path.read_text(encoding="utf-8")
    assert "## 코멘트" not in content
    mock_list_comments.assert_not_called()


def test_update_issue_requires_id(tmp_path: Path) -> None:
    settings = _make_settings()
    file_path = tmp_path / "issue_no_id.md"
    write_issue_file(
        file_path,
        IssueMarkdown(summary="Fix bug", description="Body."),
    )
    with pytest.raises(ValueError, match="Issue ID"):
        IssueSync(settings=settings).update_issue(file_path)
