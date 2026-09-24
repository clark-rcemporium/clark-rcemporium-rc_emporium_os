# RC Branded TV Loop — Autonomous Post-Payment Engine

Status: PRE-VALIDATION / DEPLOYMENT-READY MODULE  
Company: RC Emporium Technologies Inc.

## Purpose

Automate fulfillment after a customer pays for the $97 CAD founding restaurant package.

Flow:

Stripe checkout paid
→ order created
→ intake link sent
→ customer submits assets/content
→ rights/compliance checks
→ branded 1080p loop rendered
→ automated QA
→ safe orders auto-delivered
→ risky/uncertain orders held for human approval
→ 7-day follow-up
→ optional managed-update upsell

## Revenue-first gate

This module does **not** automate mass cold outreach. The commercial validation gate remains:

**PASS = 1 paid restaurant.**

Do not expand into a large platform before PASS.

## Human gates

The system is autonomous except when:
- customer cannot attest they own/have permission to use supplied assets;
- music/public-performance rights are uncertain;
- rendering or QA fails;
- content includes unsupported/risky claims;
- `AUTO_DELIVER_SAFE=false`.

## Run locally

```bash
cp .env.example .env
docker compose up --build
```

Open:
- Health: `http://localhost:8000/health`
- Intake: generated after a Stripe checkout event
- Admin: `/admin/orders` with `X-Admin-Token: <ADMIN_TOKEN>` header

## Production target

A container host with:
- HTTPS endpoint
- persistent volume mounted at `/data`
- Stripe webhook secret configured
- transactional email provider configured
- FFmpeg available

No secrets belong in GitHub.
