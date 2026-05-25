from youtrack_peristalsis.config import Settings


def test_api_base(sample_settings: None) -> None:
    settings = Settings()
    assert settings.api_base == "https://example.youtrack.cloud/api"
