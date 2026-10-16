def test_streamlit_app_imports():
    # Keep this lightweight: a full AppTest smoke test is added after dependency validation.
    import app.main  # noqa: F401
