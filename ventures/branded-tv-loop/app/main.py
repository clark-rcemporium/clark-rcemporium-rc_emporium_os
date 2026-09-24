import os, secrets, json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
import stripe

from .db import init_db, conn, now_iso, log_event, set_state, get_order_by_token, get_order, list_orders, DATA_DIR
from .render import render_order, qa_video
from .emailer import send_email

app = FastAPI(title="RC Branded TV Loop Autonomy Engine", version="1.0.0")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000").rstrip("/")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
AUTO_DELIVER_SAFE = os.getenv("AUTO_DELIVER_SAFE", "true").lower() == "true"
MAX_RENDER_RETRIES = int(os.getenv("MAX_RENDER_RETRIES", "2"))
EXPECTED_PAYMENT_LINK_ID = os.getenv("EXPECTED_PAYMENT_LINK_ID", "")
FOUNDER_EMAIL = os.getenv("FOUNDER_EMAIL", "")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True, "service": "rc-branded-tv-loop-autonomy"}

def require_admin(request: Request):
    token = request.headers.get("x-admin-token", "")
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(403, "Forbidden")

async def create_order_from_session(session):
    email = (session.get("customer_details") or {}).get("email") or session.get("customer_email")
    session_id = session["id"]
    with conn() as c:
        existing = c.execute("SELECT * FROM orders WHERE stripe_session_id=?", (session_id,)).fetchone()
        if existing:
            return existing["id"]
        token = secrets.token_urlsafe(32)
        cur = c.execute(
            """INSERT INTO orders(stripe_session_id,stripe_customer_email,amount_total,currency,state,intake_token,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (session_id,email,session.get("amount_total"),session.get("currency"),"INTAKE_PENDING",token,now_iso(),now_iso())
        )
        order_id = cur.lastrowid
    log_event(order_id, "PAYMENT_CONFIRMED", {"stripe_session_id": session_id})
    intake_url = f"{APP_BASE_URL}/intake/{token}"
    await send_email(email, "Your RC Branded TV Loop intake",
                     f"<p>Payment received.</p><p><a href='{intake_url}'>Complete your restaurant intake</a></p>")
    if FOUNDER_EMAIL:
        await send_email(FOUNDER_EMAIL, f"New paid TV Loop order #{order_id}", f"<p>Intake: {intake_url}</p>")
    return order_id

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(500, "Webhook secret not configured")
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(400, f"Invalid webhook: {e}")
    event_id = event["id"]
    with conn() as c:
        if c.execute("SELECT 1 FROM processed_stripe_events WHERE event_id=?", (event_id,)).fetchone():
            return {"ok": True, "duplicate": True}
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment_link = session.get("payment_link")
        if EXPECTED_PAYMENT_LINK_ID and payment_link != EXPECTED_PAYMENT_LINK_ID:
            with conn() as c:
                c.execute("INSERT OR IGNORE INTO processed_stripe_events(event_id,processed_at) VALUES(?,?)", (event_id, now_iso()))
            return {"ok": True, "ignored": True}
        if session.get("payment_status") == "paid":
            await create_order_from_session(session)
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO processed_stripe_events(event_id,processed_at) VALUES(?,?)", (event_id, now_iso()))
    return {"ok": True}

@app.get("/intake/{token}", response_class=HTMLResponse)
def intake_form(token: str):
    order = get_order_by_token(token)
    if not order: raise HTTPException(404)
    return f"""
    <html><body style='font-family:Arial;max-width:760px;margin:40px auto'>
    <h1>RC Branded TV Loop Intake</h1><p>Order #{order['id']}</p>
    <form action='/intake/{token}' method='post' enctype='multipart/form-data'>
      <label>Restaurant display name</label><br><input name='public_name' required style='width:100%'><br><br>
      <label>Brand colours</label><br><input name='brand_colors' style='width:100%'><br><br>
      <label>Promotions/menu highlights — one per line, max 5</label><br><textarea name='promotions' rows='7' style='width:100%'></textarea><br><br>
      <label>Social handles</label><br><input name='social_handles' style='width:100%'><br><br>
      <label>Events / announcements</label><br><textarea name='events_text' rows='4' style='width:100%'></textarea><br><br>
      <label>Style</label><br><select name='style'><option>modern</option><option>upscale</option><option>casual</option><option>energetic</option></select><br><br>
      <label>Audio</label><br><select name='audio_mode'><option value='silent'>Silent video — venue audio handled separately</option></select><br><br>
      <label>Logo (PNG/JPG)</label><br><input type='file' name='logo' accept='image/png,image/jpeg'><br><br>
      <label><input type='checkbox' name='rights_attested' value='yes' required> I own or have permission to use all supplied content.</label><br><br>
      <label>Notes</label><br><textarea name='notes' rows='4' style='width:100%'></textarea><br><br>
      <button type='submit'>Submit and create my loop</button>
    </form></body></html>"""

@app.post("/intake/{token}", response_class=HTMLResponse)
async def intake_submit(token: str, background_tasks: BackgroundTasks,
    public_name: str = Form(...), brand_colors: str = Form(""), promotions: str = Form(""),
    social_handles: str = Form(""), events_text: str = Form(""), style: str = Form("modern"),
    audio_mode: str = Form("silent"), rights_attested: str = Form(...), notes: str = Form(""),
    logo: UploadFile | None = File(None)):
    order = get_order_by_token(token)
    if not order: raise HTTPException(404)
    oid = order["id"]
    logo_path = None
    if logo and logo.filename:
        ext = Path(logo.filename).suffix.lower()
        if ext not in [".png", ".jpg", ".jpeg"]: raise HTTPException(400, "Logo must be PNG or JPG")
        order_dir = DATA_DIR / "orders" / str(oid); order_dir.mkdir(parents=True, exist_ok=True)
        logo_path = order_dir / f"logo{ext}"; logo_path.write_bytes(await logo.read())
    promotions_list = [x.strip() for x in promotions.splitlines() if x.strip()][:5]
    attested = rights_attested == "yes"
    human_review = 0 if attested and audio_mode == "silent" else 1
    with conn() as c:
        c.execute("""INSERT INTO intake(order_id,public_name,brand_colors,promotions_json,social_handles,events_text,style,logo_path,notes)
        VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(order_id) DO UPDATE SET public_name=excluded.public_name,brand_colors=excluded.brand_colors,
        promotions_json=excluded.promotions_json,social_handles=excluded.social_handles,events_text=excluded.events_text,style=excluded.style,
        logo_path=excluded.logo_path,notes=excluded.notes""",
        (oid, public_name, brand_colors, json.dumps(promotions_list), social_handles, events_text, style, str(logo_path) if logo_path else None, notes))
        c.execute("UPDATE orders SET audio_mode=?, rights_attested=?, human_review=?, updated_at=? WHERE id=?",
                  (audio_mode, int(attested), human_review, now_iso(), oid))
    set_state(oid, "INTAKE_RECEIVED")
    background_tasks.add_task(process_order, oid)
    return "<h2>Thank you. Your materials were received and production has started.</h2>"

async def process_order(order_id: int):
    order = get_order(order_id)
    with conn() as c: intake = c.execute("SELECT * FROM intake WHERE order_id=?", (order_id,)).fetchone()
    if not order or not intake: set_state(order_id, "FAILED"); return
    if not order["rights_attested"] or order["audio_mode"] != "silent":
        set_state(order_id, "HUMAN_REVIEW", human_review=1); return
    attempts = order["render_attempts"] or 0
    if attempts >= MAX_RENDER_RETRIES: set_state(order_id, "FAILED", human_review=1); return
    try:
        set_state(order_id, "RENDERING", render_attempts=attempts + 1)
        out = render_order(order_id, order, intake)
        set_state(order_id, "QA")
        qa = qa_video(out); log_event(order_id, "QA_RESULT", qa)
        if not qa["passed"]: set_state(order_id, "HUMAN_REVIEW", human_review=1); return
        delivery_token = secrets.token_urlsafe(32)
        set_state(order_id, "READY", output_path=str(out), delivery_token=delivery_token)
        if AUTO_DELIVER_SAFE and not order["human_review"]: await deliver_order(order_id)
        else: set_state(order_id, "HUMAN_REVIEW", human_review=1)
    except Exception as e:
        log_event(order_id, "ERROR", {"message": str(e)}); set_state(order_id, "HUMAN_REVIEW", human_review=1)

async def deliver_order(order_id: int):
    order = get_order(order_id)
    if not order or order["state"] not in ("READY", "HUMAN_REVIEW"): return
    if not order["output_path"] or not Path(order["output_path"]).exists(): set_state(order_id, "FAILED", human_review=1); return
    token = order["delivery_token"] or secrets.token_urlsafe(32)
    if not order["delivery_token"]:
        with conn() as c: c.execute("UPDATE orders SET delivery_token=? WHERE id=?", (token, order_id))
    url = f"{APP_BASE_URL}/download/{token}"
    await send_email(order["stripe_customer_email"], "Your RC Branded TV Loop is ready",
                     f"<p>Your video passed automated QA.</p><p><a href='{url}'>Download your branded TV loop</a></p>")
    set_state(order_id, "DELIVERED")
    log_event(order_id, "FOLLOWUP_SCHEDULED", {"due_after_days": 7})

@app.get("/download/{token}")
def download(token: str):
    with conn() as c: order = c.execute("SELECT * FROM orders WHERE delivery_token=?", (token,)).fetchone()
    if not order or order["state"] not in ("DELIVERED", "FOLLOWUP_DUE", "UPSELL_SENT"): raise HTTPException(404)
    path = Path(order["output_path"])
    if not path.exists(): raise HTTPException(404)
    return FileResponse(path, media_type="video/mp4", filename="RC-Branded-TV-Loop.mp4")

@app.get("/admin/orders")
def admin_orders(request: Request):
    require_admin(request); return [dict(r) for r in list_orders()]

@app.post("/admin/orders/{order_id}/approve")
async def admin_approve(order_id: int, request: Request):
    require_admin(request); order = get_order(order_id)
    if not order: raise HTTPException(404)
    with conn() as c: c.execute("UPDATE orders SET human_review=0 WHERE id=?", (order_id,))
    if order["state"] == "HUMAN_REVIEW" and order["output_path"] and Path(order["output_path"]).exists():
        set_state(order_id, "READY", human_review=0); await deliver_order(order_id); return {"ok": True, "delivered": True}
    return {"ok": True, "delivered": False}

@app.post("/cron/followups")
async def cron_followups(request: Request):
    require_admin(request); now = datetime.now(timezone.utc); changed = 0
    with conn() as c: rows = c.execute("SELECT * FROM orders WHERE state='DELIVERED'").fetchall()
    for order in rows:
        updated = datetime.fromisoformat(order["updated_at"])
        if now - updated >= timedelta(days=7):
            await send_email(order["stripe_customer_email"], "How is your branded TV loop working?",
                "<p>Are you still using the loop? Reply with what you want changed.</p><p>If you want ongoing updates, RC Emporium can manage the content for you.</p>")
            set_state(order["id"], "UPSELL_SENT"); changed += 1
    return {"ok": True, "processed": changed}
