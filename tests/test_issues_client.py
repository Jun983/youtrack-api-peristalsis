import httpx
import pytest

from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.client.issues import IssuesClient
from youtrack_peristalsis.exceptions import YouTrackAPIError

SAMPLE_ISSUE = {
    "id": "2-42",
    "idReadable": "XAC-42",
    "summary": "Fix login bug",
    "description": "Login fails when password contains special chars.",
    "project": {"shortName": "XAC"},
    "state": {"name": "Open"},
    "assignee": {"name": "Alice"},
    "priority": {"name": "Normal"},
    "type": {"name": "Bug"},
}


def _make_client(handler) -> tuple[YouTrackClient, IssuesClient]:
    transport = httpx.MockTransport(handler)
    base = YouTrackClient()
    base._client = httpx.Client(
        base_url=base._settings.api_base,
        transport=transport,
        headers=base._client.headers,
    )
    return base, IssuesClient(base)


def test_get_issue(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/api/issues/XAC-42")
        assert "fields" in str(request.url)
        return httpx.Response(200, json=SAMPLE_ISSUE)

    base, client = _make_client(handler)
    with base:
        issue = client.get("XAC-42")

    assert issue["idReadable"] == "XAC-42"
    assert issue["summary"] == "Fix login bug"


def test_list_issues_single_page(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/api/issues")
        assert "fields" in str(request.url)
        return httpx.Response(200, json=[SAMPLE_ISSUE])

    base, client = _make_client(handler)
    with base:
        issues = client.list()

    assert len(issues) == 1
    assert issues[0]["idReadable"] == "XAC-42"


def test_list_issues_pagination(sample_settings: None) -> None:
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        # 첫 번째 요청: top=2 개 반환 (다음 페이지 존재)
        # 두 번째 요청: 0개 반환 (종료)
        if call_count == 1:
            return httpx.Response(200, json=[SAMPLE_ISSUE, SAMPLE_ISSUE])
        return httpx.Response(200, json=[])

    base, client = _make_client(handler)
    with base:
        issues = client.list(top=2)

    assert len(issues) == 2
    assert call_count == 2


def test_create_issue(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/api/issues")
        assert request.method == "POST"
        import json
        body = json.loads(request.content)
        assert body["project"]["shortName"] == "XAC"
        assert body["summary"] == "Fix login bug"
        assert body["description"] == "Login fails when password contains special chars."
        return httpx.Response(200, json=SAMPLE_ISSUE)

    base, client = _make_client(handler)
    with base:
        result = client.create(
            project_short_name="XAC",
            summary="Fix login bug",
            description="Login fails when password contains special chars.",
        )

    assert result["idReadable"] == "XAC-42"


def test_create_issue_without_description(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        import json
        body = json.loads(request.content)
        assert "description" not in body
        return httpx.Response(200, json=SAMPLE_ISSUE)

    base, client = _make_client(handler)
    with base:
        result = client.create(
            project_short_name="XAC",
            summary="Fix login bug",
        )

    assert result["idReadable"] == "XAC-42"


def test_update_issue(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/api/issues/XAC-42")
        assert request.method == "POST"
        import json
        body = json.loads(request.content)
        assert "summary" in body
        assert "description" in body
        return httpx.Response(200, json=SAMPLE_ISSUE)

    base, client = _make_client(handler)
    with base:
        result = client.update(
            "XAC-42",
            summary="Updated summary",
            description="Updated description.",
        )

    assert result["idReadable"] == "XAC-42"


def test_update_issue_summary_only(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        import json
        body = json.loads(request.content)
        assert "summary" in body
        assert "description" not in body
        return httpx.Response(200, json=SAMPLE_ISSUE)

    base, client = _make_client(handler)
    with base:
        result = client.update("XAC-42", summary="Updated summary")

    assert result["idReadable"] == "XAC-42"


def test_update_issue_empty_body_raises(sample_settings: None) -> None:
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=SAMPLE_ISSUE))
    base = YouTrackClient()
    base._client = httpx.Client(
        base_url=base._settings.api_base,
        transport=transport,
        headers=base._client.headers,
    )
    with base:
        with pytest.raises(ValueError, match="At least one of summary or description"):
            IssuesClient(base).update("XAC-42")


def test_get_issue_raises_on_error(sample_settings: None) -> None:
    transport = httpx.MockTransport(
        lambda _: httpx.Response(404, json={"error": "Not Found"}),
    )
    base = YouTrackClient()
    base._client = httpx.Client(
        base_url=base._settings.api_base,
        transport=transport,
        headers=base._client.headers,
    )
    with base:
        with pytest.raises(YouTrackAPIError, match="404"):
            IssuesClient(base).get("XAC-999")


def test_create_issue_raises_on_error(sample_settings: None) -> None:
    transport = httpx.MockTransport(
        lambda _: httpx.Response(403, json={"error": "Forbidden"}),
    )
    base = YouTrackClient()
    base._client = httpx.Client(
        base_url=base._settings.api_base,
        transport=transport,
        headers=base._client.headers,
    )
    with base:
        with pytest.raises(YouTrackAPIError, match="403"):
            IssuesClient(base).create(
                project_short_name="XAC",
                summary="Test",
            )
