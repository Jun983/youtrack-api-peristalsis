class YouTrackAPIError(Exception):
    """Raised when the YouTrack API returns an error response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"YouTrack API error {status_code}: {message}")
