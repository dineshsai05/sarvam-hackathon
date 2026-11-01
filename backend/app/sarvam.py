"""Thin client for the Sarvam Voice Agents Instant Outbound API.

Endpoint (docs: https://docs.sarvam.ai/voice-agents/api/instant-outbound/create):
  POST {SARVAM_OUTBOUNDS_BASE_URL}/v1/orgs/{org_id}/workspaces/{workspace_id}/outbounds
  Header: X-API-Key
  Body: { app_config, user_config, webhook_config? }
  200: { "attempt_id": str }
"""
from typing import Any

import httpx

from .config import Settings


class SarvamError(RuntimeError):
    def __init__(self, status_code: int, body: Any):
        super().__init__(f"Sarvam API error {status_code}: {body}")
        self.status_code = status_code
        self.body = body


class SarvamOutboundClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self._s = settings
        self._client = client

    @property
    def _url(self) -> str:
        s = self._s
        return (
            f"{s.sarvam_outbounds_base_url.rstrip('/')}"
            f"/v1/orgs/{s.sarvam_org_id}/workspaces/{s.sarvam_workspace_id}/outbounds"
        )

    def build_payload(
        self,
        *,
        user_phone_number: str,
        agent_variables: dict[str, Any] | None = None,
        initial_language_name: str | None = None,
        initial_bot_message: str | None = None,
        webhook_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        s = self._s
        app_config: dict[str, Any] = {
            "app_id": s.sarvam_app_id,
            "app_version": s.sarvam_app_version,
            "app_type": "agent",
            "connection_config": {
                "connection_id": s.sarvam_connection_id,
                "agent_phone_number": s.sarvam_agent_phone_number,
            },
        }
        if agent_variables:
            app_config["agent_variables"] = agent_variables
        overrides: dict[str, Any] = {}
        if initial_language_name:
            overrides["initial_language_name"] = initial_language_name
        if initial_bot_message:
            overrides["initial_bot_message"] = initial_bot_message
        if overrides:
            app_config["app_overrides"] = overrides

        return {
            "app_config": app_config,
            "user_config": {"user_phone_number": user_phone_number},
            "webhook_config": {"url": s.webhook_url, "metadata": webhook_metadata or None},
        }

    async def create_outbound_call(self, **kwargs: Any) -> str:
        payload = self.build_payload(**kwargs)
        headers = {"X-API-Key": self._s.sarvam_api_key, "Content-Type": "application/json"}
        own_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=30)
        try:
            resp = await client.post(self._url, json=payload, headers=headers)
        finally:
            if own_client:
                await client.aclose()
        if resp.status_code != 200:
            try:
                body = resp.json()
            except ValueError:
                body = resp.text
            raise SarvamError(resp.status_code, body)
        data = resp.json()
        return data["attempt_id"]
