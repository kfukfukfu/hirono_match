"""
trip_planner.py
---------------
登録済みスポットのみを使い、出発地×移動手段×泊数などから
現実的な旅行モデル（時間付き行程）を組み立てる。
AI による事実の生成は行わない。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PUBLIC_TRANSPORT = frozenset({"public", "other"})
CAR_MODES = frozenset({"car", "rental"})

LODGING_CATEGORY = frozenset({"宿泊施設", "Accommodation"})
RESTAURANT_CATEGORY = frozenset({"飲食店", "Restaurant"})


@dataclass
class TripConditions:
    departure: str
    transport: str
    duration: str
    party_size: int
    companions: str
    season: str = ""
    budget: str = ""


def is_car_recommended(spot: dict[str, Any]) -> bool:
    return spot.get("public_transport_access") == "car_recommended"


def is_public_transport_mode(transport: str) -> bool:
    return transport in PUBLIC_TRANSPORT


def filter_spots_for_transport(spots: list[dict[str, Any]], transport: str) -> list[dict[str, Any]]:
    if not is_public_transport_mode(transport):
        return spots
    return [s for s in spots if not is_car_recommended(s)]


def categorize_spots(spots: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    lodging = []
    restaurants = []
    attractions = []
    for spot in spots:
        category = spot.get("category", "")
        if category in LODGING_CATEGORY:
            lodging.append(spot)
        elif category in RESTAURANT_CATEGORY:
            restaurants.append(spot)
        else:
            attractions.append(spot)
    return {
        "lodging": lodging,
        "restaurants": restaurants,
        "attractions": attractions,
    }


def pick_unique(spots: list[dict[str, Any]], count: int, used_ids: set[int]) -> list[dict[str, Any]]:
    picked = []
    for spot in spots:
        if spot["id"] in used_ids:
            continue
        picked.append(spot)
        used_ids.add(spot["id"])
        if len(picked) >= count:
            break
    return picked


def sort_by_area(spots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    order = {"taneichi": 0, "ohno": 1, "yoke": 2}
    return sorted(spots, key=lambda s: (order.get(s.get("area", ""), 9), s["id"]))


def build_access_note(conditions: TripConditions, labels: dict[str, str]) -> list[str]:
    notes = []
    key = f"access_{conditions.departure}_{conditions.transport}"
    text = labels.get(key)
    if text:
        notes.append(text)
    public_key = "access_public_notice" if is_public_transport_mode(conditions.transport) else None
    if public_key and labels.get(public_key):
        notes.append(labels[public_key])
    if conditions.season and labels.get(f"season_{conditions.season}"):
        notes.append(labels[f"season_{conditions.season}"])
    return notes


def build_summary(conditions: TripConditions, labels: dict[str, str], type_name: str) -> str:
    departure = labels.get(f"departure_{conditions.departure}", conditions.departure)
    transport = labels.get(f"transport_{conditions.transport}", conditions.transport)
    duration = labels.get(f"duration_{conditions.duration}", conditions.duration)
    companions = labels.get(f"companions_{conditions.companions}", conditions.companions)
    return labels["summary_template"].format(
        type_name=type_name,
        departure=departure,
        transport=transport,
        duration=duration,
        party_size=conditions.party_size,
        companions=companions,
    )


def spot_item(time_label: str, spot: dict[str, Any], kind: str, labels: dict[str, str]) -> dict[str, Any]:
    duration = spot.get("visit_duration_min")
    duration_text = ""
    if duration:
        duration_text = labels["stay_about"].format(minutes=duration)
    return {
        "time": time_label,
        "kind": kind,
        "spot_id": spot["id"],
        "title": spot["name"],
        "category": spot.get("category", ""),
        "genre": spot.get("genre", ""),
        "description": spot.get("description", ""),
        "image_url": spot.get("image_url", ""),
        "address": spot.get("address", ""),
        "note": duration_text,
    }


def travel_item(time_label: str, title: str, note: str = "") -> dict[str, Any]:
    return {
        "time": time_label,
        "kind": "travel",
        "spot_id": None,
        "title": title,
        "note": note,
    }


def free_item(time_label: str, title: str, note: str = "") -> dict[str, Any]:
    return {
        "time": time_label,
        "kind": "free",
        "spot_id": None,
        "title": title,
        "note": note,
    }


def build_day_trip(
    conditions: TripConditions,
    groups: dict[str, list[dict[str, Any]]],
    labels: dict[str, str],
    used_ids: set[int],
) -> list[dict[str, Any]]:
    attractions = pick_unique(sort_by_area(groups["attractions"]), 2, used_ids)
    restaurants = pick_unique(sort_by_area(groups["restaurants"]), 2, used_ids)
    items: list[dict[str, Any]] = []
    items.append(travel_item("09:00", labels["depart_home"], labels.get("morning_travel_note", "")))
    if attractions:
        items.append(spot_item("11:00", attractions[0], "spot", labels))
    if restaurants:
        items.append(spot_item("12:30", restaurants[0], "meal", labels))
    if len(attractions) > 1:
        items.append(spot_item("14:30", attractions[1], "spot", labels))
    elif groups["attractions"]:
        fallback = pick_unique(sort_by_area(groups["attractions"]), 1, used_ids)
        if fallback:
            items.append(spot_item("14:30", fallback[0], "spot", labels))
    if len(restaurants) > 1:
        items.append(spot_item("17:00", restaurants[1], "meal", labels))
    else:
        items.append(free_item("17:00", labels["free_explore"], labels["free_explore_note"]))
    items.append(travel_item("18:30", labels["return_home"]))
    return items


def build_overnight_day1(
    conditions: TripConditions,
    groups: dict[str, list[dict[str, Any]]],
    labels: dict[str, str],
    used_ids: set[int],
) -> list[dict[str, Any]]:
    attractions = pick_unique(sort_by_area(groups["attractions"]), 2, used_ids)
    restaurants = pick_unique(sort_by_area(groups["restaurants"]), 1, used_ids)
    lodging_list = pick_unique(groups["lodging"], 1, used_ids)
    items: list[dict[str, Any]] = []
    items.append(travel_item("09:30", labels["depart_home"], labels.get("morning_travel_note", "")))
    items.append(travel_item("11:30", labels["arrive_hirono"]))
    if attractions:
        items.append(spot_item("12:00", attractions[0], "spot", labels))
    if restaurants:
        items.append(spot_item("13:00", restaurants[0], "meal", labels))
    if len(attractions) > 1:
        items.append(spot_item("15:00", attractions[1], "experience", labels))
    if lodging_list:
        items.append(spot_item("18:00", lodging_list[0], "lodging", labels))
    else:
        items.append(free_item("18:00", labels["lodging_check"], labels["lodging_check_note"]))
    return items


def build_overnight_day2(
    conditions: TripConditions,
    groups: dict[str, list[dict[str, Any]]],
    labels: dict[str, str],
    used_ids: set[int],
) -> list[dict[str, Any]]:
    attractions = pick_unique(sort_by_area(groups["attractions"]), 2, used_ids)
    restaurants = pick_unique(sort_by_area(groups["restaurants"]), 1, used_ids)
    items: list[dict[str, Any]] = []
    items.append(free_item("08:30", labels["morning_free"], labels["morning_free_note"]))
    if attractions:
        items.append(spot_item("10:00", attractions[0], "spot", labels))
    if restaurants:
        items.append(spot_item("12:00", restaurants[0], "meal", labels))
    if len(attractions) > 1:
        items.append(spot_item("14:00", attractions[1], "experience", labels))
    items.append(travel_item("16:30", labels["return_home"]))
    return items


def build_multi_day3(
    groups: dict[str, list[dict[str, Any]]],
    labels: dict[str, str],
    used_ids: set[int],
) -> list[dict[str, Any]]:
    attractions = pick_unique(sort_by_area(groups["attractions"]), 2, used_ids)
    restaurants = pick_unique(sort_by_area(groups["restaurants"]), 1, used_ids)
    items: list[dict[str, Any]] = []
    items.append(free_item("09:00", labels["slow_morning"], labels["slow_morning_note"]))
    if attractions:
        items.append(spot_item("10:30", attractions[0], "spot", labels))
    if restaurants:
        items.append(spot_item("12:30", restaurants[0], "meal", labels))
    if len(attractions) > 1:
        items.append(spot_item("14:30", attractions[1], "spot", labels))
    items.append(travel_item("17:00", labels["return_home"]))
    return items


def build_trip_plan(
    main_type: dict[str, Any],
    spots: list[dict[str, Any]],
    conditions: TripConditions,
    labels: dict[str, str],
) -> dict[str, Any]:
    filtered = filter_spots_for_transport(spots, conditions.transport)
    warnings: list[str] = []

    if is_public_transport_mode(conditions.transport):
        excluded = [s for s in spots if is_car_recommended(s)]
        if excluded:
            warnings.append(labels["warning_public_excluded"].format(count=len(excluded)))

    if not filtered:
        return {
            "ok": False,
            "summary": build_summary(conditions, labels, main_type["name"]),
            "warnings": warnings,
            "error": labels["error_no_spots"],
        }

    groups = categorize_spots(filtered)
    if not groups["attractions"] and not groups["restaurants"]:
        return {
            "ok": False,
            "summary": build_summary(conditions, labels, main_type["name"]),
            "warnings": warnings,
            "error": labels["error_no_spots"],
        }

    if conditions.duration in ("1night", "2plus") and not groups["lodging"]:
        warnings.append(labels["warning_no_lodging"])

    used_ids: set[int] = set()
    days: list[dict[str, Any]] = []

    if conditions.duration == "day_trip":
        days.append({
            "label": labels["day1"],
            "items": build_day_trip(conditions, groups, labels, used_ids),
        })
    elif conditions.duration == "1night":
        days.append({
            "label": labels["day1"],
            "items": build_overnight_day1(conditions, groups, labels, used_ids),
        })
        days.append({
            "label": labels["day2"],
            "items": build_overnight_day2(conditions, groups, labels, used_ids),
        })
    else:
        days.append({
            "label": labels["day1"],
            "items": build_overnight_day1(conditions, groups, labels, used_ids),
        })
        days.append({
            "label": labels["day2"],
            "items": build_overnight_day2(conditions, groups, labels, used_ids),
        })
        days.append({
            "label": labels["day3"],
            "items": build_multi_day3(groups, labels, used_ids),
        })

    return {
        "ok": True,
        "summary": build_summary(conditions, labels, main_type["name"]),
        "travel_notes": build_access_note(conditions, labels),
        "warnings": warnings,
        "days": days,
        "disclaimer": labels["disclaimer"],
    }
