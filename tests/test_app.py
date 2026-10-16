from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_without_exceptions():
    app = AppTest.from_file("app/main.py", default_timeout=30).run()
    assert not app.exception
    assert any("GeoMind" in title.value for title in app.title)
    assert any("GeoProof" in header.value for header in app.subheader)
