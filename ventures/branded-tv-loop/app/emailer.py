import os, httpx

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "RC Emporium <orders@example.com>")

async def send_email(to, subject, html):
    if not to:
        return {"sent": False, "reason": "no-recipient"}
    if not RESEND_API_KEY:
        return {"sent": False, "reason": "email-not-configured"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={"from": EMAIL_FROM, "to": [to], "subject": subject, "html": html},
        )
        r.raise_for_status()
        return {"sent": True, "response": r.json()}
