"""
app.py
------
「ひろのまっち」の Flask メインアプリケーション。
URL ルーティング、診断スコア計算、テンプレートへのデータ受け渡しを担当する。
"""

import os
from urllib.parse import quote

from flask import Flask, render_template, request, redirect, url_for, abort, session, jsonify

from database import get_db
from i18n import get_lang, translate, translate_value, localize_row, SUPPORTED_LANGS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-hirono-match-local")

RECOMMENDED_SPOT_LIMIT = 3


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
    }


@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    """ヘッダーの言語切替ボタン用。選択を session に保存して元のページへ戻る。"""
    if lang_code in SUPPORTED_LANGS:
        session["lang"] = lang_code
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for("index"))


@app.template_filter("map_url")
def map_url_filter(address):
    """住所から Google マップ検索 URL を生成する"""
    return f"https://www.google.com/maps/search/?api=1&query={quote(address)}"


def fetch_questions_with_choices():
    """診断用の質問と選択肢を DB から取得する"""
    db = get_db()
    questions = db.execute("SELECT * FROM questions ORDER BY id").fetchall()
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


def get_question_count():
    """診断の質問数を DB から取得する"""
    db = get_db()
    count = db.execute("SELECT COUNT(*) AS c FROM questions").fetchone()["c"]
    db.close()
    return count


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

    question_count = get_question_count()
    if len(choice_ids) != question_count:
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
    return len(question_ids) == question_count


def calculate_scores(choice_ids):
    """
    選択された choice_id のリストから、旅行タイプごとのスコアを計算する。
    返り値: スコア降順のリスト（name, description, icon, score, percentage を含む）
    """
    db = get_db()
    scores = {}

    for choice_id in choice_ids:
        rows = db.execute(
            """SELECT cs.type_id, cs.score, tt.name, tt.description, tt.icon,
                      tt.name_en, tt.description_en
               FROM choice_scores cs
               JOIN travel_types tt ON tt.id = cs.type_id
               WHERE cs.choice_id = ?""",
            (choice_id,),
        ).fetchall()

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

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def fetch_recommended_spots(type_id, limit=RECOMMENDED_SPOT_LIMIT):
    """診断タイプに関連するおすすめスポットを取得する（最大3件）"""
    db = get_db()
    spots = db.execute(
        """SELECT s.*
           FROM spots s
           JOIN spot_types st ON st.spot_id = s.id
           WHERE st.type_id = ?
           ORDER BY s.id
           LIMIT ?""",
        (type_id, limit),
    ).fetchall()
    db.close()
    return [
        localize_row(spot, ("name", "category", "genre", "description"))
        for spot in spots
    ]


def fetch_spot(spot_id):
    """スポット1件を取得する"""
    db = get_db()
    spot = db.execute("SELECT * FROM spots WHERE id = ?", (spot_id,)).fetchone()
    db.close()
    if spot is None:
        return None
    return localize_row(spot, ("name", "category", "genre", "description"))


@app.route("/")
def index():
    """トップ画面"""
    return render_template("index.html")


@app.route("/diagnosis")
def diagnosis():
    """診断画面（5問・1問ずつ表示・1つ選択）"""
    questions = fetch_questions_with_choices()
    return render_template("diagnosis.html", questions=questions)


@app.route("/result", methods=["POST"])
def result():
    """診断結果画面"""
    choice_ids = request.form.getlist("choice_id")

    if not validate_answers(choice_ids):
        return redirect(url_for("diagnosis"))

    choice_ids = [int(c) for c in choice_ids]
    ranked = calculate_scores(choice_ids)

    if not ranked:
        return redirect(url_for("diagnosis"))

    main_type = ranked[0]
    type_percentages = ranked[:3]

    return render_template(
        "result.html",
        main_type=main_type,
        type_percentages=type_percentages,
        recommended_spots=fetch_recommended_spots(main_type["id"]),
    )


@app.route("/spot/<int:spot_id>")
def spot_detail(spot_id):
    """スポット詳細画面"""
    spot = fetch_spot(spot_id)
    if spot is None:
        abort(404)
    return render_template("spot_detail.html", spot=spot)


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


if __name__ == "__main__":
    app.run(debug=True)
