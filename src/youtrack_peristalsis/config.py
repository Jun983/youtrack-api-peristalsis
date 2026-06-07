from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """YouTrack connection settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    youtrack_base_url: str = Field(
        ...,
        description="YouTrack instance URL without trailing slash",
    )
    youtrack_token: str = Field(
        ...,
        description="Permanent token (perm:...)",
    )
    article_prefix: str | None = Field(
        default=None,
        alias="YOUTRACK_ARTICLE_PREFIX",
        description="Article id prefix (e.g. XAC for XAC-13). Used when pulling by number.",
    )
    default_project: str | None = Field(
        default=None,
        alias="YOUTRACK_PROJECT",
        description="Default project shortName for new articles (e.g. XAC)",
    )
    default_parent_article: str | None = Field(
        default=None,
        alias="YOUTRACK_PARENT_ARTICLE",
        description="Default parent article idReadable for sub-articles (e.g. NP-A-1)",
    )
    default_issue_project: str | None = Field(
        default=None,
        alias="YOUTRACK_ISSUE_PROJECT",
        description="Default project shortName for new issues (e.g. XAC)",
    )
    issue_prefix: str | None = Field(
        default=None,
        alias="YOUTRACK_ISSUE_PREFIX",
        description="Issue id prefix (e.g. XAC for XAC-42). Used when pulling by number.",
    )

    @property
    def api_base(self) -> str:
        return f"{self.youtrack_base_url.rstrip('/')}/api"
