"""旅行プラン機能のテスト"""

from app import (
    app,
    calculate_scores,
    fetch_lodging_candidates_for_trip_plan,
    fetch_lodging_near_recommended_spots,
    fetch_recommended_spots_for_result,
    fetch_spot,
)
from trip_planner import TripConditions, build_trip_plan, filter_spots_for_transport


def sample_spots():
    return [
        {
            "id": 1,
            "name": "Spot A",
            "category": "観光",
            "genre": "海岸",
            "description": "Desc A",
            "image_url": "images/spots/a.jpg",
            "address": "Address A",
            "public_transport_access": "good",
            "visit_duration_min": 60,
            "area": "taneichi",
        },
        {
            "id": 2,
            "name": "Spot B",
            "category": "飲食店",
            "genre": "海鮮",
            "description": "Desc B",
            "image_url": "images/spots/b.jpg",
            "address": "Address B",
            "public_transport_access": "good",
            "visit_duration_min": 45,
            "area": "ohno",
        },
        {
            "id": 3,
            "name": "Observatory",
            "category": "観光",
            "genre": "星空",
            "description": "Desc C",
            "image_url": "images/spots/c.jpg",
            "address": "Address C",
            "public_transport_access": "car_recommended",
            "visit_duration_min": 90,
            "area": "yoke",
        },
    ]


def sample_labels():
    return {
        "summary_template": "{type_name} · {departure} · {transport} · {duration} · {party_size} · {companions}",
        "departure_tokyo": "Tokyo",
        "transport_public": "Public",
        "duration_day_trip": "Day trip",
        "companions_couple": "Couple",
        "access_public_notice": "Public notice",
        "stay_about": "About {minutes} min",
        "depart_home": "Depart",
        "return_home": "Return",
        "arrive_hirono": "Arrive",
        "free_explore": "Explore",
        "free_explore_note": "Free time",
        "lodging_check": "Lodging",
        "lodging_check_note": "Check lodging",
        "morning_free": "Morning",
        "morning_free_note": "Morning note",
        "slow_morning": "Slow morning",
        "slow_morning_note": "Slow note",
        "day1": "Day 1",
        "day2": "Day 2",
        "day3": "Day 3",
        "warning_public_excluded": "Excluded {count}",
        "warning_no_lodging": "No lodging",
        "error_no_spots": "No spots",
        "disclaimer": "Disclaimer",
    }


def test_public_transport_excludes_car_recommended():
    spots = sample_spots()
    filtered = filter_spots_for_transport(spots, "public")
    assert len(filtered) == 2
    assert all(s["public_transport_access"] != "car_recommended" for s in filtered)


def test_build_trip_plan_public_transport():
    main_type = {"id": 1, "name": "Test Type", "description": "", "icon": ""}
    conditions = TripConditions(
        departure="tokyo",
        transport="public",
        duration="day_trip",
        party_size=2,
        companions="couple",
    )
    plan = build_trip_plan(main_type, sample_spots(), conditions, sample_labels())
    assert plan["ok"] is True
    assert plan["warnings"]
    spot_ids = {
        item["spot_id"]
        for day in plan["days"]
        for item in day["items"]
        if item.get("spot_id")
    }
    assert 3 not in spot_ids


def test_trip_flow_with_session():
    with app.test_client() as client:
        r = client.get("/trip/conditions")
        assert r.status_code == 302
        assert "/diagnosis" in r.headers["Location"]

        client.post(
            "/result",
            data={"choice_id": ["1", "5", "9", "13", "17"]},
            follow_redirects=True,
        )

        r = client.get("/trip/conditions")
        assert r.status_code == 200
        text = r.get_data(as_text=True)
        assert "trip-conditions" in text
        assert "trip-form" in text

        r = client.post(
            "/trip/conditions",
            data={
                "transport": "rental",
                "duration": "1night",
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        text = r.get_data(as_text=True)
        assert "trip-plan" in text
        assert "trip-timeline" in text


def test_result_has_trip_cta():
    with app.test_client() as client:
        r = client.post(
            "/result",
            data={"choice_id": ["1", "5", "9", "13", "17"]},
            follow_redirects=True,
        )
        text = r.get_data(as_text=True)
        assert "btn-trip-cta" in text
        assert "/trip/conditions" in text


def test_language_switch_on_result():
    with app.test_client() as client:
        client.post(
            "/result",
            data={"choice_id": ["1", "5", "9", "13", "17"]},
            follow_redirects=True,
        )

        r = client.get("/result")
        ja_text = r.get_data(as_text=True)
        assert "あなたの洋野旅タイプ" in ja_text

        r = client.get(
            "/set-language/en",
            headers={"Referer": "http://localhost/result"},
            follow_redirects=True,
        )
        en_text = r.get_data(as_text=True)
        assert "Your Hirono travel type" in en_text or "Recommended" in en_text

        r = client.get(
            "/set-language/ja",
            headers={"Referer": "http://127.0.0.1/result"},
            follow_redirects=True,
        )
        ja_again = r.get_data(as_text=True)
        assert "あなたの洋野旅タイプ" in ja_again


def _day1_lodging_item(plan):
    for item in plan["days"][0]["items"]:
        if item["time"] == "18:00":
            return item
    return None


def test_trip_plan_includes_lodging_from_nearby_candidates():
    """1泊2日・宿泊候補あり → Day1 18:00 が kind=lodging"""
    choice_ids = [1, 5, 9, 13, 17]
    main_type = calculate_scores(choice_ids)[0]
    spots = [
        {
            "id": 1,
            "name": "Attraction",
            "category": "観光",
            "genre": "海岸",
            "description": "Desc",
            "image_url": "images/spots/a.jpg",
            "address": "Address",
            "public_transport_access": "good",
            "visit_duration_min": 60,
            "area": "taneichi",
        }
    ]
    lodging_candidates = fetch_lodging_candidates_for_trip_plan(choice_ids)
    assert lodging_candidates

    conditions = TripConditions(
        departure="tokyo",
        transport="rental",
        duration="1night",
        party_size=2,
        companions="couple",
    )
    plan = build_trip_plan(
        main_type,
        spots,
        conditions,
        sample_labels(),
        lodging_candidates=lodging_candidates,
    )
    lodging_item = _day1_lodging_item(plan)
    assert lodging_item is not None
    assert lodging_item["kind"] == "lodging"
    assert lodging_item["spot_id"] == lodging_candidates[0]["id"]
    assert lodging_item["title"] == lodging_candidates[0]["name"]


def _sample_attraction():
    return {
        "id": 1,
        "name": "Attraction",
        "category": "観光",
        "genre": "海岸",
        "description": "Desc",
        "image_url": "images/spots/a.jpg",
        "address": "Address",
        "public_transport_access": "good",
        "visit_duration_min": 60,
        "area": "taneichi",
    }


def test_trip_plan_prefers_same_address_lodging():
    """same_address の宿泊施設が same_area より先頭候補になる"""
    choice_ids = [1, 5, 9, 13, 17]
    recommended = fetch_recommended_spots_for_result(calculate_scores(choice_ids))
    nearby = fetch_lodging_near_recommended_spots(recommended)
    assert nearby[0]["proximity"] == "same_address"
    assert nearby[0]["id"] == 9

    lodging_candidates = fetch_lodging_candidates_for_trip_plan(choice_ids)
    plan = build_trip_plan(
        calculate_scores(choice_ids)[0],
        [_sample_attraction()],
        TripConditions("tokyo", "rental", "1night", 2, "couple"),
        sample_labels(),
        lodging_candidates=lodging_candidates,
    )
    lodging_item = _day1_lodging_item(plan)
    assert lodging_item["spot_id"] == 9


def test_trip_plan_lodging_fallback_when_no_candidates():
    """宿泊候補0件 → 従来の「宿泊」プレースホルダ"""
    main_type = {"id": 1, "name": "Test Type", "description": "", "icon": ""}
    spots = [
        {
            "id": 1,
            "name": "Attraction",
            "category": "観光",
            "genre": "海岸",
            "description": "Desc",
            "image_url": "images/spots/a.jpg",
            "address": "Address",
            "public_transport_access": "good",
            "visit_duration_min": 60,
            "area": "yoke",
        }
    ]
    plan = build_trip_plan(
        main_type,
        spots,
        TripConditions("tokyo", "rental", "1night", 2, "couple"),
        sample_labels(),
        lodging_candidates=[],
    )
    lodging_item = _day1_lodging_item(plan)
    assert lodging_item["kind"] == "free"
    assert lodging_item["title"] == "Lodging"
    assert lodging_item["spot_id"] is None
    assert sample_labels()["warning_no_lodging"] in plan["warnings"]


def test_trip_plan_public_transport_filters_lodging_candidates():
    """公共交通では car_recommended 宿泊を除外する"""
    car_lodging = fetch_spot(33)  # 大谷温泉（宿泊）
    assert car_lodging["public_transport_access"] == "car_recommended"

    main_type = {"id": 1, "name": "Test Type", "description": "", "icon": ""}
    plan = build_trip_plan(
        main_type,
        [_sample_attraction()],
        TripConditions("tokyo", "public", "1night", 2, "couple"),
        sample_labels(),
        lodging_candidates=[car_lodging],
    )
    lodging_item = _day1_lodging_item(plan)
    assert lodging_item["kind"] == "free"


def test_trip_flow_includes_lodging_on_plan_page():
    with app.test_client() as client:
        client.post(
            "/result",
            data={"choice_id": ["1", "5", "9", "13", "17"]},
            follow_redirects=True,
        )
        client.post(
            "/trip/conditions",
            data={
                "transport": "rental",
                "duration": "1night",
            },
            follow_redirects=True,
        )
        text = client.get("/trip/plan").get_data(as_text=True)
        assert "trip-kind-lodging" in text


if __name__ == "__main__":
    test_public_transport_excludes_car_recommended()
    test_build_trip_plan_public_transport()
    test_trip_flow_with_session()
    test_result_has_trip_cta()
    test_language_switch_on_result()
    test_trip_plan_includes_lodging_from_nearby_candidates()
    test_trip_plan_prefers_same_address_lodging()
    test_trip_plan_lodging_fallback_when_no_candidates()
    test_trip_plan_public_transport_filters_lodging_candidates()
    test_trip_flow_includes_lodging_on_plan_page()
    print("Trip planner tests passed")
