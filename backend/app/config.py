from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Sarvam Voice Agents
    sarvam_api_key: str = Field(..., alias="SARVAM_API_KEY")
    sarvam_org_id: str = Field(..., alias="SARVAM_ORG_ID")
    sarvam_workspace_id: str = Field(..., alias="SARVAM_WORKSPACE_ID")
    sarvam_app_id: str = Field(..., alias="SARVAM_APP_ID")
    sarvam_app_version: int = Field(1, alias="SARVAM_APP_VERSION")
    sarvam_connection_id: str = Field(..., alias="SARVAM_CONNECTION_ID")
    sarvam_agent_phone_number: str = Field(..., alias="SARVAM_AGENT_PHONE_NUMBER")
    # Base URL for the Instant Outbound service (docs: Voice Agents API -> Base URLs)
    sarvam_outbounds_base_url: str = Field(
        "https://apps.sarvam.ai/api/outbounds", alias="SARVAM_OUTBOUNDS_BASE_URL"
    )

    # Webhook
    public_base_url: str = Field(..., alias="PUBLIC_BASE_URL")
    webhook_token: str = Field(..., alias="WEBHOOK_TOKEN")

    # DB / CORS
    database_url: str = Field(..., alias="DATABASE_URL")
    cors_origins: str = Field("http://localhost:3000", alias="CORS_ORIGINS")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def webhook_url(self) -> str:
        return f"{self.public_base_url.rstrip('/')}/webhooks/sarvam?token={self.webhook_token}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
