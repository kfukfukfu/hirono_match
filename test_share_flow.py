from app import app

with app.test_client() as client:
    r = client.post("/result", data={"choice_id": ["1", "5", "9", "13", "17"]})
    text = r.get_data(as_text=True)
    assert "result-share" in text
    assert "data-share-action" in text
    assert "result-hero-label" in text
    assert "Instagram" in text
    assert "result-top" in text
    assert "result-hero-type" in text
    assert text.index("result-desc-text") < text.index("result-type-mix") < text.index("result-actions-bar")
    print("Share flow checks passed")
