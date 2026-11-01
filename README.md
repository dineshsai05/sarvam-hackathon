# InsureWise: AI-Powered Motor Insurance Advisor

InsureWise is a voice AI motor insurance advisor for India. A customer leaves their number on the
website, and a Sarvam Voice Agent calls back in their chosen language (English, Hindi, Telugu or
Tamil), learns about their car and budget, answers coverage questions from real insurer policy
documents, and recommends a suitable policy. After the call, the transcript and extracted details
land in a database as a structured lead summary.

Built with Next.js, FastAPI, PostgreSQL and Sarvam Voice Agents with Knowledge Bases.

## Try it

**Open https://happen-delegation-explains-resumes.trycloudflare.com, enter your name and mobile number, and the AI advisor calls you within seconds.**

The call comes from +91 80642 69894. The advisor asks whether you prefer English, Hindi, Telugu or Tamil, then helps you compare private car insurance.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/dineshsai05/sarvam-hackathon)

## How it works

Website signup → Sarvam Voice Agents instant outbound call → post-call webhook stored in Postgres.

```
web/      Next.js signup page (name, phone, language, consent)  -> POST /leads
backend/  FastAPI: /leads places the call via Sarvam Outbounds API,
          /webhooks/sarvam receives status, transcript and extracted variables
```

## Sarvam endpoints used

| Purpose | Method / URL |
|---|---|
| Place instant outbound call | `POST https://apps.sarvam.ai/api/outbounds/v1/orgs/{org_id}/workspaces/{workspace_id}/outbounds` |
| Post-call webhook (Sarvam → us) | `POST {PUBLIC_BASE_URL}/webhooks/sarvam?token=…` |

Auth header: `X-API-Key: <Voice Agents key>` (create at https://indus.sarvam.ai/samvaad/settings/api-key).
Docs: https://docs.sarvam.ai/voice-agents/api/instant-outbound/create and
https://docs.sarvam.ai/voice-agents/api/instant-outbound/webhook-payload

## 0. Sarvam platform setup (dashboard, one time)

1. **Knowledge base**: Workspace → Knowledge base → Create. Upload the files from `knowledge_base/`
   (see `knowledge_base/README.md` for names, descriptions and layout). Wait for ingestion.
2. **Agent**: Build → New agent. Paste the greeting, instruction, variables and language settings from
   `agent/prompt.md`. Settings → Knowledge bases → attach the KB. Commit a version and note the
   **app_id** and **app_version** from Deploy with Code.
3. **Phone number**: Deploy → Phone Numbers → Add Connection → *Rent from Sarvam* (KYC, then Buy Number;
   30-day auto-renewing rental from wallet credits), or *Bring your own* Exotel. Note the
   **connection_id** and the number in E.164.
4. **API key**: Settings → API Key (Voice Agents key, not the TTS/STT key).
5. **Test**: use the agent's test panel, then place one real call via `POST /leads` to your own number.

## 1. Backend

```bash
cd backend
cp .env.example .env            # fill in SARVAM_* values (see below)
docker compose up -d db         # Postgres on localhost:5432
uv sync                         # or: python -m venv .venv && pip install -e .
uv run uvicorn app.main:app --reload --port 8000
```

Expose it so Sarvam can reach the webhook, then put that URL in `.env` as `PUBLIC_BASE_URL`:

```bash
ngrok http 8000
```

Run tests (no Postgres or network needed):

```bash
uv run pytest
```

### Where to find each `.env` value

| Variable | Where |
|---|---|
| `SARVAM_API_KEY` | Samvaad → Settings → API Key |
| `SARVAM_APP_ID`, `SARVAM_APP_VERSION` | Your agent → Deploy with Code (instant recipe shows both) |
| `SARVAM_CONNECTION_ID`, `SARVAM_AGENT_PHONE_NUMBER` | Deploy → Telephony (Exotel connection or rented Sarvam number) |
| `PUBLIC_BASE_URL` | Your ngrok / cloudflared HTTPS URL |
| `WEBHOOK_TOKEN` | Any long random string, e.g. `openssl rand -hex 32` |

### Agent variables

`/leads` sends `user_name`, `lead_id` and `preferred_language` as `agent_variables`.
Define variables with the same names on the agent in the Sarvam dashboard so the prompt can
reference them, and add output variables (vehicle, budget, policies_discussed, next_step, …).
Whatever the agent fills in comes back in the webhook as `final_agent_variables` and is stored on
`call_attempts.final_agent_variables`.

## Deploy for a persistent URL (Render, free tier)

1. Click the **Deploy to Render** button above (or New → Blueprint → this repo). `render.yaml`
   creates the `insurewise-api` web service and an `insurewise-db` Postgres with all Sarvam values
   pre-filled except the key.
2. When prompted, enter `SARVAM_API_KEY`. Everything else is already set; the webhook URL is
   derived from Render's own `RENDER_EXTERNAL_URL`.
3. After the first deploy, your API lives at `https://insurewise-api.onrender.com` (or similar).
   Check `https://<your-service>.onrender.com/health`.
4. Deploy the website on Vercel: import the repo, set **Root Directory** to `web` and
   `NEXT_PUBLIC_API_URL` to the Render URL. Then add the Vercel URL to `CORS_ORIGINS` on Render.

Free Render services sleep after 15 minutes idle; the first request after that takes ~30 s. Open the
health URL once before a demo.

## 2. Website

```bash
cd web
cp .env.local.example .env.local
npm install
npm run dev                     # http://localhost:3000
```

## API

| Method | Path | Notes |
|---|---|---|
| POST | `/leads` | `{name, phone, preferred_language?, consent}` → saves lead, places call, returns `attempt_id` |
| POST | `/webhooks/sarvam?token=…` | Sarvam posts here after each attempt |
| GET | `/leads` | Leads with their call attempts (for an admin dashboard) |
| GET | `/leads/{id}` | One lead |
| GET | `/health` | |

Interactive docs at http://localhost:8000/docs.

## Compliance note

Outbound calls in India must respect TRAI DND. Sarvam's org-wide DND list (Campaigns page → DND)
blocks numbers from campaigns; the webhook reports NDNC rejections as `status: failed` with
`failure_reason` prefixed by the provider. Collect explicit consent (the form enforces it) and have
the agent disclose it is an AI.
