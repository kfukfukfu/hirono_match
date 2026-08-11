from app import app

with app.test_client() as client:
    r = client.post("/result", data={"choice_id": ["1", "5", "9", "13", "17"]})
    text = r.get_data(as_text=True)
    assert "result-share" in text
    assert "data-share-action" in text
    assert "HIRONOMATCH" in text
    assert "Instagram" in text
    assert "result-story-card" in text
    assert "result-story-category" in text
    assert text.index("result-story-desc") < text.index("result-type-mix") < text.index("result-actions-bar")
    print("Share flow checks passed")
