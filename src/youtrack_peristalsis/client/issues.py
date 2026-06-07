from __future__ import annotations

from typing import Any

import httpx

from youtrack_peristalsis.client.base import YouTrackClient
from youtrack_peristalsis.exceptions import YouTrackAPIError

_ISSUE_FIELDS = (
    "id,idReadable,summary,description,created,updated,"
    "project(id,shortName),"
    "reporter(id,name),"
    "assignee(id,name),"
    "state(id,name),"
    "priority(id,name),"
    "type(id,name)"
)


class IssuesClient:
    """YouTrack Issues API."""

    def __init__(self, client: YouTrackClient) -> None:
        self._client = client

    def list(
        self,
        *,
        query: str | None = None,
        top: int = 100,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        skip = 0
        while True:
            params: dict[str, Any] = {
                "fields": _ISSUE_FIELDS,
                "$top": top,
                "$skip": skip,
            }
            if query:
                params["query"] = query
            response = self._client.get("/issues", params=params)
            batch = self._parse_list(response)
            results.extend(batch)
            if len(batch) < top:
                break
            skip += top
        return results

    def get(self, issue_id: str) -> dict[str, Any]:
        response = self._client.get(
            f"/issues/{issue_id}",
            params={"fields": _ISSUE_FIELDS},
        )
        return self._parse(response)

    def create(
        self,
        *,
        project_short_name: str,
        summary: str,
        description: str = "",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "project": {"shortName": project_short_name},
            "summary": summary,
        }
        if description:
            body["description"] = description

        response = self._client.post(
            "/issues",
            params={"fields": _ISSUE_FIELDS},
            json=body,
        )
        return self._parse(response)

    def update(
        self,
        issue_id: str,
        *,
        summary: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if summary is not None:
            body["summary"] = summary
        if description is not None:
            body["description"] = description

        if not body:
            raise ValueError("At least one of summary or description must be provided")

        response = self._client.post(
            f"/issues/{issue_id}",
            params={"fields": _ISSUE_FIELDS},
            json=body,
        )
        return self._parse(response)

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

    @staticmethod
    def _parse_list(response: httpx.Response) -> list[dict[str, Any]]:
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
