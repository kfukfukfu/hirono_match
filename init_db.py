"""
init_db.py
----------
データベースのテーブル作成と初期データ投入を行うスクリプト。
初回セットアップ時に `python init_db.py` を実行する。
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "hirono_match.db"

# --- テーブル定義 ---
SCHEMA = """
CREATE TABLE IF NOT EXISTS travel_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    image_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    image_url TEXT NOT NULL,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);

CREATE TABLE IF NOT EXISTS choice_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    choice_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    score INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (choice_id) REFERENCES choices(id),
    FOREIGN KEY (type_id) REFERENCES travel_types(id)
);

CREATE TABLE IF NOT EXISTS spots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    genre TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    address TEXT NOT NULL,
    official_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS spot_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spot_id INTEGER NOT NULL,
    type_id INTEGER NOT NULL,
    FOREIGN KEY (spot_id) REFERENCES spots(id),
    FOREIGN KEY (type_id) REFERENCES travel_types(id)
);
"""

# --- 旅行タイプ（8種類） ---
TRAVEL_TYPES = [
    ("星空ヒーラー", "自然や星空で癒やされたい人。静かな夜の空を見上げて、心身ともにリフレッシュする旅が向いています。", "images/icons/star.svg"),
    ("グルメ探究家", "地域の食を楽しみたい人。地元の食材や名物を味わい、食を通じて洋野町の魅力を発見しましょう。", "images/icons/food.svg"),
    ("シーサイドリラックス", "海辺でゆったり過ごしたい人。波音を聞きながら、のんびりと海の時間を楽しむ旅がぴったりです。", "images/icons/sea.svg"),
    ("フォトハンター", "写真映えする景色を楽しみたい人。絶景スポットを巡り、思い出に残る一枚を撮りたいあなたに。", "images/icons/photo.svg"),
    ("アウトドアチャレンジャー", "自然体験やアクティビティを楽しみたい人。体を動かしながら、洋野町の自然を体感しましょう。", "images/icons/outdoor.svg"),
    ("体験クリエイター", "地域ならではの体験をしたい人。木工や地元文化に触れ、旅先でしかできない体験を求めるタイプです。", "images/icons/experience.svg"),
    ("のんびり散策派", "自分のペースで町を巡りたい人。決まった予定に縛られず、好きな場所を自由に歩き回る旅が好きです。", "images/icons/walk.svg"),
    ("カフェブレイク派", "落ち着いた時間を過ごしたい人。カフェで一息つきながら、ゆったりとした時間を大切にします。", "images/icons/cafe.svg"),
]

# --- 診断質問（5問・各問1つ選択） ---
QUESTIONS = [
    ("旅行で重視したいことは？", "images/questions/q1.svg"),
    ("洋野町で楽しみたい時間の過ごし方は？", "images/questions/q2.svg"),
    ("旅行の理想のペースは？", "images/questions/q3.svg"),
    ("洋野町で撮りたい写真は？", "images/questions/q4.svg"),
    ("あなたの旅行スタイルは？", "images/questions/q5.svg"),
]

# 各質問の選択肢: (テキスト, 画像, [(type_id, score), ...])
# type_id は 1〜8（travel_types の id）
CHOICES = [
    # Q1
    [
        ("星空や自然を見る", "images/choices/stargazing.svg", [(1, 3), (4, 1)]),
        ("美味しいものを食べる", "images/choices/eat.svg", [(2, 3)]),
        ("写真を撮る", "images/choices/camera.svg", [(4, 3), (3, 1)]),
        ("地域ならではの体験をする", "images/choices/craft.svg", [(6, 3), (5, 1)]),
    ],
    # Q2
    [
        ("海辺でゆったり", "images/choices/beach.svg", [(3, 3), (1, 1)]),
        ("カフェで一息", "images/choices/cafe.svg", [(8, 3), (7, 1)]),
        ("町を散策", "images/choices/stroll.svg", [(7, 3), (4, 1)]),
        ("アクティビティ", "images/choices/active.svg", [(5, 3), (6, 1)]),
    ],
    # Q3
    [
        ("のんびり", "images/choices/free.svg", [(7, 3), (8, 1)]),
        ("計画的に巡る", "images/choices/plan.svg", [(6, 2), (2, 2)]),
        ("思いきり動く", "images/choices/nature.svg", [(5, 3), (6, 1)]),
        ("その場の気分で", "images/choices/relax.svg", [(3, 2), (1, 2)]),
    ],
    # Q4
    [
        ("星空", "images/choices/night.svg", [(1, 3), (4, 1)]),
        ("海の景色", "images/choices/ocean.svg", [(3, 3), (4, 1)]),
        ("料理", "images/choices/dish.svg", [(2, 3)]),
        ("体験の様子", "images/choices/workshop.svg", [(6, 3), (4, 1)]),
    ],
    # Q5
    [
        ("癒やし重視", "images/choices/healing.svg", [(1, 3), (3, 1)]),
        ("食べ歩き", "images/choices/foodwalk.svg", [(2, 3), (7, 1)]),
        ("記録に残す", "images/choices/memory.svg", [(4, 3), (6, 1)]),
        ("新しい発見", "images/choices/new.svg", [(6, 3), (5, 1)]),
    ],
]

# --- 洋野町スポット ---
SPOTS = [
    (
        "ひろのまきば天文台",
        "観光スポット",
        "天文台",
        "標高約300mの丘の上にあり、満天の星空を楽しめる洋野町の人気スポット。天体観望会も開催されています。",
        "images/spots/observatory.svg",
        "岩手県九戸郡洋野町中野字大野43-1",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "種市海浜公園",
        "観光スポット",
        "公園",
        "太平洋に面した広い海浜公園。キャンプ場や海水浴場があり、海辺でのんびり過ごせます。",
        "images/spots/kaihin.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "はまなす亭",
        "飲食店",
        "海鮮料理",
        "洋野町の新鮮な海の幸を味わえる食事処。地元の食材を使った定食や海鮮丼が人気です。",
        "images/spots/hamanasu.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "大野木工",
        "観光スポット",
        "体験施設",
        "地域の木工文化に触れられる施設。木工体験や作品展示を楽しめ、お土産も購入できます。",
        "images/spots/mokko.svg",
        "岩手県九戸郡洋野町中野字大野",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "種市海岸",
        "観光スポット",
        "海岸",
        "美しい海岸線が続く絶景スポット。夕日や波の音を楽しみながら、ゆったりとした時間を過ごせます。",
        "images/spots/coast.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "洋野町観光物産センター",
        "観光スポット",
        "物産",
        "地元の特産品やお土産が揃うセンター。洋野町の魅力を知る入り口として最適です。",
        "images/spots/souvenir.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "カフェ・マリンブルー",
        "飲食店",
        "カフェ",
        "海を望むカフェ。地元のコーヒーやスイーツを楽しみながら、穏やかな時間を過ごせます。",
        "images/spots/cafe.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "民宿 海の家",
        "宿泊施設",
        "民宿",
        "海の近くに位置する民宿。地元の家庭的なおもてなしと、新鮮な朝食が魅力です。",
        "images/spots/minshuku.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "ホテル洋野リゾート",
        "宿泊施設",
        "ホテル",
        "太平洋を一望できるリゾートホテル。温泉施設もあり、のんびりとした滞在に最適です。",
        "images/spots/hotel.svg",
        "岩手県九戸郡洋野町種市",
        "https://www.town.hirono.iwate.jp/",
    ),
    (
        "洋野トレイル",
        "観光スポット",
        "ハイキング",
        "自然豊かなトレッキングコース。四季折々の景色を楽しみながら、体を動かして町を巡れます。",
        "images/spots/trail.svg",
        "岩手県九戸郡洋野町",
        "https://www.town.hirono.iwate.jp/",
    ),
]

# スポットと旅行タイプの関連 (spot_index: [type_ids])
SPOT_TYPES = {
    0: [1, 4],       # 天文台 → 星空ヒーラー, フォトハンター
    1: [3, 5],       # 海浜公園 → シーサイド, アウトドア
    2: [2],          # はまなす亭 → グルメ
    3: [6, 4],       # 大野木工 → 体験, フォト
    4: [3, 1, 4],    # 種市海岸 → シーサイド, 星空, フォト
    5: [7, 2],       # 物産センター → 散策, グルメ
    6: [8, 7],       # カフェ → カフェ, 散策
    7: [3, 1],       # 民宿 → シーサイド, 星空
    8: [3, 8],       # ホテル → シーサイド, カフェ
    9: [5, 7, 1],    # トレイル → アウトドア, 散策, 星空
}


def init_db():
    """テーブル作成と初期データ投入"""
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(SCHEMA)

    # 旅行タイプ
    for name, desc, icon in TRAVEL_TYPES:
        cursor.execute(
            "INSERT INTO travel_types (name, description, icon) VALUES (?, ?, ?)",
            (name, desc, icon),
        )

    # 質問・選択肢・スコア
    for q_idx, (q_text, q_img) in enumerate(QUESTIONS):
        cursor.execute(
            "INSERT INTO questions (text, image_url) VALUES (?, ?)",
            (q_text, q_img),
        )
        question_id = cursor.lastrowid

        for c_text, c_img, scores in CHOICES[q_idx]:
            cursor.execute(
                "INSERT INTO choices (question_id, text, image_url) VALUES (?, ?, ?)",
                (question_id, c_text, c_img),
            )
            choice_id = cursor.lastrowid

            for type_id, score in scores:
                cursor.execute(
                    "INSERT INTO choice_scores (choice_id, type_id, score) VALUES (?, ?, ?)",
                    (choice_id, type_id, score),
                )

    # スポット
    for spot in SPOTS:
        cursor.execute(
            """INSERT INTO spots
               (name, category, genre, description, image_url, address, official_url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            spot,
        )

    # スポットとタイプの関連
    for spot_idx, type_ids in SPOT_TYPES.items():
        spot_id = spot_idx + 1
        for type_id in type_ids:
            cursor.execute(
                "INSERT INTO spot_types (spot_id, type_id) VALUES (?, ?)",
                (spot_id, type_id),
            )

    conn.commit()
    conn.close()
    print(f"データベースを初期化しました: {DB_PATH}")


if __name__ == "__main__":
    init_db()
