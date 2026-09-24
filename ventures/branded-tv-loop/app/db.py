import os, sqlite3, json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "tvloop.sqlite3"

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS processed_stripe_events (
  event_id TEXT PRIMARY KEY,
  processed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stripe_session_id TEXT UNIQUE,
  stripe_customer_email TEXT,
  business_name TEXT,
  contact_name TEXT,
  phone TEXT,
  amount_total INTEGER,
  currency TEXT,
  state TEXT NOT NULL,
  intake_token TEXT UNIQUE NOT NULL,
  delivery_token TEXT UNIQUE,
  audio_mode TEXT DEFAULT 'silent',
  rights_attested INTEGER DEFAULT 0,
  human_review INTEGER DEFAULT 0,
  render_attempts INTEGER DEFAULT 0,
  output_path TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS intake (
  order_id INTEGER PRIMARY KEY,
  public_name TEXT,
  brand_colors TEXT,
  promotions_json TEXT,
  social_handles TEXT,
  events_text TEXT,
  style TEXT,
  logo_path TEXT,
  notes TEXT,
  FOREIGN KEY(order_id) REFERENCES orders(id)
);
CREATE TABLE IF NOT EXISTS order_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(order_id) REFERENCES orders(id)
);
"""

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.executescript(SCHEMA)

def log_event(order_id, event_type, payload=None):
    with conn() as c:
        c.execute(
            "INSERT INTO order_events(order_id,event_type,payload_json,created_at) VALUES(?,?,?,?)",
            (order_id, event_type, json.dumps(payload or {}), now_iso()),
        )

def set_state(order_id, state, **fields):
    fields = dict(fields)
    fields["state"] = state
    fields["updated_at"] = now_iso()
    clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [order_id]
    with conn() as c:
        c.execute(f"UPDATE orders SET {clause} WHERE id=?", values)
    log_event(order_id, "STATE", {"state": state, **fields})

def get_order_by_token(token):
    with conn() as c:
        return c.execute("SELECT * FROM orders WHERE intake_token=?", (token,)).fetchone()

def get_order(order_id):
    with conn() as c:
        return c.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()

def list_orders():
    with conn() as c:
        return c.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
