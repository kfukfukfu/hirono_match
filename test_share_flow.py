from app import app

with app.test_client() as client:
    r = client.post(
        "/result",
        data={"choice_id": ["1", "5", "9", "13", "17"]},
        follow_redirects=True,
    )
    text = r.get_data(as_text=True)
    assert "result-mobile" in text
    assert "result-label" in text
    assert "result-type-name" in text
    assert "percentage-simple-list" in text
    assert "result-spots" in text
    assert "result-lodging" not in text
    assert "近くに泊まるなら" not in text
    assert "result-spot-stars" in text
    assert "●" in text or "○" in text
    assert text.index("result-spots") < text.index("result-actions-mobile")
    assert "data-share-action" in text
    assert text.index("result-type-desc") < text.index("percentage-simple-list") < text.index("result-actions-mobile")
    print("Share flow checks passed")
