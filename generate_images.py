"""プレースホルダー用 SVG 画像を一括生成するスクリプト"""
from pathlib import Path

BASE = Path(__file__).parent / "static" / "images"

COLORS = {
    "hero": ("#1a6b8a", "#87CEEB", "洋野町"),
    "star": ("#1a1a2e", "#ffd700", "★"),
    "food": ("#e76f51", "#f4a261", "食"),
    "sea": ("#0077b6", "#90e0ef", "海"),
    "photo": ("#6c5ce7", "#a29bfe", "📷"),
    "outdoor": ("#2d6a4f", "#95d5b2", "外"),
    "experience": ("#bc6c25", "#dda15e", "体"),
    "walk": ("#588157", "#a3b18a", "散"),
    "cafe": ("#6f4e37", "#d4a574", "☕"),
}

SPOT_COLORS = [
    ("#1a6b8a", "#48cae4", "天文台"),
    ("#0077b6", "#90e0ef", "海浜公園"),
    ("#e76f51", "#f4a261", "はまなす亭"),
    ("#bc6c25", "#dda15e", "大野木工"),
    ("#023e8a", "#caf0f8", "種市海岸"),
    ("#588157", "#a3b18a", "物産"),
    ("#6f4e37", "#d4a574", "カフェ"),
    ("#457b9d", "#a8dadc", "民宿"),
    ("#1d3557", "#457b9d", "ホテル"),
    ("#2d6a4f", "#95d5b2", "トレイル"),
]

CHOICE_LABELS = [
    "景色", "食べる", "海", "アクティブ", "カメラ", "食事", "癒やし", "体験",
    "星", "カフェ", "散策", "自然", "海を見る", "海鮮", "撮影", "体験",
    "絶景", "料理", "自然風景", "工房", "自由", "計画", "人気", "休息",
    "写真", "味", "リラックス", "発見", "緑", "店探し", "散歩", "イベント",
    "星空", "海産", "海岸", "アウトドア", "癒やし旅", "食べ歩き", "写真旅", "のんびり",
]

CARD_IMAGES = [
    ("nature.svg", "#0f4d66", "#48cae4", "自然"),
    ("food.svg", "#c44536", "#f4a261", "グルメ"),
    ("photo.svg", "#5f4b8b", "#a29bfe", "写真"),
    ("experience.svg", "#8b5a2b", "#dda15e", "体験"),
    ("forest.svg", "#2d6a4f", "#95d5b2", "森林"),
    ("walk.svg", "#588157", "#b7e4c7", "散策"),
    ("coast.svg", "#0077b6", "#90e0ef", "海岸"),
    ("cafe.svg", "#6f4e37", "#d4a574", "カフェ"),
    ("scenery.svg", "#1d3557", "#457b9d", "絶景"),
    ("seafood.svg", "#e76f51", "#f4a261", "海産"),
    ("workshop.svg", "#bc6c25", "#e9c46a", "工房"),
    ("relax.svg", "#023e8a", "#caf0f8", "リラックス"),
    ("stars.svg", "#1a1a2e", "#4cc9f0", "星空"),
    ("restaurant.svg", "#e63946", "#f4a261", "食事"),
    ("landscape.svg", "#386641", "#a7c957", "風景"),
    ("outdoor.svg", "#2d6a4f", "#52b788", "アウトドア"),
    ("healing.svg", "#1a6b8a", "#90e0ef", "癒やし"),
    ("gourmet.svg", "#d62828", "#fcbf49", "食べ歩き"),
    ("camera.svg", "#7209b7", "#b5179e", "カメラ"),
    ("adventure.svg", "#40916c", "#95d5b2", "冒険"),
]


def svg(bg1, bg2, label, w=400, h=300):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg1}"/>
      <stop offset="100%" style="stop-color:{bg2}"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#g)" rx="12"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        fill="white" font-size="{min(w,h)//4}" font-family="sans-serif">{label}</text>
</svg>'''


def main():
    dirs = [BASE, BASE / "icons", BASE / "questions", BASE / "choices", BASE / "choices" / "cards", BASE / "spots"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    (BASE / "hero.svg").write_text(svg(*COLORS["hero"], 800, 420), encoding="utf-8")

    for name, colors in COLORS.items():
        if name == "hero":
            continue
        (BASE / "icons" / f"{name}.svg").write_text(svg(*colors, 128, 128), encoding="utf-8")

    for i in range(1, 11):
        (BASE / "questions" / f"q{i}.svg").write_text(
            svg("#1a6b8a", "#48cae4", f"Q{i}", 400, 200), encoding="utf-8"
        )

    choice_files = [
        "scenery", "eat", "beach", "active", "camera", "meal", "heal", "craft",
        "stargazing", "cafe", "stroll", "nature", "ocean", "seafood", "snapshot", "activity",
        "landscape", "dish", "forest", "workshop", "free", "plan", "popular", "rest",
        "memory", "taste", "relax", "new", "green", "shop", "walk", "event",
        "night", "fish", "coast", "outdoor", "healing", "foodwalk", "phototrip", "slowtrip",
    ]
    for i, fname in enumerate(choice_files):
        label = CHOICE_LABELS[i] if i < len(CHOICE_LABELS) else fname
        (BASE / "choices" / f"{fname}.svg").write_text(
            svg("#457b9d", "#a8dadc", label, 160, 160), encoding="utf-8"
        )

    cards_dir = BASE / "choices" / "cards"
    for fname, c1, c2, label in CARD_IMAGES:
        (cards_dir / fname).write_text(svg(c1, c2, label, 480, 224), encoding="utf-8")

    spot_files = [
        "observatory", "kaihin", "hamanasu", "mokko", "coast",
        "souvenir", "cafe", "minshuku", "hotel", "trail",
    ]
    for i, fname in enumerate(spot_files):
        c = SPOT_COLORS[i]
        (BASE / "spots" / f"{fname}.svg").write_text(svg(c[0], c[1], c[2], 400, 240), encoding="utf-8")

    print("SVG images generated.")


if __name__ == "__main__":
    main()
