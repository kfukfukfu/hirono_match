"""旅行プラン機能のテスト"""

from app import app
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
                "departure": "tokyo",
                "transport": "rental",
                "duration": "1night",
                "party_size": "2",
                "companions": "couple",
                "season": "spring",
                "budget": "medium",
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


if __name__ == "__main__":
    test_public_transport_excludes_car_recommended()
    test_build_trip_plan_public_transport()
    test_trip_flow_with_session()
    test_result_has_trip_cta()
    test_language_switch_on_result()
    print("Trip planner tests passed")
