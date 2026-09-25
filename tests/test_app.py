from src.app import app


def test_top_page_shows_three_phases():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Learn" in page
    assert "Build" in page
    assert "Attack &amp; Defend" in page
