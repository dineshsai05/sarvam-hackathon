import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

# Languages accepted by OutboundAppOverrides.initial_language_name (Create outbound call docs)
SarvamLanguage = Literal[
    "Bengali", "Gujarati", "Kannada", "Malayalam", "Tamil", "Telugu", "Punjabi",
    "Sanskrit", "Odia", "Marathi", "Hindi", "English", "Assamese",
]

_E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_indian_phone(raw: str) -> str:
    """Accept '98765 43210', '09876543210', '+91 98765-43210' etc. -> '+919876543210'."""
    digits = re.sub(r"[^\d+]", "", raw.strip())
    if digits.startswith("+"):
        candidate = digits
    elif digits.startswith("0") and len(digits) == 11:
        candidate = "+91" + digits[1:]
    elif len(digits) == 10:
        candidate = "+91" + digits
    elif len(digits) == 12 and digits.startswith("91"):
        candidate = "+" + digits
    else:
        candidate = "+" + digits
    if not _E164.match(candidate):
        raise ValueError("phone must be a valid Indian mobile number")
    return candidate


class LeadCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str
    preferred_language: SarvamLanguage | None = None
    consent: bool

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: str) -> str:
        return normalize_indian_phone(v)

    @field_validator("consent")
    @classmethod
    def _consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("consent is required before we can call you")
        return v


class CallAttemptOut(BaseModel):
    attempt_id: str
    status: str
    duration: float | None
    interaction_id: str | None
    failure_reason: str | None
    final_agent_variables: dict[str, Any] | None
    transcript: list[dict[str, Any]] | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class LeadOut(BaseModel):
    id: str
    name: str
    phone: str
    preferred_language: str | None
    consent: bool
    created_at: datetime
    calls: list[CallAttemptOut] = []

    model_config = {"from_attributes": True}


class LeadCreatedResponse(BaseModel):
    lead_id: str
    attempt_id: str
    message: str


# ---- Sarvam webhook payload (docs: Instant outbound call webhook payload) ----

class ChannelInfo(BaseModel):
    channel_type: str
    channel_provider: str
    agent_phone_number: str


class WebhookConfigEcho(BaseModel):
    url: str
    metadata: dict[str, Any] | None = None


class TranscriptTurn(BaseModel):
    role: Literal["agent", "user"]
    en_text: str


class SarvamOutboundWebhook(BaseModel):
    attempt_id: str
    status: Literal["connected", "no_answer", "busy", "failed"]
    channel_info: ChannelInfo
    duration: float | None = None
    interaction_id: str | None = None
    failure_reason: str | None = None
    final_agent_variables: dict[str, Any] | None = None
    webhook_config: WebhookConfigEcho | None = None
    interaction_transcript: list[TranscriptTurn] | None = None

    model_config = {"extra": "allow"}
