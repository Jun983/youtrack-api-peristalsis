from __future__ import annotations

from typing import Any

import httpx

from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.exceptions import YouTrackAPIError

_ARTICLE_FIELDS = (
    "id,idReadable,summary,content,created,updated,"
    "project(id,shortName),parentArticle(id,idReadable,summary)"
)


class ArticlesClient:
    """YouTrack Knowledge Base (기술 자료) Articles API."""

    def __init__(self, client: YouTrackClient) -> None:
        self._client = client

    def get(self, article_id: str) -> dict[str, Any]:
        response = self._client.get(
            f"/articles/{article_id}",
            params={"fields": _ARTICLE_FIELDS},
        )
        return self._parse(response)

    def create(
        self,
        *,
        project_short_name: str,
        summary: str,
        content: str,
        parent_article_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "project": {"shortName": project_short_name},
            "summary": summary,
            "content": content,
        }
        if parent_article_id:
            body["parentArticle"] = self._article_ref(parent_article_id)

        response = self._client.post(
            "/articles",
            params={"fields": _ARTICLE_FIELDS},
            json=body,
        )
        created = self._parse(response)

        if parent_article_id and not created.get("parentArticle"):
            self._link_as_child(parent_article_id, created["id"])

        return created

    def update(
        self,
        article_id: str,
        *,
        summary: str | None = None,
        content: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if summary is not None:
            body["summary"] = summary
        if content is not None:
            body["content"] = content

        if not body:
            raise ValueError("At least one of summary or content must be provided")

        response = self._client.post(
            f"/articles/{article_id}",
            params={"fields": _ARTICLE_FIELDS},
            json=body,
        )
        return self._parse(response)

    def _link_as_child(self, parent_article_id: str, child_db_id: str) -> None:
        response = self._client.post(
            f"/articles/{parent_article_id}/childArticles",
            params={"fields": "id,idReadable,summary"},
            json={"id": child_db_id},
        )
        self._parse(response)

    @staticmethod
    def _article_ref(article_id: str) -> dict[str, str]:
        if "-" in article_id and article_id[0].isalpha():
            return {"idReadable": article_id}
        return {"id": article_id}

    @staticmethod
    def _parse(response: httpx.Response) -> dict[str, Any]:
        if response.is_success:
            return response.json()

        message = response.text
        try:
            payload = response.json()
            if isinstance(payload, dict):
                message = payload.get("error_description") or payload.get("error") or message
        except ValueError:
            pass
        raise YouTrackAPIError(response.status_code, message)
