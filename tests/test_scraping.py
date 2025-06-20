import sys
from unittest import mock
from unittest.mock import MagicMock, patch
import pytest

pytest.importorskip("bs4")
from bs4 import BeautifulSoup

# Mock unavailable modules so src.app can be imported
sys.modules.setdefault("streamlit", MagicMock())
sys.modules.setdefault("pandas", MagicMock())
sys.modules.setdefault("requests", MagicMock())

import src.app


def test_extract_whatsapp_number():
    html = '<a href="https://wa.me/56912345678">Chat</a>'
    soup = BeautifulSoup(html, "html.parser")
    assert src.app.extract_whatsapp_number(soup) == "912345678"


def test_scrape_vehicle_details(tmp_path):
    html = (
        "<img src=\"data:image/png;base64,AA==\" />"
        "<a href=\"https://wa.me/56911122233\">WhatsApp</a>"
        "<div class=\"features-item-value-vehculo\">2021 TestCar</div>"
        "<div class=\"features-item-value-precio\">$10,000</div>"
        "<div class=\"view-more-container\"><div class=\"view-more-target\">"
        "<p>Great car</p></div></div>"
    )

    class MockResponse:
        status_code = 200
        content = html.encode("utf-8")

    with patch.object(src.app.requests, "get", return_value=MockResponse()):
        with patch("builtins.open", mock.mock_open()), \
             patch("os.path.join", return_value=str(tmp_path / "img.png")):
            data = src.app.scrape_vehicle_details("http://example.com")

    assert data["nombre"] == "2021 TestCar"
    assert data["whatsapp_number"] == "911122233"
    assert data["precio"] == "10,000"
    assert data["descripcion"] == "Great car"
    assert data["contact_image_file"].endswith("img.png")
