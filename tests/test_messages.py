import sys
import os
from unittest.mock import MagicMock, patch
import sqlite3
import importlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def import_app():
    with patch.dict(
        sys.modules,
        {
            "streamlit": MagicMock(),
            "pandas": MagicMock(),
            "requests": MagicMock(),
            "bs4": MagicMock(),
        },
    ):
        sys.path.insert(0, ROOT)
        import src.app

        importlib.reload(src.app)
        sys.path.remove(ROOT)
        return src.app


def make_memory_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE mensajes (id INTEGER PRIMARY KEY AUTOINCREMENT, descripcion TEXT NOT NULL)"
    )
    return conn


def test_add_message():
    conn = make_memory_db()
    app = import_app()
    with patch.object(app, "get_connection", return_value=conn):
        msg_id = app.add_message("Hola")
    cur = conn.cursor()
    cur.execute("SELECT descripcion FROM mensajes WHERE id=?", (msg_id,))
    row = cur.fetchone()
    assert row[0] == "Hola"


def test_update_message():
    conn = make_memory_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO mensajes (descripcion) VALUES ('Old')")
    msg_id = cur.lastrowid
    conn.commit()
    app = import_app()
    with patch.object(app, "get_connection", return_value=conn):
        result = app.update_message(msg_id, "New")
    assert result is True
    cur.execute("SELECT descripcion FROM mensajes WHERE id=?", (msg_id,))
    assert cur.fetchone()[0] == "New"


def test_delete_message():
    conn = make_memory_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO mensajes (descripcion) VALUES ('Temp')")
    msg_id = cur.lastrowid
    conn.commit()
    app = import_app()
    with patch.object(app, "get_connection", return_value=conn):
        result = app.delete_message(msg_id)
    assert result is True
    cur.execute("SELECT COUNT(*) FROM mensajes WHERE id=?", (msg_id,))
    assert cur.fetchone()[0] == 0

