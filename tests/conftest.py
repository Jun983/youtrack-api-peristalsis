import pytest


@pytest.fixture
def sample_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTRACK_BASE_URL", "https://example.youtrack.cloud")
    monkeypatch.setenv("YOUTRACK_TOKEN", "perm:test-token")
    monkeypatch.delenv("YOUTRACK_PROJECT", raising=False)
    monkeypatch.delenv("YOUTRACK_ARTICLE_PREFIX", raising=False)
    monkeypatch.delenv("YOUTRACK_PARENT_ARTICLE", raising=False)
