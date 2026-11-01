import logging
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .config import Settings, get_settings
from .db import get_db, init_db
from .models import CallAttempt, Lead
from .sarvam import SarvamError, SarvamOutboundClient
from .schemas import LeadCreate, LeadCreatedResponse, LeadOut, SarvamOutboundWebhook

log = logging.getLogger("advisor")
logging.basicConfig(level=logging.INFO)

_settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    log.info("Webhook URL registered with Sarvam on each call: %s", _settings.webhook_url)
    yield


app = FastAPI(title="AI Motor Insurance Advisor API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


_STATIC = Path(__file__).parent / "static"


@app.get("/", include_in_schema=False)
def signup_page() -> FileResponse:
    """Public signup page: name + mobile -> instant call. Served from the API so one URL is the whole demo."""
    return FileResponse(_STATIC / "index.html")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/leads", response_model=LeadCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    body: LeadCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LeadCreatedResponse:
    """Save the lead, then immediately place a Sarvam instant outbound call."""
    lead = Lead(
        name=body.name,
        phone=body.phone,
        preferred_language=body.preferred_language,
        consent=body.consent,
    )
    db.add(lead)
    db.commit()

    client = SarvamOutboundClient(settings)
    try:
        attempt_id = await client.create_outbound_call(
            user_phone_number=lead.phone,
            # These keys must match the Input variables defined on your agent in the Sarvam dashboard.
            agent_variables={"user_name": lead.name, "lead_id": lead.id},
            # Call opens in the agent's Starting language (English). The agent asks the caller to
            # pick English / Hindi / Telugu / Tamil and switches via the built-in Language switch tool.
            initial_language_name=lead.preferred_language,
            webhook_metadata={"lead_id": lead.id},
        )
    except SarvamError as e:
        log.error("Sarvam outbound failed for lead %s: %s", lead.id, e)
        raise HTTPException(status_code=502, detail={"error": "sarvam_outbound_failed", "upstream": e.body})

    db.add(CallAttempt(attempt_id=attempt_id, lead_id=lead.id, status="pending"))
    db.commit()
    return LeadCreatedResponse(
        lead_id=lead.id,
        attempt_id=attempt_id,
        message="Thanks! Our advisor will call you in a moment.",
    )


@app.post("/webhooks/sarvam", status_code=status.HTTP_200_OK)
def sarvam_webhook(
    payload: SarvamOutboundWebhook,
    token: str = Query(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Receives the post-call payload Sarvam POSTs after every instant outbound attempt.

    Sarvam does not document a signature header, so we guard the endpoint with the
    ?token= secret we embed in webhook_config.url when creating the call.
    """
    if token != settings.webhook_token:
        raise HTTPException(status_code=401, detail="bad webhook token")

    attempt = db.get(CallAttempt, payload.attempt_id)
    if attempt is None:
        # Attempt we don't know about (e.g. created from the dashboard). Try metadata, else store orphan-free.
        lead_id = (payload.webhook_config.metadata or {}).get("lead_id") if payload.webhook_config else None
        if not lead_id or db.get(Lead, lead_id) is None:
            log.warning("Webhook for unknown attempt %s and no lead_id metadata; ignoring", payload.attempt_id)
            return {"received": True, "stored": False}
        attempt = CallAttempt(attempt_id=payload.attempt_id, lead_id=lead_id)
        db.add(attempt)

    attempt.status = payload.status
    attempt.duration = payload.duration
    attempt.interaction_id = payload.interaction_id
    attempt.failure_reason = payload.failure_reason
    attempt.channel_provider = payload.channel_info.channel_provider
    attempt.agent_phone_number = payload.channel_info.agent_phone_number
    attempt.final_agent_variables = payload.final_agent_variables
    attempt.transcript = (
        [t.model_dump() for t in payload.interaction_transcript] if payload.interaction_transcript else None
    )
    attempt.raw_webhook = payload.model_dump(mode="json")
    attempt.completed_at = datetime.now(timezone.utc)
    db.commit()
    log.info("Call %s -> %s (lead %s)", attempt.attempt_id, attempt.status, attempt.lead_id)
    return {"received": True, "stored": True}


@app.get("/leads", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db), limit: int = 100) -> list[Lead]:
    stmt = select(Lead).options(selectinload(Lead.calls)).order_by(Lead.created_at.desc()).limit(limit)
    return list(db.scalars(stmt))


@app.get("/leads/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: str, db: Session = Depends(get_db)) -> Lead:
    stmt = select(Lead).options(selectinload(Lead.calls)).where(Lead.id == lead_id)
    lead = db.scalars(stmt).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="lead not found")
    return lead
