import os, tempfile
os.environ["DATA_DIR"] = tempfile.mkdtemp()
from app.db import init_db, conn

def test_db_initializes():
    init_db()
    with conn() as c:
        n = c.execute("select count(*) as n from orders").fetchone()["n"]
    assert n == 0
