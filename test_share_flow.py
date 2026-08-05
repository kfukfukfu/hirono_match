from app import app

with app.test_client() as client:
    r = client.post("/result", data={"choice_id": ["1", "5", "9", "13", "17"]})
    text = r.get_data(as_text=True)
    assert "result-share" in text
    assert "data-share-action" in text
    assert "HIRONOMATCH" in text
    assert "結果をシェアする" in text
    assert text.index("result-type-desc") < text.index("result-share") < text.index("result-actions-mobile")
    print("Share flow checks passed")
