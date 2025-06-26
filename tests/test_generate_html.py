import os
import sys
import importlib
import re
from unittest.mock import MagicMock, patch
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def import_app():
    with patch.dict(sys.modules, {"streamlit": MagicMock(), "requests": MagicMock(), "bs4": MagicMock(), "pandas": MagicMock()}):
        sys.path.insert(0, ROOT)
        import src.app
        importlib.reload(src.app)
        sys.path.remove(ROOT)
        return src.app

def test_generate_html_rotates_messages():
    app = import_app()
    class Row(dict):
        def to_dict(self):
            return dict(self)

    class FakeDF:
        def __init__(self, rows):
            self.rows = [Row(r) for r in rows]

        def iterrows(self):
            for idx, row in enumerate(self.rows):
                yield idx, row

    df = FakeDF([
        {"telefono": "123", "nombre": "A"},
        {"telefono": "456", "nombre": "B"},
        {"telefono": "789", "nombre": "C"},
    ])
    messages = ["Hola {nombre} 1", "Hola {nombre} 2"]
    html_bytes, fname = app.generate_html(df, messages)
    html = html_bytes.decode("utf-8")
    links = re.findall(r'href="([^"]+)"', html)
    assert urllib.parse.quote("Hola A 1") in links[0]
    assert urllib.parse.quote("Hola B 2") in links[1]
    assert urllib.parse.quote("Hola C 1") in links[2]
