from typing import Any

import httpx

from youtrack_peristalsis.config import Settings


class YouTrackClient:
    """Thin HTTP wrapper for YouTrack REST API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._client = httpx.Client(
            base_url=self._settings.api_base,
            headers={
                "Authorization": f"Bearer {self._settings.youtrack_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> httpx.Response:
        return self._client.request(method, path, params=params, json=json)

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "YouTrackClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
