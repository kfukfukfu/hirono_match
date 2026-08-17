"""おすすめスポット近傍の宿泊施設取得のテスト"""

from app import (
    LODGING_NEAR_SAME_ADDRESS,
    LODGING_NEAR_SAME_AREA,
    fetch_lodging_near_recommended_spots,
    fetch_recommended_spots_for_result,
    fetch_spot,
    calculate_scores,
)


def _spot_item(spot_id):
    spot = fetch_spot(spot_id)
    assert spot is not None
    return spot


def test_same_address_pairs():
    pairs = [
        (2, 24),   # 種市海浜公園 ↔ キャンプ場
        (3, 23),   # はまなす亭 ↔ ゲストハウス
        (7, 22),   # マリンサイドスパ種市 ↔ たねいち
        (19, 25),  # 大谷温泉
        (16, 26),  # アグリパーク
        (8, 27),   # ヒロノット
        (4, 9),    # 大野木工 ↔ グリーンヒル大野
    ]
    for spot_id, lodging_id in pairs:
        result = fetch_lodging_near_recommended_spots([_spot_item(spot_id)])
        matched = next((item for item in result if item["id"] == lodging_id), None)
        assert matched is not None, f"spot {spot_id}: lodging {lodging_id} not found"
        assert matched["proximity"] == LODGING_NEAR_SAME_ADDRESS
        rel = next(r for r in matched["related_spots"] if r["spot_id"] == spot_id)
        assert rel["relation"] == LODGING_NEAR_SAME_ADDRESS


def test_same_area_without_same_address():
    """種市海岸は taneichi。同一住所の宿泊はなく、area 一致の宿泊が候補。"""
    result = fetch_lodging_near_recommended_spots([_spot_item(5)])
    assert result
    assert all(item["proximity"] == LODGING_NEAR_SAME_AREA for item in result)
    assert all(item["id"] in {22, 23, 24, 27, 29} for item in result)


def test_deduplicate_and_sort_priority():
    """複数おすすめスポットで同一宿泊が重複せず、同一住所が area より先。"""
    recommended = [_spot_item(2), _spot_item(5), _spot_item(12)]
    result = fetch_lodging_near_recommended_spots(recommended)
    ids = [item["id"] for item in result]
    assert ids.count(24) == 1
    camp = next(item for item in result if item["id"] == 24)
    assert camp["proximity"] == LODGING_NEAR_SAME_ADDRESS
    relations = {r["spot_id"]: r["relation"] for r in camp["related_spots"]}
    assert relations[2] == LODGING_NEAR_SAME_ADDRESS
    assert relations[5] == LODGING_NEAR_SAME_AREA
    assert relations[12] == LODGING_NEAR_SAME_AREA

    first_area_only = next(item for item in result if item["proximity"] == LODGING_NEAR_SAME_AREA and item["id"] != 24)
    first_address = next(item for item in result if item["proximity"] == LODGING_NEAR_SAME_ADDRESS)
    assert result.index(first_address) < result.index(first_area_only)


def test_no_match_outside_recommended_areas():
    """yoke のきのこの駅には area 一致の宿泊がない。"""
    result = fetch_lodging_near_recommended_spots([_spot_item(18)])
    assert result == []


def test_integration_with_recommended_spots():
    """診断結果のおすすめスポット列から宿泊候補を取得できる。"""
    choice_ids = [1, 5, 9, 13, 17]
    ranked = calculate_scores(choice_ids)
    recommended = fetch_recommended_spots_for_result(ranked)
    lodging = fetch_lodging_near_recommended_spots(recommended)
    assert isinstance(lodging, list)
    for item in lodging:
        assert {"id", "name", "area", "address", "proximity", "related_spots"} <= set(item.keys())
        assert item["proximity"] in (LODGING_NEAR_SAME_ADDRESS, LODGING_NEAR_SAME_AREA)
        assert item["related_spots"]


if __name__ == "__main__":
    test_same_address_pairs()
    test_same_area_without_same_address()
    test_deduplicate_and_sort_priority()
    test_no_match_outside_recommended_areas()
    test_integration_with_recommended_spots()
    print("Lodging proximity tests passed")
