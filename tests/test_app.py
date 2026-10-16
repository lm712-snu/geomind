from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_without_exceptions():
    app_path = Path(__file__).resolve().parents[1] / "app" / "main.py"
    app = AppTest.from_file(app_path, default_timeout=30).run()
    assert not app.exception
    assert any("GeoMind" in title.value for title in app.title)
    assert any("GeoProof" in header.value for header in app.subheader)
