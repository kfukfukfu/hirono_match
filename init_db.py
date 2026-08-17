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
    icon TEXT NOT NULL,
    name_en TEXT NOT NULL DEFAULT '',
    description_en TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    image_url TEXT NOT NULL,
    text_en TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS choices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    subtitle TEXT NOT NULL DEFAULT '',
    image_url TEXT NOT NULL,
    text_en TEXT NOT NULL DEFAULT '',
    subtitle_en TEXT NOT NULL DEFAULT '',
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
    official_url TEXT NOT NULL,
    map_url TEXT NOT NULL DEFAULT '',
    name_en TEXT NOT NULL DEFAULT '',
    category_en TEXT NOT NULL DEFAULT '',
    genre_en TEXT NOT NULL DEFAULT '',
    description_en TEXT NOT NULL DEFAULT '',
    area TEXT NOT NULL DEFAULT 'taneichi',
    public_transport_access TEXT NOT NULL DEFAULT 'good',
    visit_duration_min INTEGER NOT NULL DEFAULT 60,
    official_sns_url TEXT NOT NULL DEFAULT '',
    info_updated_at TEXT NOT NULL DEFAULT ''
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
# (名前, 説明, アイコン, 英語名, 英語説明)
TRAVEL_TYPES = [
    (
        "星空ヒーラー",
        "自然の中で静かな時間を楽しみたいタイプ。洋野町では星空観察や海辺の景色を楽しむ旅がおすすめです。",
        "images/types/star.jpg",
        "Starry Sky Healer",
        "For travelers who enjoy quiet moments in nature. Stargazing and coastal views in Hirono Town are highly recommended.",
    ),
    (
        "グルメ探究家",
        "地域ならではの食や名物を楽しみたいタイプ。洋野町の海産物や郷土料理を味わう旅がおすすめです。",
        "images/types/food.jpg",
        "Gourmet Explorer",
        "For travelers who love local food and specialties. Enjoy Hirono's fresh seafood and regional cuisine.",
    ),
    (
        "シーサイドリラックス",
        "海辺の景色やゆったりした時間を楽しみたいタイプ。種市海岸や海浜公園でのんびり過ごす旅がおすすめです。",
        "images/types/sea.jpg",
        "Seaside Relax",
        "For travelers who want ocean views and unhurried time. Relax at Taneichi Coast or the seaside park.",
    ),
    (
        "フォトハンター",
        "美しい景色や思い出を写真に残したいタイプ。絶景スポットを巡りながら撮影を楽しむ旅がおすすめです。",
        "images/types/photo.jpg",
        "Photo Hunter",
        "For travelers who capture memories through photography. Visit scenic spots across Hirono Town.",
    ),
    (
        "アウトドアチャレンジャー",
        "自然の中で活動したり挑戦したいタイプ。トレッキングや海辺のアクティビティを楽しむ旅がおすすめです。",
        "images/types/outdoor.jpg",
        "Outdoor Challenger",
        "For active travelers who enjoy nature. Try trekking and seaside activities in Hirono.",
    ),
    (
        "体験クリエイター",
        "その土地ならではの体験を楽しみたいタイプ。木工体験など洋野町ならではの体験がおすすめです。",
        "images/types/experience.jpg",
        "Experience Creator",
        "For travelers seeking hands-on local experiences such as traditional woodworking.",
    ),
    (
        "のんびり散策派",
        "町歩きや自分のペースで巡る旅を好むタイプ。路地裏や物産センターを巡る旅がおすすめです。",
        "images/types/walk.jpg",
        "Leisurely Walker",
        "For travelers who prefer exploring at their own pace. Stroll through town and local shops.",
    ),
    (
        "カフェブレイク派",
        "落ち着いた空間でゆっくり過ごしたいタイプ。海を望むカフェで一息つく旅がおすすめです。",
        "images/types/cafe.jpg",
        "Cafe Break",
        "For travelers who enjoy calm spaces. Take a break at cafes with ocean views.",
    ),
]

# --- 診断質問（5問） ---
# (日本語, 画像, 英語)
QUESTIONS = [
    ("旅の目的は？", "images/questions/q1.svg", "What is your travel goal?"),
    ("休日の過ごし方は？", "images/questions/q2.svg", "How do you spend your day off?"),
    ("旅で大事なのは？", "images/questions/q3.svg", "What matters most on a trip?"),
    ("気になる場所は？", "images/questions/q4.svg", "What places interest you?"),
    ("理想の旅は？", "images/questions/q5.svg", "What is your ideal trip?"),
]

# 各選択肢: (タイトル, サブタイトル, 画像, スコア, 英語タイトル, 英語サブタイトル)
CHOICES = [
    [
        ("星空・自然", "静かな景色や自然を楽しむ", "images/choices/cards/nature.svg", [(1, 3)], "Stars & Nature", "Quiet scenery and the outdoors"),
        ("ご当地グルメ", "地域ならではの味を楽しむ", "images/choices/cards/food.svg", [(2, 3)], "Local Food", "Flavors unique to the region"),
        ("思い出を残す", "写真や景色で旅を記録する", "images/choices/cards/photo.svg", [(4, 3)], "Capture Memories", "Record your trip in photos"),
        ("特別な体験", "ここでしかできない思い出", "images/choices/cards/experience.svg", [(6, 3)], "Special Experiences", "Memories only found here"),
    ],
    [
        ("自然へ出かける", "緑あふれる場所でリフレッシュ", "images/choices/cards/forest.svg", [(1, 3)], "Head into Nature", "Refresh among greenery"),
        ("のんびり散策", "好きなペースで街を歩く", "images/choices/cards/walk.svg", [(7, 3)], "Leisurely Stroll", "Explore town at your pace"),
        ("海辺でゆっくり", "海を眺めながら癒やされる", "images/choices/cards/coast.svg", [(3, 3)], "Relax by the Sea", "Unwind with ocean views"),
        ("カフェで休息", "落ち着いた時間を過ごす", "images/choices/cards/cafe.svg", [(8, 3)], "Rest at a Cafe", "Enjoy a calm moment"),
    ],
    [
        ("絶景", "印象に残る景色を求める", "images/choices/cards/scenery.svg", [(4, 3)], "Scenic Views", "Seek unforgettable landscapes"),
        ("地元の味", "その土地でしか味わえない食", "images/choices/cards/seafood.svg", [(2, 3), (7, 1)], "Local Flavors", "Taste what the region offers"),
        ("特別な経験", "新しい体験や発見", "images/choices/cards/workshop.svg", [(6, 3)], "New Experiences", "Discover something new"),
        ("リラックス", "ゆったりと心を休める", "images/choices/cards/relax.svg", [(8, 3), (3, 1)], "Relaxation", "Rest body and mind"),
    ],
    [
        ("星空スポット", "夜の空や自然の景観", "images/choices/cards/stars.svg", [(1, 3)], "Stargazing Spots", "Night skies and nature"),
        ("人気のお店", "地元の味を楽しめる場所", "images/choices/cards/restaurant.svg", [(7, 3), (2, 1)], "Popular Eateries", "Places locals love"),
        ("写真スポット", "思い出に残る一枚を", "images/choices/cards/landscape.svg", [(4, 3)], "Photo Spots", "Picture-perfect views"),
        ("自然体験", "体を動かして自然を感じる", "images/choices/cards/outdoor.svg", [(5, 3)], "Outdoor Activities", "Move and feel nature"),
    ],
    [
        ("癒やしの旅", "自然の中で心身をリセット", "images/choices/cards/healing.svg", [(3, 3), (1, 1)], "Healing Trip", "Reset mind and body in nature"),
        ("グルメ旅", "食べ歩きを楽しむ旅", "images/choices/cards/gourmet.svg", [(2, 3)], "Food Trip", "Explore through local cuisine"),
        ("写真旅", "絶景を巡って記録する旅", "images/choices/cards/camera.svg", [(4, 3)], "Photo Journey", "Tour scenic highlights"),
        ("アドベンチャー旅", "活動的に楽しむ旅", "images/choices/cards/adventure.svg", [(5, 3)], "Adventure Trip", "An active, energetic journey"),
    ],
]

# --- 洋野町スポット ---
# (name, category, genre, description, image, address, official_url, map_url,
#  name_en, category_en, genre_en, description_en)
SPOTS = [
    (
        "ひろのまきば天文台",
        "観光スポット",
        "天文台",
        "標高約300mの丘の上にあり、満天の星空を楽しめる洋野町の人気スポット。天体観望会も開催されています。",
        "images/spots/observatory.jpg",
        "岩手県九戸郡洋野町大野66-8-142",
        "https://ohnocampus.jp/search_facility/hirono-makiba-tenmondai/",
        "https://maps.app.goo.gl/DbPupFwt5GXorRpY9",
        "Hirono Makiba Observatory",
        "Sightseeing",
        "Observatory",
        "A popular hilltop observatory about 300m above sea level, offering spectacular stargazing. Public viewing events are held regularly.",
    ),
    (
        "種市海浜公園",
        "観光スポット",
        "公園",
        "太平洋に面した広い海浜公園。キャンプ場や海水浴場があり、海辺でのんびり過ごせます。",
        "images/spots/kaihin.jpg",
        "岩手県九戸郡洋野町種市18-105",
        "https://portal.town.hirono.iwate.jp/tour/tour-6744/",
        "https://maps.app.goo.gl/rz4xbTwpxxqDbm4CA",
        "Taneichi Seaside Park",
        "Sightseeing",
        "Park",
        "A spacious seaside park facing the Pacific Ocean with camping and swimming areas—perfect for a relaxed day by the water.",
    ),
    (
        "はまなす亭",
        "飲食店",
        "海鮮料理",
        "洋野町の新鮮な海の幸を味わえる食事処。地元の食材を使った定食や海鮮丼が人気です。",
        "images/spots/hamanasu.jpg",
        "岩手県九戸郡洋野町種市22-131-3",
        "https://uninosato-hamanasutei.com/",
        "https://maps.app.goo.gl/XgYVzU532nXc2sjEA",
        "Hamanasu-tei",
        "Restaurant",
        "Seafood",
        "A local dining spot serving Hirono's fresh seafood. Set meals and seafood bowls made with regional ingredients are popular.",
    ),
    (
        "大野木工",
        "観光スポット",
        "体験施設",
        "地域の木工文化に触れられる施設。木工体験や作品展示を楽しめ、お土産も購入できます。",
        "images/spots/mokko.jpg",
        "岩手県九戸郡洋野町大野58-12-30",
        "https://ohnocampus.jp/search_facility/mokkohin/",
        "https://maps.app.goo.gl/WZ6PoepXf83Yt7xk8",
        "Ohno Woodcraft Center",
        "Sightseeing",
        "Workshop",
        "Discover local woodworking culture through hands-on workshops, exhibitions, and souvenir shopping.",
    ),
    (
        "種市海岸",
        "観光スポット",
        "海岸",
        "美しい海岸線が続く絶景スポット。夕日や波の音を楽しみながら、ゆったりとした時間を過ごせます。",
        "images/spots/coast.jpg",
        "岩手県九戸郡洋野町種市 窓岩",
        "https://www.town.hirono.iwate.jp/doc/2006010101001/",
        "",
        "Taneichi Coast",
        "Sightseeing",
        "Coast",
        "A scenic stretch of coastline where you can enjoy sunsets and the sound of waves at a relaxed pace.",
    ),
    (
        "道の駅おおの",
        "観光スポット",
        "物産",
        "地元の特産品やお土産が揃うセンター。洋野町の魅力を知る入り口として最適です。",
        "images/spots/oono.jpg",
        "岩手県九戸郡洋野町種市22-133-11",
        "https://www.town.hirono.iwate.jp/doc/2015070700031/",
        "https://maps.app.goo.gl/RCDF9SgNqN9AJvXo8",
        "Michi-no-Eki Ohno (Roadside Station Ohno)",
        "Sightseeing",
        "Local Products",
        "A gateway to Hirono Town with local specialties and souvenirs—a great starting point for your visit.",
    ),
    (
        "マリンサイドスパ種市",
        "飲食店",
        "カフェ",
        "海を望むカフェ。地元のコーヒーやスイーツを楽しみながら、穏やかな時間を過ごせます。",
        "images/spots/marin.jpg",
        "岩手県九戸郡洋野町種市23-27-19",
        "https://www.marin-taneichi.com/",
        "https://maps.app.goo.gl/8kuT9yQCG3BjcaJ47",
        "Marine Side Spa Taneichi",
        "Restaurant",
        "Cafe & Spa",
        "Enjoy local coffee and sweets with ocean views, or relax at this seaside spa facility.",
    ),
    (
        "洋野町にぎわい創造交流施設ヒロノット",
        "観光スポット",
        "交流施設",
        "閉校した中学校をリノベーションした町の交流拠点施設。コワーキング、簡易宿泊、多目的室などがあり、地域とのつながりを感じられます。",
        "images/spots/hironott.jpg",
        "岩手県九戸郡洋野町種市7-116-21",
        "https://hirono-nigiwai.com/",
        "https://maps.app.goo.gl/5KdoknEo1TLirogn7",
        "Hirono Nigiwai Exchange Facility Hironott",
        "Sightseeing",
        "Exchange Facility",
        "A renovated former school serving as Hirono's community hub with coworking, simple lodging, and multipurpose rooms.",
    ),
    (
        "グリーンヒル大野",
        "宿泊施設",
        "ホテル",
        "太平洋を一望できるリゾートホテル。温泉施設もあり、のんびりとした滞在に最適です。",
        "images/spots/hotel.jpg",
        "岩手県九戸郡洋野町大野58-12-30",
        "https://ohnocampus.jp/search_facility/greenhill-ohno/",
        "https://maps.app.goo.gl/MVGUGu9eB7n8NFLv9",
        "Green Hill Ohno",
        "Accommodation",
        "Hotel",
        "A resort hotel with Pacific Ocean views and hot spring facilities—ideal for a relaxing stay.",
    ),
    (
        "洋野トレイル",
        "観光スポット",
        "ハイキング",
        "自然豊かなトレッキングコース。四季折々の景色を楽しみながら、体を動かして町を巡れます。",
        "images/spots/trail.jpg",
        "岩手県九戸郡洋野町角浜",
        "https://hirono-kankou.jp/topic/topic-156/",
        "",
        "Hirono Trail",
        "Sightseeing",
        "Hiking",
        "A nature-rich trekking route where you can explore the town while enjoying scenery through all four seasons.",
    ),
    (
        "たねいち産直ふれあい広場",
        "観光スポット",
        "産直・物産",
        "旬の野菜や海の幸が揃う複合産直施設。テナントの飲食店や専門店もあり、洋野町の食と土産を一度に楽しめます。",
        "images/spots/taneichi_market.jpg",
        "岩手県九戸郡洋野町種市32-95-1",
        "https://tane-choku.com/",
        "https://maps.app.goo.gl/search/たねいち産直ふれあい広場+洋野町",
        "Taneichi Farmers Market",
        "Sightseeing",
        "Local Market",
        "A complex direct-sales market with fresh produce, seafood, and tenant shops—your one-stop for Hirono food and souvenirs.",
    ),
    (
        "かめふく",
        "飲食店",
        "海鮮料理",
        "三陸の新鮮な魚介を使った海鮮定食や丼が人気の食事処。地元の海の幸を存分に味わえます。",
        "images/spots/kamefuku.jpg",
        "岩手県九戸郡洋野町種市32-47",
        "https://www.instagram.com/kamefuku_official0730/",
        "https://maps.app.goo.gl/search/かめふく+洋野町",
        "Kamefuku",
        "Restaurant",
        "Seafood",
        "A local favorite for seafood set meals and rice bowls made with fresh Sanriku catch.",
    ),
    (
        "ヒロノバ",
        "飲食店",
        "カフェ",
        "古民家を改装したカフェ兼レンタルスペース。サイフォンコーヒーや地元食材のスイーツ、ヒロノバーガーが楽しめます。",
        "images/spots/hironoba.jpg",
        "岩手県九戸郡洋野町種市23-27-73",
        "https://space-hironoba.com/",
        "https://maps.app.goo.gl/search/ヒロノバ+洋野町",
        "Hironoba",
        "Restaurant",
        "Cafe",
        "A renovated folk-house cafe and community space serving siphon coffee, local sweets, and the popular Hironoba burger.",
    ),
    (
        "café よるべ",
        "飲食店",
        "カフェ",
        "地元食材を活かしたランチが人気のリノベカフェ。鯖カレーや季節限定メニューで、のんびり過ごせます。",
        "images/spots/yorube.jpg",
        "岩手県九戸郡洋野町種市23-128-3",
        "https://portal.town.hirono.iwate.jp/feature/feature-60128/",
        "https://maps.app.goo.gl/search/cafeよるべ+洋野町",
        "café Yorube",
        "Restaurant",
        "Cafe",
        "A cozy renovated cafe known for local-ingredient lunches such as mackerel curry and seasonal specials.",
    ),
    (
        "中野食堂",
        "飲食店",
        "食堂",
        "JR種市駅近くの老舗食堂。ラーメンやかつ丼、海鮮料理など、地元の人にも愛される味を楽しめます。",
        "images/spots/nakano_shokudo.jpg",
        "岩手県九戸郡洋野町種市23-25-109",
        "https://hirono-kankou.jp/gourmet/gourmet-203/",
        "https://maps.app.goo.gl/search/なかの食堂+洋野町",
        "Nakano Shokudo",
        "Restaurant",
        "Diner",
        "A long-loved diner near Taneichi Station serving ramen, katsudon, and seafood favorites.",
    ),
    (
        "アグリパークおおさわ",
        "観光スポット",
        "ふるさと交流",
        "田園に囲まれたふるさと交流館。日帰り温泉、郷土料理、そば打ち体験や釣りなど、自然と交流を楽しめます。",
        "images/spots/agripark_osawa.jpg",
        "岩手県九戸郡洋野町種市69-16-1",
        "https://www.agripark.net/",
        "https://maps.app.goo.gl/search/アグリパークおおさわ+洋野町",
        "Agri Park Osawa",
        "Sightseeing",
        "Farm & Hot Spring",
        "A countryside exchange facility with day-use baths, local cuisine, soba-making, and fishing experiences.",
    ),
    (
        "café Cocoyo（ここよ）",
        "飲食店",
        "カフェ",
        "洋野町大野にあるアットホームなカフェ。グリーンカレーや手作りランチ定食など、地元の食材を使った料理が楽しめます。",
        "images/spots/cocoyo.jpg",
        "岩手県九戸郡洋野町大野71-3-8",
        "https://www.instagram.com/cafe.cocoyo",
        "https://maps.app.goo.gl/search/café+Cocoyo+洋野町",
        "café Cocoyo",
        "Restaurant",
        "Cafe",
        "A welcoming cafe in Ohno serving homemade lunches including green curry and set meals with local ingredients.",
    ),
    (
        "きのこの駅",
        "飲食店",
        "きのこ料理",
        "天然きのこを扱う長根商店が運営するきのこ料理専門店。自社栽培のきのこを使ったラーメンや鍋など、珍しいきのこ料理が味わえます。",
        "images/spots/kinoko_eki.jpg",
        "岩手県九戸郡洋野町有家9-13-7",
        "https://naganekinoko.wixsite.com/website",
        "https://maps.app.goo.gl/search/きのこの駅+洋野町",
        "Kinoko no Eki",
        "Restaurant",
        "Mushroom Cuisine",
        "A mushroom specialty restaurant run by Nagane Foods, offering rare mushroom dishes from their own cultivation.",
    ),
    (
        "大谷温泉",
        "観光スポット",
        "温泉",
        "久慈平岳の麓にある洋野町唯一の天然温泉。ラドン泉の名湯として、日帰り入浴や宿泊でゆったり過ごせます。",
        "images/spots/ooya_onsen.jpg",
        "岩手県九戸郡洋野町種市74-137-14",
        "http://www.ooyaonsen.com/",
        "https://maps.app.goo.gl/search/大谷温泉+洋野町",
        "Ooya Onsen",
        "Sightseeing",
        "Hot Spring",
        "Hirono's only natural hot spring at the foot of Mt. Kuji-Hira, known for its radon-rich waters and day-use baths.",
    ),
    (
        "陶芸工房",
        "観光スポット",
        "体験施設",
        "おおのキャンパス内の陶芸工房。てびねりやろくろ、絵付けなど、初心者でも気軽に陶芸体験ができます。",
        "images/spots/togei.jpg",
        "岩手県九戸郡洋野町大野58-12-30",
        "https://ohnocampus.jp/search_facility/togei/",
        "https://maps.app.goo.gl/WZ6PoepXf83Yt7xk8",
        "Pottery Workshop",
        "Sightseeing",
        "Workshop",
        "A pottery studio at Ohno Campus where beginners can try hand-building, wheel throwing, and glazing.",
    ),
    (
        "裂き織り工房",
        "観光スポット",
        "体験施設",
        "おおのキャンパス内の裂き織り工房。古布を裂いて織る南部の伝統工芸を、コースターなどの小作品から体験できます。",
        "images/spots/sakiori.jpg",
        "岩手県九戸郡洋野町大野58-12-30",
        "https://ohnocampus.jp/search_facility/sakiori/",
        "https://maps.app.goo.gl/WZ6PoepXf83Yt7xk8",
        "Sakiori Weaving Workshop",
        "Sightseeing",
        "Workshop",
        "A sakiori weaving studio at Ohno Campus where you can try the traditional craft of weaving with recycled fabric.",
    ),
]

SPOT_TYPES = {
    0: [1, 4],
    1: [3, 5],
    2: [2],
    3: [6, 4],
    4: [1, 3, 4],
    5: [7, 2],
    6: [8, 7],
    7: [7],
    8: [3],
    9: [5, 4],
    10: [2, 7],
    11: [2, 3],
    12: [8, 7],
    13: [8, 2],
    14: [2, 7],
    15: [6, 5],
    16: [8, 2, 7],
    17: [2],
    18: [1, 3],
    19: [6],
    20: [6],
}


# area, public_transport_access, visit_duration_min, official_sns_url, info_updated_at
SPOT_EXTRA = [
    ("ohno", "car_recommended", 90, "", "2026-03-01"),
    ("taneichi", "good", 120, "", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("ohno", "limited", 90, "", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("taneichi", "good", 90, "", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("ohno", "limited", 480, "", "2026-03-01"),
    ("taneichi", "car_recommended", 180, "", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("taneichi", "good", 60, "https://www.instagram.com/kamefuku_official0730/", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("taneichi", "good", 60, "", "2026-03-01"),
    ("taneichi", "good", 45, "", "2026-03-01"),
    ("ohno", "car_recommended", 120, "", "2026-03-01"),
    ("ohno", "limited", 60, "https://www.instagram.com/cafe.cocoyo", "2026-03-01"),
    ("yoke", "car_recommended", 60, "", "2026-03-01"),
    ("ohno", "car_recommended", 120, "", "2026-03-01"),
    ("ohno", "limited", 90, "", "2026-03-01"),
    ("ohno", "limited", 60, "", "2026-03-01"),
]


def init_db():
    """テーブル作成と初期データ投入"""
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(SCHEMA)

    for name, desc, icon, name_en, desc_en in TRAVEL_TYPES:
        cursor.execute(
            """INSERT INTO travel_types
               (name, description, icon, name_en, description_en)
               VALUES (?, ?, ?, ?, ?)""",
            (name, desc, icon, name_en, desc_en),
        )

    for q_text, q_img, q_text_en in QUESTIONS:
        cursor.execute(
            "INSERT INTO questions (text, image_url, text_en) VALUES (?, ?, ?)",
            (q_text, q_img, q_text_en),
        )
        question_id = cursor.lastrowid

        q_idx = QUESTIONS.index((q_text, q_img, q_text_en))
        for row in CHOICES[q_idx]:
            c_title, c_subtitle, c_img, scores, c_title_en, c_subtitle_en = row
            cursor.execute(
                """INSERT INTO choices
                   (question_id, text, subtitle, image_url, text_en, subtitle_en)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (question_id, c_title, c_subtitle, c_img, c_title_en, c_subtitle_en),
            )
            choice_id = cursor.lastrowid

            for type_id, score in scores:
                cursor.execute(
                    "INSERT INTO choice_scores (choice_id, type_id, score) VALUES (?, ?, ?)",
                    (choice_id, type_id, score),
                )

    for spot_idx, spot in enumerate(SPOTS):
        area, access, duration, sns_url, updated = SPOT_EXTRA[spot_idx]
        cursor.execute(
            """INSERT INTO spots
               (name, category, genre, description, image_url, address, official_url, map_url,
                name_en, category_en, genre_en, description_en,
                area, public_transport_access, visit_duration_min, official_sns_url, info_updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (*spot, area, access, duration, sns_url, updated),
        )

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
