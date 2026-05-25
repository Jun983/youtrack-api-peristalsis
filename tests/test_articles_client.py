import httpx
import pytest

from youtrack_peristalsis.client.articles import ArticlesClient
from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.exceptions import YouTrackAPIError


def test_get_article(sample_settings: None) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/api/articles/NP-A-1")
        assert "fields" in str(request.url)
        return httpx.Response(
            200,
            json={
                "id": "226-0",
                "idReadable": "NP-A-1",
                "summary": "Title",
                "content": "Body",
                "project": {"shortName": "NP"},
            },
        )

    transport = httpx.MockTransport(handler)
    with YouTrackClient() as base:
        base._client = httpx.Client(
            base_url=base._settings.api_base,
            transport=transport,
            headers=base._client.headers,
        )
        article = ArticlesClient(base).get("NP-A-1")

    assert article["idReadable"] == "NP-A-1"


def test_create_raises_on_error(sample_settings: None) -> None:
    transport = httpx.MockTransport(
        lambda _: httpx.Response(403, json={"error": "Forbidden"}),
    )
    with YouTrackClient() as base:
        base._client = httpx.Client(
            base_url=base._settings.api_base,
            transport=transport,
            headers=base._client.headers,
        )
        with pytest.raises(YouTrackAPIError, match="403"):
            ArticlesClient(base).create(
                project_short_name="NP",
                summary="X",
                content="Y",
            )
