"""
app.py
------
「ひろのまっち」の Flask メインアプリケーション。
URL ルーティング、診断スコア計算、テンプレートへのデータ受け渡しを担当する。
"""

import os
from urllib.parse import quote, urlparse

from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify, flash

from database import get_db
from contact import is_valid_email, save_inquiry
from i18n import get_lang, translate, translate_value, localize_row, SUPPORTED_LANGS
from basic_auth import init_basic_auth
from trip_planner import TripConditions, build_trip_plan

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-hirono-match-local")
init_basic_auth(app)

RECOMMENDED_SPOT_LIMIT = 5
QUESTION_COUNT = 5

TRIP_DEPARTURES = frozenset({"tokyo", "morioka", "hachinohe", "hanamaki", "nearby", "other"})
TRIP_TRANSPORTS = frozenset({"car", "rental", "public", "other"})
TRIP_DURATIONS = frozenset({"day_trip", "1night", "2plus"})
TRIP_COMPANIONS = frozenset({"solo", "couple", "family", "friends", "group"})
TRIP_SEASONS = frozenset({"spring", "summer", "autumn", "winter", "undecided", ""})
TRIP_BUDGETS = frozenset({"low", "medium", "high", "undecided", ""})


@app.context_processor
def inject_i18n():
    """
    すべてのテンプレートで使える変数を注入する。
    _(...) … 翻訳関数（例: {{ _('nav.diagnosis') }}）
    lang   … 現在の言語コード（"ja" または "en"）
    """
    return {
        "_": translate,
        "tv": translate_value,
        "lang": get_lang(),
        "supported_langs": SUPPORTED_LANGS,
        "location_map_image": (
            "images/hirono-location-map-en.png"
            if get_lang() == "en"
            else "images/hirono-location-map.png"
        ),
    }


@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    """ヘッダーの言語切替ボタン用。選択を session に保存して元のページへ戻る。"""
    if lang_code in SUPPORTED_LANGS:
        session["lang"] = lang_code
        session.modified = True
    return redirect(language_redirect_target())


def language_redirect_target():
    """言語切替後の遷移先。POST専用URLや外部サイトへのリダイレクトを避ける。"""
    referrer = request.referrer
    if not referrer:
        return url_for("index")

    ref = urlparse(referrer)
    if ref.netloc and not _referrer_host_matches(ref.netloc):
        return url_for("index")

    path = ref.path or "/"
    if path == "/result":
        if get_diagnosis_result():
            return url_for("result")
        return url_for("diagnosis")

    if ref.query:
        return f"{path}?{ref.query}"
    return path


def _referrer_host_matches(referrer_netloc: str) -> bool:
    """同一サイトからの言語切替か判定（localhost / 127.0.0.1 の差異も許容）"""
    def host_only(netloc: str) -> str:
        if netloc.startswith("["):
            return netloc.split("]")[0] + "]"
        return netloc.rsplit(":", 1)[0].lower()

    ref_host = host_only(referrer_netloc)
    req_host = host_only(request.host)
    if ref_host == req_host:
        return True

    local_hosts = {"localhost", "127.0.0.1", "::1"}
    return ref_host in local_hosts and req_host in local_hosts


@app.template_filter("map_url")
def map_url_filter(address):
    """住所から Google マップ検索 URL を生成する"""
    return f"https://www.google.com/maps/search/?api=1&query={quote(address)}"


@app.template_filter("is_instagram_url")
def is_instagram_url_filter(url):
    return bool(url) and "instagram.com" in url.lower()


def get_diagnosis_result():
    """セッションに保存された診断結果を、現在の表示言語で返す"""
    data = session.get("diagnosis_result")
    if not data:
        return None

    choice_ids = data.get("choice_ids")
    if not choice_ids:
        return None

    ranked = calculate_scores(choice_ids)
    if not ranked:
        return None

    main_type = ranked[0]
    return {
        "main_type_id": main_type["id"],
        "main_type_name": main_type["name"],
        "main_type_description": main_type["description"],
        "main_type_icon": main_type["icon"],
        "choice_ids": choice_ids,
    }


def save_diagnosis_result(choice_ids):
    session["diagnosis_result"] = {
        "choice_ids": [int(c) for c in choice_ids],
    }
    session.modified = True


def build_result_context():
    """診断結果画面用のデータを、現在の表示言語で組み立てる"""
    diagnosis = get_diagnosis_result()
    if diagnosis is None:
        return None

    ranked = calculate_scores(diagnosis["choice_ids"])
    if not ranked:
        return None

    main_type = ranked[0]
    return {
        "main_type": main_type,
        "type_percentages": ranked[:3],
        "recommended_spots": fetch_recommended_spots_for_result(ranked),
    }


def fetch_travel_type(type_id):
    db = get_db()
    row = db.execute("SELECT * FROM travel_types WHERE id = ?", (type_id,)).fetchone()
    db.close()
    if row is None:
        return None
    return localize_row(row, ("name", "description"))


def fetch_spots_for_type(type_id):
    """診断タイプに紐づく登録スポットをすべて取得"""
    db = get_db()
    spots = db.execute(
        """SELECT s.*
           FROM spots s
           JOIN spot_types st ON st.spot_id = s.id
           WHERE st.type_id = ?
           ORDER BY s.id""",
        (type_id,),
    ).fetchall()
    db.close()
    return [
        localize_row(spot, ("name", "category", "genre", "description"))
        for spot in spots
    ]


def spot_website_url(spot):
    url = spot.get("official_url", "")
    if url and "instagram.com" not in url.lower():
        return url
    return ""


def spot_sns_url(spot):
    sns = spot.get("official_sns_url", "")
    if sns:
        return sns
    url = spot.get("official_url", "")
    if url and "instagram.com" in url.lower():
        return url
    return ""


def spot_map_url(spot):
    if spot.get("map_url"):
        return spot["map_url"]
    if spot.get("address"):
        return map_url_filter(spot["address"])
    return ""


def parse_trip_conditions(form):
    departure = form.get("departure", "").strip()
    transport = form.get("transport", "").strip()
    duration = form.get("duration", "").strip()
    companions = form.get("companions", "").strip()
    season = form.get("season", "").strip()
    budget = form.get("budget", "").strip()

    try:
        party_size = int(form.get("party_size", "0"))
    except ValueError:
        party_size = 0

    if departure not in TRIP_DEPARTURES:
        return None
    if transport not in TRIP_TRANSPORTS:
        return None
    if duration not in TRIP_DURATIONS:
        return None
    if companions not in TRIP_COMPANIONS:
        return None
    if season not in TRIP_SEASONS:
        return None
    if budget not in TRIP_BUDGETS:
        return None
    if party_size < 1 or party_size > 10:
        return None

    return TripConditions(
        departure=departure,
        transport=transport,
        duration=duration,
        party_size=party_size,
        companions=companions,
        season=season,
        budget=budget,
    )


def get_trip_planner_labels():
    labels = translate_value("trip.planner")
    return labels if isinstance(labels, dict) else {}


def fetch_questions_with_choices():
    """診断用の質問と選択肢を DB から取得する"""
    db = get_db()
    questions = db.execute(
        "SELECT * FROM questions ORDER BY id LIMIT ?",
        (QUESTION_COUNT,),
    ).fetchall()
    result = []

    for q in questions:
        choices = db.execute(
            "SELECT * FROM choices WHERE question_id = ? ORDER BY id",
            (q["id"],),
        ).fetchall()
        result.append({
            "question": localize_row(q, ("text",)),
            "choices": [localize_row(c, ("text", "subtitle")) for c in choices],
        })

    db.close()
    return result


def validate_answers(choice_ids):
    """
    回答の妥当性を検証する。
    - 全問に1つずつ回答していること
    - 存在する choice_id であること
    """
    if not choice_ids:
        return False

    try:
        choice_ids = [int(c) for c in choice_ids]
    except ValueError:
        return False

    if len(choice_ids) != QUESTION_COUNT:
        return False

    placeholders = ",".join("?" * len(choice_ids))
    db = get_db()
    rows = db.execute(
        f"SELECT id, question_id FROM choices WHERE id IN ({placeholders})",
        choice_ids,
    ).fetchall()
    db.close()

    if len(rows) != len(choice_ids):
        return False

    question_ids = {row["question_id"] for row in rows}
    return len(question_ids) == QUESTION_COUNT


def calculate_scores(choice_ids):
    """
    選択された choice_id のリストから、旅行タイプごとのスコアを計算する。
    同点時は Q5（最終回答）の得点優先、それでも同点なら type_id 昇順。
    返り値: スコア降順のリスト（name, description, icon, score, percentage を含む）
    """
    db = get_db()
    scores = {}
    q5_scores = {}

    for i, choice_id in enumerate(choice_ids):
        rows = db.execute(
            """SELECT cs.type_id, cs.score, tt.name, tt.description, tt.icon,
                      tt.name_en, tt.description_en
               FROM choice_scores cs
               JOIN travel_types tt ON tt.id = cs.type_id
               WHERE cs.choice_id = ?""",
            (choice_id,),
        ).fetchall()

        is_q5 = i == len(choice_ids) - 1
        for row in rows:
            type_id = row["type_id"]
            localized = localize_row(row, ("name", "description"))
            if type_id not in scores:
                scores[type_id] = {
                    "id": type_id,
                    "name": localized["name"],
                    "description": localized["description"],
                    "icon": row["icon"],
                    "score": 0,
                }
            scores[type_id]["score"] += row["score"]
            if is_q5:
                q5_scores[type_id] = q5_scores.get(type_id, 0) + row["score"]

    db.close()

    total = sum(s["score"] for s in scores.values()) or 1
    ranked = []
    for s in scores.values():
        ranked.append(
            {
                **s,
                "percentage": round(s["score"] / total * 100),
            }
        )

    ranked.sort(
        key=lambda x: (
            -x["score"],
            -q5_scores.get(x["id"], 0),
            x["id"],
        )
    )
    return ranked


def _format_recommendation_stars(star_count: int) -> str:
    """1〜5のおすすめ度を星5段階の文字列に変換する"""
    count = max(1, min(5, star_count))
    return "●" * count + "○" * (5 - count)


def fetch_recommended_spots_for_result(ranked, limit=RECOMMENDED_SPOT_LIMIT):
    """
    診断結果のタイプ順位に基づき、おすすめスポットを返す。
    各スポットは紐づくタイプのうち最も順位の高いタイプを基準に並べ、⭐1〜5で表示する。
    """
    type_rank = {t["id"]: index for index, t in enumerate(ranked)}
    db = get_db()
    spots = db.execute("SELECT * FROM spots ORDER BY id").fetchall()
    type_rows = db.execute("SELECT spot_id, type_id FROM spot_types").fetchall()
    db.close()

    types_by_spot = {}
    for row in type_rows:
        types_by_spot.setdefault(row["spot_id"], []).append(row["type_id"])

    recommendations = []
    for spot in spots:
        linked_type_ids = types_by_spot.get(spot["id"], [])
        linked_ranks = [
            type_rank[type_id]
            for type_id in linked_type_ids
            if type_id in type_rank
        ]
        if not linked_ranks:
            continue

        best_rank = min(linked_ranks)
        star_count = max(1, 5 - best_rank)

        item = localize_row(spot, ("name", "category", "genre", "description"))
        item["recommendation_stars"] = star_count
        item["recommendation_stars_display"] = _format_recommendation_stars(star_count)
        item["_best_type_rank"] = best_rank
        recommendations.append(item)

    recommendations.sort(key=lambda s: (s["_best_type_rank"], s["id"]))
    for item in recommendations:
        item.pop("_best_type_rank", None)
    return recommendations[:limit]


def fetch_spot(spot_id):
    """スポット1件を取得する"""
    db = get_db()
    spot = db.execute("SELECT * FROM spots WHERE id = ?", (spot_id,)).fetchone()
    db.close()
    if spot is None:
        return None
    return localize_row(spot, ("name", "category", "genre", "description"))


@app.route("/health")
def health():
    """Render のヘルスチェック用（Basic 認証の対象外）"""
    return "ok", 200


@app.route("/")
def index():
    """トップ画面"""
    return render_template("index.html")


@app.route("/diagnosis")
def diagnosis():
    """診断画面（5問・1問ずつ表示・1つ選択）"""
    questions = fetch_questions_with_choices()
    if len(questions) < QUESTION_COUNT:
        abort(503)
    return render_template("diagnosis.html", questions=questions)


@app.route("/result", methods=["GET", "POST"])
def result():
    """診断結果画面（GET: 表示 / POST: 回答送信 → GETへリダイレクト）"""
    if request.method == "POST":
        choice_ids = request.form.getlist("choice_id")

        if not validate_answers(choice_ids):
            return redirect(url_for("diagnosis"))

        save_diagnosis_result([int(c) for c in choice_ids])
        return redirect(url_for("result"))

    context = build_result_context()
    if context is None:
        return redirect(url_for("diagnosis"))

    return render_template("result.html", **context)


@app.route("/spot/<int:spot_id>")
def spot_detail(spot_id):
    """スポット詳細画面"""
    spot = fetch_spot(spot_id)
    if spot is None:
        abort(404)
    return render_template(
        "spot_detail.html",
        spot=spot,
        spot_website=spot_website_url(spot),
        spot_sns=spot_sns_url(spot),
        spot_map=spot_map_url(spot),
    )


@app.route("/trip/conditions", methods=["GET", "POST"])
def trip_conditions():
    """旅行条件入力（診断結果を持つユーザーのみ）"""
    diagnosis = get_diagnosis_result()
    if diagnosis is None:
        flash(translate("trip.conditions.need_diagnosis"), "error")
        return redirect(url_for("diagnosis"))

    default_form = {
        "departure": "tokyo",
        "transport": "rental",
        "duration": "1night",
        "party_size": "2",
        "companions": "couple",
        "season": "undecided",
        "budget": "undecided",
    }

    if request.method == "POST":
        conditions = parse_trip_conditions(request.form)
        if conditions is None:
            flash(translate("trip.conditions.error_invalid"), "error")
            return render_template(
                "trip_conditions.html",
                diagnosis=diagnosis,
                form=request.form.to_dict(),
            )

        session["trip_conditions"] = {
            "departure": conditions.departure,
            "transport": conditions.transport,
            "duration": conditions.duration,
            "party_size": conditions.party_size,
            "companions": conditions.companions,
            "season": conditions.season,
            "budget": conditions.budget,
        }
        return redirect(url_for("trip_plan"))

    return render_template(
        "trip_conditions.html",
        diagnosis=diagnosis,
        form=default_form,
    )


@app.route("/trip/plan")
def trip_plan():
    """旅行モデル表示"""
    diagnosis = get_diagnosis_result()
    raw_conditions = session.get("trip_conditions")
    if diagnosis is None or not raw_conditions:
        flash(translate("trip.plan.need_conditions"), "error")
        return redirect(url_for("diagnosis"))

    conditions = TripConditions(
        departure=raw_conditions["departure"],
        transport=raw_conditions["transport"],
        duration=raw_conditions["duration"],
        party_size=int(raw_conditions["party_size"]),
        companions=raw_conditions["companions"],
        season=raw_conditions.get("season", ""),
        budget=raw_conditions.get("budget", ""),
    )

    main_type = fetch_travel_type(diagnosis["main_type_id"])
    if main_type is None:
        flash(translate("trip.plan.error_type"), "error")
        return redirect(url_for("diagnosis"))

    spots = fetch_spots_for_type(diagnosis["main_type_id"])
    plan = build_trip_plan(main_type, spots, conditions, get_trip_planner_labels())

    return render_template(
        "trip_plan.html",
        diagnosis=diagnosis,
        main_type=main_type,
        conditions=conditions,
        plan=plan,
    )


@app.route("/api/spots")
def api_spots():
    """お気に入り一覧用。IDリストから現在の表示言語でスポット情報を返す。"""
    ids_param = request.args.get("ids", "")
    if not ids_param:
        return jsonify([])

    try:
        spot_ids = [int(x.strip()) for x in ids_param.split(",") if x.strip()]
    except ValueError:
        abort(400)

    spots = []
    for spot_id in spot_ids:
        spot = fetch_spot(spot_id)
        if spot:
            spots.append({
                "id": spot["id"],
                "name": spot["name"],
                "category": spot["category"],
                "image_url": spot["image_url"],
            })
    return jsonify(spots)


@app.route("/favorites")
def favorites():
    """お気に入り一覧画面（localStorage で管理）"""
    return render_template("favorites.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """お問い合わせ画面"""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not message:
            flash(translate("contact.error_message_required"), "error")
            return render_template(
                "contact.html",
                form={"name": name, "email": email, "message": message},
            )

        if email and not is_valid_email(email):
            flash(translate("contact.error_email_invalid"), "error")
            return render_template(
                "contact.html",
                form={"name": name, "email": email, "message": message},
            )

        save_inquiry(name, email, message, get_lang())
        flash(translate("contact.success"), "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", form={"name": "", "email": "", "message": ""})


if __name__ == "__main__":
    app.run(debug=True)
