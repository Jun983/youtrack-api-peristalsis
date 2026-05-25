import pytest


@pytest.fixture
def sample_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOUTRACK_BASE_URL", "https://example.youtrack.cloud")
    monkeypatch.setenv("YOUTRACK_TOKEN", "perm:test-token")
    monkeypatch.setenv("YOUTRACK_DOCS_DIR", "/tmp/youtrack-docs-test")
